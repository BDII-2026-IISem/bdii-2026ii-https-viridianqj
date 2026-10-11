from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from apps.common.status import RecordStatus
from apps.security.models import RefreshToken, User
from apps.security.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    TokenPairSerializer,
)
from apps.security.tokens import generate_refresh_value, hash_refresh_value

INVALID_CREDENTIALS = "Credenciales inválidas."
INVALID_TOKEN = "Token inválido."


def _find_user(username, email):
    """Si llegan username y email, ambos deben coincidir (email sin distinguir mayúsculas)."""
    queryset = User.objects.all()
    if username:
        queryset = queryset.filter(username=username)
    if email:
        queryset = queryset.filter(email__iexact=email)
    return queryset.first()


def create_refresh(user, device_info="", family_id=None):
    """Crea la fila en refresh_tokens; devuelve (valor_en_claro, fila)."""
    raw = generate_refresh_value()
    extra = {"family_id": family_id} if family_id else {}
    row = RefreshToken.objects.create(
        user=user,
        token_hash=hash_refresh_value(raw),
        device_info=device_info[:255],
        expires_at=RefreshToken.default_expiry(),
        **extra,
    )
    return raw, row


def issue_refresh(user, device_info="", family_id=None):
    """Devuelve solo el valor en claro (única vez que existe)."""
    return create_refresh(user, device_info, family_id)[0]


def token_payload(user, refresh_value):
    lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    return {
        "access": str(AccessToken.for_user(user)),
        "refresh": refresh_value,
        "token_type": "Bearer",
        "access_expires_in": int(lifetime.total_seconds()),
    }


def _unauthorized(message):
    return Response({"detail": message}, status=status.HTTP_401_UNAUTHORIZED)


def _revoke_family(family_id, now):
    """Apaga todos los tokens de la familia (reuso detectado)."""
    family = RefreshToken.objects.filter(family_id=family_id)
    family.filter(revoked_at__isnull=True).update(revoked_at=now)
    family.update(status=RecordStatus.INACTIVE, updated_at=now)


def _deactivate(row):
    row.status = RecordStatus.INACTIVE
    row.save(update_fields=["status", "updated_at"])


class LoginAPIView(APIView):
    authentication_classes = []  # un Bearer vencido no debe estorbar el login
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: TokenPairSerializer,
            401: OpenApiResponse(description="Credenciales inválidas."),
        },
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = _find_user(data.get("username"), data.get("email"))
        if user is None:
            User().set_password(data["password"])  # iguala el tiempo de respuesta
            return _unauthorized(INVALID_CREDENTIALS)
        if not user.check_password(data["password"]) or not user.is_active:
            return _unauthorized(INVALID_CREDENTIALS)

        update_last_login(None, user)
        refresh = issue_refresh(user, device_info=request.META.get("HTTP_USER_AGENT", ""))
        return Response(token_payload(user, refresh))


class RefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=RefreshSerializer,
        responses={
            200: TokenPairSerializer,
            401: OpenApiResponse(description="Token inválido, vencido o reutilizado."),
        },
        auth=[],
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_hash = hash_refresh_value(serializer.validated_data["refresh"])

        payload = None
        # Los cambios (revocar familia, inactivar, rotar) se confirman al salir del
        # bloque; por eso la respuesta 401 se devuelve DESPUÉS, no dentro.
        with transaction.atomic():
            row = next(iter(RefreshToken.objects.select_for_update().filter(token_hash=token_hash)), None)
            if row is not None:
                payload = self._rotate(row, request)

        if payload is None:
            return _unauthorized(INVALID_TOKEN)
        return Response(payload)

    @staticmethod
    def _rotate(row, request):
        now = timezone.now()

        # Reuso: ya rotado, revocado o inactivo -> se asume robo y cae la familia
        if (
            row.replaced_by_id is not None
            or row.revoked_at is not None
            or row.status != RecordStatus.ACTIVE
        ):
            _revoke_family(row.family_id, now)
            return None

        # Vencido: solo ese token (un vencimiento no prueba que fue copiado)
        if row.expires_at <= now:
            _deactivate(row)
            return None

        user = row.user
        if not user.is_active:
            _deactivate(row)
            return None

        device_info = request.META.get("HTTP_USER_AGENT", "") or row.device_info
        raw, new_row = create_refresh(user, device_info, family_id=row.family_id)
        row.replaced_by = new_row
        row.save(update_fields=["replaced_by", "updated_at"])
        return token_payload(user, raw)


def _revoke_token(row, now):
    """Cierra solo este token. Si ya tenía revoked_at, lo conserva."""
    if row.revoked_at is None:
        row.revoked_at = now
    row.status = RecordStatus.INACTIVE
    row.save(update_fields=["revoked_at", "status", "updated_at"])


class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            204: OpenApiResponse(description="Sesión cerrada."),
            401: OpenApiResponse(description="Token inexistente o ya rotado."),
        },
        auth=[],
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_hash = hash_refresh_value(serializer.validated_data["refresh"])

        closed = False
        # Igual que en refresh: los cambios se confirman al salir del bloque,
        # y la respuesta 401 se devuelve después.
        with transaction.atomic():
            row = next(iter(RefreshToken.objects.select_for_update().filter(token_hash=token_hash)), None)
            if row is not None:
                now = timezone.now()
                if row.replaced_by_id is not None:
                    _revoke_family(row.family_id, now)  # reuso de un token ya rotado
                else:
                    _revoke_token(row, now)
                    closed = True

        if not closed:
            return _unauthorized(INVALID_TOKEN)
        return Response(status=status.HTTP_204_NO_CONTENT)

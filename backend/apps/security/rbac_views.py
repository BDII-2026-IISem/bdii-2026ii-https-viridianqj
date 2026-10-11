from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.security.serializers import ProfileSerializer


class ProfileAPIView(RetrieveUpdateAPIView):
    """Perfil del usuario autenticado: no recibe id y no consulta la matriz RBAC."""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


# ───────────── ISS-23 · CRUD de la matriz RBAC ─────────────
from apps.common.viewsets import SoftDeleteModelViewSet  # noqa: E402

from .models import Resource, ResourceRole, Role, RoleUser, User  # noqa: E402
from .serializers import (  # noqa: E402
    ResourceRoleSerializer,
    ResourceSerializer,
    RoleSerializer,
    RoleUserSerializer,
    UserSerializer,
)


class _StatusFilterMixin:
    """Permite filtrar con ?status=ACTIVE / ?status=INACTIVE en el listado."""

    # AC-24-02: el detalle se publica como <int:pk>
    lookup_value_converter = "int"

    def get_queryset(self):
        qs = super().get_queryset()
        wanted = self.request.query_params.get("status")
        if wanted:
            qs = qs.filter(status=wanted.upper())
        return qs


class UserViewSet(_StatusFilterMixin, SoftDeleteModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer


class RoleViewSet(_StatusFilterMixin, SoftDeleteModelViewSet):
    queryset = Role.objects.all().order_by("id")
    serializer_class = RoleSerializer


class RoleUserViewSet(_StatusFilterMixin, SoftDeleteModelViewSet):
    queryset = RoleUser.objects.all().order_by("id")
    serializer_class = RoleUserSerializer


class ResourceViewSet(_StatusFilterMixin, SoftDeleteModelViewSet):
    queryset = Resource.objects.all().order_by("id")
    serializer_class = ResourceSerializer


class ResourceRoleViewSet(_StatusFilterMixin, SoftDeleteModelViewSet):
    queryset = ResourceRole.objects.all().order_by("id")
    serializer_class = ResourceRoleSerializer

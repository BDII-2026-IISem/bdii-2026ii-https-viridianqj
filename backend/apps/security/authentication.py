from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.common.status import RecordStatus


class BrasaGoJWTAuthentication(JWTAuthentication):
    """Valida firma y vigencia (clase base) y además exige usuario ACTIVE."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if user.status != RecordStatus.ACTIVE or not user.is_active:
            raise exceptions.AuthenticationFailed("Usuario inactivo.", code="user_inactive")
        return user


from drf_spectacular.extensions import OpenApiAuthenticationExtension  # noqa: E402


class BrasaGoJWTScheme(OpenApiAuthenticationExtension):
    """Le dice a Swagger cómo se autentica BrasaGoJWTAuthentication."""

    target_class = "apps.security.authentication.BrasaGoJWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}

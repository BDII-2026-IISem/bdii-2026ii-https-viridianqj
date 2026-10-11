from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if not attrs.get("username") and not attrs.get("email"):
            raise serializers.ValidationError("Debes enviar username o email.")
        return attrs


class TokenPairSerializer(serializers.Serializer):
    """Solo documenta la respuesta en OpenAPI."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    token_type = serializers.CharField()
    access_expires_in = serializers.IntegerField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=True)


from apps.security.models import User  # noqa: E402


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "avatar", "status"]
        read_only_fields = ["id", "username", "status"]

    def validate_email(self, value):
        value = value.strip().lower()
        taken = User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk)
        if taken.exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")
        return value


# ───────────── ISS-23 · CRUD de la matriz RBAC ─────────────
from django.contrib.auth import password_validation as _pv  # noqa: E402
from django.core.exceptions import ValidationError as _DjangoValidationError  # noqa: E402

from .models import Resource, ResourceRole, Role, RoleUser, User  # noqa: E402


class UserSerializer(serializers.ModelSerializer):
    # AC-23-01: la contraseña nunca se devuelve
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "status"]
        read_only_fields = ["id"]

    def validate_password(self, value):
        try:
            _pv.validate_password(value, self.instance)
        except _DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": ["Este campo es obligatorio."]})
        user = User(**validated_data)
        user.set_password(password)  # AC-23-02
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # AC-23-02
        instance.save()
        return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleUser
        fields = ["id", "role", "user", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "method", "route", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ResourceRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceRole
        fields = ["id", "resource", "role", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

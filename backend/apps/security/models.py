from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from apps.common.status import RecordStatus


class StoreUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("status", RecordStatus.ACTIVE)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("status", RecordStatus.ACTIVE)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField("correo electrónico", max_length=150, unique=True)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=8,
        choices=RecordStatus.choices,
        default=RecordStatus.ACTIVE,
        db_column="is_active",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StoreUserManager()

    # Reemplaza al BooleanField heredado: Django sigue leyendo user.is_active
    @property
    def is_active(self):
        return self.status == RecordStatus.ACTIVE

    @is_active.setter
    def is_active(self, value):
        self.status = RecordStatus.ACTIVE if value else RecordStatus.INACTIVE

    class Meta:
        db_table = "users"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=RecordStatus.values),
                name="users_is_active_valid",
            )
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

import uuid  # noqa: E402

from django.conf import settings  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.common.models import BrasaGoModel  # noqa: E402


class RefreshToken(BrasaGoModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="refresh_tokens",
        db_column="user_id",
    )
    token_hash = models.CharField(max_length=64, unique=True)
    device_info = models.CharField(max_length=255, blank=True, default="")
    family_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    replaced_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replacements",
    )
    # El diagrama llama a esta columna is_valid
    status = models.CharField(
        max_length=8,
        choices=RecordStatus.choices,
        default=RecordStatus.ACTIVE,
        db_column="is_valid",
    )

    class Meta:
        db_table = "refresh_tokens"
        verbose_name = "token de refresco"
        verbose_name_plural = "tokens de refresco"
        ordering = ["-created_at"]
        constraints = [BrasaGoModel.status_constraint("refresh_tokens_status_valid")]

    def __str__(self):
        return f"{self.user} · {self.family_id}"

    @property
    def is_usable(self):
        return (
            self.status == RecordStatus.ACTIVE
            and self.revoked_at is None
            and self.replaced_by_id is None
            and self.expires_at > timezone.now()
        )

    @classmethod
    def lifetime(cls):
        return settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

    @classmethod
    def default_expiry(cls):
        return timezone.now() + cls.lifetime()


class HttpMethod(models.TextChoices):
    GET = "GET", "GET"
    POST = "POST", "POST"
    PUT = "PUT", "PUT"
    PATCH = "PATCH", "PATCH"
    DELETE = "DELETE", "DELETE"


class Role(BrasaGoModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "roles"
        verbose_name = "rol"
        verbose_name_plural = "roles"
        ordering = ["name"]
        constraints = [BrasaGoModel.status_constraint("roles_is_active_valid")]

    def __str__(self):
        return self.name


class RoleUser(BrasaGoModel):
    role = models.ForeignKey(
        Role, on_delete=models.RESTRICT, related_name="assignments", db_column="role_id"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="role_links",
        db_column="user_id",
    )

    class Meta:
        db_table = "role_users"
        verbose_name = "rol de usuario"
        verbose_name_plural = "roles de usuarios"
        constraints = [
            models.UniqueConstraint(fields=["role", "user"], name="role_user_unique"),
            BrasaGoModel.status_constraint("role_users_is_active_valid"),
        ]

    def __str__(self):
        return f"usuario {self.user_id} → rol {self.role_id}"


class Resource(BrasaGoModel):
    method = models.CharField(max_length=10, choices=HttpMethod.choices)
    # Patrón de ruta tal como lo devuelve resolve(path).route (no el path con id)
    route = models.CharField(max_length=255, db_column="path")

    class Meta:
        db_table = "resources"
        verbose_name = "recurso"
        verbose_name_plural = "recursos"
        ordering = ["route", "method"]
        constraints = [
            models.UniqueConstraint(
                fields=["method", "route"], name="resource_method_route_uniq"
            ),
            models.CheckConstraint(
                condition=models.Q(method__in=HttpMethod.values),
                name="resources_method_valid",
            ),
            BrasaGoModel.status_constraint("resources_is_active_valid"),
        ]

    def __str__(self):
        return f"{self.method} {self.route}"


class ResourceRole(BrasaGoModel):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.RESTRICT,
        related_name="grants",
        db_column="resource_id",
    )
    role = models.ForeignKey(
        Role, on_delete=models.RESTRICT, related_name="grants", db_column="role_id"
    )

    class Meta:
        db_table = "resource_roles"
        verbose_name = "permiso de rol"
        verbose_name_plural = "permisos de roles"
        constraints = [
            models.UniqueConstraint(
                fields=["resource", "role"], name="resource_role_unique"
            ),
            BrasaGoModel.status_constraint("resource_roles_is_active_valid"),
        ]

    def __str__(self):
        return f"rol {self.role_id} → recurso {self.resource_id}"

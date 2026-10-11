from django.contrib import admin

# Register your models here.


from apps.security.models import RefreshToken  # noqa: E402


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "family_id", "expires_at", "revoked_at", "status")
    list_filter = ("status",)
    readonly_fields = ("token_hash", "family_id", "created_at", "updated_at")


from apps.security.models import Resource, ResourceRole, Role, RoleUser  # noqa: E402


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status")
    search_fields = ("name",)


@admin.register(RoleUser)
class RoleUserAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "status")
    list_filter = ("role", "status")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "method", "route", "status")
    list_filter = ("method", "status")
    search_fields = ("route",)


@admin.register(ResourceRole)
class ResourceRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "resource", "status")
    list_filter = ("role", "status")

from django.urls import path

from apps.security.auth_views import LoginAPIView, LogoutAPIView, RefreshAPIView
from apps.security.rbac_views import ProfileAPIView

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshAPIView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/profile/", ProfileAPIView.as_view(), name="auth-profile"),
]


# ───────────── ISS-23 · CRUD de la matriz RBAC ─────────────
from rest_framework.routers import SimpleRouter  # noqa: E402

from .rbac_views import (  # noqa: E402
    ResourceRoleViewSet,
    ResourceViewSet,
    RoleUserViewSet,
    RoleViewSet,
    UserViewSet,
)

router = SimpleRouter(use_regex_path=False)
router.register("users", UserViewSet, basename="user")
router.register("roles", RoleViewSet, basename="role")
router.register("role-users", RoleUserViewSet, basename="role-user")
router.register("resources", ResourceViewSet, basename="resource")
router.register("resource-roles", ResourceRoleViewSet, basename="resource-role")

urlpatterns += router.urls

from rest_framework.permissions import BasePermission

from apps.common.status import RecordStatus
from apps.security.models import ResourceRole


class HasResourceAccess(BasePermission):
    """User → RoleUser → Role → ResourceRole → Resource(method, route), todo ACTIVE."""

    message = "No tiene autorización para ejecutar esta operación."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.status != RecordStatus.ACTIVE:
            return False
        if request.method == "OPTIONS":  # preflight, no es una operación de negocio
            return True

        match = request.resolver_match
        if match is None:
            return False
        method = "GET" if request.method == "HEAD" else request.method.upper()

        active = RecordStatus.ACTIVE
        return ResourceRole.objects.filter(
            status=active,
            resource__status=active,
            resource__method=method,
            resource__route=match.route,
            role__status=active,
            role__assignments__user=user,
            role__assignments__status=active,
        ).exists()

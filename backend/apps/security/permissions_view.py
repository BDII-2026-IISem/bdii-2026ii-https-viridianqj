import re

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.status import RecordStatus
from apps.security.models import ResourceRole


def normalize_path(route: str) -> str:
    """Convierte la ruta de Django en '/api/recurso/:id/' para compararla en el cliente."""
    path = re.sub(r"\(\?P<[^>]+>[^)]+\)", ":id", route)
    path = re.sub(r"<[^>]+>", ":id", path)
    path = path.rstrip("$")
    return "/" + path.lstrip("/")


class PermissionsAPIView(APIView):
    """Concesiones activas del usuario autenticado: método, ruta normalizada y rol."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        active = RecordStatus.ACTIVE
        grants = (
            ResourceRole.objects.filter(
                status=active,
                resource__status=active,
                role__status=active,
                role__assignments__user=request.user,
                role__assignments__status=active,
            )
            .values_list("resource__method", "resource__route", "role__name")
            .distinct()
        )
        permissions = [
            {"method": method, "path": normalize_path(route), "role": role}
            for method, route, role in sorted(set(grants))
        ]
        return Response({"permissions": permissions})

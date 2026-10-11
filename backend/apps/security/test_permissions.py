from io import StringIO
from types import SimpleNamespace

from django.core.management import call_command
from django.test import override_settings
from django.urls import path, resolve
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework.views import APIView

from apps.common.status import RecordStatus
from apps.common.testing import authenticate, create_active_user, grant_access
from apps.security.models import Resource
from apps.security.permissions import HasResourceAccess


class ProbeView(APIView):
    permission_classes = [HasResourceAccess]

    def get(self, request, pk=None):
        return Response({"ok": True})

    def patch(self, request, pk=None):
        return Response({"ok": True})


# URLs solo para estos tests (ver override_settings más abajo)
urlpatterns = [
    path("api/probe/", ProbeView.as_view()),
    path("api/probe/<int:pk>/", ProbeView.as_view()),
]

DETAIL = "api/probe/<int:pk>/"


@override_settings(ROOT_URLCONF="apps.security.test_permissions")
class HasResourceAccessTests(APITestCase):
    def setUp(self):
        self.user = create_active_user("ana", "ana@example.com")

    def test_authenticated_without_grant_is_403(self):
        authenticate(self.client, self.user)
        response = self.client.get("/api/probe/7/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "No tiene autorización para ejecutar esta operación."
        )

    def test_no_user_is_401(self):
        self.assertEqual(self.client.get("/api/probe/7/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_active_grant_allows_any_id_of_the_route_pattern(self):
        grant_access(self.user, "GET", DETAIL)
        authenticate(self.client, self.user)
        self.assertEqual(self.client.get("/api/probe/7/").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get("/api/probe/15/").status_code, status.HTTP_200_OK)

    def test_turning_off_any_link_gives_403(self):
        links = grant_access(self.user, "GET", DETAIL)
        authenticate(self.client, self.user)
        self.assertEqual(self.client.get("/api/probe/7/").status_code, status.HTTP_200_OK)
        for name, obj in links.items():
            with self.subTest(name):
                obj.status = RecordStatus.INACTIVE
                obj.save()
                self.assertEqual(
                    self.client.get("/api/probe/7/").status_code, status.HTTP_403_FORBIDDEN
                )
                obj.status = RecordStatus.ACTIVE
                obj.save()
                self.assertEqual(
                    self.client.get("/api/probe/7/").status_code, status.HTTP_200_OK
                )

    def test_grant_is_per_method_and_head_counts_as_get(self):
        grant_access(self.user, "GET", DETAIL)
        authenticate(self.client, self.user)
        self.assertEqual(self.client.head("/api/probe/7/").status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.patch("/api/probe/7/", {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_grant_is_per_route_pattern(self):
        grant_access(self.user, "GET", DETAIL)
        authenticate(self.client, self.user)
        self.assertEqual(self.client.get("/api/probe/").status_code, status.HTTP_403_FORBIDDEN)

    def test_other_users_grant_does_not_leak(self):
        grant_access(self.user, "GET", DETAIL)
        other = create_active_user("luis", "luis@example.com")
        authenticate(self.client, other)
        self.assertEqual(self.client.get("/api/probe/7/").status_code, status.HTTP_403_FORBIDDEN)

    def test_options_is_allowed_without_grant(self):
        authenticate(self.client, self.user)
        self.assertEqual(self.client.options("/api/probe/7/").status_code, status.HTTP_200_OK)


class HasResourceAccessUnitTests(APITestCase):
    def setUp(self):
        self.user = create_active_user("ana", "ana@example.com")

    def test_inactive_user_is_denied_by_the_permission_itself(self):
        grant_access(self.user, "GET", DETAIL)
        self.user.status = RecordStatus.INACTIVE
        self.user.save()
        request = SimpleNamespace(
            user=self.user, method="GET", resolver_match=SimpleNamespace(route=DETAIL)
        )
        self.assertFalse(HasResourceAccess().has_permission(request, None))

    def test_missing_resolver_match_is_denied(self):
        request = SimpleNamespace(user=self.user, method="GET", resolver_match=None)
        self.assertFalse(HasResourceAccess().has_permission(request, None))


class SeededRoutesTests(APITestCase):
    def test_seeded_routes_match_what_the_resolver_returns(self):
        call_command("seed_rbac", verbosity=0, stdout=StringIO())
        for url in (
            "/api/clientes/",
            "/api/clientes/1/",
            "/api/domiciliarios/",
            "/api/domiciliarios/1/",
            "/api/pedidos/1/estado/",
        ):
            with self.subTest(url):
                route = resolve(url).route
                self.assertTrue(Resource.objects.filter(route=route).exists(), route)

    def test_profile_is_not_governed_by_the_matrix(self):
        # El perfil solo exige JWT; no consulta la matriz, así que no se siembra.
        call_command("seed_rbac", verbosity=0, stdout=StringIO())
        route = resolve("/api/auth/profile/").route
        self.assertFalse(Resource.objects.filter(route=route).exists(), route)

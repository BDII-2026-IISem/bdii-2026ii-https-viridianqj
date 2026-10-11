from django.core.management import call_command
from django.test import TestCase

from .models import Resource

COLLECTIONS = ("users", "roles", "role-users", "resources", "resource-roles")


class SeedRbacTests(TestCase):
    def test_seed_is_idempotent(self):
        call_command("seed_rbac")
        first = Resource.objects.count()
        call_command("seed_rbac")
        self.assertEqual(first, Resource.objects.count())

    def test_matrix_detail_routes_use_int_converter(self):  # AC-24-02
        call_command("seed_rbac")
        for name in COLLECTIONS:
            self.assertTrue(
                Resource.objects.filter(method="GET", route=f"api/{name}/<int:pk>/").exists(),
                name,
            )
            self.assertFalse(
                Resource.objects.filter(route=f"api/{name}/<str:pk>/").exists(), name
            )

    def test_auth_open_routes_are_not_seeded(self):
        call_command("seed_rbac")
        for route in ("api/auth/login/", "api/auth/refresh/", "api/auth/logout/", "api/auth/profile/"):
            self.assertFalse(Resource.objects.filter(route=route).exists(), route)

    def test_every_seeded_resource_is_active(self):
        call_command("seed_rbac")
        self.assertFalse(Resource.objects.exclude(status="ACTIVE").exists())

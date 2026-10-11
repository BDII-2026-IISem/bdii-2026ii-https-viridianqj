from io import StringIO
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models import RestrictedError
from django.test import TestCase
from django.urls import resolve

from apps.security.models import Resource, ResourceRole, Role, RoleUser, User


class RbacModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", "ana@example.com", "Clave-123456")
        self.role = Role.objects.create(name="ADMIN")
        self.resource = Resource.objects.create(method="GET", route="api/clientes/")

    def test_role_name_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Role.objects.create(name="ADMIN")

    def test_role_user_pair_unique(self):
        RoleUser.objects.create(role=self.role, user=self.user)
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoleUser.objects.create(role=self.role, user=self.user)

    def test_resource_method_route_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Resource.objects.create(method="GET", route="api/clientes/")
        # mismo path con otro método sí es otro recurso
        Resource.objects.create(method="POST", route="api/clientes/")

    def test_resource_role_pair_unique(self):
        ResourceRole.objects.create(resource=self.resource, role=self.role)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ResourceRole.objects.create(resource=self.resource, role=self.role)

    def test_status_check_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Role.objects.create(name="MALO", status="BAD")

    def test_role_with_links_cannot_be_deleted(self):
        RoleUser.objects.create(role=self.role, user=self.user)
        with self.assertRaises(RestrictedError):
            self.role.delete()


class SeedRbacTests(TestCase):
    def test_seed_stores_the_route_resolve_returns(self):
        call_command("seed_rbac", verbosity=0, stdout=StringIO())
        route = resolve("/api/pedidos/1/").route
        self.assertNotIn("1", route.replace("api/pedidos/", "").replace("<int:pk>", ""))
        self.assertTrue(Resource.objects.filter(method="GET", route=route).exists())
        self.assertTrue(Resource.objects.filter(method="DELETE", route=route).exists())

    def test_seed_is_idempotent(self):
        call_command("seed_rbac", verbosity=0, stdout=StringIO())
        total = Resource.objects.count()
        self.assertGreater(total, 0)
        call_command("seed_rbac", verbosity=0, stdout=StringIO())
        self.assertEqual(Resource.objects.count(), total)

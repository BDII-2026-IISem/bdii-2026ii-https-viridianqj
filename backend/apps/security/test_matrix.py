from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.common.testing import PASSWORD

from .models import Resource, ResourceRole, Role, RoleUser, User

MATRIX = {
    "api/users/": "api/users/<int:pk>/",
    "api/roles/": "api/roles/<int:pk>/",
    "api/role-users/": "api/role-users/<int:pk>/",
    "api/resources/": "api/resources/<int:pk>/",
    "api/resource-roles/": "api/resource-roles/<int:pk>/",
}


class SecurityMatrixApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="matrix-admin", email="matrix-admin@example.com", password=PASSWORD
        )
        role = Role.objects.create(name="MATRIX_ADMIN")
        RoleUser.objects.create(role=role, user=self.admin)
        for collection, detail in MATRIX.items():
            for method, route in (
                ("GET", collection), ("POST", collection),
                ("GET", detail), ("PATCH", detail), ("PUT", detail), ("DELETE", detail),
            ):
                res = Resource.objects.create(method=method, route=route)
                ResourceRole.objects.create(resource=res, role=role)
        self.client.force_authenticate(user=self.admin)

    def test_role_crud(self):
        created = self.client.post("/api/roles/", {"name": "bodega"}, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        role_id = created.data["id"]

        listing = self.client.get("/api/roles/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertIn("bodega", [r["name"] for r in listing.data["results"]]
                      if isinstance(listing.data, dict) else [r["name"] for r in listing.data])

        detail = self.client.get(f"/api/roles/{role_id}/")
        self.assertEqual(detail.data["name"], "bodega")

        patched = self.client.patch(f"/api/roles/{role_id}/", {"name": "bodega2"}, format="json")
        self.assertEqual(patched.data["name"], "bodega2")

        deleted = self.client.delete(f"/api/roles/{role_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        # AC-23-03: la fila sigue existiendo, solo queda INACTIVE
        self.assertEqual(Role.objects.get(pk=role_id).status, "INACTIVE")

    def test_user_password_is_hashed_and_hidden(self):
        resp = self.client.post(
            "/api/users/",
            {"username": "bodega1", "email": "bodega1@example.com", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", resp.data)  # AC-23-01
        user = User.objects.get(username="bodega1")
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))  # AC-23-02

    def test_user_weak_password_rejected(self):
        resp = self.client.post(
            "/api/users/",
            {"username": "debil", "email": "debil@example.com", "password": "123"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_requires_password_on_create(self):
        resp = self.client.post(
            "/api/users/", {"username": "sinclave", "email": "sc@example.com"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_role_resource_chain(self):
        role = self.client.post("/api/roles/", {"name": "bodega"}, format="json").data
        user = self.client.post(
            "/api/users/",
            {"username": "bodega1", "email": "bodega1@example.com", "password": PASSWORD},
            format="json",
        ).data

        def as_new_user(method="get"):
            c = APIClient()
            c.force_authenticate(user=User.objects.get(pk=user["id"]))
            return getattr(c, method)("/api/clientes/")

        # sin rol
        self.assertEqual(as_new_user().status_code, status.HTTP_403_FORBIDDEN)

        # solo RoleUser (AC-23-04)
        self.client.post("/api/role-users/", {"role": role["id"], "user": user["id"]}, format="json")
        self.assertEqual(as_new_user().status_code, status.HTTP_403_FORBIDDEN)

        # recurso registrado pero sin ResourceRole
        res = self.client.post(
            "/api/resources/", {"method": "GET", "route": "api/clientes/"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(as_new_user().status_code, status.HTTP_403_FORBIDDEN)

        # ResourceRole activo (AC-23-05)
        self.client.post(
            "/api/resource-roles/", {"resource": res.data["id"], "role": role["id"]}, format="json"
        )
        self.assertEqual(as_new_user().status_code, status.HTTP_200_OK)
        self.assertEqual(as_new_user("post").status_code, status.HTTP_403_FORBIDDEN)

    def test_matrix_requires_authentication(self):
        anon = APIClient()
        for collection in ("users", "roles", "role-users", "resources", "resource-roles"):
            self.assertEqual(
                anon.get(f"/api/{collection}/").status_code, status.HTTP_401_UNAUTHORIZED
            )

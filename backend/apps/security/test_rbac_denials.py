from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.common.testing import PASSWORD

from .models import Resource, ResourceRole, Role, RoleUser, User

URL = "/api/clientes/"
ROUTE = "api/clientes/"


class RbacTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rbac-user", email="rbac-user@example.com", password=PASSWORD
        )
        self.client.force_authenticate(user=self.user)

    def _grant_get(self):
        """Crea la cadena completa: rol, asignación, recurso y concesión."""
        role = Role.objects.create(name="rbac-role")
        link = RoleUser.objects.create(role=role, user=self.user)
        resource = Resource.objects.create(method="GET", route=ROUTE)
        grant = ResourceRole.objects.create(resource=resource, role=role)
        return role, link, resource, grant

    def test_missing_grant_is_403_and_missing_identity_is_401(self):
        # AC-25-03: identidad válida, sin concesión
        self.assertEqual(self.client.get(URL).status_code, status.HTTP_403_FORBIDDEN)
        # AC-25-02: sin identidad
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(URL).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_is_never_403(self):  # AC-25-04
        anon = APIClient()
        for url in (URL, "/api/productos/", "/api/pedidos/", "/api/roles/", "/api/users/"):
            with self.subTest(url):
                self.assertEqual(anon.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_any_inactive_link_denies(self):
        role, link, resource, grant = self._grant_get()
        self.assertEqual(self.client.get(URL).status_code, status.HTTP_200_OK)
        for label, obj in (
            ("rol", role),
            ("role_user", link),
            ("resource_role", grant),
            ("resource", resource),
        ):
            with self.subTest(label):
                type(obj).objects.filter(pk=obj.pk).update(status="INACTIVE")
                self.assertEqual(self.client.get(URL).status_code, status.HTTP_403_FORBIDDEN)
                type(obj).objects.filter(pk=obj.pk).update(status="ACTIVE")
                self.assertEqual(self.client.get(URL).status_code, status.HTTP_200_OK)

    def test_granting_get_does_not_grant_post(self):
        self._grant_get()
        self.assertEqual(self.client.get(URL).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(URL, {}, format="json").status_code,
                         status.HTTP_403_FORBIDDEN)

    def test_inactive_user_with_valid_jwt_is_401(self):
        self._grant_get()
        login = APIClient().post(
            "/api/auth/login/",
            {"username": "rbac-user", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        bearer = {"HTTP_AUTHORIZATION": f"Bearer {login.data['access']}"}
        anon = APIClient()
        self.assertEqual(anon.get(URL, **bearer).status_code, status.HTTP_200_OK)

        User.objects.filter(pk=self.user.pk).update(status="INACTIVE")
        # El token sigue bien firmado, pero la identidad ya no está vigente
        self.assertEqual(anon.get(URL, **bearer).status_code, status.HTTP_401_UNAUTHORIZED)

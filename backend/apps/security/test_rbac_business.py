from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.status import RecordStatus
from apps.common.testing import PASSWORD, create_active_user, grant, grant_crud

BUSINESS_URLS = (
    "/api/clientes/",
    "/api/productos/",
    "/api/productos/disponibles/",
    "/api/pedidos/",
    "/api/pagos/",
    "/api/reservas/",
    "/api/insumos/",
    "/api/recetas/",
    "/api/domiciliarios/",
    "/api/entregas/",
)


class BusinessRbacTests(APITestCase):
    def setUp(self):
        self.user = create_active_user("nora", "nora@example.com")

    def test_missing_grant_is_403_and_missing_identity_is_401(self):
        self.assertEqual(self.client.get("/api/clientes/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get("/api/clientes/").status_code, status.HTTP_403_FORBIDDEN)

    def test_granted_method_passes_and_other_methods_do_not(self):
        grant(self.user, "GET", "/api/clientes/")
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get("/api/clientes/").status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post("/api/clientes/", {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_grant_on_one_collection_does_not_open_another(self):
        grant(self.user, "GET", "/api/clientes/")
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get("/api/productos/").status_code, status.HTTP_403_FORBIDDEN)

    def test_grant_crud_covers_the_detail_route_for_any_id(self):
        grant_crud(self.user, "/api/clientes/", "/api/clientes/1/")
        self.client.force_authenticate(user=self.user)
        # 404 = el permiso pasó y el cliente 999 no existe; no es un 403
        self.assertEqual(self.client.get("/api/clientes/999/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get("/api/productos/999/").status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_role_blocks_business(self):
        role, _ = grant(self.user, "GET", "/api/clientes/")
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get("/api/clientes/").status_code, status.HTTP_200_OK)
        role.status = RecordStatus.INACTIVE
        role.save()
        self.assertEqual(self.client.get("/api/clientes/").status_code, status.HTTP_403_FORBIDDEN)

    def test_every_business_endpoint_rejects_anonymous_with_401(self):
        for url in BUSINESS_URLS:
            with self.subTest(url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_every_business_endpoint_rejects_ungranted_user_with_403(self):
        self.client.force_authenticate(user=self.user)
        for url in BUSINESS_URLS:
            with self.subTest(url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_and_open_endpoints_do_not_use_the_matrix(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get("/api/auth/profile/").status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=None)
        login = self.client.post(
            "/api/auth/login/", {"username": "nora", "password": "mala-clave"}, format="json"
        )
        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(login.data["detail"], "Credenciales inválidas.")
        self.assertEqual(self.client.get("/api/schema/").status_code, status.HTTP_200_OK)
        ok = self.client.post(
            "/api/auth/login/", {"username": "nora", "password": PASSWORD}, format="json"
        )
        self.assertEqual(ok.status_code, status.HTTP_200_OK)

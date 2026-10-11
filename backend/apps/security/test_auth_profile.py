from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.common.status import RecordStatus
from apps.common.testing import PASSWORD, create_active_user
from apps.security.models import User

LOGIN = "/api/auth/login/"
PROFILE = "/api/auth/profile/"


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = create_active_user("ana", "ana@example.com")

    def _access(self):
        response = self.client.post(
            LOGIN, {"username": "ana", "password": PASSWORD}, format="json"
        )
        return response.data["access"]

    def _auth(self, token=None):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token or self._access()}")

    def test_profile_requires_token_and_rejects_inactive_user(self):
        self.assertEqual(self.client.get(PROFILE).status_code, status.HTTP_401_UNAUTHORIZED)
        self._auth()
        ok = self.client.get(PROFILE)
        self.assertEqual(ok.status_code, status.HTTP_200_OK, ok.data)
        self.assertEqual(ok.data["username"], "ana")
        patch = self.client.patch(PROFILE, {"firstName": "Ana"}, format="json")
        self.assertEqual(patch.status_code, status.HTTP_200_OK, patch.data)
        self.user.status = RecordStatus.INACTIVE
        self.user.save()
        self.assertEqual(self.client.get(PROFILE).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_header_is_401_with_bearer_challenge(self):
        response = self.client.get(PROFILE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Bearer", response["WWW-Authenticate"])

    def test_get_returns_expected_fields_and_no_password(self):
        self._auth()
        response = self.client.get(PROFILE)
        self.assertEqual(
            set(response.data),
            {"id", "username", "email", "first_name", "last_name", "avatar", "status"},
        )
        self.assertNotIn("password", response.data)

    def test_patch_is_persisted(self):
        self._auth()
        response = self.client.patch(
            PROFILE, {"firstName": "Ana", "lastName": "Pérez"}, format="json"
        )
        self.assertEqual(response.data["first_name"], "Ana")
        self.user.refresh_from_db()
        self.assertEqual((self.user.first_name, self.user.last_name), ("Ana", "Pérez"))
        self.assertNotIn("password", response.data)

    def test_username_and_status_are_read_only(self):
        self._auth()
        response = self.client.patch(
            PROFILE, {"username": "hack", "status": "INACTIVE"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "ana")
        self.assertEqual(self.user.status, RecordStatus.ACTIVE)

    def test_email_is_normalized_and_unique_ignoring_case(self):
        create_active_user("luis", "luis@example.com")
        self._auth()
        clash = self.client.patch(PROFILE, {"email": "LUIS@EXAMPLE.COM"}, format="json")
        self.assertEqual(clash.status_code, status.HTTP_400_BAD_REQUEST)
        fresh = self.client.patch(PROFILE, {"email": "Nuevo@Example.COM"}, format="json")
        self.assertEqual(fresh.status_code, status.HTTP_200_OK, fresh.data)
        self.assertEqual(User.objects.get(username="ana").email, "nuevo@example.com")

    def test_only_get_and_patch_are_allowed(self):
        self._auth()
        for method in ("put", "post", "delete"):
            with self.subTest(method):
                response = getattr(self.client, method)(PROFILE, {}, format="json")
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_garbage_token_is_401(self):
        self._auth("esto.no.es.un.jwt")
        self.assertEqual(self.client.get(PROFILE).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_value_is_not_valid_as_access(self):
        refresh = self.client.post(
            LOGIN, {"username": "ana", "password": PASSWORD}, format="json"
        ).data["refresh"]
        self._auth(refresh)
        self.assertEqual(self.client.get(PROFILE).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_access_is_401(self):
        token = AccessToken.for_user(self.user)
        token.set_exp(from_time=timezone.now() - timedelta(hours=2), lifetime=timedelta(minutes=60))
        self._auth(str(token))
        self.assertEqual(self.client.get(PROFILE).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_api_requires_token(self):
        self.assertEqual(self.client.get("/api/productos/").status_code, status.HTTP_401_UNAUTHORIZED)

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.common.status import RecordStatus
from apps.common.testing import PASSWORD, create_active_user
from apps.security.models import RefreshToken
from apps.security.tokens import hash_refresh_value

URL = "/api/auth/login/"
INVALID = "Credenciales inválidas."


class LoginTests(APITestCase):
    def setUp(self):
        self.user = create_active_user("ana", "ana@example.com")

    def _login(self, **data):
        return self.client.post(URL, data, format="json", HTTP_USER_AGENT="BrasaGoTest/1.0")

    def test_login_with_username(self):
        response = self._login(username="ana", password=PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["refresh"])
        self.assertEqual(response.data["token_type"], "Bearer")
        self.assertEqual(response.data["access_expires_in"], 3600)

    def test_login_with_email_ignores_case(self):
        response = self._login(email="ANA@Example.COM", password=PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_username_and_email_must_match(self):
        response = self._login(username="ana", email="otra@example.com", password=PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_has_no_password(self):
        response = self._login(username="ana", password=PASSWORD)
        self.assertNotIn("password", response.data)
        self.assertNotIn(PASSWORD, str(response.data))

    def test_refresh_is_stored_only_hashed(self):
        response = self._login(username="ana", password=PASSWORD)
        refresh = response.data["refresh"]
        self.assertEqual(RefreshToken.objects.count(), 1)
        row = RefreshToken.objects.get()
        self.assertEqual(row.user_id, self.user.id)
        self.assertEqual(row.token_hash, hash_refresh_value(refresh))
        self.assertNotEqual(row.token_hash, refresh)
        self.assertEqual(row.status, RecordStatus.ACTIVE)
        self.assertEqual(row.device_info, "BrasaGoTest/1.0")
        self.assertTrue(row.is_usable)

    def test_access_token_is_a_valid_jwt(self):
        response = self._login(username="ana", password=PASSWORD)
        token = AccessToken(response.data["access"])
        self.assertEqual(int(token["user_id"]), self.user.id)

    def test_login_updates_last_login(self):
        self.assertIsNone(self.user.last_login)
        self._login(username="ana", password=PASSWORD)
        self.user.refresh_from_db()
        self.assertLessEqual(self.user.last_login, timezone.now())

    def test_each_login_creates_its_own_family(self):
        self._login(username="ana", password=PASSWORD)
        self._login(username="ana", password=PASSWORD)
        families = set(RefreshToken.objects.values_list("family_id", flat=True))
        self.assertEqual(len(families), 2)

    def test_inactive_user_is_401(self):
        self.user.status = RecordStatus.INACTIVE
        self.user.save()
        response = self._login(username="ana", password=PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(RefreshToken.objects.count(), 0)

    def test_bad_password_is_401(self):
        response = self._login(username="ana", password="otra-clave")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], INVALID)
        self.assertEqual(RefreshToken.objects.count(), 0)

    def test_unknown_user_gets_the_same_401(self):
        response = self._login(username="nadie", password=PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], INVALID)

    def test_missing_username_and_email_is_400(self):
        response = self._login(password=PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_bearer_does_not_block_login(self):
        response = self.client.post(
            URL,
            {"username": "ana", "password": PASSWORD},
            format="json",
            HTTP_AUTHORIZATION="Bearer token.vencido.o.basura",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

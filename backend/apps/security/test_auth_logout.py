from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.status import RecordStatus
from apps.common.testing import PASSWORD, create_active_user
from apps.security.models import RefreshToken
from apps.security.tokens import hash_refresh_value

LOGIN = "/api/auth/login/"
REFRESH = "/api/auth/refresh/"
LOGOUT = "/api/auth/logout/"


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = create_active_user("ana", "ana@example.com")

    def _login(self):
        response = self.client.post(
            LOGIN, {"username": "ana", "password": PASSWORD}, format="json"
        )
        return response.data["refresh"]

    def _refresh(self, token):
        return self.client.post(REFRESH, {"refresh": token}, format="json")

    def _logout(self, token, **extra):
        return self.client.post(LOGOUT, {"refresh": token}, format="json", **extra)

    def _row(self, raw):
        return RefreshToken.objects.get(token_hash=hash_refresh_value(raw))

    def test_logout_invalidates_refresh(self):
        refresh = self._login()
        self.assertEqual(self._logout(refresh).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self._refresh(refresh).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_closes_the_token(self):
        refresh = self._login()
        response = self._logout(refresh)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.content)
        row = self._row(refresh)
        self.assertEqual(row.status, RecordStatus.INACTIVE)
        self.assertIsNotNone(row.revoked_at)
        self.assertFalse(row.is_usable)

    def test_logout_is_idempotent_and_keeps_revoked_at(self):
        refresh = self._login()
        self._logout(refresh)
        first = self._row(refresh).revoked_at
        self.assertEqual(self._logout(refresh).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self._row(refresh).revoked_at, first)

    def test_unknown_token_is_401(self):
        response = self._logout("no-existe")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Token inválido.")

    def test_missing_refresh_is_400(self):
        response = self.client.post(LOGOUT, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_rotated_token_is_401_and_kills_family(self):
        a = self._login()
        b = self._refresh(a).data["refresh"]
        self.assertEqual(self._logout(a).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self._refresh(b).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_latest_token_after_rotation(self):
        a = self._login()
        b = self._refresh(a).data["refresh"]
        self.assertEqual(self._logout(b).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self._refresh(b).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self._refresh(a).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_only_closes_that_session(self):
        phone = self._login()
        laptop = self._login()
        self._logout(phone)
        self.assertEqual(self._refresh(laptop).status_code, status.HTTP_200_OK)

    def test_logout_ignores_a_bad_bearer(self):
        refresh = self._login()
        response = self._logout(refresh, HTTP_AUTHORIZATION="Bearer basura.vencida")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_of_expired_token_is_not_an_error(self):
        refresh = self._login()
        RefreshToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self._logout(refresh).status_code, status.HTTP_204_NO_CONTENT)

from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.common.status import RecordStatus
from apps.common.testing import PASSWORD, create_active_user
from apps.security.models import RefreshToken
from apps.security.tokens import hash_refresh_value

LOGIN = "/api/auth/login/"
REFRESH = "/api/auth/refresh/"


class RefreshRotationTests(APITestCase):
    def setUp(self):
        self.user = create_active_user("ana", "ana@example.com")

    def _login(self):
        response = self.client.post(
            LOGIN,
            {"username": "ana", "password": PASSWORD},
            format="json",
            HTTP_USER_AGENT="BrasaGoTest/1.0",
        )
        return response.data["refresh"]

    def _refresh(self, token, **extra):
        return self.client.post(REFRESH, {"refresh": token}, format="json", **extra)

    def _row(self, raw):
        return RefreshToken.objects.get(token_hash=hash_refresh_value(raw))

    def test_refresh_rotates_and_reuse_revokes_family(self):
        a = self._login()
        first = self._refresh(a)
        self.assertEqual(first.status_code, status.HTTP_200_OK, first.data)
        b = first.data["refresh"]
        self.assertNotEqual(a, b)
        self.assertEqual(self._refresh(a).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self._refresh(b).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_has_new_access_and_same_shape_as_login(self):
        response = self._refresh(self._login())
        self.assertEqual(response.data["token_type"], "Bearer")
        self.assertEqual(response.data["access_expires_in"], 3600)
        token = AccessToken(response.data["access"])
        self.assertEqual(int(token["user_id"]), self.user.id)

    def test_new_token_keeps_family_and_links_the_old_one(self):
        a = self._login()
        response = self._refresh(a)
        old, new = self._row(a), self._row(response.data["refresh"])
        self.assertEqual(old.family_id, new.family_id)
        self.assertEqual(old.replaced_by_id, new.id)
        self.assertEqual(new.device_info, "BrasaGoTest/1.0")
        self.assertTrue(new.is_usable)
        self.assertFalse(old.is_usable)

    def test_unknown_token_is_401(self):
        response = self._refresh("no-existe")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Token inválido.")

    def test_missing_refresh_is_400(self):
        response = self.client.post(REFRESH, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_token_is_401_and_does_not_revoke_family(self):
        a = self._login()
        RefreshToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self._refresh(a).status_code, status.HTTP_401_UNAUTHORIZED)
        row = self._row(a)
        self.assertEqual(row.status, RecordStatus.INACTIVE)
        self.assertIsNone(row.revoked_at)

    def test_inactive_user_is_401_and_token_is_deactivated(self):
        a = self._login()
        self.user.status = RecordStatus.INACTIVE
        self.user.save()
        self.assertEqual(self._refresh(a).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self._row(a).status, RecordStatus.INACTIVE)

    def test_revoked_token_is_401_and_kills_the_family(self):
        a = self._login()
        RefreshToken.objects.update(revoked_at=timezone.now())
        self.assertEqual(self._refresh(a).status_code, status.HTTP_401_UNAUTHORIZED)
        family = RefreshToken.objects.filter(family_id=self._row(a).family_id)
        self.assertFalse(family.exclude(status=RecordStatus.INACTIVE).exists())

    def test_reuse_only_affects_its_own_family(self):
        a1 = self._login()
        a2 = self._login()  # otra sesión = otra familia
        self._refresh(a1)
        self.assertEqual(self._refresh(a1).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self._refresh(a2).status_code, status.HTTP_200_OK)

    def test_invalid_bearer_does_not_block_refresh(self):
        response = self._refresh(self._login(), HTTP_AUTHORIZATION="Bearer basura.vencida")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

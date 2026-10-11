import hashlib
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import RestrictedError
from django.test import TestCase
from django.utils import timezone

from apps.common.status import RecordStatus
from apps.security.models import RefreshToken, User
from apps.security.tokens import generate_refresh_value, hash_refresh_value


class RefreshTokenModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", "ana@example.com", "Clave-123456")

    def _make(self, **overrides):
        raw = generate_refresh_value()
        data = {
            "user": self.user,
            "token_hash": hash_refresh_value(raw),
            "expires_at": RefreshToken.default_expiry(),
        }
        data.update(overrides)
        return raw, RefreshToken.objects.create(**data)

    def test_only_hash_is_stored(self):
        raw, token = self._make()
        self.assertNotEqual(token.token_hash, raw)
        self.assertEqual(len(token.token_hash), 64)
        self.assertEqual(token.token_hash, hashlib.sha256(raw.encode()).hexdigest())
        self.assertFalse(RefreshToken.objects.filter(token_hash=raw).exists())

    def test_helpers_generate_random_values(self):
        self.assertNotEqual(generate_refresh_value(), generate_refresh_value())
        self.assertEqual(hash_refresh_value("abc"), hash_refresh_value("abc"))

    def test_fresh_token_is_usable(self):
        _, token = self._make()
        self.assertTrue(token.is_usable)
        self.assertEqual(token.status, RecordStatus.ACTIVE)

    def test_unusable_states(self):
        _, replacement = self._make()
        cases = {
            "revocado": {"revoked_at": timezone.now()},
            "vencido": {"expires_at": timezone.now() - timedelta(seconds=1)},
            "reemplazado": {"replaced_by": replacement},
            "inactivo": {"status": RecordStatus.INACTIVE},
        }
        for name, extra in cases.items():
            with self.subTest(name):
                _, token = self._make(**extra)
                self.assertFalse(token.is_usable)

    def test_token_hash_is_unique(self):
        raw, _ = self._make()
        with self.assertRaises(IntegrityError), transaction.atomic():
            RefreshToken.objects.create(
                user=self.user,
                token_hash=hash_refresh_value(raw),
                expires_at=RefreshToken.default_expiry(),
            )

    def test_status_check_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._make(status="BAD")

    def test_each_session_has_its_own_family(self):
        _, first = self._make()
        _, second = self._make()
        self.assertNotEqual(first.family_id, second.family_id)

    def test_user_with_tokens_cannot_be_deleted(self):
        self._make()
        with self.assertRaises(RestrictedError):
            self.user.delete()

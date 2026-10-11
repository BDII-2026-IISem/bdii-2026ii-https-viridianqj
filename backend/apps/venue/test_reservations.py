from apps.common.testing import authenticate_as_admin
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.factories import make_world
from apps.common.status import RecordStatus
from apps.venue.models import DiningTable, Reservation

BASE = "/api/reservas/"


class ReservationApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)
        self.branch, self.table, self.customer, _ = make_world()

    def _payload(self, **overrides):
        data = {
            "client": self.customer.id,
            "table": self.table.id,
            "startsAt": "2026-11-01T19:00:00Z",
        }
        data.update(overrides)
        return data

    def test_default_duration_two_hours(self):
        response = self.client.post(BASE, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        reservation = Reservation.objects.get(pk=response.data["id"])
        self.assertEqual(reservation.ends_at - reservation.starts_at, timedelta(hours=2))
        self.assertEqual(response.data["reservation_status"], "PENDIENTE")
        self.assertEqual(response.data["table_name"], "Mesa 1")

    def test_overlap_rejected(self):
        self.client.post(BASE, self._payload(), format="json")
        clash = self.client.post(
            BASE, self._payload(startsAt="2026-11-01T20:00:00Z"), format="json"
        )
        self.assertEqual(clash.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("table", clash.data)

    def test_back_to_back_allowed(self):
        self.client.post(BASE, self._payload(), format="json")
        next_slot = self.client.post(
            BASE, self._payload(startsAt="2026-11-01T21:00:00Z"), format="json"
        )
        self.assertEqual(next_slot.status_code, status.HTTP_201_CREATED, next_slot.data)

    def test_other_table_allowed(self):
        other = DiningTable.objects.create(branch=self.branch, name="Mesa 2")
        self.client.post(BASE, self._payload(), format="json")
        response = self.client.post(BASE, self._payload(table=other.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_end_before_start_rejected(self):
        response = self.client.post(
            BASE, self._payload(endsAt="2026-11-01T18:00:00Z"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ends_at", response.data)

    def test_cancelled_does_not_block(self):
        first = self.client.post(BASE, self._payload(), format="json")
        patch = self.client.patch(
            f"{BASE}{first.data['id']}/", {"reservationStatus": "CANCELADA"}, format="json"
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK, patch.data)
        again = self.client.post(BASE, self._payload(), format="json")
        self.assertEqual(again.status_code, status.HTTP_201_CREATED, again.data)

    def test_delete_cancels_and_deactivates(self):
        first = self.client.post(BASE, self._payload(), format="json")
        response = self.client.delete(f"{BASE}{first.data['id']}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        reservation = Reservation.objects.get(pk=first.data["id"])
        self.assertEqual(reservation.reservation_status, "CANCELADA")
        self.assertEqual(reservation.status, RecordStatus.INACTIVE)

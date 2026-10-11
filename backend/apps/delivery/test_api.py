from apps.common.testing import authenticate_as_admin
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.factories import make_order, make_world
from apps.common.status import RecordStatus
from apps.delivery.models import Courier

COURIERS = "/api/domiciliarios/"
DELIVERIES = "/api/entregas/"


class DeliveryApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)
        branch, _, customer, dish = make_world()
        self.courier = Courier.objects.create(name="Pedro Moto")
        self.home_order = make_order(branch, customer, dish, channel="DOMICILIO")
        self.pickup_order = make_order(branch, customer, dish, channel="RECOGIDA")

    def _create(self, order=None):
        return self.client.post(
            DELIVERIES,
            {"order": (order or self.home_order).id, "courier": self.courier.id},
            format="json",
        )

    def test_create_for_domicilio(self):
        response = self._create()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["delivery_status"], "PENDIENTE")
        self.assertEqual(response.data["courier_name"], "Pedro Moto")

    def test_pickup_order_rejected(self):
        response = self._create(self.pickup_order)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order", response.data)

    def test_one_delivery_per_order(self):
        self._create()
        response = self._create()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_stamps_dates(self):
        delivery_id = self._create().data["id"]
        url = f"{DELIVERIES}{delivery_id}/"
        on_way = self.client.patch(url, {"deliveryStatus": "EN_CAMINO"}, format="json")
        self.assertEqual(on_way.status_code, status.HTTP_200_OK, on_way.data)
        self.assertIsNotNone(on_way.data["started_at"])
        self.assertIsNone(on_way.data["finished_at"])
        done = self.client.patch(url, {"deliveryStatus": "ENTREGADA"}, format="json")
        self.assertEqual(done.status_code, status.HTTP_200_OK, done.data)
        self.assertIsNotNone(done.data["finished_at"])

    def test_final_state_locked(self):
        delivery_id = self._create().data["id"]
        url = f"{DELIVERIES}{delivery_id}/"
        self.client.patch(url, {"deliveryStatus": "ENTREGADA"}, format="json")
        response = self.client.patch(url, {"deliveryStatus": "EN_CAMINO"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_courier_rejected(self):
        self.courier.status = RecordStatus.INACTIVE
        self.courier.save()
        response = self._create()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("courier", response.data)

    def test_courier_soft_delete(self):
        response = self.client.delete(f"{COURIERS}{self.courier.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.courier.refresh_from_db()
        self.assertEqual(self.courier.status, RecordStatus.INACTIVE)

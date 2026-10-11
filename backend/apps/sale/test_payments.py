from apps.common.testing import authenticate_as_admin
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.factories import make_order, make_world
from apps.common.status import RecordStatus
from apps.sale.models import Order, Payment

PAYMENTS = "/api/pagos/"


class PaymentApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)
        branch, _, customer, dish = make_world()
        self.order = make_order(branch, customer, dish, quantity=2)  # total 64000.00

    def _pay(self, amount, payment_status="PAGADO", **overrides):
        data = {
            "order": self.order.id,
            "method": "EFECTIVO",
            "amount": str(amount),
            "paymentStatus": payment_status,
        }
        data.update(overrides)
        return self.client.post(PAYMENTS, data, format="json")

    def test_create_sets_paid_at(self):
        response = self._pay("30000.00")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIsNotNone(response.data["paid_at"])
        self.assertEqual(response.data["payment_status"], "PAGADO")

    def test_partial_payments_up_to_total(self):
        self.assertEqual(self._pay("30000.00").status_code, status.HTTP_201_CREATED)
        self.assertEqual(self._pay("34000.00").status_code, status.HTTP_201_CREATED)
        extra = self._pay("1.00")
        self.assertEqual(extra.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", extra.data)

    def test_overpay_rejected(self):
        response = self._pay("64000.01")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pending_does_not_count(self):
        self.assertEqual(
            self._pay("64000.00", "PENDIENTE").status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(self._pay("64000.00").status_code, status.HTTP_201_CREATED)

    def test_amount_must_be_positive(self):
        self.assertEqual(self._pay("0").status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_pay_cancelled_order(self):
        self.order.void()
        response = self._pay("1000.00")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order", response.data)

    def test_delete_voids_payment(self):
        payment_id = self._pay("64000.00").data["id"]
        response = self.client.delete(f"{PAYMENTS}{payment_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(payment.payment_status, "ANULADO")
        self.assertEqual(payment.status, RecordStatus.INACTIVE)
        self.assertEqual(self._pay("64000.00").status_code, status.HTTP_201_CREATED)


class OrderStatusApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)
        branch, _, customer, dish = make_world()
        self.order = make_order(branch, customer, dish)
        self.url = f"/api/pedidos/{self.order.id}/estado/"

    def _move(self, new_status):
        return self.client.patch(self.url, {"orderStatus": new_status}, format="json")

    def test_happy_path(self):
        for step in ("EN_PREPARACION", "LISTO", "ENTREGADO"):
            response = self._move(step)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
            self.assertEqual(response.data["order_status"], step)

    def test_invalid_jump_rejected(self):
        response = self._move("LISTO")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order_status", response.data)

    def test_final_state_locked(self):
        for step in ("EN_PREPARACION", "LISTO", "ENTREGADO"):
            self._move(step)
        self.assertEqual(self._move("EN_PREPARACION").status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_voids_order(self):
        response = self._move("CANCELADO")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, Order.OrderStatus.CANCELADO)
        self.assertEqual(self.order.status, RecordStatus.INACTIVE)
        self.assertFalse(
            self.order.details.filter(status=RecordStatus.ACTIVE).exists()
        )

    def test_cancel_blocked_with_paid_payments(self):
        Payment.objects.create(
            order=self.order,
            method="EFECTIVO",
            amount=Decimal("10000.00"),
            paid_at=timezone.now(),
            payment_status="PAGADO",
        )
        response = self._move("CANCELADO")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, RecordStatus.ACTIVE)

    def test_unknown_order_404(self):
        response = self.client.patch(
            "/api/pedidos/999999/estado/", {"orderStatus": "LISTO"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

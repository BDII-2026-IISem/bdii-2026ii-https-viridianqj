from apps.common.testing import authenticate_as_admin
from decimal import Decimal
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from apps.client.models import Client
from apps.common.status import RecordStatus
from apps.product.models import Product
from apps.sale.models import Order, OrderDetail
from apps.venue.models import Branch, DiningTable

BASE = "/api/pedidos/"


class OrderRegisterApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)
        self.branch = Branch.objects.create(name="Sede Centro")
        self.table = DiningTable.objects.create(branch=self.branch, name="Mesa 1")
        self.customer = Client.objects.create(
            document_type="CC", document_number="1000000001", name="Cliente Prueba"
        )
        self.dish = Product.objects.create(
            sku="BRG-001", name="Bandeja paisa", price=Decimal("32000.00")
        )
        self.drink = Product.objects.create(
            sku="BRG-002", name="Jugo", price=Decimal("8000.00")
        )

    def _payload(self, items, **overrides):
        data = {
            "clientId": self.customer.id,
            "branchId": self.branch.id,
            "channel": "RECOGIDA",
            "items": items,
        }
        data.update(overrides)
        return data

    def test_register_snapshots_price_and_totals(self):
        response = self.client.post(
            BASE,
            self._payload(
                [
                    {"productId": self.dish.id, "quantity": 2},
                    {"productId": self.drink.id, "quantity": 1, "notes": "Sin hielo"},
                ]
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["subtotal"], "72000.00")
        self.assertEqual(response.data["total"], "72000.00")
        self.assertEqual(response.data["status"], RecordStatus.ACTIVE)
        self.assertEqual(response.data["order_status"], Order.OrderStatus.PENDIENTE)
        self.assertEqual(response.data["branch_name"], "Sede Centro")
        self.assertEqual(len(response.data["details"]), 2)
        self.dish.price = Decimal("99999.00")
        self.dish.save()
        line = OrderDetail.objects.get(order_id=response.data["id"], product=self.dish)
        self.assertEqual(line.unit_price, Decimal("32000.00"))
        self.assertEqual(line.total, Decimal("64000.00"))

    def test_table_and_channel_rules(self):
        items = [{"productId": self.dish.id, "quantity": 1}]
        no_table = self.client.post(
            BASE, self._payload(items, channel="MESA"), format="json"
        )
        self.assertEqual(no_table.status_code, status.HTTP_400_BAD_REQUEST)
        takeaway_with_table = self.client.post(
            BASE, self._payload(items, tableId=self.table.id), format="json"
        )
        self.assertEqual(takeaway_with_table.status_code, status.HTTP_400_BAD_REQUEST)
        other_branch = Branch.objects.create(name="Sede Norte")
        foreign_table = DiningTable.objects.create(branch=other_branch, name="Mesa 9")
        wrong_branch = self.client.post(
            BASE,
            self._payload(items, channel="MESA", tableId=foreign_table.id),
            format="json",
        )
        self.assertEqual(wrong_branch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        valid = self.client.post(
            BASE,
            self._payload(items, channel="MESA", tableId=self.table.id),
            format="json",
        )
        self.assertEqual(valid.status_code, status.HTTP_201_CREATED, valid.data)
        self.assertEqual(valid.data["table_name"], "Mesa 1")

    def test_inactive_client_product_or_branch_is_rejected(self):
        items = [{"productId": self.dish.id, "quantity": 1}]
        self.customer.status = RecordStatus.INACTIVE
        self.customer.save()
        by_client = self.client.post(BASE, self._payload(items), format="json")
        self.assertEqual(by_client.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client_id", by_client.data)
        self.customer.status = RecordStatus.ACTIVE
        self.customer.save()

        Product.objects.filter(pk=self.dish.pk).update(status=RecordStatus.INACTIVE)
        by_product = self.client.post(BASE, self._payload(items), format="json")
        self.assertEqual(by_product.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", by_product.data)
        Product.objects.filter(pk=self.dish.pk).update(status=RecordStatus.ACTIVE)

        Branch.objects.filter(pk=self.branch.pk).update(status=RecordStatus.INACTIVE)
        by_branch = self.client.post(BASE, self._payload(items), format="json")
        self.assertEqual(by_branch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("branch_id", by_branch.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_detail_failure_rolls_back_the_order(self):
        original = OrderDetail.save
        calls = {"count": 0}

        def fail_second(detail, *args, **kwargs):
            calls["count"] += 1
            if calls["count"] == 2:
                raise RuntimeError("fallo al guardar el detalle")
            return original(detail, *args, **kwargs)

        payload = self._payload(
            [
                {"productId": self.dish.id, "quantity": 1},
                {"productId": self.drink.id, "quantity": 1},
            ]
        )
        with patch.object(OrderDetail, "save", fail_second):
            with self.assertRaises(RuntimeError):
                self.client.post(BASE, payload, format="json")
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderDetail.objects.count(), 0)

    def test_empty_items_bad_quantity_and_unknown_product(self):
        empty = self.client.post(BASE, self._payload([]), format="json")
        self.assertEqual(empty.status_code, status.HTTP_400_BAD_REQUEST)
        zero = self.client.post(
            BASE, self._payload([{"productId": self.dish.id, "quantity": 0}]), format="json"
        )
        self.assertEqual(zero.status_code, status.HTTP_400_BAD_REQUEST)
        unknown = self.client.post(
            BASE, self._payload([{"productId": 999999, "quantity": 1}]), format="json"
        )
        self.assertEqual(unknown.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_without_client_is_allowed(self):
        payload = self._payload([{"productId": self.drink.id, "quantity": 3}])
        del payload["clientId"]
        response = self.client.post(BASE, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIsNone(response.data["client"])
        self.assertIsNone(response.data["client_name"])
        self.assertEqual(response.data["total"], "24000.00")

    def test_detail_keeps_historical_price(self):
        created = self.client.post(
            BASE,
            self._payload([{"productId": self.dish.id, "quantity": 1}]),
            format="json",
        )
        Product.objects.filter(pk=self.dish.pk).update(price=Decimal("99999.00"))
        detail = self.client.get(f"{BASE}{created.data['id']}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["details"][0]["unit_price"], "32000.00")
        self.assertEqual(detail.data["details"][0]["product_name"], "Bandeja paisa")

    def test_list_returns_the_registered_order(self):
        created = self.client.post(
            BASE,
            self._payload([{"productId": self.dish.id, "quantity": 1}]),
            format="json",
        )
        listed = self.client.get(BASE)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertTrue(any(row["id"] == created.data["id"] for row in listed.data))

    def test_void_is_idempotent(self):
        created = self.client.post(
            BASE,
            self._payload([{"productId": self.dish.id, "quantity": 2}]),
            format="json",
        )
        order_id = created.data["id"]
        first = self.client.delete(f"{BASE}{order_id}/")
        self.assertEqual(first.status_code, status.HTTP_204_NO_CONTENT)
        after_first = Order.objects.get(pk=order_id).updated_at
        second = self.client.delete(f"{BASE}{order_id}/")
        self.assertEqual(second.status_code, status.HTTP_204_NO_CONTENT)
        order = Order.objects.get(pk=order_id)
        self.assertEqual(order.updated_at, after_first)
        self.assertEqual(order.status, RecordStatus.INACTIVE)
        self.assertEqual(order.order_status, Order.OrderStatus.CANCELADO)
        self.assertEqual(
            order.details.filter(status=RecordStatus.INACTIVE).count(), 1
        )
        self.assertEqual(Order.objects.count(), 1)

    def test_detail_only_allows_get_and_delete(self):
        created = self.client.post(
            BASE,
            self._payload([{"productId": self.dish.id, "quantity": 1}]),
            format="json",
        )
        url = f"{BASE}{created.data['id']}/"
        self.assertEqual(
            self.client.put(url, {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.patch(url, {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.get(f"{BASE}999999/").status_code, status.HTTP_404_NOT_FOUND
        )

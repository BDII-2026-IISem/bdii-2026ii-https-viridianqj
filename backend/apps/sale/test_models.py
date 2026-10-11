from decimal import Decimal

from django.db.models import RestrictedError
from django.test import TestCase

from apps.client.models import Client
from apps.common.status import RecordStatus
from apps.product.models import Product
from apps.sale.models import Order, OrderDetail
from apps.venue.models import Branch


class OrderDetailTests(TestCase):
    def setUp(self):
        branch = Branch.objects.create(name="Sede Centro")
        self.customer = Client.objects.create(
            document_type="CC", document_number="1000000001", name="Cliente Prueba"
        )
        self.product = Product.objects.create(
            sku="BRG-001", name="Bandeja paisa", price=Decimal("32000.00")
        )
        self.order = Order.objects.create(
            client=self.customer, branch=branch, channel=Order.Channel.RECOGIDA
        )
        self.detail = OrderDetail.objects.create(
            order=self.order, product=self.product,
            quantity=3, unit_price=self.product.price,
        )

    def test_total_is_quantity_times_unit_price(self):
        self.assertEqual(self.detail.total, Decimal("96000.00"))

    def test_historical_price_is_preserved(self):
        self.product.price = Decimal("40000.00")
        self.product.save()
        self.detail.refresh_from_db()
        self.assertEqual(self.detail.unit_price, Decimal("32000.00"))
        self.assertEqual(self.detail.total, Decimal("96000.00"))

    def test_foreign_keys_restrict_delete(self):
        with self.assertRaises(RestrictedError):
            self.product.delete()

    def test_no_many_to_many_on_product(self):
        self.assertFalse(any(f.many_to_many for f in Product._meta.get_fields()))

    def test_void_deactivates_order_and_details(self):
        self.order.void()
        self.order.refresh_from_db()
        self.detail.refresh_from_db()
        self.assertEqual(self.order.status, RecordStatus.INACTIVE)
        self.assertEqual(self.order.order_status, Order.OrderStatus.CANCELADO)
        self.assertEqual(self.detail.status, RecordStatus.INACTIVE)

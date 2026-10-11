import json
from decimal import Decimal

from django.test import TestCase
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from apps.client.models import Client
from apps.product.models import Product
from apps.sale.models import Order, OrderDetail
from apps.sale.serializers import OrderSerializer
from apps.venue.models import Branch


class OrderSerializerTests(TestCase):
    def setUp(self):
        branch = Branch.objects.create(name="Sede Centro")
        customer = Client.objects.create(
            document_type="CC", document_number="1000000001", name="Cliente Prueba"
        )
        product = Product.objects.create(
            sku="BRG-001", name="Bandeja paisa", price=Decimal("32000.00")
        )
        self.order = Order.objects.create(
            client=customer, branch=branch, channel=Order.Channel.RECOGIDA
        )
        OrderDetail.objects.create(
            order=self.order, product=product, quantity=2, unit_price=product.price
        )

    def test_order_exposes_names_and_details(self):
        content = CamelCaseJSONRenderer().render(OrderSerializer(self.order).data)
        data = json.loads(content)
        self.assertEqual(data["branchName"], "Sede Centro")
        self.assertEqual(data["clientName"], "Cliente Prueba")
        self.assertIsNone(data["tableName"])
        self.assertEqual(len(data["details"]), 1)
        self.assertEqual(data["details"][0]["productName"], "Bandeja paisa")
        self.assertEqual(data["details"][0]["total"], "64000.00")
        self.assertIn("orderedAt", data)

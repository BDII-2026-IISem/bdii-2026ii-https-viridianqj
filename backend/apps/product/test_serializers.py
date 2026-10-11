from decimal import Decimal

from django.test import TestCase
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from apps.product.models import Product
from apps.product.serializers import ProductSerializer


class ProductSerializerTests(TestCase):
    def test_json_uses_camel_case(self):
        product = Product.objects.create(
            sku="BRG-001", name="Bandeja paisa", price=Decimal("32000.00")
        )
        content = CamelCaseJSONRenderer().render(ProductSerializer(product).data)
        self.assertIn(b"createdAt", content)
        self.assertNotIn(b"created_at", content)

    def test_negative_price_is_rejected(self):
        serializer = ProductSerializer(data={"sku": "BRG-002", "name": "Jugo", "price": "-1"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_sku_must_be_unique(self):
        Product.objects.create(sku="BRG-003", name="Sopa", price=Decimal("9000.00"))
        serializer = ProductSerializer(data={"sku": "BRG-003", "name": "Otra", "price": "1000"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("sku", serializer.errors)

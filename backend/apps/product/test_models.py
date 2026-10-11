from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.common.status import RecordStatus
from apps.product.models import Product


class ProductModelTests(TestCase):
    def test_default_status_is_active(self):
        product = Product.objects.create(
            sku="BRG-100", name="Arepa", price=Decimal("5000.00")
        )
        self.assertEqual(product.status, RecordStatus.ACTIVE)

    def test_duplicate_sku_is_rejected(self):
        Product.objects.create(sku="BRG-101", name="Empanada", price=Decimal("3000.00"))
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    sku="BRG-101", name="Otra", price=Decimal("1000.00")
                )

    def test_duplicate_name_is_allowed(self):
        Product.objects.create(sku="BRG-102", name="Jugo", price=Decimal("4000.00"))
        Product.objects.create(sku="BRG-103", name="Jugo", price=Decimal("4500.00"))
        self.assertEqual(Product.objects.filter(name="Jugo").count(), 2)

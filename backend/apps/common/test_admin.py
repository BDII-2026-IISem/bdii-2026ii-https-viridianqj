from decimal import Decimal

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from apps.client.models import Client
from apps.product.models import Product
from apps.sale.models import Order, OrderDetail
from apps.security.models import User
from apps.venue.models import Branch, DiningTable

ADMIN_MODELS = [Client, Product, Branch, DiningTable, Order, OrderDetail]


def admin_url(model, action, *args):
    name = f"admin:{model._meta.app_label}_{model._meta.model_name}_{action}"
    return reverse(name, args=args)


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="admin_test",
            email="admin@example.com",
            password="Clave-Segura-123",
        )

    def setUp(self):
        self.client.force_login(self.superuser)

    def test_models_are_registered(self):
        for model in ADMIN_MODELS:
            self.assertIn(model, admin.site._registry)

    def test_changelists_open(self):
        for model in ADMIN_MODELS:
            response = self.client.get(admin_url(model, "changelist"))
            self.assertEqual(response.status_code, 200, model.__name__)

    def test_orders_and_details_cannot_be_added(self):
        for model in (Order, OrderDetail):
            response = self.client.get(admin_url(model, "add"))
            self.assertEqual(response.status_code, 403, model.__name__)

    def test_order_change_page_opens_but_delete_is_forbidden(self):
        branch = Branch.objects.create(name="Sede Centro")
        product = Product.objects.create(
            sku="BRG-001", name="Bandeja paisa", price=Decimal("32000.00")
        )
        order = Order.objects.create(branch=branch, channel=Order.Channel.RECOGIDA)
        OrderDetail.objects.create(
            order=order, product=product, quantity=1, unit_price=product.price
        )
        change = self.client.get(admin_url(Order, "change", order.pk))
        self.assertEqual(change.status_code, 200)
        delete = self.client.get(admin_url(Order, "delete", order.pk))
        self.assertEqual(delete.status_code, 403)

"""Datos de prueba compartidos por los tests de la extensión del negocio."""
from decimal import Decimal

from django.utils import timezone

from apps.client.models import Client
from apps.product.models import Product
from apps.sale.models import Order
from apps.venue.models import Branch, DiningTable


def make_world():
    branch = Branch.objects.create(name="Sede Centro")
    table = DiningTable.objects.create(branch=branch, name="Mesa 1")
    customer = Client.objects.create(
        document_type="CC", document_number="1000000001", name="Cliente Prueba"
    )
    dish = Product.objects.create(
        sku="BRG-001", name="Bandeja paisa", price=Decimal("32000.00")
    )
    return branch, table, customer, dish


def make_order(branch, customer, dish, channel="RECOGIDA", table=None, quantity=1):
    return Order.objects.register(
        client=customer,
        branch=branch,
        table=table,
        channel=channel,
        ordered_at=timezone.now(),
        items=[{"product_id": dish.id, "quantity": quantity, "notes": None}],
    )

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.common.status import RecordStatus
from apps.product.models import Product


class OrderQuerySet(models.QuerySet):
    def register(self, *, client, branch, table, channel, ordered_at, items):
        if not items:
            raise ValidationError({"items": ["El pedido requiere al menos un producto."]})
        for item in items:
            if int(item["quantity"]) < 1:
                raise ValidationError({"items": ["La cantidad debe ser al menos 1."]})

        is_table_order = channel == self.model.Channel.MESA
        if is_table_order and table is None:
            raise ValidationError({"table_id": ["Un pedido en mesa requiere mesa."]})
        if not is_table_order and table is not None:
            raise ValidationError({"table_id": ["Solo los pedidos en mesa llevan mesa."]})

        with transaction.atomic():
            if branch.status != RecordStatus.ACTIVE:
                raise ValidationError({"branch_id": ["La sede debe estar ACTIVE."]})
            if client is not None and client.status != RecordStatus.ACTIVE:
                raise ValidationError({"client_id": ["El cliente debe estar ACTIVE."]})
            if table is not None:
                if table.branch_id != branch.id:
                    raise ValidationError({"table_id": ["La mesa no pertenece a la sede."]})
                if table.status != RecordStatus.ACTIVE:
                    raise ValidationError({"table_id": ["La mesa debe estar ACTIVE."]})

            product_ids = {item["product_id"] for item in items}
            products = {p.id: p for p in Product.objects.filter(pk__in=product_ids)}
            if len(products) != len(product_ids):
                raise ValidationError({"items": ["Hay productos que no existen."]})
            for product in products.values():
                if product.status != RecordStatus.ACTIVE:
                    raise ValidationError(
                        {"items": [f"El producto {product.name} no está ACTIVE."]}
                    )

            lines = []
            subtotal = Decimal("0.00")
            for item in items:
                product = products[item["product_id"]]
                quantity = int(item["quantity"])
                line_total = (product.price * quantity).quantize(Decimal("0.01"))
                lines.append((product, quantity, line_total, item.get("notes") or None))
                subtotal += line_total
            subtotal = subtotal.quantize(Decimal("0.01"))

            order = self.model(
                client=client,
                branch=branch,
                table=table,
                channel=channel,
                ordered_at=ordered_at,
                subtotal=subtotal,
                total=subtotal,
            )
            order.save()
            for product, quantity, line_total, notes in lines:
                order.details.create(
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    total=line_total,
                    notes=notes,
                )
            return order


class OrderManager(models.Manager.from_queryset(OrderQuerySet)):
    pass

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from apps.client.models import Client
from apps.common.models import BrasaGoModel
from apps.common.status import RecordStatus
from apps.product.models import Product
from apps.sale.managers import OrderManager
from apps.venue.models import Branch, DiningTable


class Order(BrasaGoModel):
    class Channel(models.TextChoices):
        MESA = "MESA", "Mesa"
        RECOGIDA = "RECOGIDA", "Recogida"
        DOMICILIO = "DOMICILIO", "Domicilio"

    class OrderStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_PREPARACION = "EN_PREPARACION", "En preparación"
        LISTO = "LISTO", "Listo"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    client = models.ForeignKey(
        Client, on_delete=models.RESTRICT, db_column="cliente_id",
        related_name="orders", null=True, blank=True,
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.RESTRICT, db_column="sede_id", related_name="orders"
    )
    table = models.ForeignKey(
        DiningTable, on_delete=models.RESTRICT, db_column="mesa_id",
        related_name="orders", null=True, blank=True,
    )
    channel = models.CharField(max_length=10, choices=Channel.choices, db_column="canal")
    ordered_at = models.DateTimeField(default=timezone.now, db_column="fecha")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    order_status = models.CharField(
        max_length=16, choices=OrderStatus.choices,
        default=OrderStatus.PENDIENTE, db_column="estado",
    )

    objects = OrderManager()

    class Meta:
        db_table = "pedidos"
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-ordered_at", "-id"]
        constraints = [
            BrasaGoModel.status_constraint("pedidos_is_active_valid"),
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0) & models.Q(total__gte=0),
                name="pedidos_montos_non_neg",
            ),
            models.CheckConstraint(
                condition=models.Q(channel__in=["MESA", "RECOGIDA", "DOMICILIO"]),
                name="pedidos_canal_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    order_status__in=[
                        "PENDIENTE", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO",
                    ]
                ),
                name="pedidos_estado_valid",
            ),
        ]

    def __str__(self):
        return f"Pedido {self.pk}"

    def void(self):
        """Anula el pedido y sus detalles. La devolución de insumos se agrega
        cuando exista la app de inventario."""
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=self.pk)
            if order.status == RecordStatus.INACTIVE:
                return order
            for line in order.details.select_for_update().order_by("id"):
                if line.status != RecordStatus.ACTIVE:
                    continue
                line.status = RecordStatus.INACTIVE
                line.save(update_fields=["status", "updated_at"])
            order.status = RecordStatus.INACTIVE
            order.order_status = Order.OrderStatus.CANCELADO
            order.save(update_fields=["status", "order_status", "updated_at"])
            return order


class OrderDetail(BrasaGoModel):
    order = models.ForeignKey(
        Order, on_delete=models.RESTRICT, db_column="pedido_id", related_name="details"
    )
    product = models.ForeignKey(
        Product, on_delete=models.RESTRICT, db_column="producto_id",
        related_name="order_details",
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)], db_column="cantidad")
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, db_column="valor_unitario"
    )
    total = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(
        max_length=255, null=True, blank=True, db_column="observaciones"
    )

    class Meta:
        db_table = "detalles_pedidos"
        verbose_name = "detalle de pedido"
        verbose_name_plural = "detalles de pedidos"
        ordering = ["id"]
        constraints = [
            BrasaGoModel.status_constraint("detalles_pedidos_is_active_valid"),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1)
                & models.Q(unit_price__gte=0)
                & models.Q(total__gte=0),
                name="detalles_pedidos_montos_valid",
            ),
        ]

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total = (self.unit_price * self.quantity).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)


from django.db import models  # noqa: E402
from django.db.models import Q  # noqa: E402
from apps.common.models import BrasaGoModel as _Base  # noqa: E402


class Payment(_Base):
    class Method(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        OTRO = "OTRO", "Otro"

    class PaymentStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADO = "PAGADO", "Pagado"
        ANULADO = "ANULADO", "Anulado"

    order = models.ForeignKey(
        "sale.Order", on_delete=models.RESTRICT,
        db_column="pedido_id", related_name="payments",
    )
    method = models.CharField(max_length=30, choices=Method.choices, db_column="metodo")
    amount = models.DecimalField(max_digits=12, decimal_places=2, db_column="monto")
    paid_at = models.DateTimeField(db_column="fecha")
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices,
        default=PaymentStatus.PENDIENTE, db_column="estado",
    )

    class Meta:
        db_table = "pagos"
        verbose_name = "pago"
        verbose_name_plural = "pagos"
        ordering = ["-paid_at", "id"]
        constraints = [
            _Base.status_constraint("pagos_is_active_valid"),
            models.CheckConstraint(condition=Q(amount__gt=0), name="pagos_monto_positivo"),
            models.CheckConstraint(
                condition=Q(payment_status__in=["PENDIENTE", "PAGADO", "ANULADO"]),
                name="pagos_estado_valido",
            ),
            models.CheckConstraint(
                condition=Q(method__in=["EFECTIVO", "TARJETA", "TRANSFERENCIA", "OTRO"]),
                name="pagos_metodo_valido",
            ),
        ]

    def __str__(self):
        return f"Pago {self.pk} · pedido {self.order_id} · {self.amount}"

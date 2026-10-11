from django.db import models
from django.db.models import F, Q

from apps.common.models import BrasaGoModel


class Courier(BrasaGoModel):
    name = models.CharField(max_length=150, db_column="nombre")
    description = models.CharField(
        max_length=255, null=True, blank=True, db_column="descripcion"
    )

    class Meta:
        db_table = "domiciliarios"
        verbose_name = "domiciliario"
        verbose_name_plural = "domiciliarios"
        ordering = ["name", "id"]
        constraints = [BrasaGoModel.status_constraint("domiciliarios_is_active_valid")]

    def __str__(self):
        return self.name


class Delivery(BrasaGoModel):
    class DeliveryStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_CAMINO = "EN_CAMINO", "En camino"
        ENTREGADA = "ENTREGADA", "Entregada"
        CANCELADA = "CANCELADA", "Cancelada"

    order = models.OneToOneField(
        "sale.Order", on_delete=models.RESTRICT,
        db_column="pedido_id", related_name="delivery",
    )
    courier = models.ForeignKey(
        Courier, on_delete=models.RESTRICT,
        db_column="domiciliario_id", related_name="deliveries",
    )
    started_at = models.DateTimeField(null=True, blank=True, db_column="fecha_inicio")
    finished_at = models.DateTimeField(null=True, blank=True, db_column="fecha_fin")
    total = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, db_column="total"
    )
    delivery_status = models.CharField(
        max_length=20, choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDIENTE, db_column="estado",
    )
    notes = models.CharField(max_length=255, null=True, blank=True, db_column="observaciones")

    class Meta:
        db_table = "entregas"
        verbose_name = "entrega"
        verbose_name_plural = "entregas"
        ordering = ["-id"]
        constraints = [
            BrasaGoModel.status_constraint("entregas_is_active_valid"),
            models.CheckConstraint(
                condition=Q(delivery_status__in=["PENDIENTE", "EN_CAMINO", "ENTREGADA", "CANCELADA"]),
                name="entregas_estado_valido",
            ),
            models.CheckConstraint(
                condition=Q(total__isnull=True) | Q(total__gte=0),
                name="entregas_total_valido",
            ),
            models.CheckConstraint(
                condition=Q(started_at__isnull=True)
                | Q(finished_at__isnull=True)
                | Q(finished_at__gte=F("started_at")),
                name="entregas_fechas_validas",
            ),
        ]

    def __str__(self):
        return f"Entrega {self.pk} · pedido {self.order_id}"

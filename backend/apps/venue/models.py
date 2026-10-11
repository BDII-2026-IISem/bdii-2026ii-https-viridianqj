from django.db import models

from apps.common.models import BrasaGoModel


class Branch(BrasaGoModel):
    name = models.CharField(max_length=150, db_column="nombre")
    description = models.CharField(
        max_length=255, null=True, blank=True, db_column="descripcion"
    )

    class Meta:
        db_table = "sedes"
        verbose_name = "sede"
        verbose_name_plural = "sedes"
        ordering = ["name", "id"]
        constraints = [BrasaGoModel.status_constraint("sedes_is_active_valid")]

    def __str__(self):
        return self.name


class DiningTable(BrasaGoModel):
    branch = models.ForeignKey(
        Branch, on_delete=models.PROTECT, db_column="sede_id", related_name="tables"
    )
    name = models.CharField(max_length=150, db_column="nombre")
    description = models.CharField(
        max_length=255, null=True, blank=True, db_column="descripcion"
    )

    class Meta:
        db_table = "mesas"
        verbose_name = "mesa"
        verbose_name_plural = "mesas"
        ordering = ["branch", "name"]
        constraints = [BrasaGoModel.status_constraint("mesas_is_active_valid")]

    def __str__(self):
        return f"{self.branch} - {self.name}"


from django.db.models import F, Q  # noqa: E402


class Reservation(BrasaGoModel):
    class ReservationStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        COMPLETADA = "COMPLETADA", "Completada"
        CANCELADA = "CANCELADA", "Cancelada"

    client = models.ForeignKey(
        "client.Client", on_delete=models.RESTRICT,
        db_column="cliente_id", related_name="reservations",
    )
    table = models.ForeignKey(
        DiningTable, on_delete=models.RESTRICT,
        db_column="mesa_id", related_name="reservations",
    )
    starts_at = models.DateTimeField(db_column="fecha_inicio")
    ends_at = models.DateTimeField(null=True, blank=True, db_column="fecha_fin")
    reservation_status = models.CharField(
        max_length=20, choices=ReservationStatus.choices,
        default=ReservationStatus.PENDIENTE, db_column="estado",
    )
    notes = models.CharField(max_length=255, null=True, blank=True, db_column="observaciones")

    class Meta:
        db_table = "reservas"
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        ordering = ["-starts_at", "id"]
        constraints = [
            BrasaGoModel.status_constraint("reservas_is_active_valid"),
            models.CheckConstraint(
                condition=Q(reservation_status__in=["PENDIENTE", "CONFIRMADA", "COMPLETADA", "CANCELADA"]),
                name="reservas_estado_valido",
            ),
            models.CheckConstraint(
                condition=Q(ends_at__isnull=True) | Q(ends_at__gte=F("starts_at")),
                name="reservas_fechas_validas",
            ),
        ]

    def __str__(self):
        return f"Reserva {self.pk} · {self.table_id} · {self.starts_at:%Y-%m-%d %H:%M}"

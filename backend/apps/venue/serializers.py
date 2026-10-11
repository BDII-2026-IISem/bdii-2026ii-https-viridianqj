from datetime import timedelta

from rest_framework import serializers

from apps.common.status import RecordStatus
from apps.venue.models import Reservation

DEFAULT_DURATION = timedelta(hours=2)
BLOCKING_STATES = ["PENDIENTE", "CONFIRMADA"]


class ReservationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    table_name = serializers.CharField(source="table.name", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id", "client", "client_name", "table", "table_name",
            "starts_at", "ends_at", "reservation_status", "notes",
            "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        instance = self.instance

        def get(key):
            return attrs.get(key, getattr(instance, key, None))

        table, starts_at, ends_at = get("table"), get("starts_at"), get("ends_at")
        reservation_status = get("reservation_status") or "PENDIENTE"

        if ends_at is None:
            ends_at = starts_at + DEFAULT_DURATION
            attrs["ends_at"] = ends_at
        if ends_at < starts_at:
            raise serializers.ValidationError({"ends_at": "Debe ser posterior al inicio."})
        if table.status != RecordStatus.ACTIVE:
            raise serializers.ValidationError({"table": "La mesa está inactiva."})

        if reservation_status in BLOCKING_STATES:
            clash = Reservation.objects.filter(
                table=table,
                status=RecordStatus.ACTIVE,
                reservation_status__in=BLOCKING_STATES,
                starts_at__lt=ends_at,
                ends_at__gt=starts_at,
            )
            if instance is not None:
                clash = clash.exclude(pk=instance.pk)
            if clash.exists():
                raise serializers.ValidationError(
                    {"table": "La mesa ya tiene una reserva en ese horario."}
                )
        return attrs

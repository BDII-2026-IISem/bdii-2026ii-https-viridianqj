from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from apps.common.status import RecordStatus
from apps.delivery.models import Courier, Delivery

DELIVERY_CHANNEL = "DOMICILIO"  # ajustar si Order.Channel usa otro valor
FINAL_STATES = ("ENTREGADA", "CANCELADA")


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ["id", "name", "description", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DeliverySerializer(serializers.ModelSerializer):
    courier_name = serializers.CharField(source="courier.name", read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id", "order", "courier", "courier_name", "started_at", "finished_at",
            "total", "delivery_status", "notes", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"total": {"min_value": Decimal("0")}}

    def validate(self, attrs):
        instance = self.instance

        if instance is None or "order" in attrs:
            order = attrs["order"] if "order" in attrs else instance.order
            if order.channel != DELIVERY_CHANNEL:
                raise serializers.ValidationError(
                    {"order": f"Solo los pedidos con canal {DELIVERY_CHANNEL} tienen entrega."}
                )
            if order.order_status == "CANCELADO" or order.status != RecordStatus.ACTIVE:
                raise serializers.ValidationError({"order": "El pedido está anulado."})

        if instance is None or "courier" in attrs:
            courier = attrs["courier"] if "courier" in attrs else instance.courier
            if courier.status != RecordStatus.ACTIVE:
                raise serializers.ValidationError({"courier": "El domiciliario está inactivo."})

        if instance is not None:
            new_state = attrs.get("delivery_status", instance.delivery_status)
            if instance.delivery_status in FINAL_STATES and new_state != instance.delivery_status:
                raise serializers.ValidationError(
                    {"delivery_status": f"La entrega ya está {instance.delivery_status}."}
                )

        started = attrs.get("started_at", getattr(instance, "started_at", None))
        finished = attrs.get("finished_at", getattr(instance, "finished_at", None))
        if started and finished and finished < started:
            raise serializers.ValidationError({"finished_at": "No puede ser anterior al inicio."})
        return attrs

    def _stamp_dates(self, data, instance=None):
        state = data.get("delivery_status")
        started = data.get("started_at", getattr(instance, "started_at", None))
        finished = data.get("finished_at", getattr(instance, "finished_at", None))
        now = timezone.now()
        if state in ("EN_CAMINO", "ENTREGADA") and started is None:
            data["started_at"] = now
        if state == "ENTREGADA" and finished is None:
            data["finished_at"] = now
        return data

    def create(self, validated_data):
        return super().create(self._stamp_dates(validated_data))

    def update(self, instance, validated_data):
        return super().update(instance, self._stamp_dates(validated_data, instance))

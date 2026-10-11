from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from apps.client.models import Client
from apps.product.models import Product
from apps.sale.models import Order, OrderDetail
from apps.venue.models import Branch, DiningTable


class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderDetail
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "total",
            "notes",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    table_name = serializers.CharField(source="table.name", read_only=True, allow_null=True)
    client_name = serializers.CharField(source="client.name", read_only=True, allow_null=True)
    details = OrderDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "client",
            "client_name",
            "branch",
            "branch_name",
            "table",
            "table_name",
            "channel",
            "ordered_at",
            "subtotal",
            "total",
            "order_status",
            "status",
            "details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
    )
    quantity = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True
    )


class OrderRegisterSerializer(serializers.Serializer):
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source="client",
        allow_null=True,
        default=None,
    )
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source="branch",
    )
    table_id = serializers.PrimaryKeyRelatedField(
        queryset=DiningTable.objects.all(),
        source="table",
        allow_null=True,
        default=None,
    )
    channel = serializers.ChoiceField(choices=Order.Channel.choices)
    ordered_at = serializers.DateTimeField(required=False)
    items = OrderItemSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        items = [
            {
                "product_id": item["product"].id,
                "quantity": item["quantity"],
                "notes": item.get("notes"),
            }
            for item in validated_data["items"]
        ]
        try:
            return Order.objects.register(
                client=validated_data["client"],
                branch=validated_data["branch"],
                table=validated_data["table"],
                channel=validated_data["channel"],
                ordered_at=validated_data.get("ordered_at") or timezone.now(),
                items=items,
            )
        except DjangoValidationError as exc:
            if getattr(exc, "message_dict", None):
                raise serializers.ValidationError(exc.message_dict) from exc
            raise serializers.ValidationError(exc.messages) from exc


from decimal import Decimal  # noqa: E402

from django.db.models import Sum  # noqa: E402

from apps.common.status import RecordStatus  # noqa: E402
from apps.sale.models import Payment  # noqa: E402


class PaymentSerializer(serializers.ModelSerializer):
    paid_at = serializers.DateTimeField(required=False)

    class Meta:
        model = Payment
        fields = [
            "id", "order", "method", "amount", "paid_at",
            "payment_status", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"amount": {"min_value": Decimal("0.01")}}

    def validate(self, attrs):
        instance = self.instance
        order = attrs.get("order", getattr(instance, "order", None))
        amount = attrs.get("amount", getattr(instance, "amount", None))
        payment_status = attrs.get(
            "payment_status", getattr(instance, "payment_status", "PENDIENTE")
        )

        if order.order_status == "CANCELADO" or order.status != RecordStatus.ACTIVE:
            raise serializers.ValidationError({"order": "El pedido está anulado."})

        if payment_status == "PAGADO":
            paid = Payment.objects.filter(
                order=order, payment_status="PAGADO", status=RecordStatus.ACTIVE
            )
            if instance is not None:
                paid = paid.exclude(pk=instance.pk)
            total_paid = paid.aggregate(total=Sum("amount"))["total"] or Decimal("0")
            if total_paid + amount > order.total:
                raise serializers.ValidationError(
                    {"amount": "El pago supera el saldo pendiente del pedido."}
                )
        return attrs

    def create(self, validated_data):
        validated_data.setdefault("paid_at", timezone.now())
        return super().create(validated_data)


ORDER_TRANSITIONS = {
    "PENDIENTE": {"EN_PREPARACION", "CANCELADO"},
    "EN_PREPARACION": {"LISTO", "CANCELADO"},
    "LISTO": {"ENTREGADO", "CANCELADO"},
    "ENTREGADO": set(),
    "CANCELADO": set(),
}


class OrderStatusSerializer(serializers.Serializer):
    order_status = serializers.ChoiceField(choices=[(s, s) for s in ORDER_TRANSITIONS])

    def validate_order_status(self, value):
        order = self.context["order"]
        if value not in ORDER_TRANSITIONS.get(order.order_status, set()):
            raise serializers.ValidationError(
                f"No se puede pasar de {order.order_status} a {value}."
            )
        if value == "CANCELADO" and order.payments.filter(
            payment_status="PAGADO", status=RecordStatus.ACTIVE
        ).exists():
            raise serializers.ValidationError(
                "No se puede cancelar un pedido con pagos registrados; anule los pagos primero."
            )
        return value

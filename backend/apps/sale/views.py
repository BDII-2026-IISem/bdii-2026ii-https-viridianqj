from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasResourceAccess
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.sale.models import Order
from apps.sale.serializers import OrderRegisterSerializer, OrderSerializer


class OrderReadViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.select_related(
        "client", "branch", "table"
    ).prefetch_related("details__product")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, HasResourceAccess]
    lookup_value_converter = "int"

    def perform_destroy(self, instance):
        instance.void()


class OrderRegisterAPIView(APIView):
    permission_classes = [IsAuthenticated, HasResourceAccess]

    def post(self, request):
        serializer = OrderRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        order = (
            Order.objects.select_related("client", "branch", "table")
            .prefetch_related("details__product")
            .get(pk=order.pk)
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderCollectionAPIView(APIView):
    permission_classes = [IsAuthenticated, HasResourceAccess]

    @extend_schema(responses=OrderSerializer(many=True))
    def get(self, request, *args, **kwargs):
        queryset = OrderReadViewSet.queryset.all()
        return Response(OrderSerializer(queryset, many=True).data)

    @extend_schema(request=OrderRegisterSerializer, responses={201: OrderSerializer})
    def post(self, request, *args, **kwargs):
        handler = OrderRegisterAPIView()
        handler.request = request
        handler.format_kwarg = None
        handler.args = ()
        handler.kwargs = {}
        return handler.post(request)


from django.shortcuts import get_object_or_404  # noqa: E402

from apps.common.status import RecordStatus  # noqa: E402
from apps.sale.models import Payment  # noqa: E402
from apps.sale.serializers import OrderStatusSerializer, PaymentSerializer  # noqa: E402


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("order")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, HasResourceAccess]

    def perform_destroy(self, instance):
        instance.payment_status = "ANULADO"
        instance.status = RecordStatus.INACTIVE
        instance.save(update_fields=["payment_status", "status", "updated_at"])


class OrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, HasResourceAccess]

    @extend_schema(request=OrderStatusSerializer, responses=OrderSerializer)
    def patch(self, request, pk):
        queryset = Order.objects.select_related("client", "branch", "table").prefetch_related(
            "details__product"
        )
        order = get_object_or_404(queryset, pk=pk)
        serializer = OrderStatusSerializer(data=request.data, context={"order": order})
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["order_status"]

        if new_status == "CANCELADO":
            order.void()
            order.refresh_from_db()
            if order.order_status != "CANCELADO":
                order.order_status = "CANCELADO"
                order.save(update_fields=["order_status", "updated_at"])
        else:
            order.order_status = new_status
            order.save(update_fields=["order_status", "updated_at"])

        order = queryset.get(pk=order.pk)
        return Response(OrderSerializer(order).data)

from apps.common.status import RecordStatus
from apps.common.viewsets import SoftDeleteModelViewSet
from apps.delivery.models import Courier, Delivery
from apps.delivery.serializers import CourierSerializer, DeliverySerializer


class CourierViewSet(SoftDeleteModelViewSet):
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer


class DeliveryViewSet(SoftDeleteModelViewSet):
    queryset = Delivery.objects.select_related("order", "courier")
    serializer_class = DeliverySerializer

    def perform_destroy(self, instance):
        instance.delivery_status = "CANCELADA"
        instance.status = RecordStatus.INACTIVE
        instance.save(update_fields=["delivery_status", "status", "updated_at"])

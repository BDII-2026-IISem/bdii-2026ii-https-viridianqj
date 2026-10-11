from apps.common.status import RecordStatus
from apps.common.viewsets import SoftDeleteModelViewSet
from apps.venue.models import Reservation
from apps.venue.serializers import ReservationSerializer


class ReservationViewSet(SoftDeleteModelViewSet):
    queryset = Reservation.objects.select_related("client", "table")
    serializer_class = ReservationSerializer

    def perform_destroy(self, instance):
        instance.reservation_status = "CANCELADA"
        instance.status = RecordStatus.INACTIVE
        instance.save(update_fields=["reservation_status", "status", "updated_at"])

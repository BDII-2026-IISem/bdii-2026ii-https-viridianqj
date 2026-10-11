from rest_framework.routers import SimpleRouter

from apps.venue.views import ReservationViewSet

router = SimpleRouter()
router.register("reservas", ReservationViewSet, basename="reservation")

urlpatterns = router.urls

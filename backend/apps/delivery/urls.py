from rest_framework.routers import SimpleRouter

from apps.delivery.views import CourierViewSet, DeliveryViewSet

router = SimpleRouter()
router.register("domiciliarios", CourierViewSet, basename="courier")
router.register("entregas", DeliveryViewSet, basename="delivery")

urlpatterns = router.urls

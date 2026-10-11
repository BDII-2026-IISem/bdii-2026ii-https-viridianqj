from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.sale.views import (
    OrderCollectionAPIView,
    OrderReadViewSet,
    OrderStatusAPIView,
    PaymentViewSet,
)

router = SimpleRouter()
router.register("pagos", PaymentViewSet, basename="payment")

urlpatterns = [
    path("pedidos/", OrderCollectionAPIView.as_view(), name="order-collection"),
    path(
        "pedidos/<int:pk>/",
        OrderReadViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="order-detail",
    ),
    path("pedidos/<int:pk>/estado/", OrderStatusAPIView.as_view(), name="order-status"),
] + router.urls

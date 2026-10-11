from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.product.views import AvailableProductListAPIView, ProductViewSet

router = SimpleRouter(use_regex_path=False)
router.register("productos", ProductViewSet, basename="product")

urlpatterns = [
    path(
        "productos/disponibles/",
        AvailableProductListAPIView.as_view(),
        name="product-available",
    ),
]
urlpatterns += router.urls

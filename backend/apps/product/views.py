from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasResourceAccess
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.common.status import RecordStatus
from apps.product.models import Product
from apps.product.serializers import ProductSerializer


class CatalogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasResourceAccess]
    lookup_value_converter = "int"

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def perform_destroy(self, instance):
        instance.status = RecordStatus.INACTIVE
        instance.save(update_fields=["status", "updated_at"])


class ProductViewSet(CatalogViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class AvailableProductListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, HasResourceAccess]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(status=RecordStatus.ACTIVE)

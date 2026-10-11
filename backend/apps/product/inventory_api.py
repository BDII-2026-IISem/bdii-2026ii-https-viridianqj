from decimal import Decimal

from rest_framework import serializers
from rest_framework.routers import SimpleRouter

from apps.common.status import RecordStatus
from apps.common.viewsets import SoftDeleteModelViewSet
from apps.product.models import RecipeItem, Supply


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ["id", "code", "name", "unit", "min_stock", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"min_stock": {"min_value": Decimal("0")}}


class RecipeItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    supply_name = serializers.CharField(source="supply.name", read_only=True)

    class Meta:
        model = RecipeItem
        fields = [
            "id", "product", "product_name", "supply", "supply_name",
            "quantity", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"quantity": {"min_value": Decimal("0.01")}}

    def validate_product(self, value):
        if value.status != RecordStatus.ACTIVE:
            raise serializers.ValidationError("El producto está inactivo.")
        return value

    def validate_supply(self, value):
        if value.status != RecordStatus.ACTIVE:
            raise serializers.ValidationError("El insumo está inactivo.")
        return value


class SupplyViewSet(SoftDeleteModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer


class RecipeItemViewSet(SoftDeleteModelViewSet):
    queryset = RecipeItem.objects.select_related("product", "supply")
    serializer_class = RecipeItemSerializer


router = SimpleRouter()
router.register("insumos", SupplyViewSet, basename="supply")
router.register("recetas", RecipeItemViewSet, basename="recipe-item")

urlpatterns = router.urls

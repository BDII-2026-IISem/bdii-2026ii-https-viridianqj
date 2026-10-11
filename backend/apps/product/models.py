from django.db import models

from apps.common.models import BrasaGoModel


class Product(BrasaGoModel):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150, db_column="nombre")
    description = models.CharField(
        max_length=255, null=True, blank=True, db_column="descripcion"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, db_column="precio")

    class Meta:
        db_table = "productos"
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["name", "id"]
        constraints = [
            BrasaGoModel.status_constraint("productos_is_active_valid"),
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="productos_precio_non_neg"
            ),
        ]

    def __str__(self):
        return self.name


from django.db import models  # noqa: E402
from django.db.models import Q  # noqa: E402
from apps.common.models import BrasaGoModel as _Base  # noqa: E402


class Supply(_Base):
    code = models.CharField(max_length=30, unique=True, db_column="codigo")
    name = models.CharField(max_length=150, db_column="nombre")
    unit = models.CharField(max_length=20, db_column="unidad_medida")
    min_stock = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, db_column="stock_minimo"
    )

    class Meta:
        db_table = "insumos"
        verbose_name = "insumo"
        verbose_name_plural = "insumos"
        ordering = ["name", "id"]
        constraints = [
            _Base.status_constraint("insumos_is_active_valid"),
            models.CheckConstraint(
                condition=Q(min_stock__isnull=True) | Q(min_stock__gte=0),
                name="insumos_stock_minimo_valido",
            ),
        ]

    def __str__(self):
        return f"{self.code} · {self.name}"


class RecipeItem(_Base):
    product = models.ForeignKey(
        "product.Product", on_delete=models.RESTRICT,
        db_column="producto_id", related_name="recipe_items",
    )
    supply = models.ForeignKey(
        "product.Supply", on_delete=models.RESTRICT,
        db_column="insumo_id", related_name="recipe_items",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, db_column="cantidad")

    class Meta:
        db_table = "recetas_insumos"
        verbose_name = "receta de insumo"
        verbose_name_plural = "recetas de insumos"
        ordering = ["product", "supply"]
        constraints = [
            _Base.status_constraint("recetas_is_active_valid"),
            models.UniqueConstraint(fields=["product", "supply"], name="recetas_producto_insumo_uq"),
            models.CheckConstraint(condition=Q(quantity__gt=0), name="recetas_cantidad_positiva"),
        ]

    def __str__(self):
        return f"Producto {self.product_id} · insumo {self.supply_id} · {self.quantity}"

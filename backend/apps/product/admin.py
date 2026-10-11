from django.contrib import admin

from apps.product.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("sku", "name", "description")
    list_editable = ("price", "status")
    ordering = ("name", "id")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Información", {"fields": ("sku", "name", "description")}),
        ("Precio", {"fields": ("price",)}),
        ("Estado", {"fields": ("status",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


from apps.product.models import RecipeItem, Supply  # noqa: E402


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "unit", "min_stock", "status")
    search_fields = ("code", "name")


@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "supply", "quantity", "status")

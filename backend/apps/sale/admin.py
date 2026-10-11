from django.contrib import admin

from apps.sale.models import Order, OrderDetail


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("product", "quantity", "unit_price", "total", "notes", "status")
    readonly_fields = ("product", "quantity", "unit_price", "total", "notes", "status")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "branch",
        "table",
        "channel",
        "ordered_at",
        "subtotal",
        "total",
        "order_status",
        "status",
    )
    list_filter = ("status", "order_status", "channel", "branch", "ordered_at")
    search_fields = ("client__name", "client__document_number", "branch__name")
    ordering = ("-ordered_at", "-id")
    date_hierarchy = "ordered_at"
    readonly_fields = (
        "client",
        "branch",
        "table",
        "channel",
        "ordered_at",
        "subtotal",
        "total",
        "order_status",
        "status",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Información del pedido",
            {"fields": ("client", "branch", "table", "channel")},
        ),
        ("Estado", {"fields": ("order_status", "status")}),
        ("Totales", {"fields": ("subtotal", "total"), "classes": ("collapse",)}),
        ("Fecha", {"fields": ("ordered_at",), "classes": ("collapse",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    inlines = (OrderDetailInline,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("client", "branch", "table")


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price", "total", "status")
    list_filter = ("status", "order__ordered_at", "product__status")
    search_fields = ("order__client__name", "product__name", "product__sku")
    ordering = ("-order__ordered_at", "id")
    readonly_fields = (
        "order",
        "product",
        "quantity",
        "unit_price",
        "total",
        "notes",
        "status",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Línea",
            {"fields": ("order", "product", "quantity", "unit_price", "total", "notes")},
        ),
        ("Estado", {"fields": ("status",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "order", "order__client", "product"
        )


from apps.sale.models import Payment  # noqa: E402


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "method", "amount", "paid_at", "payment_status", "status")
    list_filter = ("method", "payment_status")

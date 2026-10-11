from django.contrib import admin

from apps.delivery.models import Courier, Delivery


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "status")
    search_fields = ("name",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "courier", "delivery_status", "started_at", "finished_at", "total")
    list_filter = ("delivery_status",)

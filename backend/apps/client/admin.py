from django.contrib import admin

from apps.client.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "document_type",
        "document_number",
        "email",
        "phone",
        "status",
        "created_at",
    )
    list_filter = ("status", "document_type")
    search_fields = ("name", "document_number", "email", "phone")
    list_editable = ("status",)
    ordering = ("name", "id")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Información del cliente",
            {"fields": ("name", "document_type", "document_number", "email", "phone")},
        ),
        ("Estado", {"fields": ("status",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

from django.contrib import admin

from apps.venue.models import Branch, DiningTable


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "description")
    list_editable = ("status",)
    ordering = ("name", "id")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "description", "status")}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin):
    list_display = ("name", "branch", "status", "created_at")
    list_filter = ("status", "branch")
    search_fields = ("name", "description", "branch__name")
    list_editable = ("status",)
    ordering = ("branch__name", "name")
    autocomplete_fields = ("branch",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Mesa", {"fields": ("branch", "name", "description")}),
        ("Estado", {"fields": ("status",)}),
        (
            "Auditoría",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("branch")


from apps.venue.models import Reservation  # noqa: E402


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "table", "starts_at", "ends_at", "reservation_status", "status")
    list_filter = ("reservation_status", "status")

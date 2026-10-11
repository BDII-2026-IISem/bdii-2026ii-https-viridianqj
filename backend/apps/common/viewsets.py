from rest_framework import viewsets

from apps.common.status import RecordStatus


class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    """CRUD completo; DELETE no borra la fila: la deja INACTIVE."""

    def perform_destroy(self, instance):
        instance.status = RecordStatus.INACTIVE
        instance.save(update_fields=["status", "updated_at"])

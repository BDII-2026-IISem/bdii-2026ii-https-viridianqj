from django.db import models


class RecordStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Activo"
    INACTIVE = "INACTIVE", "Inactivo"
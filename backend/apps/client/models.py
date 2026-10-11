from django.core.validators import MinLengthValidator
from django.db import models

from apps.common.models import BrasaGoModel


class Client(BrasaGoModel):
    class DocumentType(models.TextChoices):
        CC = "CC", "Cédula de ciudadanía"
        CE = "CE", "Cédula de extranjería"
        TI = "TI", "Tarjeta de identidad"
        NIT = "NIT", "NIT"
        PASAPORTE = "PASAPORTE", "Pasaporte"

    document_type = models.CharField(
        max_length=20, choices=DocumentType.choices, db_column="tipo_documento"
    )
    document_number = models.CharField(
        max_length=30, unique=True, db_column="numero_documento"
    )
    name = models.CharField(
        max_length=150, validators=[MinLengthValidator(2)], db_column="nombre"
    )
    phone = models.CharField(
        max_length=30, null=True, blank=True, db_column="telefono"
    )
    email = models.EmailField(max_length=150, null=True, blank=True)

    class Meta:
        db_table = "clientes"
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["name", "id"]
        constraints = [BrasaGoModel.status_constraint("clientes_is_active_valid")]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

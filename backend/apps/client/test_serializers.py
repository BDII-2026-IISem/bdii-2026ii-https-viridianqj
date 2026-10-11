from django.test import TestCase
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from apps.client.models import Client
from apps.client.serializers import ClientSerializer


class ClientSerializerTests(TestCase):
    def test_json_uses_camel_case(self):
        client = Client.objects.create(
            document_type="CC", document_number="1000000001", name="María Prueba"
        )
        content = CamelCaseJSONRenderer().render(ClientSerializer(client).data)
        self.assertIn(b"createdAt", content)
        self.assertNotIn(b"created_at", content)
        self.assertIn(b"documentNumber", content)

    def test_email_is_normalized(self):
        serializer = ClientSerializer(data={
            "document_type": "CC",
            "document_number": "1000000002",
            "name": "Maria Prueba",
            "email": "Maria@Example.com",
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.save().email, "maria@example.com")

    def test_blank_email_becomes_null(self):
        serializer = ClientSerializer(data={
            "document_type": "CC",
            "document_number": "1000000003",
            "name": "Sin Correo",
            "email": "",
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.save().email)

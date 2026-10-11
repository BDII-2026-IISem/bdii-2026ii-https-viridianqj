from apps.common.testing import authenticate_as_admin
import json

from rest_framework import status
from rest_framework.test import APITestCase

from apps.client.models import Client
from apps.common.status import RecordStatus

BASE = "/api/clientes/"


def payload(**overrides):
    data = {
        "documentType": "CC",
        "documentNumber": "1000000001",
        "name": "María García",
    }
    data.update(overrides)
    return data


class ClientApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)

    def test_create_defaults_and_persists(self):
        response = self.client.post(
            BASE,
            payload(email="Maria@Example.com", phone="3001234567"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], RecordStatus.ACTIVE)
        self.assertEqual(response.data["email"], "maria@example.com")
        wire = json.loads(response.content)
        self.assertIn("createdAt", wire)
        self.assertIn("documentNumber", wire)
        self.assertNotIn("created_at", wire)
        stored = Client.objects.get(pk=response.data["id"])
        self.assertEqual(stored.name, "María García")
        self.assertEqual(stored.document_number, "1000000001")

    def test_invalid_data_and_duplicate_document(self):
        short = self.client.post(BASE, payload(name="A"), format="json")
        self.assertEqual(short.status_code, status.HTTP_400_BAD_REQUEST)
        bad_type = self.client.post(BASE, payload(documentType="XX"), format="json")
        self.assertEqual(bad_type.status_code, status.HTTP_400_BAD_REQUEST)
        first = self.client.post(BASE, payload(), format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        duplicate = self.client.post(BASE, payload(name="Otra Persona"), format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("document_number", duplicate.data)

    def test_soft_delete_keeps_the_row(self):
        created = self.client.post(BASE, payload(name="Pedro León"), format="json")
        deleted = self.client.delete(f"{BASE}{created.data['id']}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        stored = Client.objects.get(pk=created.data["id"])
        self.assertEqual(stored.status, RecordStatus.INACTIVE)
        self.assertEqual(Client.objects.count(), 1)

    def test_list_retrieve_and_update(self):
        created = self.client.post(
            BASE, payload(name="Luisa Mora", phone="111"), format="json"
        )
        pk = created.data["id"]
        listed = self.client.get(BASE)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listed.data), 1)
        detail = self.client.get(f"{BASE}{pk}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["name"], "Luisa Mora")
        updated = self.client.patch(
            f"{BASE}{pk}/", {"phone": "222", "status": "INACTIVE"}, format="json"
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["phone"], "222")
        self.assertEqual(updated.data["status"], "INACTIVE")

    def test_status_filter(self):
        self.client.post(
            BASE, payload(documentNumber="2000000001", name="Activo Uno"), format="json"
        )
        other = self.client.post(
            BASE, payload(documentNumber="2000000002", name="Inactivo Dos"), format="json"
        )
        self.client.delete(f"{BASE}{other.data['id']}/")
        listed = self.client.get(f"{BASE}?status=INACTIVE")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual([c["name"] for c in listed.data], ["Inactivo Dos"])

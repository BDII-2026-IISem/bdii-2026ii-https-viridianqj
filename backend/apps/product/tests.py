from apps.common.testing import authenticate_as_admin
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.status import RecordStatus
from apps.product.models import Product

BASE = "/api/productos/"


def payload(**overrides):
    data = {"sku": "BRG-001", "name": "Bandeja paisa", "price": "32000.00"}
    data.update(overrides)
    return data


class ProductApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)

    def test_create_retrieve_update_and_soft_delete(self):
        created = self.client.post(
            BASE, payload(description="Plato típico"), format="json"
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        pk = created.data["id"]
        listed = self.client.get(BASE)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual([p["sku"] for p in listed.data], ["BRG-001"])
        detail = self.client.get(f"{BASE}{pk}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["name"], "Bandeja paisa")
        updated = self.client.patch(
            f"{BASE}{pk}/", {"price": "35000.00"}, format="json"
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["price"], "35000.00")
        deleted = self.client.delete(f"{BASE}{pk}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        stored = Product.objects.get(pk=pk)
        self.assertEqual(stored.status, RecordStatus.INACTIVE)
        self.assertEqual(stored.price, Decimal("35000.00"))

    def test_default_status_is_active(self):
        created = self.client.post(BASE, payload(), format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["status"], RecordStatus.ACTIVE)

    def test_duplicate_sku_rejected_but_duplicate_name_allowed(self):
        first = self.client.post(BASE, payload(), format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        same_sku = self.client.post(BASE, payload(name="Otro nombre"), format="json")
        self.assertEqual(same_sku.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sku", same_sku.data)
        same_name = self.client.post(BASE, payload(sku="BRG-002"), format="json")
        self.assertEqual(same_name.status_code, status.HTTP_201_CREATED)

    def test_negative_price_is_rejected(self):
        response = self.client.post(BASE, payload(price="-1"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)
        self.assertEqual(Product.objects.count(), 0)

    def test_status_filter(self):
        self.client.post(BASE, payload(sku="BRG-010", name="Activo"), format="json")
        other = self.client.post(
            BASE, payload(sku="BRG-011", name="Retirado"), format="json"
        )
        self.client.delete(f"{BASE}{other.data['id']}/")
        listed = self.client.get(f"{BASE}?status=ACTIVE")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual([p["name"] for p in listed.data], ["Activo"])

    def test_product_crud_and_available_filter(self):
        created = self.client.post(
            BASE, payload(sku="BRG-020", name="Agua"), format="json"
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        available = self.client.get(f"{BASE}disponibles/")
        self.assertEqual(available.status_code, status.HTTP_200_OK)
        self.assertEqual([p["name"] for p in available.data], ["Agua"])
        post = self.client.post(f"{BASE}disponibles/", payload(), format="json")
        # Con RBAC (default-deny) el permiso se evalúa antes que el 405:
        # no existe un Resource para POST en esta ruta, así que se deniega.
        self.assertEqual(post.status_code, status.HTTP_403_FORBIDDEN)
        self.client.delete(f"{BASE}{created.data['id']}/")
        empty = self.client.get(f"{BASE}disponibles/")
        self.assertEqual(empty.status_code, status.HTTP_200_OK)
        self.assertEqual(empty.data, [])
        self.assertEqual(Product.objects.filter(pk=created.data["id"]).count(), 1)

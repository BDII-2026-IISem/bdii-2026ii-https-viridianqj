from apps.common.testing import authenticate_as_admin
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.factories import make_world
from apps.common.status import RecordStatus
from apps.product.models import RecipeItem, Supply

SUPPLIES = "/api/insumos/"
RECIPES = "/api/recetas/"


class SupplyApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)

    def test_create_and_unique_code(self):
        payload = {"code": "INS-001", "name": "Carne de res", "unit": "kg", "minStock": "5.00"}
        response = self.client.post(SUPPLIES, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["code"], "INS-001")
        self.assertEqual(response.data["status"], RecordStatus.ACTIVE)
        duplicate = self.client.post(SUPPLIES, payload, format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        listing = self.client.get(SUPPLIES)
        self.assertEqual(len(listing.data), 1)

    def test_negative_min_stock_rejected(self):
        response = self.client.post(
            SUPPLIES,
            {"code": "INS-002", "name": "Sal", "unit": "kg", "minStock": "-1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_is_soft(self):
        supply = Supply.objects.create(code="INS-003", name="Arroz", unit="kg")
        response = self.client.delete(f"{SUPPLIES}{supply.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        supply.refresh_from_db()
        self.assertEqual(supply.status, RecordStatus.INACTIVE)


class RecipeApiTests(APITestCase):
    def setUp(self):
        authenticate_as_admin(self.client)
        _, _, _, self.dish = make_world()
        self.supply = Supply.objects.create(code="INS-010", name="Frijol", unit="kg")

    def _payload(self, **overrides):
        data = {"product": self.dish.id, "supply": self.supply.id, "quantity": "0.25"}
        data.update(overrides)
        return data

    def test_create_recipe_item(self):
        response = self.client.post(RECIPES, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["product_name"], "Bandeja paisa")
        self.assertEqual(response.data["supply_name"], "Frijol")

    def test_duplicate_pair_rejected(self):
        RecipeItem.objects.create(
            product=self.dish, supply=self.supply, quantity=Decimal("1.50")
        )
        response = self.client.post(RECIPES, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_quantity_rejected(self):
        response = self.client.post(RECIPES, self._payload(quantity="0"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_supply_rejected(self):
        self.supply.status = RecordStatus.INACTIVE
        self.supply.save()
        response = self.client.post(RECIPES, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

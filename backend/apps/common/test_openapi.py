import json

from django.test import TestCase


class OpenApiTests(TestCase):
    def _schema(self):
        response = self.client.get("/api/schema/", {"format": "json"})
        self.assertEqual(response.status_code, 200)
        return response, json.loads(response.content)

    def test_schema_and_docs_are_open_without_token(self):
        for url in ("/api/schema/", "/api/schema/swagger-ui/", "/api/schema/redoc/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

    def test_schema_documents_the_business_endpoints(self):
        _, schema = self._schema()
        paths = schema["paths"]
        for expected in (
            "/api/clientes/",
            "/api/productos/",
            "/api/productos/disponibles/",
            "/api/pedidos/",
        ):
            self.assertIn(expected, paths)
        self.assertTrue(any(p.startswith("/api/pedidos/{") for p in paths))
        self.assertEqual(schema["info"]["title"], "BrasaGo API")

    def test_schema_uses_camel_case(self):
        response, _ = self._schema()
        text = response.content.decode()
        self.assertIn("createdAt", text)
        self.assertIn("documentNumber", text)
        self.assertNotIn("created_at", text)
        self.assertNotIn("document_number", text)

import unittest
from fastapi.testclient import TestClient
from Backend_server.main import app


class TestMainApp(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_app_startup(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, [404, 200])

    def test_anamoly_detection_router(self):
        response = self.client.get("/anomaly")
        self.assertIn(response.status_code, [200, 404])

    def test_db_router(self):
        response = self.client.get("/db")
        self.assertIn(response.status_code, [200, 404])

    def test_rule_router(self):
        response = self.client.get("/rules")
        self.assertIn(response.status_code, [200, 404])

    def test_create_rules_router(self):
        response = self.client.get("/create-rules")
        self.assertIn(response.status_code, [200, 404])


if __name__ == "__main__":
    unittest.main()

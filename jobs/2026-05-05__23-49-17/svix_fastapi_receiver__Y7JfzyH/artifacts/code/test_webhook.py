import unittest
from fastapi.testclient import TestClient
from main import app

class TestWebhook(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_missing_headers(self):
        response = self.client.post("/webhook", json={"test": "data"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Missing Svix headers")

    def test_invalid_signature(self):
        headers = {
            "svix-id": "msg_p5jXN87S8vL5U69S",
            "svix-timestamp": "1614265330",
            "svix-signature": "v1,g0hM9L9v9639v999999999999999999999999999999="
        }
        response = self.client.post("/webhook", json={"test": "data"}, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid signature")

if __name__ == "__main__":
    unittest.main()

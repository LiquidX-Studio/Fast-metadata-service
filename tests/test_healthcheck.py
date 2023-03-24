import unittest
from http import HTTPStatus

from fastapi.testclient import TestClient

from main import app


class TestHealthcheckEndpoint(unittest.TestCase):
    client = TestClient(app)

    def test_get_healthcheck(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, HTTPStatus.OK)

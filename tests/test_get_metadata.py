import os
import unittest
from http import HTTPStatus

from fastapi.testclient import TestClient

from main import app
from module.env import Env


class TestGetMetadataEndpoint(unittest.TestCase):
    client = TestClient(app)

    def test_get_metadata(self):
        for token in range(1, 4):
            response = self.client.get(f"/metadata/{token}")
            file_path = os.path.join(Env.METADATA_FOLDER, f"{token}.json")
            with open(file_path, "rb") as metadata_file:
                self.assertEqual(response.read(), metadata_file.read().strip())

    def test_get_metadata_non_exist_metadata_file(self):
        response = self.client.get(f"/metadata/5")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_metadata_invalid_json_format(self):
        response = self.client.get(f"/metadata/4")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_get_metadata_beyond_token_id_range(self):
        for token in [0, int(Env.MAX_TOKEN_ID) + 1]:
            response = self.client.get(f"/metadata/{token}")
            self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_get_metadata_with_invalid_token_format(self):
        for token in ["legawa", 2.0, False]:
            response = self.client.get(f"/metadata/{token}")
            self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

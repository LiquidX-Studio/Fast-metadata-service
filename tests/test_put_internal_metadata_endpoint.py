import json
import os
import shutil
import stat
import unittest
from http import HTTPStatus

from fastapi.testclient import TestClient

from main import app
from module.env import Env
from module.response import Response
from tests.constant import METADATA_DIR, TEST_FILE
from tests.utils import generate_token


class TestPutInternalMetadataEndpoint(unittest.TestCase):
    client = TestClient(app)
    token = generate_token()
    header = {"Authorization": f"{token}"}
    backup_dir = os.path.join(TEST_FILE, "backup")
    new_metadata = {
        "name": "New Name",
        "attributes": [
            {
                "trait_type": "Attack",
                "value": 0
            }
        ]
    }

    def tearDown(self):
        if os.path.isdir(self.backup_dir):
            shutil.rmtree(self.backup_dir)

    def test_change_existing_metadata_file(self):
        token_id = 1
        metadata_file = os.path.join(METADATA_DIR, f"{token_id}.json")
        with open(metadata_file) as file:
            metadata = json.load(file)

        response = self.client.put(f"/internal/update/metadata/{token_id}",
                                   json=self.new_metadata,
                                   headers=self.header)

        expected_response = {"name": "New Name",
                             "image_url": "https://pixelmon-training-rewards.s3-accelerate.amazonaws.com/0/Moler.jpg",
                             "animation_url": "https://pixelmon-test-nft.s3.ap-southeast-1.amazonaws.com/6/Moler.mp4",
                             "external_url": "https://pixelmon.club/",
                             "attributes": [{"trait_type": "Species", "value": "Moler"},
                                            {"trait_type": "Origin", "value": "Earth"},
                                            {"trait_type": "Rarity", "value": "Uncommon"},
                                            {"trait_type": "HP", "value": 33},
                                            {"trait_type": "Attack", "value": 0},
                                            {"trait_type": "Defense", "value": 46},
                                            {"trait_type": "Special Attack", "value": 27},
                                            {"trait_type": "Special Defense", "value": 32},
                                            {"trait_type": "Affinity", "value": 100},
                                            {"trait_type": "Luck", "value": 4, "display_type": "boost_number"},
                                            {"trait_type": "Reward Multiplier", "value": 10,
                                             "display_type": "boost_percentage"},
                                            {"trait_type": "Unknown 1", "value": 3},
                                            {"trait_type": "Unknown 2", "value": 8},
                                            {"trait_type": "Generation", "value": 1, "display_type": "number"},
                                            {"trait_type": "Evolution", "value": 1, "display_type": "number"},
                                            {"trait_type": "Hatched On", "value": 1652217733, "display_type": "date"}],
                             "hatched": True,
                             "reward_bitmask": 6}

        with open(metadata_file, "w") as file:
            file.write(json.dumps(metadata))

        self.assertTrue(os.path.isdir(self.backup_dir))
        self.assertGreater(len(os.listdir(self.backup_dir)), 0)
        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_change_nonexist_metadata_file(self):
        token_id = 5
        response = self.client.put(f"/internal/update/metadata/{token_id}",
                                   json=self.new_metadata,
                                   headers=self.header)
        detail, status = Response.NOT_FOUND
        self.assertEqual(response.json(), detail)
        self.assertEqual(response.status_code, status)

    def test_change_nonexist_metadata_attribute(self):
        token_id = 1
        new_metadata = {
            "new_key": "new_value",
            "attributes": [
                {
                    "trait_type": "New trait",
                    "value": "new value"
                }
            ]
        }
        response = self.client.put(f"/internal/update/metadata/{token_id}",
                                   json=new_metadata,
                                   headers=self.header)
        expected_response = {
            "detail": "Trait type(s) 'New trait' not found in metadata"
        }
        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_change_nonexist_key_in_metadata(self):
        token_id = 1
        new_metadata = {
            "new_key": "new_value",
        }
        response = self.client.put(f"/internal/update/metadata/{token_id}",
                                   json=new_metadata,
                                   headers=self.header)
        expected_response = {
            "detail": "Key(s) 'new_key' not found in metadata"
        }
        self.assertEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_update_metadata_with_invalid_token_id(self):
        token_id = Env.MAX_TOKEN_ID + 1
        response = self.client.put(f"/internal/update/metadata/{token_id}",
                                   json=self.new_metadata,
                                   headers=self.header)

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_update_metadata_with_empty_metadata(self):
        token_id = 1
        response = self.client.put(f"/internal/update/metadata/{token_id}",
                                   json={},
                                   headers=self.header)

        detail, status = Response.VALUE_REQUIRED
        self.assertDictEqual(response.json(), detail)
        self.assertEqual(response.status_code, status)

    def test_update_metadata_with_failed_to_save_to_storage(self):
        token_id = 1
        metadata = os.path.join(METADATA_DIR, f"{token_id}.json")
        read_only_permission = stat.S_IRUSR
        os.chmod(metadata, read_only_permission)
        response = self.client.put(f"/internal/update/metadata/{token_id}",
                                   json=self.new_metadata,
                                   headers=self.header)
        read_write_permission = stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP + stat.S_IROTH
        os.chmod(metadata, read_write_permission)
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

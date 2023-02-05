import asyncio
import json
import os
import unittest
from unittest.mock import patch

from module.utils import save_metadata
from module.env import Env
from module.response import Response
from tests.constant import METADATA_DIR


class TestSaveMetadata(unittest.TestCase):

    metadata = {
        "name": "some name",
        "image_url": "https://image-url.url/image.png"
    }
    token_id = 5

    @patch.object(Env, 'METADATA_FOLDER')
    def setUp(self, mock_folder) -> None:
        mock_folder.return_value = METADATA_DIR

    def test_create_new_metadata(self):
        file_path = os.path.join(Env.METADATA_FOLDER, f"{self.token_id}.json")
        response = asyncio.run(save_metadata(self.token_id, self.metadata))
        with open(file_path, "r") as file:
            self.assertEqual(json.loads(file.read()), self.metadata)
            self.assertEqual(response, Response.OK)
        os.unlink(file_path)

    def test_prevent_overwrite_data(self):
        file_path = os.path.join(Env.METADATA_FOLDER, f"{self.token_id}.json")
        asyncio.run(save_metadata(self.token_id, self.metadata))
        response = asyncio.run(save_metadata(self.token_id, self.metadata))
        os.unlink(file_path)
        self.assertEqual(response, Response.FILE_EXISTS)

    def test_overwrite_data(self):
        new_metadata = {
            "name": "new name",
            "image_url": "https://image-url.url/image.png"
        }
        file_path = os.path.join(Env.METADATA_FOLDER, f"{self.token_id}.json")
        asyncio.run(save_metadata(self.token_id, self.metadata))
        response = asyncio.run(save_metadata(self.token_id, new_metadata, overwrite=True))
        with open(file_path, "r") as file:
            self.assertEqual(json.loads(file.read()), new_metadata)
            self.assertEqual(response, Response.OK)
        os.unlink(file_path)

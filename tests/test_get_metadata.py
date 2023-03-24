import asyncio
import json
import os
import unittest
from http import HTTPStatus
from unittest.mock import patch

from module.utils import get_metadata
from module.env import Env
from module.response import Response
from tests.constant import METADATA_DIR


class TestGetMetadata(unittest.TestCase):

    @patch.object(Env, 'METADATA_FOLDER')
    def setUp(self, mock_folder) -> None:
        mock_folder.return_value = METADATA_DIR

    def test_get_metadata(self):
        response, status = asyncio.run(get_metadata(2))
        file_path = os.path.join(Env.METADATA_FOLDER, "2.json")
        with open(file_path) as metadata_file:
            metadata = json.loads(metadata_file.read())
            self.assertDictEqual(metadata, response)
            self.assertEqual(status, HTTPStatus.OK)

    def test_get_metadata_not_found(self):
        response = asyncio.run(get_metadata(3749210))
        self.assertEqual(response, Response.NOT_FOUND)

    def test_get_invalid_metadata_format(self):
        _, status = asyncio.run(get_metadata(4))
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
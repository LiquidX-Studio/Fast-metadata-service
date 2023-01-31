import asyncio
import unittest
from unittest.mock import patch

from module.logger import logger
from module.schema.storage import StorageType
from module.storage.main import Storage


class TestStorageS3(unittest.TestCase):
    storage = Storage(logger, StorageType.S3)

    @patch("module.storage.s3.aioboto3")
    def test_get_file(self, mock_storage):
        mock_storage.Session().client("s3").get_object.return_value = "hello"
        asyncio.run(self.storage.get("hello"))

    def test_invalid_parameter(self):
        response = asyncio.run(self.storage.get(""))
        self.assertIsNone(response)

    def test_client_error(self):
        response = asyncio.run(self.storage.get("nonexist-file"))
        self.assertIsNone(response)

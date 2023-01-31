import asyncio
import os
import stat
import unittest

from module.logger import logger
from module.schema.storage import StorageType
from module.storage.main import Storage
from tests.constant import METADATA_DIR


class TestStorageLocal(unittest.TestCase):
    storage = Storage(logger, StorageType.Local)

    def test_get_file(self):
        metadata = os.path.join(METADATA_DIR, "1.json")
        content = asyncio.run(self.storage.get(metadata))
        with open(metadata, "rb") as file:
            self.assertEqual(content, file.read())

    def test_read_nonexist_file(self):
        metadata = os.path.join(METADATA_DIR, "nonexist.json")
        content = asyncio.run(self.storage.get(metadata))
        self.assertIsNone(content)

    def test_read_restricted_file(self):
        metadata = os.path.join(METADATA_DIR, "2.json")
        os.chmod(metadata, 200)
        content = asyncio.run(self.storage.get(metadata))
        os.chmod(metadata, stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP + stat.S_IROTH)
        self.assertIsNone(content)

    def test_read_directory(self):
        content = asyncio.run(self.storage.get(METADATA_DIR))
        self.assertIsNone(content)

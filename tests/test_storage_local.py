import asyncio
import os
import stat
import unittest
from http import HTTPStatus
from unittest.mock import patch

import aiofiles
import aiofiles.os

from module.logger import logger
from module.response import Response
from module.schema.storage import StorageType
from module.storage.main import Storage
from tests.constant import METADATA_DIR


class TestStorageLocal(unittest.TestCase):
    storage = Storage(logger, StorageType.Local)

    def test_read_file(self):
        metadata = os.path.join(METADATA_DIR, "1.json")
        response, status = asyncio.run(self.storage.get(metadata))
        with open(metadata, "rb") as file:
            self.assertEqual(response, file.read())
        self.assertEqual(status, HTTPStatus.OK)

    def test_read_nonexist_file(self):
        metadata = os.path.join(METADATA_DIR, "nonexist.json")
        response, status = asyncio.run(self.storage.get(metadata))
        expected_response, expected_status = Response.NOT_FOUND
        self.assertDictEqual(expected_response, response)
        self.assertEqual(status, expected_status)

    def test_read_restricted_file(self):
        metadata = os.path.join(METADATA_DIR, "2.json")
        write_only_permission = stat.S_IWUSR
        os.chmod(metadata, write_only_permission)
        response, status = asyncio.run(self.storage.get(metadata))
        read_write_permission = stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP + stat.S_IROTH
        os.chmod(metadata, read_write_permission)
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(expected_response, response)
        self.assertEqual(status, expected_status)

    def test_read_directory(self):
        response, status = asyncio.run(self.storage.get(METADATA_DIR))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(expected_response, response)
        self.assertEqual(status, expected_status)

    @patch.object(aiofiles, "open")
    def test_unknown_exception_on_read(self, mock_aiofiles):
        mock_aiofiles.side_effect = Exception
        response, status = asyncio.run(self.storage.get(METADATA_DIR))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(expected_response, response)

    def test_write_file(self):
        metadata = os.path.join(METADATA_DIR, "1.json")
        with open(metadata, "rb") as file:
            metadata = metadata.replace("1.json", "test.json")
            response, status = asyncio.run(self.storage.put(metadata, file.read()))

        self.assertEqual(response, {"status": "success"})
        self.assertEqual(status, HTTPStatus.OK)
        os.unlink(metadata)

    def test_write_file_nonexist_directory(self):
        response, status = asyncio.run(self.storage.put("path/to/nonexist/directory/file.json", b"test"))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(expected_response, response)
        self.assertEqual(status, expected_status)

    def test_write_file_to_directory(self):
        response, status = asyncio.run(self.storage.put(METADATA_DIR, b"test"))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(expected_response, response)
        self.assertEqual(status, expected_status)

    def test_write_permission_error(self):
        metadata = os.path.join(METADATA_DIR, "4.json")
        read_only_permission = stat.S_IRUSR
        os.chmod(metadata, read_only_permission)
        response, status = asyncio.run(self.storage.put(metadata, b"test", overwrite=True))
        read_write_permission = stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP + stat.S_IROTH
        os.chmod(metadata, read_write_permission)
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(expected_response, response)
        self.assertEqual(status, expected_status)

    @patch.object(aiofiles, "open")
    def test_unknown_exception_on_write(self, mock_aiofiles):
        mock_aiofiles.side_effect = Exception
        response, status = asyncio.run(self.storage.put(METADATA_DIR, b"test"))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(expected_response, response)
        self.assertEqual(status, expected_status)

    def test_check_path_exists(self):
        metadata = os.path.join(METADATA_DIR, "2.json")
        response, status = asyncio.run(self.storage.is_exists(metadata))
        self.assertTrue(response)
        self.assertEqual(status, HTTPStatus.OK)

    def test_check_path_not_exists(self):
        metadata = os.path.join(METADATA_DIR, "non-exist.json")
        response, status = asyncio.run(self.storage.is_exists(metadata))
        self.assertFalse(response)
        self.assertEqual(status, HTTPStatus.NOT_FOUND)

    @patch.object(aiofiles.os.path, "exists")
    def test_unknown_exception_on_check_path(self, mock_path_exists):
        mock_path_exists.side_effect = Exception
        metadata = os.path.join(METADATA_DIR, "2.json")
        response = asyncio.run(self.storage.is_exists(metadata))
        self.assertEqual(response, Response.STORAGE_OPERATION_FAIL)

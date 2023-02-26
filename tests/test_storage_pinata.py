import asyncio
import json
import unittest
from collections import namedtuple
from http import HTTPStatus
from unittest.mock import patch

from aiohttp import ClientSession

from module.logger import logger
from module.response import Response
from module.schema.storage import StorageType
from module.storage.main import Storage
from tests.mock_class import MockAioHTTP


class TestStoragePinata(unittest.TestCase):
    storage = Storage(logger, StorageType.Pinata)
    ReturnValue = namedtuple("expected_return_value", ["status", "message"])
    response = {
        "rows": [
            {
                "ipfs_pin_hash": "QmYQv4Fn7qWucBneGPehjzc6wHNMCA8P7pz4qGzd666666"
            }
        ]
    }

    @patch.object(ClientSession, "request")
    def test_get_file(self, mock_http):
        expected_return_value = self.ReturnValue(status=200, message=json.dumps(self.response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res, status = asyncio.run(self.storage.get("3.json"))
        self.assertEqual(res, expected_return_value.message)
        self.assertEqual(status, expected_return_value.status)

    @patch.object(ClientSession, "request")
    def test_get_file_in_directory(self, mock_http):
        response = {
            "rows": [
                {
                    "ipfs_pin_hash": "QmYQv4Fn7qWucBneGPehjzc6wHNMCA8P7pz4qGzd999999"
                }
            ]
        }

        expected_return_value = self.ReturnValue(status=200, message=json.dumps(response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res, status = asyncio.run(self.storage.get("directory/3.json"))
        self.assertEqual(res, expected_return_value.message)
        self.assertEqual(status, expected_return_value.status)

    @patch.object(ClientSession, "request")
    def test_invalid_access_key(self, mock_http):
        response = {
            "error": {
                "reason": "INVALID_API_KEYS",
                "details": "Invalid API key provided"
            }
        }

        expected_return_value = self.ReturnValue(status=401, message=json.dumps(response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.get("directory/3.json"))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_invalid_request(self, mock_http):
        response = {
            "error": {
                "reason": "INVALID_REQUEST",
                "details": "Invalid request body provided"
            }
        }

        expected_return_value = self.ReturnValue(status=400, message=json.dumps(response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.get("directory/3.json"))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_pinata_failure(self, mock_http):
        response = {
            "error": {
                "reason": "INTERNAL_ERROR",
                "details": "Failed to respond"
            }
        }

        expected_return_value = self.ReturnValue(status=500, message=json.dumps(response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.get("directory/3.json"))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_invalid_json_response(self, mock_http):
        expected_return_value = self.ReturnValue(status=200, message=b"str response")
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.get("directory/3.json"))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_raise_unknown_exception(self, mock_http):
        mock_http.side_effect = Exception("Unknown error")
        res = asyncio.run(self.storage.get("directory/3.json"))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_timeout_request(self, mock_http):
        mock_http.side_effect = asyncio.exceptions.TimeoutError
        res = asyncio.run(self.storage.get("directory/3.json"))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_nonexist_file(self, mock_http):
        expected_return_value = self.ReturnValue(status=500, message=b"no link named")
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.storage._fetch_metadata("directory/3.json"))
        self.assertEqual(res, Response.NOT_FOUND)

    @patch.object(ClientSession, "request")
    def test_overwrite_file(self, mock_http):
        expected_return_value = self.ReturnValue(status=200, message=json.dumps(self.response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.put("3.json", b"new content", overwrite=True))
        self.assertEqual(res, Response.OK)

    @patch.object(ClientSession, "request")
    def test_prevent_overwriting_file(self, mock_http):
        expected_return_value = self.ReturnValue(status=200, message=json.dumps(self.response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.put("3.json", b"new content", overwrite=False))
        self.assertEqual(res, Response.FILE_EXISTS)

    @patch.object(ClientSession, "request")
    def test_create_new_file(self, mock_http):
        response = {"rows": []}
        expected_return_value = self.ReturnValue(status=200, message=json.dumps(response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.put("3.json", b"new content", overwrite=False))
        self.assertEqual(res, Response.OK)

    def test_update_directory(self):
        res = asyncio.run(self.storage.put("directory/3.json", b"new content", overwrite=False))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_fail_to_connect_pinata_when_uploading(self, mock_http):
        expected_return_value = self.ReturnValue(status=500, message=b"failed to upload")
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.put("3.json", b"new content", overwrite=False))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_fail_to_upload(self, mock_http):
        expected_first_return_value = self.ReturnValue(status=200, message=json.dumps(self.response).encode("utf-8"))
        expected_second_return_value = self.ReturnValue(status=500, message=b"failed to upload")
        mock_http().__aenter__.side_effect = [MockAioHTTP(expected_return_value=expected_first_return_value),
                                              MockAioHTTP(expected_return_value=expected_second_return_value)]
        res = asyncio.run(self.storage.put("3.json", b"new content", overwrite=True))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(ClientSession, "request")
    def test_file_exists(self, mock_http):
        expected_return_value = self.ReturnValue(status=200, message=json.dumps(self.response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        exists, status = asyncio.run(self.storage.is_exists("3.json"))
        self.assertTrue(exists)
        self.assertEqual(status, HTTPStatus.OK)

    @patch.object(ClientSession, "request")
    def test_file_exists(self, mock_http):
        expected_return_value = self.ReturnValue(status=200, message=json.dumps(self.response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        exists, status = asyncio.run(self.storage.is_exists("directory/3.json"))
        self.assertTrue(exists)
        self.assertEqual(status, HTTPStatus.OK)

    @patch.object(ClientSession, "request")
    def test_file_not_exists(self, mock_http):
        response = {"rows": []}
        expected_return_value = self.ReturnValue(status=200, message=json.dumps(response).encode("utf-8"))
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        exists, status = asyncio.run(self.storage.is_exists("3.json"))
        self.assertFalse(exists)
        self.assertEqual(status, HTTPStatus.NOT_FOUND)

    @patch.object(ClientSession, "request")
    def test_file_not_exists(self, mock_http):
        expected_return_value = self.ReturnValue(status=500, message=b"failed to connect")
        mock_http().__aenter__.return_value = MockAioHTTP(expected_return_value=expected_return_value)
        res = asyncio.run(self.storage.is_exists("3.json"))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

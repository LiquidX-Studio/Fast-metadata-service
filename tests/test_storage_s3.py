import asyncio
import unittest
from http import HTTPStatus
from unittest.mock import patch

import botocore.exceptions

from module.logger import logger
from module.response import Response
from module.schema.storage import StorageType
from module.storage.main import Storage
from module.storage.s3 import aioboto3
from tests.mock_class import MockAioboto3Session, S3Method


class DummyMetadataFile:
    async def read(self):
        return {"name": "NFT", "image_url": "https://image-url"}


class TestStorageS3(unittest.TestCase):
    storage = Storage(logger, StorageType.S3)

    @patch.object(aioboto3, "Session")
    def test_get_file(self, mock_boto3):
        return_value = {"Body": DummyMetadataFile()}
        mock_boto3.return_value = MockAioboto3Session(S3Method.get_object, expected_return_value=return_value)
        response, status = asyncio.run(self.storage.get("hello"))
        self.assertDictEqual(response, {"name": "NFT", "image_url": "https://image-url"})
        self.assertEqual(status, HTTPStatus.OK)

    @patch.object(aioboto3, "Session")
    def test_invalid_parameter_on_read(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(
            S3Method.get_object,
            expected_side_effect=botocore.exceptions.ParamValidationError(report="invalid parameter")
        )
        response, status = asyncio.run(self.storage.get("hello"))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(response, expected_response)
        self.assertEqual(status, expected_status)

    @patch.object(aioboto3, "Session")
    def test_client_error_on_read(self, mock_boto3):
        error = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": "Unknown"}},
            operation_name="test"
        )

        mock_boto3.return_value = MockAioboto3Session(S3Method.get_object, expected_side_effect=error)
        response, status = asyncio.run(self.storage.get(".cry"))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(response, expected_response)
        self.assertEqual(status, expected_status)

    @patch.object(aioboto3, "Session")
    def test_file_not_found(self, mock_boto3):
        error = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": "NoSuchKey"}},
            operation_name="test"
        )

        mock_boto3.return_value = MockAioboto3Session(S3Method.get_object, expected_side_effect=error)
        response, status = asyncio.run(self.storage.get("nonexist-file"))
        expected_response, expected_status = Response.NOT_FOUND
        self.assertDictEqual(response, expected_response)
        self.assertEqual(status, expected_status)

    @patch.object(aioboto3, "Session")
    def test_unknown_exception_on_read(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(S3Method.get_object, expected_side_effect=Exception)
        response, status = asyncio.run(self.storage.get("test"))
        expected_response, expected_status = Response.STORAGE_OPERATION_FAIL
        self.assertDictEqual(response, expected_response)
        self.assertEqual(status, expected_status)

    @patch.object(aioboto3, "Session")
    def test_upload_file_and_overwrite(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(S3Method.put_object, expected_return_value=Response.OK)
        response = asyncio.run(self.storage.put("4.json", b"test", overwrite=True))
        self.assertEqual(response, Response.OK)
        response = asyncio.run(self.storage.put("new-directory/4.json", b"test", overwrite=True))
        self.assertEqual(response, Response.OK)

    @patch.object(aioboto3, "Session")
    def test_upload_file_and_not_overwrite(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(S3Method.head_object, expected_return_value=True)
        exists, status = asyncio.run(self.storage.put("4.json", b"test", overwrite=False))
        self.assertTrue(exists)
        self.assertEqual(status, HTTPStatus.CONFLICT)

    @patch.object(aioboto3, "Session")
    def test_failed_to_upload_file(self, mock_boto3):
        error = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": "Unknown"}},
            operation_name="test"
        )
        mock_boto3.return_value = MockAioboto3Session(S3Method.head_object, expected_side_effect=error)
        res = asyncio.run(self.storage.put("4.json", b"test", overwrite=False))
        self.assertEqual(res, Response.STORAGE_OPERATION_FAIL)

    @patch.object(aioboto3, "Session")
    def test_upload_new_file_and_not_overwrite(self, mock_boto3):
        error = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": "404"}},
            operation_name="test"
        )

        mock_boto3.return_value = MockAioboto3Session(
            S3Method.head_object,
            expected_side_effect=error
        )
        response = asyncio.run(self.storage.put("new-directory/4x.json", b"test", overwrite=False))
        self.assertEqual(response, Response.OK)

    @patch.object(aioboto3, "Session")
    def test_invalid_parameter_on_write(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(
            S3Method.put_object,
            expected_side_effect=botocore.exceptions.ParamValidationError(report="invalid parameter")
        )
        response = asyncio.run(self.storage.put("4.json", b"test", overwrite=True))
        self.assertEqual(response, Response.STORAGE_OPERATION_FAIL)

    @patch.object(aioboto3, "Session")
    def test_client_error_on_write(self, mock_boto3):
        error = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": "Unknown"}},
            operation_name="test"
        )

        mock_boto3.return_value = MockAioboto3Session(
            S3Method.put_object,
            expected_side_effect=error
        )

        response = asyncio.run(self.storage.put("4.json", b"test", overwrite=True))
        self.assertEqual(response, Response.STORAGE_OPERATION_FAIL)

    @patch.object(aioboto3, "Session")
    def test_unknown_exception_on_write(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(
            S3Method.put_object,
            expected_side_effect=Exception
        )
        response = asyncio.run(self.storage.put("4.json", b"test", overwrite=True))
        self.assertEqual(response, Response.STORAGE_OPERATION_FAIL)

    @patch.object(aioboto3, "Session")
    def test_check_file_exists(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(S3Method.head_object, expected_return_value=True)
        exists, status = asyncio.run(self.storage.is_exists("4.json"))
        self.assertTrue(exists)
        self.assertEqual(status, HTTPStatus.OK)

        error = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": "404"}},
            operation_name="test"
        )

        mock_boto3.return_value = MockAioboto3Session(
            S3Method.head_object,
            expected_side_effect=error
        )

        exists, status = asyncio.run(self.storage.is_exists("4.json"))
        self.assertFalse(exists)
        self.assertEqual(status, HTTPStatus.NOT_FOUND)

    @patch.object(aioboto3, "Session")
    def test_check_file_client_error(self, mock_boto3):
        error = botocore.exceptions.ClientError(
            error_response={"Error": {"Code": "Unknown"}},
            operation_name="test"
        )
        mock_boto3.return_value = MockAioboto3Session(S3Method.head_object, expected_side_effect=error)
        response = asyncio.run(self.storage.is_exists("4.json"))
        self.assertEqual(response, Response.STORAGE_OPERATION_FAIL)

    @patch.object(aioboto3, "Session")
    def test_invalid_parameter_on_check(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(
            S3Method.head_object,
            expected_side_effect=botocore.exceptions.ParamValidationError(report="invalid parameter")
        )
        response = asyncio.run(self.storage.is_exists("4.json"))
        self.assertEqual(response, Response.STORAGE_OPERATION_FAIL)

    @patch.object(aioboto3, "Session")
    def test_check_file_unknown_exception(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(
            S3Method.head_object,
            expected_side_effect=Exception
        )
        response = asyncio.run(self.storage.is_exists("4.json"))
        self.assertEqual(response, Response.STORAGE_OPERATION_FAIL)

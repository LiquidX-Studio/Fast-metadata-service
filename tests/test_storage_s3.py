import asyncio
import unittest
from unittest.mock import patch

import botocore.exceptions

from module.logger import logger
from module.schema.storage import StorageType
from module.storage.main import Storage
from module.storage.s3 import aioboto3
from tests.mock_class import MockAioboto3Session


class DummyMetadataFile:
    async def read(self):
        return {"name": "NFT", "image_url": "https://image-url"}


class TestStorageS3(unittest.TestCase):
    storage = Storage(logger, StorageType.S3)

    def param_validation_error(self, *args, **kwargs):
        raise botocore.exceptions.ParamValidationError(report="invalid parameter")

    def client_error(self, *args, **kwargs):
        raise botocore.exceptions.ClientError(error_response={}, operation_name="test")

    @patch.object(aioboto3, "Session")
    def test_get_file(self, mock_boto3):
        return_value = {"Body": DummyMetadataFile()}
        mock_boto3.return_value = MockAioboto3Session(expected_return_value=return_value)
        response = asyncio.run(self.storage.get("hello"))
        self.assertDictEqual(response, {"name": "NFT", "image_url": "https://image-url"})

    @patch.object(aioboto3, "Session")
    def test_invalid_parameter(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(expected_side_effect=self.param_validation_error)
        response = asyncio.run(self.storage.get("hello"))
        self.assertIsNone(response)

    @patch.object(aioboto3, "Session")
    def test_client_error(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(expected_side_effect=self.client_error)
        response = asyncio.run(self.storage.get("nonexist-file"))
        self.assertIsNone(response)

    @patch.object(aioboto3, "Session")
    def test_unknown_exception(self, mock_boto3):
        mock_boto3.return_value = MockAioboto3Session(expected_side_effect=Exception)
        response = asyncio.run(self.storage.get("test"))
        self.assertIsNone(response)

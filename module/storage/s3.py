"""This module is used to interact with AWS S3 bucket"""

import logging
from http import HTTPStatus
from typing import Union

import aioboto3
import botocore.exceptions
from pydantic import validate_arguments

from module.env import Env
from module.response import Response
from module.storage.storage_interface import StorageInterface


class S3Storage(StorageInterface):
    """This class is used to interact with AWS S3 bucket"""

    S3 = "s3"
    bucket = Env.S3_BUCKET_NAME

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(self, logger: logging.Logger, config: dict, **kwargs):
        """Initialize S3Storage class

        Args:
            logger (logging.Logger): Logger object
            config (dict): Configuration dictionary
            **kwargs: Arbitrary keyword arguments

        """

        self.access_key = config.get("access_key")
        self.secret_key = config.get("secret_key")
        self.logger = logger

    @validate_arguments
    async def get(self, path: str, **kwargs) -> Union[tuple[bytes, HTTPStatus], Response]:
        """Get file from S3 bucket

        Args:
            path (str): Path to file

        Returns:
            Union[tuple[bytes, HTTPStatus], Response]: Response data and HTTP status

        """

        session = aioboto3.Session()
        async with session.client(self.S3,
                                  aws_access_key_id=self.access_key,
                                  aws_secret_access_key=self.secret_key) as s3:
            try:
                self.logger.info("Load file %s from bucket %s", path, self.bucket)
                file = await s3.get_object(Bucket=self.bucket, Key=path)
                if file is not None:
                    return await file["Body"].read(), HTTPStatus.OK
            except botocore.exceptions.ParamValidationError as err:
                self.logger.error("Invalid parameter added when loading from S3 bucket. Error: %s", str(err))
            except botocore.exceptions.ClientError as err:
                self.logger.error("Failed to load file from S3 bucket. Error: %s", str(err))
                if "NoSuchKey" in str(err):
                    return Response.NOT_FOUND
            except Exception as err:
                self.logger.error("Failed to run operation on S3 bucket. Error: %s", str(err))
            return Response.STORAGE_OPERATION_FAIL

    @validate_arguments
    async def put(self, path: str, content: bytes, overwrite=False, **kwargs) -> Response:
        """Put file to S3 bucket

        Args:
            path (str): Path to file
            content (bytes): File content in bytes
            overwrite (bool, optional): Overwrite file if exists. Defaults to False

        Returns:
            dict: Response data
            HTTPStatus: HTTP response code

        """

        session = aioboto3.Session()

        if not overwrite:
            response, status = await self.is_exists(path)
            if response:
                self.logger.warning("Abort overwriting file %s since it exists in bucket %s", path, self.bucket)
            if status != HTTPStatus.NOT_FOUND and status != HTTPStatus.OK:
                return response, status
            elif status == HTTPStatus.OK:
                return Response.FILE_EXISTS

        async with session.client(self.S3,
                                  aws_access_key_id=self.access_key,
                                  aws_secret_access_key=self.secret_key) as s3:
            try:
                self.logger.info("Save file %s to bucket %s", path, self.bucket)
                await s3.put_object(Bucket=self.bucket, Key=path, Body=content)
                return Response.OK
            except botocore.exceptions.ParamValidationError as err:
                self.logger.error("Invalid parameter added when saving to S3 bucket. Error: %s", str(err))
            except botocore.exceptions.ClientError as err:
                self.logger.error("Failed to save file to S3 bucket. Error: %s", str(err))
            except Exception as err:
                self.logger.error("Failed to run operation on S3 bucket. Error: %s", str(err))
            return Response.STORAGE_OPERATION_FAIL

    @validate_arguments
    async def is_exists(self,
                        path: str,
                        **kwargs) -> Union[tuple[bool, HTTPStatus], Response]:
        """Check if file exists in S3 bucket

        Args:
            path (str): Path to file
            **kwargs: Arbitrary keyword arguments

        Returns:
            Union[tuple[bool, HTTPStatus], Response]: Response data and HTTP status

        """

        session = aioboto3.Session()
        async with session.client(self.S3,
                                  aws_access_key_id=self.access_key,
                                  aws_secret_access_key=self.secret_key) as s3:
            try:
                await s3.head_object(Bucket=self.bucket, Key=path)
                self.logger.info("File %s exists in bucket %s", path, self.bucket)
                return True, HTTPStatus.OK
            except botocore.exceptions.ParamValidationError as err:
                self.logger.error("Invalid parameter added when accessing S3 bucket. Error: %s", str(err))
            except botocore.exceptions.ClientError as err:
                if "error occurred (404)" in str(err):
                    self.logger.warning("File %s in bucket %s not found. Error: %s", path, self.bucket, str(err))
                    return False, HTTPStatus.NOT_FOUND
                self.logger.error("Failed to check file in S3 bucket. Error: %s", str(err))
            except Exception as err:
                self.logger.error("Failed to run operation on S3 bucket. Error: %s", str(err))
        return Response.STORAGE_OPERATION_FAIL

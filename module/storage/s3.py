"""This module is used to interact with AWS S3 bucket"""

import logging

import aioboto3
import botocore.exceptions
from pydantic import validate_arguments

from module.env import Env
from module.storage.interface import StorageInterface


class S3Storage(StorageInterface):
    """This class is used to interact with AWS S3 bucket"""

    S3 = "s3"

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
    async def get(self, path: str):
        """Get file from S3 bucket

        Args:
            path (str): Path to file

        Returns:
            bytes: File content in bytes
            None: File not found or error occured

        """

        session = aioboto3.Session()
        bucket = Env.S3_BUCKET_NAME.value
        async with session.client(self.S3,
                                  aws_access_key_id=self.access_key,
                                  aws_secret_access_key=self.secret_key) as s3:
            try:
                self.logger.info("Load file %s from bucket %s", path, bucket)
                file = await s3.get_object(Bucket=bucket, Key=path)
                if file is not None:
                    return await file["Body"].read()
            except botocore.exceptions.ParamValidationError as e:
                self.logger.error("Invalid parameter added when loading from S3 bucket. Error: %s", str(e))
            except botocore.exceptions.ClientError as e:
                self.logger.error("Failed to load file from S3 bucket. Error: %s", str(e))
            except Exception as e:
                self.logger.error("Failed to run operation on S3 bucket. Error: %s", str(e))

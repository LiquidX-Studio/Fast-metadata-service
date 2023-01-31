import logging

from pydantic import validate_arguments

from module.schema.storage import StorageType, Configuration
from module.storage.interface import StorageInterface
from module.storage.local import LocalStorage
from module.storage.s3 import S3Storage


class Storage(StorageInterface):
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(self, logger: logging.Logger, storage: StorageType, config: Configuration = {}, **kwargs):
        if storage == StorageType.S3:
            self.storage = S3Storage(logger, config)
        elif storage == StorageType.Local:
            self.storage = LocalStorage(logger)

    @validate_arguments
    async def get(self, path: str):
        return await self.storage.get(path)

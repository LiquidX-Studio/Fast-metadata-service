"""Main class storage aggregates all supported storage types.
This class should be the one that's imported if we want to
interact with storage.

Suppose we want to interact with a specific storage.
we can write the following code:

from module.env import Env
from module.storage.main import Storage

storage = Storage(logger, storage=Env.STORAGE_TYPE)
file = storage.get("metadata/1.json")

The code above will read the metadata/1.json file from a
storage specified in STORAGE_TYPE environment variable.
If STORAGE_TYPE value is "local" then it will find the file
within the project directory.

"""

import logging

from pydantic import validate_arguments

from module.schema.storage import StorageType, Configuration
from module.storage.interface import StorageInterface
from module.storage.local import LocalStorage
from module.storage.s3 import S3Storage


class Storage(StorageInterface):
    """Main storage class that aggregates all storage class"""

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(self, logger: logging.Logger, storage: StorageType, config: Configuration = {}, **kwargs):
        """Initializes the storage class. It will return respective
        storage class.

        Args:
            logger (logging.Logger): Logger object
            storage (StorageType): Storage type
            config (Configuration, optional): Configuration object. Defaults to {}.
            **kwargs: Arbitrary keyword arguments.

        Returns: Storage object

        """

        if storage == StorageType.S3:
            self.storage = S3Storage(logger, config)
        elif storage == StorageType.Local:
            self.storage = LocalStorage(logger)

    @validate_arguments
    async def get(self, path: str):
        """Method to get file from a storage"""
        return await self.storage.get(path)

import logging

from pydantic import validate_arguments

from module.storage.interface import StorageInterface


class LocalStorage(StorageInterface):
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(self, logger: logging.Logger, **kwargs):
        self.logger = logger

    @validate_arguments
    async def get(self, path: str) -> bytes:
        self.logger.info("Load file %s from local storage", path)
        try:
            with open(path, "rb") as file:
                return file.read()
        except FileNotFoundError:
            self.logger.error("File %s not found", path)
        except PermissionError as err:
            self.logger.error("Don't have permission to read %s. Error: %s", path, str(err))
        except Exception as err:
            self.logger.error("Failed to run read operation on %s. Error: %s", path, str(err))

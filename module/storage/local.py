"""This module is used to interact with local storage. Keep in mind
that there is no sanitization in this module, so it may be possible to
load file OUTSIDE the project directory.

"""

import logging

from pydantic import validate_arguments

from module.storage.interface import StorageInterface


class LocalStorage(StorageInterface):
    """Class to interact with local storage"""

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(self, logger: logging.Logger, **kwargs):
        """Initializes the LocalStorage class

        Args:
            logger (logging.Logger): Logger to use
            **kwargs (dict): Additional keyword arguments

        """
        self.logger = logger

    @validate_arguments
    async def get(self, path: str) -> bytes:
        """Get file from local storage. Keep in mind that
        there is no sanitization in this module, so it may
        be possible to load file OUTSIDE the project
        directory.

        Args:
            path (str): Path to the file to load.

        Returns:
            bytes: File content
            None: error occurred

        """

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

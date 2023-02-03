"""This module is used to interact with local storage. Keep in mind
that there is no sanitization in this module, so it may be possible to
load file OUTSIDE the project directory.

"""

import logging
import os
from http import HTTPStatus
from typing import Union

import aiofiles
import aiofiles.os
from pydantic import validate_arguments

from module.response import Response
from module.storage.storage_interface import StorageInterface


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
    async def get(self, path: str, **kwargs) -> Union[tuple[bytes, HTTPStatus], Response]:
        """Get file from local storage. Keep in mind that
        there is no sanitization in this module, so it may
        be possible to load file OUTSIDE the project
        directory.

        Args:
            path (str): Path to the file to load.

        Returns:
            Union[tuple[bytes, HTTPStatus], Response]: Response data and HTTP status

        """

        self.logger.info("Load file %s from local storage", path)
        try:
            async with aiofiles.open(path, "rb") as file:
                return await file.read(), HTTPStatus.OK
        except FileNotFoundError:
            self.logger.error("File %s not found", path)
            return Response.NOT_FOUND
        except IsADirectoryError:
            self.logger.error("Path %s is a directory", path)
        except PermissionError as err:
            self.logger.error("Don't have permission to read %s. Error: %s", path, str(err))
        except Exception as err:
            self.logger.error("Failed to run read operation on %s. Error: %s", path, str(err))
        return Response.STORAGE_OPERATION_FAIL

    @validate_arguments
    async def put(self, path: str, content: bytes, overwrite=False, **kwargs) -> Response:
        """Put file to local storage. Keep in mind that
        there is no sanitization in this module, so it may
        be possible to load file OUTSIDE the project
        directory.

        Args:
            path (str): Path to the file to load.
            content (bytes): File content to save.
            overwrite (bool, optional): Overwrite the file if it exists. Defaults to False.

        Returns:
            dict: response data
            HTTPStatus: HTTP status code

        """
        self.logger.info("Save file %s to local storage", path)
        try:
            if not overwrite and await aiofiles.os.path.isfile(path):
                self.logger.warning("Abort overwriting file %s since it exists", path)
                return Response.FILE_EXISTS

            async with aiofiles.open(path, "wb") as file:
                await file.write(content)
                return Response.OK
        except FileNotFoundError:
            self.logger.error("Directory %s not found", os.path.dirname(path))
        except IsADirectoryError:
            self.logger.error("Path %s is a directory", path)
        except PermissionError as err:
            self.logger.error("Don't have permission to write %s. Error: %s", path, str(err))
        except Exception as err:
            self.logger.error("Failed to run write operation on %s. Error: %s", path, str(err))
        return Response.STORAGE_OPERATION_FAIL

    @validate_arguments
    async def is_exists(self, path: str, **kwargs) -> Union[tuple[bool, HTTPStatus], Response]:
        """Check if file exists in local storage. Keep in mind that
        there is no sanitization in this module, so it may
        be possible to load file OUTSIDE the project
        directory.

        Args:
            path (str): Path to the file to load.

        Returns:
            Union[tuple[bool, HTTPStatus], Response]: Response data and HTTP status

        """

        try:
            exists = await aiofiles.os.path.exists(path)
            if exists:
                self.logger.info("File %s exists in local storage", path)
                return exists, HTTPStatus.OK
            else:
                self.logger.warning("File %s not found in local storage", path)
                return exists, HTTPStatus.NOT_FOUND
        except Exception as err:
            self.logger.error("Failed to check file %s. Error: %s", path, str(err))
            return Response.STORAGE_OPERATION_FAIL

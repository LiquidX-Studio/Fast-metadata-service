import asyncio
import json
import logging
import os
import urllib.parse
from http import HTTPStatus
from typing import Union

import aiohttp
from pydantic import validate_arguments, constr

from module.env import Env
from module.response import Response
from module.storage.storage_interface import StorageInterface


class PinataStorage(StorageInterface):
    """Class to interact with Pinata Storage"""

    timeout = aiohttp.ClientTimeout(total=10)

    def __init__(self, logger: logging.Logger, config: dict, **kwargs):
        """Initialize Pinata Storage class

        Args:
            logger (logging.Logger): Logger object
            config (dict): Configuration dictionary
            **kwargs: Arbitrary keyword arguments

        """

        if Env.PINATA_GATEWAY:
            self.host = f"https://{Env.PINATA_GATEWAY}.mypinata.cloud/ipfs/"
        else:
            self.host = "https://gateway.pinata.cloud/ipfs/"
        self.access_key = config.get("access_key")
        self.secret_key = config.get("secret_key")
        self.headers = {
            "pinata_api_key": self.access_key,
            "pinata_secret_api_key": self.secret_key
        }
        self.logger = logger

    @validate_arguments
    async def get(self, path: constr(min_length=1), **kwargs) -> Union[tuple[bytes, HTTPStatus], Response]:
        """Method to get file from Pinata storage

        Args:
            path (str): File path

        Returns:
            Union[tuple[bytes, HTTPStatus], Response]: Response data and HTTP Status

        Reference: https://docs.pinata.cloud/pinata-api/data/query-files

        """

        directory = os.path.dirname(path)
        file_path = path
        if directory:
            file_path = directory.split(os.path.sep)[0]
        response, status = await self._fetch_cid(file_path)
        if status != HTTPStatus.OK:
            return response, status
        file_hash = response
        if directory:
            file_hash = os.path.join(file_hash, os.path.sep.join(path.split(os.path.sep)[1:]))
        return await self._fetch_metadata(file_hash)

    @validate_arguments
    async def put(self, path: str, data: bytes, overwrite=False, **kwargs) -> Response:
        """Method to upload file to Pinata storage
        Currently, Pinata supports only replacing files in the root
        directory since IPFS keep files inside the folder immutable.
        So there is no way to overwrite a file inside a
        folder. Therefore, the operation will fail and raise an exception
        if we try to update a folder.

        Args:
            path (str): File path
            data (bytes): File data
            overwrite (bool, optional): Overwrite file. Defaults to False
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: response data
            HTTPStatus: HTTP status code

        Reference: 
        https://docs.pinata.cloud/pinata-api/pinning/pin-file-or-directory
        https://docs.pinata.cloud/pinata-api/pinning/remove-files-unpin

        """

        if os.path.dirname(path):
            self.logger.error("Overwrite a file inside a folder is not supported in IPFS")
            return Response.STORAGE_OPERATION_FAIL

        response, status = await self._fetch_cid(path)
        if status != HTTPStatus.OK and status != HTTPStatus.NOT_FOUND:
            return response, status

        if not overwrite and status == HTTPStatus.OK:
            self.logger.warning(f"Abort overwriting file since {path} already exists")
            return Response.FILE_EXISTS

        original_file_hash = response
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        body = {
            "file": data,
            "pinataOptions": '{"cidVersion": 1}',
            "pinataMetadata": f'{{"name": "{path}"}}'
        }

        response, status = await self._fetch(url, method="post", data=body, headers=self.headers)

        if status != HTTPStatus.OK:
            self.logger.error("Failed to upload file to Pinata. Error: %s", response)
            return Response.STORAGE_OPERATION_FAIL

        if overwrite:  # Unpin old file after upload a new one
            self.logger.info("Unpin file %s with CID %s from Pinata", path, original_file_hash)
            url = f"https://api.pinata.cloud/pinning/unpin/{original_file_hash}"
            await self._fetch(url, method="delete", headers=self.headers)

        return Response.OK

    @validate_arguments
    async def is_exists(self, path: str, **kwargs) -> Union[tuple[bool, HTTPStatus], Response]:
        """Method to check if file exists in the Pinata storage

        Args:
            path (str): File path
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Union[tuple[bool, HTTPStatus], Response]: Response data and HTTP Status

        """

        directory = os.path.dirname(path)
        file_path = path
        if directory:
            file_path = directory.split(os.path.sep)[0]
        response, status = await self._fetch_cid(file_path)
        if status != HTTPStatus.OK and status != HTTPStatus.NOT_FOUND:
            return response, status
        file_hash = response
        if directory and status == HTTPStatus.OK:
            file_hash = os.path.join(file_hash, os.path.sep.join(path.split(os.path.sep)[1:]))
            _, status = await self._fetch_metadata(file_hash)
        return status == HTTPStatus.OK, status

    async def _fetch(self, url: str, method: str, body: dict = {}, data=None, headers: dict = {}) -> (bytes, int):
        self.logger.info("Send %s request to Pinata %s", method.upper(), url)
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                if body:
                    async with session.request(method, url, json=body, headers=headers) as response:
                        return await response.read(), response.status
                else:
                    async with session.request(method, url, data=data, headers=headers) as response:
                        return await response.read(), response.status
        except asyncio.exceptions.TimeoutError:
            self.logger.error("Timeout error while connecting to Pinata")
            return Response.STORAGE_OPERATION_FAILED
        except Exception:
            self.logger.error("Failed to send %s request to %s\n Request details:\nheaders: %s\nbody: %s\ndata: %s",
                              method.upper(),
                              url,
                              headers,
                              body,
                              data)

    async def _fetch_cid(self, path: str) -> (str, int):
        try:
            url = f"https://api.pinata.cloud/data/pinList?includeCount=false&metadata[name]={path}&status=pinned"
            response, status = await self._fetch(url, method="get", headers=self.headers)
            if status != HTTPStatus.OK:
                raise ValueError
            response_data = json.loads(response.decode("utf-8"))
            if not response_data.get("rows", []):
                self.logger.error("File %s not found in Pinata Storage", path)
                return Response.NOT_FOUND
            return response_data["rows"][0].get("ipfs_pin_hash", ""), HTTPStatus.OK
        except json.decoder.JSONDecodeError:
            self.logger.error("Failed to parse Pinata response to JSON: %s", response)
        except ValueError:
            message = response.decode("utf-8")
            if status == HTTPStatus.UNAUTHORIZED:
                self.logger.error("Pinata access key or secret key is invalid: %s", message)
            elif status == HTTPStatus.BAD_REQUEST:
                self.logger.error("Invalid request sent to Pinata: %s", message)
            else:
                self.logger.error("Failed to load file from Pinata Storage: %s", message)
        except Exception as err:
            self.logger.error("Failed to load file from Pinata Storage: %s", err)
        return Response.STORAGE_OPERATION_FAIL

    async def _fetch_metadata(self, path: str) -> (bytes, int):
        url = urllib.parse.urljoin(self.host, path)
        response, status = await self._fetch(method="get", url=url)
        if status == HTTPStatus.INTERNAL_SERVER_ERROR and "no link named" in response.decode("utf-8"):
            return Response.NOT_FOUND
        return response, status

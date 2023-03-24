import json
import os
from datetime import datetime
from http import HTTPStatus
from typing import Union

from pydantic import validate_arguments, ValidationError

from config import storage
from module.env import Env
from module.logger import logger
from module.response import Response, _message
from module.schema.metadata import Attribute, Metadata


@validate_arguments
def update_metadata(source_metadata: Metadata,
                    new_value: dict,
                    overwrite=True) -> Union[tuple[dict, HTTPStatus], Response]:
    """Update value/attributes in metadata

    Args:
        source_metadata (Metadata): metadata to update
        new_value (Metadata): key/value pairs to update
        overwrite (bool, optional): overwrite existing key/attributes. Defaults to True

    Returns:
        Union[tuple[dict, HTTPStatus], Response]: Response data and HTTP status code

    """

    source_metadata = source_metadata.dict(exclude_none=True)
    ignored_keys = set()

    for key, value in new_value.items():
        if key == "attributes":
            response, status = update_attributes(source_metadata.get("attributes", []), value, overwrite)
            if status != HTTPStatus.OK:
                return response, status
            source_metadata[key] = response
            continue

        if overwrite:
            if key in source_metadata:
                source_metadata[key] = value
                continue
            ignored_keys.add(key)
        else:
            if key in source_metadata:
                ignored_keys.add(key)
                continue
            source_metadata[key] = value

    if ignored_keys:
        if not overwrite:
            issue = "already exists"
        else:
            issue = "not found"
        return _message(f"Key(s) '{', '.join(ignored_keys)}' {issue} in metadata", HTTPStatus.BAD_REQUEST)

    return source_metadata, HTTPStatus.OK


@validate_arguments
def update_attributes(source_attribute: list[Attribute],
                      new_attribute: list[Attribute],
                      overwrite=True) -> Union[tuple[list[dict], HTTPStatus], Response]:
    """Update attributes in metadata

    Args:
        source_attribute (list): attributes to update
        new_attribute (list[Attribute]): key/value pairs to update
        overwrite (bool, optional): overwrite existing attributes. Defaults to True

    Returns:
        Union[tuple[list[Attribute], HTTPStatus], Response]: Response data and HTTP status code

    """

    if not new_attribute or (not source_attribute and overwrite):
        return _message("No attributes to update", HTTPStatus.BAD_REQUEST)

    flattened_attributes = _flatten_attributes(source_attribute)
    ignored_keys = set()

    for attribute in new_attribute:
        current_attribute = attribute.dict(exclude_none=True)
        if overwrite:
            if attribute.trait_type in flattened_attributes:
                flattened_attributes[attribute.trait_type].update(current_attribute)
                continue
            ignored_keys.add(attribute.trait_type)

        elif not overwrite:
            if attribute.trait_type in flattened_attributes:
                ignored_keys.add(attribute.trait_type)
                continue
            flattened_attributes[attribute.trait_type] = current_attribute

    if ignored_keys:
        if not overwrite:
            issue = "already exists"
        else:
            issue = "not found"
        return _message(f"Trait type(s) '{', '.join(ignored_keys)}' {issue} in metadata", HTTPStatus.BAD_REQUEST)

    return list(flattened_attributes.values()), HTTPStatus.OK


@validate_arguments
def _flatten_attributes(attributes: list[Attribute]) -> dict[str, dict]:
    """Flatten list of attributes

    Args:
        attributes (list[Attribute]): list of attributes

    Returns:
         dict[str, dict]: flattened attributes

    """

    flattened_attributes = {}
    for attribute in attributes:
        flattened_attributes[attribute.trait_type] = attribute.dict(exclude_none=True)
    return flattened_attributes

@validate_arguments
async def get_metadata(token: int) -> Union[tuple[dict, HTTPStatus], Response]:
    """Get metadata for specific token ID from storage.
    It will load metadata from a directory specified
    in METADATA_FOLDER environment variable.

    Args:
        token (int): token ID

    Returns:
        Union[tuple[dict, HTTPStatus], Response]: Response data and HTTP status code

    """

    path = os.path.join(Env.METADATA_FOLDER, f"{token}.json")
    logger.info("Load metadata for token ID %s from path %s", token, path)
    response, status = await storage.get(path)
    if status != HTTPStatus.OK:
        return response, status
    try:
        Metadata.parse_raw(response)
    except ValidationError as err:
        logger.error("Invalid metadata format. Error: %s", str(err.errors()))
        return json.loads(err.json()), HTTPStatus.BAD_REQUEST
    return json.loads(response.decode("utf-8")), HTTPStatus.OK

@validate_arguments
async def save_metadata(token: int, metadata: Metadata, overwrite=False) -> Response:
    """Save metadata for specific token ID to storage.
    It will save to a folder specified in METADATA_FOLDER
    environment variable.

    Args:
        token (int): token ID
        metadata (Metadata): metadata in JSON format
        overwrite (bool, optional): overwrite existing metadata. Defaults to False

    Returns:
        Response: Response data

    """

    path = os.path.join(Env.METADATA_FOLDER, f"{token}.json")
    logger.info("Save metadata for token ID %s to path %s", token, path)
    return await storage.put(path,
                             metadata.json(exclude_none=True).encode("utf-8"),
                             overwrite)

@validate_arguments
async def create_backup(path: str, data: bytes) -> Response:
    """Create a backup file. It will create a 'backup' directory
    in a given path then put the backup file inside the backup
    directory. The backup file will contain data given in the
    parameter and the filename renamed to the following format:

        "filename_timestamp.extension"
    e.g.
        "myfile_09:22:05.445279.txt"

    Args:
        path (str): backup path
        data (bytes): file content

    Returns:
        Response: Response data

    """

    folder, file_ = os.path.split(path)
    filename, extension = os.path.splitext(file_)
    timestamp = datetime.now()
    backup_folder = os.path.join(folder, "backup", timestamp.date().isoformat())
    backup_file = f"{filename}_{timestamp.time().isoformat()}{extension}"
    backup_path = os.path.join(backup_folder, backup_file)
    logger.info("Backup file %s to %s", path, backup_path)
    return await storage.put(backup_path, data)
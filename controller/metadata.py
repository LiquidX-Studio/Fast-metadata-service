import json
import logging
import os
from http import HTTPStatus

from pydantic import ValidationError

from config import storage
from module.env import Env
from module.schema.metadata import Metadata


async def get(token: int, logger: logging.Logger):
    path = os.path.join(Env.METADATA_FOLDER, f"{token}.json")
    logger.info("Load metadata for token ID %s from path %s", token, path)
    metadata = await storage.get(path)
    try:
        Metadata.parse_raw(metadata)
    except ValidationError as err:
        logger.error("Invalid metadata format. Error: %s", str(err.errors()))
        return json.loads(err.json()), HTTPStatus.INTERNAL_SERVER_ERROR
    return json.loads(metadata.decode("utf-8")), HTTPStatus.OK

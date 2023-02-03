"""Metadata controller module contains all logic related to metadata.
It will be the logic behind the metadata endpoint

"""

import json
import os
from http import HTTPStatus

from pydantic import ValidationError

from config import storage
from module.env import Env
from module.logger import logger
from module.schema.metadata import Metadata


async def get(token: int):
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

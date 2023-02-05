"""Internal metadata controller contains logic that needed by backend
to interact with metadata. This will be the logic behind /internal/metadata
endpoint.

"""

import asyncio
import json
from copy import deepcopy
from http import HTTPStatus

from module.env import Env
from module.response import Response
from module.schema.metadata import MetadataRequestBody
from module.utils import get_metadata, update_metadata, save_metadata, create_backup


async def put(token: int, new_metadata: MetadataRequestBody) -> (dict, HTTPStatus):
    """Update metadata value controller

    Args:
        token (int): Metadata token ID
        new_metadata (MetadataRequestBody): Metadata value to be updated.

    Returns:
        response (dict): Response data
        status (HTTPStatus): HTTP status code

    """

    new_metadata = new_metadata.dict(exclude_unset=True)
    if not new_metadata:
        return Response.VALUE_REQUIRED
    response, status = await get_metadata(token)
    if status != HTTPStatus.OK:
        return response, status
    original_metadata = deepcopy(json.dumps(response, ensure_ascii=False).encode("utf-8"))
    response, status = update_metadata(response, new_metadata, overwrite=True)
    if status != HTTPStatus.OK:
        return response, status

    # Store files concurrently
    responses = await asyncio.gather(
        create_backup(Env.METADATA_FOLDER, original_metadata),
        save_metadata(token, response, overwrite=True)
    )

    for upload_response in responses:
        _, status = upload_response
        if status != HTTPStatus.OK:
            return upload_response

    return response, status

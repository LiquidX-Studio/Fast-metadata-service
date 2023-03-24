"""Metadata controller module contains logic related to metadata.
It will be the logic behind the metadata endpoint

"""

from http import HTTPStatus

from module.utils import get_metadata


async def get(token: int) -> tuple[dict, HTTPStatus]:
    """Get metadata for a given token.

    Args:
        token (int): Token to get metadata for.

    Returns:
        tuple[dict, HTTPStatus]: Response data and HTTP status code.

    """

    return await get_metadata(token)

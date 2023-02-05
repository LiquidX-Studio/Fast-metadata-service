"""This module contains HTTP response and message that should be used
for returning response to the client as a placeholder if something is
fail or some task is success but does not return any useful
information for client.

"""

from enum import Enum
from http import HTTPStatus


def _message(message: str, status_code: HTTPStatus) -> (dict, HTTPStatus):
    return {"detail": message}, status_code


class Response(tuple, Enum):
    """Customized HTTP response template that follows
    FastAPI response pattern

    """

    FILE_EXISTS = _message("file already exists", HTTPStatus.CONFLICT)
    INVALID_TOKEN = _message("invalid token", HTTPStatus.UNAUTHORIZED)
    NOT_FOUND = _message("not found", HTTPStatus.NOT_FOUND)
    OK = _message("success", HTTPStatus.OK)
    STORAGE_OPERATION_FAIL = _message("fail to run operation on storage", HTTPStatus.INTERNAL_SERVER_ERROR)
    VALUE_REQUIRED = _message("value required", HTTPStatus.BAD_REQUEST)

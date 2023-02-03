"""This module contains HTTP response and message that should be used
for returning response to the client as a placeholder if something is
fail or some task is success but does not return any useful
information for client.

"""

from enum import Enum
from http import HTTPStatus


def _error(message: str, status_code: HTTPStatus) -> (dict, HTTPStatus):
    return {"error": message}, status_code


def _status(message: str, status_code: HTTPStatus) -> (dict, HTTPStatus):
    return {"status": message}, status_code


class Response(tuple, Enum):
    FILE_EXISTS = _error("file already exists", HTTPStatus.CONFLICT)
    NOT_FOUND = _error("not found", HTTPStatus.NOT_FOUND)
    OK = _status("success", HTTPStatus.OK)
    STORAGE_OPERATION_FAIL = _error("fail to run operation on storage", HTTPStatus.INTERNAL_SERVER_ERROR)

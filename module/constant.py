"""Constant variables that will be used throughout the program"""

import uuid
from contextvars import ContextVar
from enum import Enum

from module.env import Env


class EndpointTag(str, Enum):
    PUBLIC_METADATA_API = "Public Metadata API"


CORRELATION_ID = ContextVar("correlation_id", default=uuid.UUID("00000000-0000-0000-0000-000000000000"))

try:
    MAX_TOKEN_ID = int(Env.MAX_TOKEN_ID)
except ValueError:  # pragma: no cover
    raise ValueError("MAX_TOKEN_ID environment variable is required and should be an integer")

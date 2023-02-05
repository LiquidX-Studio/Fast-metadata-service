"""Constant variables that will be used throughout the program"""

import uuid
from contextvars import ContextVar
from enum import Enum


class EndpointTag(str, Enum):
    PUBLIC_METADATA_API = "Public Metadata API"
    PRIVATE_METADATA_API = "Private Metadata API"


CORRELATION_ID = ContextVar("correlation_id", default=uuid.UUID("00000000-0000-0000-0000-000000000000"))

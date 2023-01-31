import os
from enum import Enum, auto
from typing import Any


class AutoSetEnv(str, Enum):
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return os.getenv(name, "")


class Env(AutoSetEnv):
    LOGGING_LEVEL = auto()
    MAX_TOKEN_ID = auto()
    METADATA_FOLDER = auto()
    PRODUCTION = auto()
    S3_BUCKET_NAME = auto()
    STORAGE_ACCESS_KEY = auto()
    STORAGE_SECRET_KEY = auto()
    STORAGE_TYPE = auto()

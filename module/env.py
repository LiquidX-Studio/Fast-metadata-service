"""A list of available environment variables that's used for configuration.
Any environment variable should be stored here, so it's easy to keep track of it."""

import os
from enum import Enum, auto
from typing import Any


class AutoSetEnv(str, Enum):
    """This class is used to automatically set the environment variables."""

    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return os.getenv(name, "")


class Env(AutoSetEnv):
    """This class contains a list of environment variable that's used for configuration.
    Add new property to this class and set the value to `auto()` to automatically set
    the environment variables. If the value is not set then it will be set to `""`
    (empty string).

    example:

    `LOGGING_LEVEL = auto()`

    is the same as

    `LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "")`

    """

    LOGGING_LEVEL = auto()
    MAX_TOKEN_ID = auto()
    METADATA_FOLDER = auto()
    PRODUCTION = auto()
    S3_BUCKET_NAME = auto()
    STORAGE_ACCESS_KEY = auto()
    STORAGE_SECRET_KEY = auto()
    STORAGE_TYPE = auto()

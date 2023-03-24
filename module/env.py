"""A list of available environment variables that's used for configuration.
Any environment variable should be stored here, so it's easy to keep track of it.

"""

from typing import Optional, Literal

from pydantic import BaseSettings, conint

from module.schema.storage import StorageType


class Settings(BaseSettings):
    """This class contains a list of environment variable that's used for configuration.
    Add new property to this class to automatically set the environment variables.

    """

    LOGGING_LEVEL: Optional[str]
    MAX_TOKEN_ID: conint(gt=0)
    METADATA_FOLDER: Optional[str]
    PINATA_GATEWAY: Optional[str]
    PRODUCTION: Optional[Literal["true"]]
    S3_BUCKET_NAME: Optional[str]
    SECRET_KEY: str
    STORAGE_ACCESS_KEY: Optional[str] = ""
    STORAGE_SECRET_KEY: Optional[str] = ""
    STORAGE_TYPE: StorageType


Env = Settings()  # Import this variable to get the environment variable value

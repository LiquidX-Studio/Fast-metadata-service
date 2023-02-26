"""Storage schema for Storage class"""

from enum import Enum

from pydantic import BaseModel


class StorageType(str, Enum):
    """This schema will validate the value of STORAGE_TYPE environment variable.
    All supported storage type is located in the `module.storage` module, excluding
    "interface" and "main" file. If the value of STORAGE_TYPE does not match any of
    the property then an exception will be raised. We can add new storage types by
    adding a new property under this class.
    For example,

    Pinata = "pinata"

    It will add support for Pinata storage. After that, we also need to write the code
    to integrate with Pinata storage and put it in the `module.storage` module.

    """

    S3 = "s3"
    Local = "local"
    Pinata = "pinata"


class Configuration(BaseModel):
    """This schema will validate configuration paramater in the Storage class"""

    access_key: str
    secret_key: str

    class Config:
        extra = "allow"

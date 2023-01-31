from enum import Enum

from pydantic import BaseModel


class StorageType(str, Enum):
    S3 = "s3"
    Local = "local"


class Configuration(BaseModel):
    access_key: str
    secret_key: str

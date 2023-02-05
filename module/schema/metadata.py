"""Metadata schema to enforce metadata structure with the help of
Pydantic module. The schema is following the metadata structure
that's supported in Opensea
https://docs.opensea.io/docs/metadata-standards#metadata-structure

"""

from typing import Optional, Union

from pydantic import BaseModel, AnyUrl, constr, StrictBool, StrictFloat, StrictInt


class Attribute(BaseModel):
    """Schema for metadata attribute"""

    trait_type: str
    value: Union[StrictBool, StrictInt, StrictFloat, str]
    display_type: Optional[str]


class Metadata(BaseModel):
    """Schema for Opensea metadata structure"""

    name: constr(min_length=1, strip_whitespace=True)
    description: Optional[str]
    image_url: AnyUrl
    animation_url: Optional[AnyUrl]
    external_url: Optional[AnyUrl]
    attributes: Optional[list[Attribute]]

    class Config:
        extra = "allow"

class MetadataRequestBody(Metadata):
    """Schema for metadata request body. It inherits
    from Metadata schema and makes all fields optional.

    """

    name: Optional[constr(min_length=1, strip_whitespace=True)]
    image_url: Optional[AnyUrl]

from typing import Optional, Union

from pydantic import BaseModel, AnyUrl, constr


class Attribute(BaseModel):
    trait_type: str
    value: Union[bool, str, int, float]
    display_type: Optional[str]


class Metadata(BaseModel):
    name: constr(min_length=1, strip_whitespace=True)
    description: Optional[str]
    image_url: AnyUrl
    animation_url: Optional[AnyUrl]
    external_url: Optional[AnyUrl]
    attributes: Optional[list[Attribute]]

    class Config:
        extra = "allow"

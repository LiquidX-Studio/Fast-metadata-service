"""Metadata router module contains endpoints related to metadata"""

from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

from controller import metadata
from module.constant import EndpointTag
from module.env import Env

router = APIRouter(tags=[EndpointTag.PUBLIC_METADATA_API])


@router.get("/metadata/{token}")
async def get_metadata(token: int = Path(gt=0, le=Env.MAX_TOKEN_ID)):
    content, status_code = await metadata.get(token)
    return JSONResponse(content=content, status_code=status_code)

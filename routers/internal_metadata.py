"""Metadata router module contains endpoints related
to internal operation for metadata. This endpoint is
used by the backend and requires token to access it.

"""

from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse

from controller import internal_metadata
from module.constant import EndpointTag
from module.env import Env
from module.auth import verify_token
from module.schema.metadata import MetadataRequestBody

router = APIRouter(tags=[EndpointTag.PRIVATE_METADATA_API],
                   dependencies=[Depends(verify_token)])

@router.put("/internal/update/metadata/{token}")
async def update_metadata_value(new_metadata: MetadataRequestBody,
                                token: int = Path(gt=0, le=Env.MAX_TOKEN_ID)):
    content, status_code = await internal_metadata.put(token, new_metadata)
    return JSONResponse(content=content, status_code=status_code)

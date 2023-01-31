from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

from controller import metadata
from module.constant import MAX_TOKEN_ID, EndpointTag
from module.logger import logger

router = APIRouter(tags=[EndpointTag.PUBLIC_METADATA_API])


@router.get("/metadata/{token}")
async def get_metadata(token: int = Path(gt=0, le=MAX_TOKEN_ID)):
    content, status_code = await metadata.get(token, logger)
    return JSONResponse(content=content, status_code=status_code)

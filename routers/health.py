"""Endpoint for service health check"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def healthcheck():
    return "Ok"

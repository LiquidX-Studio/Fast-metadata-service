"""Router module aggregates all existing endpoints"""

from fastapi import FastAPI

from routers import health, metadata, internal_metadata


def router(app: FastAPI):
    app.include_router(health.router)
    app.include_router(metadata.router)
    app.include_router(internal_metadata.router)

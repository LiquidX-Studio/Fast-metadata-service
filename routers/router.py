"""Router module aggregates all existing endpoints"""

from fastapi import FastAPI

from routers import metadata


def router(app: FastAPI):
    @app.get("/health")
    def healthcheck():
        return "Ok"

    app.include_router(metadata.router)

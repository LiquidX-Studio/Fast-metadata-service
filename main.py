import uuid

import uvicorn
from fastapi import FastAPI, Request

from module.constant import CORRELATION_ID
from routers.router import router

app = FastAPI()


@app.middleware("http")
async def set_correlation_id(request: Request, call_next):
    CORRELATION_ID.set(uuid.uuid4())
    return await call_next(request)


router(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

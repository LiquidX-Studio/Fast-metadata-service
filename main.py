import uuid

import uvicorn
from fastapi import FastAPI, Request, Response

from module.constant import CORRELATION_ID
from module.env import Env
from routers.router import router

app = FastAPI()


@app.middleware("http")
async def set_correlation_id(request: Request, call_next):
    CORRELATION_ID.set(uuid.uuid4())
    response = await call_next(request)
    content = b""
    async for chunk in response.body_iterator:
        content += chunk

    response.headers["correlation-id"] = f"{CORRELATION_ID.get()}"
    return Response(content=content,
                    headers=response.headers,
                    media_type=response.media_type,
                    status_code=response.status_code
                    )


router(app)

if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=Env.PORT)

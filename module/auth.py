"""Auth module contains function for authentication and
authorization purpose

"""

import jwt
from fastapi import HTTPException, Request
from fastapi.security import OAuth2

from module.env import Env


async def verify_token(request: Request) -> None:
    """Verify JWT token using secret key from environment
    variables

    Args:
        request (Request): HTTP request object

    Raises:
        HTTPException: If token is invalid

    """

    try:
        oauth = OAuth2()
        jwt_token = await oauth(request=request)
        jwt.decode(jwt_token, Env.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

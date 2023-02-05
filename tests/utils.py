import datetime

import jwt

from module.env import Env


def generate_token():
    expiry_time = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5)
    return jwt.encode(payload={"hello": "world", "exp": expiry_time},
                      key=Env.SECRET_KEY,
                      algorithm="HS256")

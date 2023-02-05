import asyncio
import datetime
import unittest
from unittest.mock import patch

import jwt
from fastapi.exceptions import HTTPException

from module.auth import verify_token
from module.env import Env
from tests.utils import generate_token


class TestVerifyToken(unittest.TestCase):
    token = generate_token()

    @patch("module.auth.Request")
    def test_valid_token(self, mock_request):
        mock_request.headers = {"Authorization": self.token}
        asyncio.run(verify_token(mock_request))

    @patch("module.auth.Request")
    def test_invalid_token(self, mock_request):
        mock_request.headers = {"Authorization": "halo"}
        with self.assertRaises(HTTPException):
            asyncio.run(verify_token(mock_request))

    @patch("module.auth.Request")
    def test_expired_token(self, mock_request):
        expiry_time = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=5)
        expired_token = jwt.encode(payload={"hello": "world", "exp": expiry_time},
                                   key=Env.SECRET_KEY,
                                   algorithm="HS256")

        mock_request.headers = {"Authorization": expired_token}
        with self.assertRaises(HTTPException):
            asyncio.run(verify_token(mock_request))

    @patch("module.auth.Request")
    def test_no_token_provided(self, mock_request):
        mock_request.headers = {}
        with self.assertRaises(HTTPException):
            asyncio.run(verify_token(mock_request))

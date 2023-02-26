from enum import Enum
from unittest.mock import AsyncMock


class S3Method(str, Enum):
    get_object = "get_object"
    head_object = "head_object"
    put_object = "put_object"


class MockAioboto3Session(AsyncMock):
    def __init__(self, method: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_return_value = kwargs.get("expected_return_value")
        self.expected_side_effect = kwargs.get("expected_side_effect")
        self.method = method

    def client(self, *args, **kwargs):
        return MockClient(method=self.method,
                          expected_side_effect=self.expected_side_effect,
                          expected_return_value=self.expected_return_value,
                          *args, **kwargs)


class MockClient(AsyncMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_return_value = kwargs.get("expected_return_value")
        self.expected_side_effect = kwargs.get("expected_side_effect")
        self.method = kwargs.get("method")

    async def __aenter__(self):
        s3 = AsyncMock()
        if self.method == S3Method.get_object:
            if self.expected_return_value is not None:
                s3.get_object.return_value = self.expected_return_value
            elif self.expected_side_effect is not None:
                s3.get_object.side_effect = self.expected_side_effect
        elif self.method == S3Method.head_object:
            if self.expected_return_value is not None:
                s3.head_object.return_value = self.expected_return_value
            elif self.expected_side_effect is not None:
                s3.head_object.side_effect = self.expected_side_effect
        elif self.method == S3Method.put_object:
            if self.expected_return_value is not None:
                s3.put_object.return_value = self.expected_return_value
            elif self.expected_side_effect is not None:
                s3.put_object.side_effect = self.expected_side_effect
        return s3

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockAioHTTP(AsyncMock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_return_value = kwargs.get("expected_return_value")

    @property
    def status(self):
        return self.expected_return_value.status

    async def read(self, *args, **kwargs):
        return self.expected_return_value.message

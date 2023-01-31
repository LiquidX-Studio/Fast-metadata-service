from unittest.mock import AsyncMock


class MockAioboto3Session(AsyncMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_return_value = kwargs.get("expected_return_value")
        self.expected_side_effect = kwargs.get("expected_side_effect")

    def client(self, *args, **kwargs):
        return MockClient(expected_side_effect=self.expected_side_effect,
                          expected_return_value=self.expected_return_value,
                          *args, **kwargs)


class MockClient(AsyncMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_return_value = kwargs.get("expected_return_value")
        self.expected_side_effect = kwargs.get("expected_side_effect")

    async def __aenter__(self):
        s3 = AsyncMock()
        if self.expected_return_value is not None:
            s3.get_object.return_value = self.expected_return_value
        elif self.expected_side_effect is not None:
            s3.get_object.side_effect = self.expected_side_effect
        return s3

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

import abc


class StorageInterface(metaclass=abc.ABCMeta):  # pragma: no cover
    @abc.abstractmethod
    async def get(self) -> bytes:
        raise NotImplementedError

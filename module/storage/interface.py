"""Storage interface define the abstract class for a storage.
All storage class should inherit from this class to create a
storage object, so that one storage type and the other has the
same public method. It could be helpful for doing migration
without a need to touch the codebase.

"""

import abc


class StorageInterface(metaclass=abc.ABCMeta):  # pragma: no cover
    """Storage interface define the abstract class for a storage.
    We can add more method if needed which then enforce us to update
    the child class also.

    """

    @abc.abstractmethod
    async def get(self) -> bytes:
        """Abstract method to get file from a storage"""
        raise NotImplementedError

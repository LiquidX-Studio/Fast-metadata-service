from module.env import Env
from module.logger import logger
from module.schema.storage import StorageType
from module.storage.local import LocalStorage
from module.storage.main import Storage
from module.storage.s3 import S3Storage
from module.storage.pinata import PinataStorage

Storage.register(StorageType.S3, S3Storage)
Storage.register(StorageType.Local, LocalStorage)
Storage.register(StorageType.Pinata, PinataStorage)
storage = Storage(logger=logger,
                  storage=Env.STORAGE_TYPE,
                  config={
                      "access_key": Env.STORAGE_ACCESS_KEY,
                      "secret_key": Env.STORAGE_SECRET_KEY
                  })

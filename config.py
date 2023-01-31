from module.env import Env
from module.logger import logger
from module.storage.main import Storage

storage = Storage(logger=logger,
                  storage=Env.STORAGE_TYPE,
                  config={
                      "access_key": Env.STORAGE_ACCESS_KEY,
                      "secret_key": Env.STORAGE_SECRET_KEY
                  })

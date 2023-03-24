"""Logger module is used for logging purpose. The code is taken from:
https://dddinpython.com/index.php/2021/09/02/request-logging-how-to/ as
an attempt to create a traceable log in Python using correlation ID.

"""

import logging

from module.constant import CORRELATION_ID


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = CORRELATION_ID.get()
        return True


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)-8s %(correlation_id)s [%(filename)s:%(lineno)d] %(message)s"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addFilter(ContextFilter())

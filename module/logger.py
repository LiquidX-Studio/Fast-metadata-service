import logging

from module.constant import CORRELATION_ID


# Taking example from https://dddinpython.com/index.php/2021/09/02/request-logging-how-to/
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

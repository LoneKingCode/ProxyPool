from functools import wraps
import traceback
from loguru import logger


def exception(func, msg='发生错误'):
    def except_execute(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} | {msg} | e:{e} traceback:{traceback.format_exc()}")
            return None

    return except_execute
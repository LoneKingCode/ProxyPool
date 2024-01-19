# coding:utf-8
import logging
import os
from logging import handlers
import colorlog


class LogUtil(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 项目路径
    rootPath = os.path.split(BASE_DIR)[0]
    path = os.path.join(rootPath, "log")
    level_relations = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    @staticmethod
    def debug(msg):
        LogUtil.log(msg, "debug")

    @staticmethod
    def info(msg):
        LogUtil.log(msg, "info")

    @staticmethod
    def warning(msg):
        LogUtil.log(msg, "warning")

    @staticmethod
    def error(msg):
        LogUtil.log(msg, "error")

    @staticmethod
    def critical(msg):
        LogUtil.log(msg, "critical")

    @staticmethod
    def log(msg, level="info"):
        os.makedirs(LogUtil.path, exist_ok=True)
        filepath = os.path.join(LogUtil.path, level + ".log")
        logger = logging.getLogger(filepath)
        logger.setLevel(logging.DEBUG)

        # Create a color formatter
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(blue)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )

        # File handler
        filehandler = handlers.TimedRotatingFileHandler(
            filename=filepath, when="D", backupCount=3, encoding="utf-8"
        )
        filehandler.setLevel(logging.WARNING)
        filehandler.setFormatter(formatter)

        # Stream handler
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(logging.DEBUG)
        streamhandler.setFormatter(formatter)

        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)
        logger.log(level=LogUtil.level_relations[level], msg=msg)

        #  添加下面一句，在记录日志之后移除句柄
        logger.removeHandler(filehandler)
        logger.removeHandler(streamhandler)


if __name__ == "__main__":
    LogUtil.info("info1")
    LogUtil.info("info2")
    LogUtil.info("info3")

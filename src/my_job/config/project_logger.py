import os
from logging import Logger

from prefect import logging


class ProjectLogger:
    @staticmethod
    def for_name(name: str) -> Logger:
        logger = logging.get_logger(name)
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        return logger

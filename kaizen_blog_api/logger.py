import logging
import sys
from logging import Formatter, Logger, StreamHandler
from typing import Union


def create_logger(logging_level: Union[int, str] = logging.INFO) -> Logger:
    handler = StreamHandler(sys.stdout)
    formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")

    logger = logging.getLogger(__name__)
    logger.propagate = False
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging_level)

    return logger

import logging
import sys
from typing import Any
from app.config.settings import settings

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO


def setup_logging() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_info(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    logger.info(message, extra=kwargs)


def log_error(logger: logging.Logger, message: str, exc_info: bool = False, **kwargs: Any) -> None:
    logger.error(message, exc_info=exc_info, extra=kwargs)


def log_warning(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    logger.warning(message, extra=kwargs)


def log_debug(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    logger.debug(message, extra=kwargs)

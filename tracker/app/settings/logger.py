"""Classes and functions to customize logs."""
import logging
import sys

from app.settings.config import AppSettings
from loguru import logger


class InterceptHandler(logging.Handler):
    """Logging handler interceptor from loguru documentaion.

    For more info see https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging  # noqa: E501
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Log the specified logging record by loguru logger."""
        try:
            # Get corresponding Loguru level if it exists
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and (frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logger(settings: AppSettings) -> None:
    """Add some loggers to loguru and config logging level."""
    logging.getLogger().handlers = [InterceptHandler()]
    logging.getLogger("aiokafka").setLevel(settings.AIOKAFKA_LOG_LEVEL.value)

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": settings.LOG_LEVEL.value,
            },
        ],
    )

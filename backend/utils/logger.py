"""
Logging configuration using Loguru.
"""

import sys
from loguru import logger
from backend.config.settings import settings


def setup_logging():
    """
    Configure standard logging format and handlers with contextual extra fields.
    """
    logger.remove()

    # Define a robust format that includes extra fields if present
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<magenta>{extra}</magenta> - <level>{message}</level>"
    )

    # Add stdout handler with colorization and formatting
    logger.add(
        sys.stdout,
        colorize=True,
        format=log_format,
        level="DEBUG" if settings.APP_ENV.value == "development" else "INFO",
        enqueue=True,  # Thread-safe asynchronous logging
        backtrace=True,
        diagnose=True if settings.APP_ENV.value == "development" else False,
    )


setup_logging()

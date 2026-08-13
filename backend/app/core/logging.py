"""
Logging configuration for Facial Recognition Attendance System.
Configures structured console logging with custom formatters.
"""

import sys
import logging

def setup_logging(debug: bool = True) -> None:
    """Configure root logger with console handler and custom format."""
    log_level = logging.DEBUG if debug else logging.INFO

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Quiet external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not debug else logging.INFO)

    logger = logging.getLogger("app")
    logger.info("Logging initialized (level=%s)", logging.getLevelName(log_level))

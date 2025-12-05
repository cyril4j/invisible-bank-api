"""
Logging configuration with structured JSON logging and daily rotation.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger
from app.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure application logging with JSON formatting and daily rotation.

    Returns:
        logging.Logger: Configured root logger
    """
    # Create log directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # JSON formatter for structured logging
    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d",
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp",
            "pathname": "file",
            "lineno": "line"
        },
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename=settings.log_file,
        when="midnight",  # Rotate at midnight
        interval=1,       # Every day
        backupCount=30,   # Keep 30 days of logs
        encoding="utf-8"
    )
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Log startup message
    logger.info(
        f"{settings.app_name} v{settings.app_version} logging initialized",
        extra={
            "environment": settings.environment,
            "log_level": settings.log_level,
            "log_file": settings.log_file
        }
    )

    return logger


# Initialize logging on module import
logger = setup_logging()

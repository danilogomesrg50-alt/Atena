"""
ATENA Framework - Logging Module
Centralized logging for all framework operations.
"""
import logging
from datetime import datetime
from pathlib import Path

from .config import LOG_FILE, LOG_FORMAT, LOG_LEVEL, LOGS_DIR


def setup_logger(name: str = "atena") -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)

    return logger


def log_operation(operation: str, status: str, details: str = "") -> None:
    """Log a framework operation with timestamp."""
    logger = setup_logger()
    message = f"[{operation}] Status: {status}"
    if details:
        message += f" | Details: {details}"
    logger.info(message)


def log_error(operation: str, error: Exception) -> None:
    """Log an error with full traceback."""
    logger = setup_logger()
    logger.error(f"[{operation}] Error: {str(error)}", exc_info=True)

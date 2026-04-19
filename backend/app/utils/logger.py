"""
Logging configuration using loguru.
Provides structured, colored logs with file rotation.
"""

import sys
from loguru import logger

# Remove default handler and add custom ones
logger.remove()

# Console handler — colored, human-readable
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# File handler — for debugging, rotated daily
logger.add(
    "logs/medscan_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
)


def get_logger(name: str):
    """Get a named logger instance."""
    return logger.bind(name=name)

import sys
from loguru import logger
from src.core.config import settings


def setup_logger():
    logger.remove()

    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | {extra}",
        level=settings.LOG_LEVEL,
        enqueue=True,
        colorize=True,
    )

    return logger

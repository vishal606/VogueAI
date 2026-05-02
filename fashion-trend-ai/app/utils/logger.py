import sys
from loguru import logger
from app.core.config import settings


def setup_logger():
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )

    # File — rotating, 30 day retention
    if settings.is_production:
        logger.add(
            "logs/fashion_trend_ai.log",
            format=log_format,
            level="INFO",
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=False,  # disable in production for security
        )
        logger.add(
            "logs/errors.log",
            format=log_format,
            level="ERROR",
            rotation="50 MB",
            retention="90 days",
            compression="gz",
        )

    return logger


logger = setup_logger()

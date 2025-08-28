"""
Logging configuration for the application
"""
import sys
from loguru import logger
from app.config import settings


def setup_logging():
    """Setup logging configuration"""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.debug else "INFO",
        colorize=True
    )
    
    # Add file logger for production
    if not settings.debug:
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO"
        )
    
    # Set loguru as the default logger for uvicorn
    logger.info("Logging setup completed")


def get_logger(name: str = __name__):
    """Get logger instance"""
    return logger.bind(name=name)

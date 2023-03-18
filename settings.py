from pydantic import BaseSettings
from loguru import logger
from sys import stderr
from typing import Optional


class Settings(BaseSettings):
    LOG_LEVEL: str = 'INFO'
    LOG_ROOT: Optional[str]

class YoungPlatformSettings(BaseSettings):
    host: str = 'https://api.youngplatform.com/api/v3'



settings = Settings()
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logger.remove()
logger.add(stderr, format=log_format, level=settings.LOG_LEVEL)

if settings.LOG_ROOT:
    logger.add(f'{settings.LOG_ROOT}/' + '{time}.log', format=log_format, level=settings.LOG_LEVEL, colorize=False, rotation='1 day', compression='zip', retention='1 month')
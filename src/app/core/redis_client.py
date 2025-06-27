import redis
from src.app.core.config import settings
from typing import Generator

import logging

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """
    Initialize and return Redis client
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        # check connection
        try:
            _redis_client.ping()
            logger.debug("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            logger.error("Could not connect to Redis.")
            raise ConnectionError(f"Could not connect to Redis: {e}. Check Redis server and REDIS_URL")
    return _redis_client


def get_redis_db() -> Generator[redis.Redis, None, None]:
    """
    FastAPI dependency to get Redis client
    provide close connection to Redis server
    """
    client = get_redis_client()
    try:
        yield client
    finally:
        pass


def close_redis_connection_pool():
    """
    close Redis connection
    """
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        logger.debug("Redis connection closed.")
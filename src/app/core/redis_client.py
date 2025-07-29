from datetime import timedelta

import redis
from src.app.core.config import settings
from typing import Generator, Optional

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


def save_refresh_token(
        redis_client: redis.Redis,
        user_id: int,
        refresh_token: str,
        expires_delta: timedelta
):
    """
    Save Redis refresh token
    key: f"refresh_token_{user_id}"
    value: refresh_token
    TTL: expires_delta (in seconds)
    """
    key = f"refresh_token_{user_id}"
    redis_client.setex(key, int(expires_delta.total_seconds()), refresh_token)
    logger.debug(f"Refresh token for user {user_id} saved in Redis.")


def get_refresh_token(
        redis_client: redis.Redis,
        user_id: int
) -> Optional[str]:
    """
    Get Redis refresh token
    """
    key = f"refresh_token_{user_id}"
    token_value = redis_client.get(key)
    return token_value


def delete_refresh_token(
        redis_client: redis.Redis,
        user_id: int
):
    """
    Delete Redis refresh token
    """
    key = f"refresh_token_{user_id}"
    redis_client.delete(key)
    logger.debug(f"Refresh token for user {user_id} deleted from Redis.")

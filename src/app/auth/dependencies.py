from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import redis
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.app.core import redis_client
from src.app.core.config import settings
from src.app.core.redis_client import get_redis_db
from src.app.database import get_db
from src.app.models.user import User

import logging

security = HTTPBearer()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
        redis_client: redis.Redis = Depends(get_redis_db)
) -> User:
    token = credentials.credentials
    logger.info("✅ get_current_user() called")
    logger.info(f"Decoding token...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token is missing 'sub' field.")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception

    is_blacklisted = redis_client.get(f"blacklist:{token}")
    if is_blacklisted:
        logger.warning(f"Token for user_id={user_id} is blacklisted.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        logger.warning(f"User not found for id: {user_id}")
        raise credentials_exception

    logger.info(f"Token valid. Authenticated user: {user.email} (id={user.id})")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC

from src.app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, expires_delta: timedelta | None = None):
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def create_password_reset_token(user_id: int) -> str:
    """
    Creates a JWT token for password reset.
    The token will contain user_id and have a short expiration time.
    """
    to_encode = {
        "sub": str(user_id)
    }
    expires_delta = timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_password_reset_token(token: str) -> dict | None:
    """
    Decodes the JWT password reset token and returns the payload.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return payload
    except JWTError:
        return None

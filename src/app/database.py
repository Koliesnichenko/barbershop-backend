from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine

# Base class for declarative SQLAlchemy model definitions.
Base = declarative_base()

_engine: Engine | None = None
_session_local: type[sessionmaker] | None = None


def get_engine() -> Engine:
    """
    Returns a SQLAlchemy engine. Initializes it if it hasn't been initialized yet.
    This function should be called when the engine is needed.
    """
    global _engine
    if _engine is None:
        from src.app.core.config import settings
        _engine = create_engine(
            settings.DATABASE_URL,
            echo=True,
            pool_pre_ping=True
        )
    return _engine


def get_session_local() -> type[sessionmaker]:
    """
    Returns a SQLAlchemy SessionLocal factory. Initializes it if it hasn't been initialized yet.
    """
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _session_local


def get_db():
    """
    FastAPI dependency to get a database session.
    Ensures the session is opened, committed/rolled back, and closed.
    """
    db = get_session_local()()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

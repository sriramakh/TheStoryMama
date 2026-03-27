"""SQLAlchemy engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import Config

engine = create_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from .models import Base

    Base.metadata.create_all(bind=engine)

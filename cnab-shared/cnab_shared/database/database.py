"""Database connection via SQLAlchemy with PostgreSQL and SQLite test support."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


class Base(DeclarativeBase):
    """Declarative base class for all CNAB SQLAlchemy models."""

    pass


def get_engine() -> Engine:
    """
    Returns the SQLAlchemy engine with lazy initialization.

    Uses SQLite in-memory when TESTING=true, otherwise reads DATABASE_URL
    for PostgreSQL.

    Returns:
        Configured SQLAlchemy engine.

    Raises:
        ValueError: If DATABASE_URL is not set outside of test mode.
    """
    global _engine

    if _engine is not None:
        return _engine

    is_testing = os.environ.get("TESTING", "false").lower() == "true"

    if is_testing:
        _engine = create_engine(
            "sqlite:///./test.db",
            connect_args={"check_same_thread": False},
        )
    else:
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            raise ValueError(
                "Environment variable DATABASE_URL is not configured. "
                "Set DATABASE_URL or define TESTING=true to use SQLite."
            )

        _engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_recycle=300,
            pool_pre_ping=True,
        )

    return _engine


def _get_session_local() -> sessionmaker:
    """Returns the session factory with lazy initialization."""
    global _SessionLocal

    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )

    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session per request."""
    SessionLocal = _get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

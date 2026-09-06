"""Shared PostgreSQL engine construction."""

from threading import Lock

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import sqlalchemy_database_url


class Base(DeclarativeBase):
    """Shared metadata for application-owned PostgreSQL tables."""


def create_database_engine(database_url: str) -> Engine:
    """Create a synchronous engine for FastAPI worker-thread endpoints."""
    return create_engine(sqlalchemy_database_url(database_url), pool_pre_ping=True)


_engines: dict[str, Engine] = {}
_engine_lock = Lock()


def get_database_engine(database_url: str) -> Engine:
    """Reuse one connection pool per configured URL in the API process."""
    with _engine_lock:
        if database_url not in _engines:
            _engines[database_url] = create_database_engine(database_url)
        return _engines[database_url]


def dispose_database_engines() -> None:
    """Release API connection pools after requests have stopped."""
    with _engine_lock:
        for engine in _engines.values():
            engine.dispose()
        _engines.clear()

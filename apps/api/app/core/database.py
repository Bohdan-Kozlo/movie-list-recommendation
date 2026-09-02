"""Shared PostgreSQL engine construction."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import sqlalchemy_database_url


class Base(DeclarativeBase):
    """Shared metadata for application-owned PostgreSQL tables."""


def create_database_engine(database_url: str) -> Engine:
    """Create a synchronous engine for FastAPI worker-thread endpoints."""
    return create_engine(sqlalchemy_database_url(database_url), pool_pre_ping=True)

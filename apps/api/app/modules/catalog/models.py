"""SQLAlchemy mappings for canonical catalogue records."""

from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

title_genres = Table(
    "catalogue_title_genres",
    Base.metadata,
    Column("title_id", ForeignKey("catalogue_titles.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("catalogue_genres.id", ondelete="CASCADE"), primary_key=True),
)


class CatalogueTitle(Base):
    """A canonical movie or TV-series record owned by this application."""

    __tablename__ = "catalogue_titles"
    __table_args__ = (
        CheckConstraint("title_type IN ('movie', 'tv')", name="ck_catalogue_title_type"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title_type: Mapped[str] = mapped_column(String(8), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    original_title: Mapped[str | None] = mapped_column(String(500))
    overview: Mapped[str | None] = mapped_column(String)
    original_language: Mapped[str] = mapped_column(String(8), nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date)
    release_year: Mapped[int | None] = mapped_column(Integer, index=True)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer)
    poster_path: Mapped[str | None] = mapped_column(String(500))
    backdrop_path: Mapped[str | None] = mapped_column(String(500))
    popularity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    vote_average: Mapped[float | None] = mapped_column(Float)
    tagline: Mapped[str | None] = mapped_column(String)
    cast: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    creators: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    genres: Mapped[list["Genre"]] = relationship(secondary=title_genres, lazy="selectin")
    external_ids: Mapped[list["ExternalIdentifier"]] = relationship(
        back_populates="title", cascade="all, delete-orphan", lazy="selectin"
    )


class Genre(Base):
    """A TMDB genre shared by canonical titles."""

    __tablename__ = "catalogue_genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class ExternalIdentifier(Base):
    """A normalized upstream identifier for a canonical title."""

    __tablename__ = "catalogue_external_ids"
    __table_args__ = (
        UniqueConstraint("provider", "value", name="uq_catalogue_external_identifier"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title_id: Mapped[UUID] = mapped_column(ForeignKey("catalogue_titles.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)

    title: Mapped[CatalogueTitle] = relationship(back_populates="external_ids")

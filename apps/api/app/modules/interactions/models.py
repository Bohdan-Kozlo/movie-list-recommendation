"""SQLAlchemy mappings for canonical user-library state."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRating(Base):
    """One immutable explicit rating for a user and canonical title."""

    __tablename__ = "user_ratings"
    __table_args__ = (
        CheckConstraint(
            "value >= 0.5 AND value <= 5.0 AND mod(value * 2, 1) = 0",
            name="ck_user_rating_half_point_range",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    title_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogue_titles.id", ondelete="CASCADE"), primary_key=True
    )
    value: Mapped[Decimal] = mapped_column(Numeric(2, 1), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class WatchlistEntry(Base):
    """A title the user intends to watch."""

    __tablename__ = "user_watchlist_entries"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    title_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogue_titles.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class WatchedTitle(Base):
    """A title the user has watched."""

    __tablename__ = "user_watched_titles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    title_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogue_titles.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class NotInterestedTitle(Base):
    """A title the user explicitly does not want recommended."""

    __tablename__ = "user_not_interested_titles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    title_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogue_titles.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

"""Create canonical user-library interaction tables.

Revision ID: 20260902_03
Revises: 20260902_02
Create Date: 2026-09-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260902_03"
down_revision: str | None = "20260902_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create ratings and independent title-state collections for each user."""
    op.create_table(
        "user_ratings",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title_id", sa.Uuid(), nullable=False),
        sa.Column("value", sa.Numeric(precision=2, scale=1), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "value >= 0.5 AND value <= 5.0 AND mod(value * 2, 1) = 0",
            name="ck_user_rating_half_point_range",
        ),
        sa.ForeignKeyConstraint(["title_id"], ["catalogue_titles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "title_id"),
    )
    for table_name in (
        "user_watchlist_entries",
        "user_watched_titles",
        "user_not_interested_titles",
    ):
        op.create_table(
            table_name,
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("title_id", sa.Uuid(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["title_id"], ["catalogue_titles.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("user_id", "title_id"),
        )


def downgrade() -> None:
    """Remove interaction state after all dependent tables are gone."""
    op.drop_table("user_not_interested_titles")
    op.drop_table("user_watched_titles")
    op.drop_table("user_watchlist_entries")
    op.drop_table("user_ratings")

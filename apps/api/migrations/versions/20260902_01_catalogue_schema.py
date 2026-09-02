"""Create canonical catalogue persistence tables.

Revision ID: 20260902_01
Revises:
Create Date: 2026-09-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260902_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create canonical title, genre, and normalized identifier tables."""
    op.create_table(
        "catalogue_titles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title_type", sa.String(length=8), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("original_title", sa.String(length=500), nullable=True),
        sa.Column("overview", sa.String(), nullable=True),
        sa.Column("original_language", sa.String(length=8), nullable=False),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("runtime_minutes", sa.Integer(), nullable=True),
        sa.Column("poster_path", sa.String(length=500), nullable=True),
        sa.Column("backdrop_path", sa.String(length=500), nullable=True),
        sa.Column("popularity", sa.Float(), nullable=False),
        sa.Column("vote_average", sa.Float(), nullable=True),
        sa.Column("tagline", sa.String(), nullable=True),
        sa.Column("cast", sa.JSON(), nullable=False),
        sa.Column("creators", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("title_type IN ('movie', 'tv')", name="ck_catalogue_title_type"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_catalogue_titles_release_year", "catalogue_titles", ["release_year"], unique=False
    )
    op.create_table(
        "catalogue_genres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "catalogue_external_ids",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("value", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(["title_id"], ["catalogue_titles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "value", name="uq_catalogue_external_identifier"),
    )
    op.create_table(
        "catalogue_title_genres",
        sa.Column("title_id", sa.Uuid(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["genre_id"], ["catalogue_genres.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["title_id"], ["catalogue_titles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("title_id", "genre_id"),
    )


def downgrade() -> None:
    """Remove catalogue tables in dependency order."""
    op.drop_table("catalogue_title_genres")
    op.drop_table("catalogue_external_ids")
    op.drop_table("catalogue_genres")
    op.drop_index("ix_catalogue_titles_release_year", table_name="catalogue_titles")
    op.drop_table("catalogue_titles")

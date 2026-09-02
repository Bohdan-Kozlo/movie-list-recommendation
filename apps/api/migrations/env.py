"""Alembic environment for the canonical catalogue schema."""

import sys
from logging.config import fileConfig
from os import getenv
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import sqlalchemy_database_url  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.modules.auth import models as auth_models  # noqa: F401, E402
from app.modules.catalog import models as catalogue_models  # noqa: F401, E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def database_url() -> str:
    """Read the same PostgreSQL connection URL used by the application."""
    configured_url = getenv("DATABASE_URL")
    if not configured_url:
        raise RuntimeError("DATABASE_URL must be configured before running migrations.")
    return sqlalchemy_database_url(configured_url)


def run_migrations_offline() -> None:
    """Generate SQL without opening a database connection."""
    context.configure(url=database_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply revisions in a transaction against PostgreSQL."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

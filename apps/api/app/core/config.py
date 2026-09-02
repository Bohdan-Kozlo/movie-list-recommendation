"""Runtime configuration read from the environment."""

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    """External services required by the catalogue module."""

    database_url: str
    tmdb_api_key: str | None
    tmdb_base_url: str = "https://api.themoviedb.org/3"

    @classmethod
    def from_environment(cls) -> "Settings":
        """Load the explicitly configured local or container environment."""
        database_url = getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL must be configured for catalogue access.")
        return cls(
            database_url=database_url,
            tmdb_api_key=getenv("TMDB_API_KEY"),
            tmdb_base_url=getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3"),
        )

    def require_tmdb_api_key(self) -> str:
        """Return configured TMDB credentials for an explicit sync command."""
        if not self.tmdb_api_key:
            raise RuntimeError("TMDB_API_KEY must be configured for catalogue synchronization.")
        return self.tmdb_api_key


def sqlalchemy_database_url(database_url: str) -> str:
    """Select psycopg 3 when a conventional PostgreSQL URL is supplied."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url

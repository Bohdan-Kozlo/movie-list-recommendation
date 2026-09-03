"""Runtime configuration read from the environment."""

from dataclasses import dataclass
from os import environ, getenv
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[4] / ".env"


def load_environment(path: Path | None = None) -> None:
    """Load local development settings without replacing process configuration."""
    environment_file = path or ENV_FILE
    if not environment_file.is_file():
        return
    for line in environment_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = stripped.partition("=")
        if not separator or not key:
            continue
        normalized_key = key.strip()
        if not environ.get(normalized_key):
            environ[normalized_key] = value.strip().strip("\"'")


load_environment()


@dataclass(frozen=True)
class Settings:
    """External services and security settings required by application modules."""

    database_url: str
    tmdb_api_key: str | None
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    auth_jwt_secret: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    web_app_url: str = "http://localhost:5173"
    auth_cookie_secure: bool = False

    @classmethod
    def from_environment(cls) -> "Settings":
        """Load the explicitly configured local or container environment."""
        load_environment()
        database_url = getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL must be configured for catalogue access.")
        return cls(
            database_url=database_url,
            tmdb_api_key=getenv("TMDB_API_KEY"),
            tmdb_base_url=getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3"),
            auth_jwt_secret=getenv("AUTH_JWT_SECRET"),
            google_client_id=getenv("GOOGLE_CLIENT_ID"),
            google_client_secret=getenv("GOOGLE_CLIENT_SECRET"),
            google_redirect_uri=getenv("GOOGLE_REDIRECT_URI"),
            web_app_url=getenv("WEB_APP_URL", "http://localhost:5173").rstrip("/"),
            auth_cookie_secure=getenv("AUTH_COOKIE_SECURE", "false").lower() == "true",
        )

    def require_tmdb_api_key(self) -> str:
        """Return configured TMDB credentials for an explicit sync command."""
        if not self.tmdb_api_key:
            raise RuntimeError("TMDB_API_KEY must be configured for catalogue synchronization.")
        return self.tmdb_api_key

    def require_auth_jwt_secret(self) -> str:
        """Return the configured key used to sign access and refresh JWTs."""
        if not self.auth_jwt_secret:
            raise RuntimeError("AUTH_JWT_SECRET must be configured for authentication.")
        return self.auth_jwt_secret

    def require_google_client_id(self) -> str:
        """Return the configured Google OpenID Connect client ID."""
        if not self.google_client_id:
            raise RuntimeError("GOOGLE_CLIENT_ID must be configured for Google sign-in.")
        return self.google_client_id

    def require_google_client_secret(self) -> str:
        """Return the configured Google OpenID Connect client secret."""
        if not self.google_client_secret:
            raise RuntimeError("GOOGLE_CLIENT_SECRET must be configured for Google sign-in.")
        return self.google_client_secret

    def require_google_redirect_uri(self) -> str:
        """Return the exact callback URL registered with Google."""
        if not self.google_redirect_uri:
            raise RuntimeError("GOOGLE_REDIRECT_URI must be configured for Google sign-in.")
        return self.google_redirect_uri


def sqlalchemy_database_url(database_url: str) -> str:
    """Select psycopg 3 when a conventional PostgreSQL URL is supplied."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url

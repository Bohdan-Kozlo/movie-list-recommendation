"""Auth module domain values and business errors."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class DuplicateEmailError(Exception):
    """Raised when registration would create a second account for an email."""


class InvalidCredentialsError(Exception):
    """Raised when a credential, token, or linked identity is invalid."""


class IdentityConflictError(Exception):
    """Raised when a second identity of the same provider targets one user."""


@dataclass(frozen=True)
class User:
    id: UUID
    email: str
    password_hash: str | None


@dataclass(frozen=True)
class GoogleProfile:
    subject: str
    email: str
    email_verified: bool


@dataclass(frozen=True)
class SessionRecord:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    expires_at: datetime
    revoked_at: datetime | None


@dataclass(frozen=True)
class SessionTokens:
    access_token: str
    refresh_token: str
    refresh_expires_at: datetime


def normalize_email(email: str) -> str:
    """Normalize the chosen case-insensitive account email policy."""
    return email.strip().lower()

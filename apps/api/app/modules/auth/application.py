"""Authentication use cases with persistence and credential seams."""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol
from uuid import UUID, uuid4


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


class AuthRepository(Protocol):
    def user_by_email(self, email: str) -> User | None: ...

    def user_by_id(self, user_id: UUID) -> User | None: ...

    def create_user(self, email: str, password_hash: str | None) -> User: ...

    def identity_user_id(self, provider: str, subject: str) -> UUID | None: ...

    def identity_exists_for_user(self, provider: str, user_id: UUID) -> bool: ...

    def link_identity(self, provider: str, subject: str, user_id: UUID) -> None: ...

    def create_session(self, session: SessionRecord) -> None: ...

    def active_session(self, session_id: UUID) -> SessionRecord | None: ...

    def replace_refresh_token(
        self,
        session_id: UUID,
        previous_token_hash: str,
        token_hash: str,
        expires_at: datetime,
    ) -> bool: ...

    def revoke_session(self, session_id: UUID) -> None: ...


class PasswordManager(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class TokenManager(Protocol):
    def issue(self, user_id: UUID, session_id: UUID) -> tuple[str, str, datetime]: ...

    def access_claims(self, token: str) -> tuple[UUID, UUID]: ...

    def refresh_claims(self, token: str) -> tuple[UUID, UUID]: ...

    def hash_refresh(self, token: str) -> str: ...


class AuthApplicationService:
    """Public account interface for password login, Google login, and sessions."""

    def __init__(
        self, repository: AuthRepository, passwords: PasswordManager, tokens: TokenManager
    ) -> None:
        self._repository = repository
        self._passwords = passwords
        self._tokens = tokens

    def register(self, email: str, password: str) -> tuple[User, SessionTokens]:
        normalized_email = normalize_email(email)
        if self._repository.user_by_email(normalized_email) is not None:
            raise DuplicateEmailError
        user = self._repository.create_user(normalized_email, self._passwords.hash(password))
        return user, self._new_session(user)

    def login(self, email: str, password: str) -> tuple[User, SessionTokens]:
        user = self._repository.user_by_email(normalize_email(email))
        if user is None or user.password_hash is None:
            raise InvalidCredentialsError
        if not self._passwords.verify(password, user.password_hash):
            raise InvalidCredentialsError
        return user, self._new_session(user)

    def sign_in_with_google(self, profile: GoogleProfile) -> tuple[User, SessionTokens]:
        if not profile.email_verified or not profile.subject or not profile.email:
            raise InvalidCredentialsError
        linked_user_id = self._repository.identity_user_id("google", profile.subject)
        if linked_user_id is not None:
            user = self._repository.user_by_id(linked_user_id)
            if user is None:
                raise InvalidCredentialsError
            return user, self._new_session(user)
        user = self._repository.user_by_email(normalize_email(profile.email))
        if user is None:
            user = self._repository.create_user(normalize_email(profile.email), None)
        elif self._repository.identity_exists_for_user("google", user.id):
            raise IdentityConflictError
        self._repository.link_identity("google", profile.subject, user.id)
        return user, self._new_session(user)

    def refresh(self, refresh_token: str) -> SessionTokens:
        user_id, session_id = self._token_claims(self._tokens.refresh_claims, refresh_token)
        session = self._repository.active_session(session_id)
        if session is None or session.user_id != user_id:
            raise InvalidCredentialsError
        previous_token_hash = self._tokens.hash_refresh(refresh_token)
        if session.refresh_token_hash != previous_token_hash:
            raise InvalidCredentialsError
        access_token, replacement, expires_at = self._tokens.issue(user_id, session_id)
        if not self._repository.replace_refresh_token(
            session_id,
            previous_token_hash,
            self._tokens.hash_refresh(replacement),
            expires_at,
        ):
            raise InvalidCredentialsError
        return SessionTokens(access_token, replacement, expires_at)

    def current_user(self, access_token: str) -> User:
        user_id, session_id = self._token_claims(self._tokens.access_claims, access_token)
        session = self._repository.active_session(session_id)
        if session is None or session.user_id != user_id:
            raise InvalidCredentialsError
        user = self._repository.user_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError
        return user

    def logout(self, access_token: str) -> None:
        _, session_id = self._token_claims(self._tokens.access_claims, access_token)
        self._repository.revoke_session(session_id)

    def logout_with_refresh(self, refresh_token: str) -> None:
        """Revoke a session when only its valid long-lived cookie remains."""
        user_id, session_id = self._token_claims(self._tokens.refresh_claims, refresh_token)
        session = self._repository.active_session(session_id)
        if session is None or session.user_id != user_id:
            raise InvalidCredentialsError
        if session.refresh_token_hash != self._tokens.hash_refresh(refresh_token):
            raise InvalidCredentialsError
        self._repository.revoke_session(session_id)

    def _new_session(self, user: User) -> SessionTokens:
        session_id = uuid4()
        access_token, refresh_token, expires_at = self._tokens.issue(user.id, session_id)
        self._repository.create_session(
            SessionRecord(
                id=session_id,
                user_id=user.id,
                refresh_token_hash=self._tokens.hash_refresh(refresh_token),
                expires_at=expires_at,
                revoked_at=None,
            )
        )
        return SessionTokens(access_token, refresh_token, expires_at)

    @staticmethod
    def _token_claims(parser: Callable[[str], tuple[UUID, UUID]], token: str) -> tuple[UUID, UUID]:
        try:
            return parser(token)
        except Exception as error:
            raise InvalidCredentialsError from error


def normalize_email(email: str) -> str:
    """Normalize the chosen case-insensitive account email policy."""
    return email.strip().lower()

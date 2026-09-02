"""Shared internal session creation used by successful sign-in use cases."""

from uuid import uuid4

from app.modules.auth.domain import SessionRecord, SessionTokens, User
from app.modules.auth.ports import AuthRepository, TokenManager


def issue_session(repository: AuthRepository, tokens: TokenManager, user: User) -> SessionTokens:
    """Create durable refresh state and return the matching browser tokens."""
    session_id = uuid4()
    access_token, refresh_token, expires_at = tokens.issue(user.id, session_id)
    repository.create_session(
        SessionRecord(
            id=session_id,
            user_id=user.id,
            refresh_token_hash=tokens.hash_refresh(refresh_token),
            expires_at=expires_at,
            revoked_at=None,
        )
    )
    return SessionTokens(access_token, refresh_token, expires_at)

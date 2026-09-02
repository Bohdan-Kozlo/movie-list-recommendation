"""Mappings for authentication persistence records."""

from app.modules.auth.domain import SessionRecord, User
from app.modules.auth.models import AuthSession, AuthUser


def to_session_record(session: AuthSession) -> SessionRecord:
    return SessionRecord(
        id=session.id,
        user_id=session.user_id,
        refresh_token_hash=session.refresh_token_hash,
        expires_at=session.expires_at,
        revoked_at=session.revoked_at,
    )


def to_user(user: AuthUser) -> User:
    return User(id=user.id, email=user.email, password_hash=user.password_hash)

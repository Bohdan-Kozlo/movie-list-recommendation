"""PostgreSQL adapter for canonical account state."""

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import Engine, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from app.adapters.postgres.mappers.auth import to_session_record, to_user
from app.modules.auth.domain import SessionRecord, User
from app.modules.auth.models import AuthIdentity, AuthSession, AuthUser


class SqlAlchemyAuthRepository:
    """Own users, external identities, and revocable browser sessions."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def user_by_email(self, email: str) -> User | None:
        with Session(self._engine) as session:
            user = session.scalar(select(AuthUser).where(AuthUser.email == email))
            return to_user(user) if user is not None else None

    def user_by_id(self, user_id: UUID) -> User | None:
        with Session(self._engine) as session:
            user = session.get(AuthUser, user_id)
            return to_user(user) if user is not None else None

    def create_user(self, email: str, password_hash: str | None) -> User:
        with Session(self._engine) as session, session.begin():
            user = AuthUser(email=email, password_hash=password_hash)
            session.add(user)
            session.flush()
            return to_user(user)

    def identity_user_id(self, provider: str, subject: str) -> UUID | None:
        with Session(self._engine) as session:
            return session.scalar(
                select(AuthIdentity.user_id).where(
                    AuthIdentity.provider == provider, AuthIdentity.subject == subject
                )
            )

    def identity_exists_for_user(self, provider: str, user_id: UUID) -> bool:
        with Session(self._engine) as session:
            return (
                session.scalar(
                    select(AuthIdentity.id).where(
                        AuthIdentity.provider == provider, AuthIdentity.user_id == user_id
                    )
                )
                is not None
            )

    def link_identity(self, provider: str, subject: str, user_id: UUID) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(AuthIdentity(provider=provider, subject=subject, user_id=user_id))

    def create_session(self, session_record: SessionRecord) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                AuthSession(
                    id=session_record.id,
                    user_id=session_record.user_id,
                    refresh_token_hash=session_record.refresh_token_hash,
                    expires_at=session_record.expires_at,
                )
            )

    def active_session(self, session_id: UUID) -> SessionRecord | None:
        with Session(self._engine) as session:
            record = session.scalar(
                select(AuthSession).where(
                    AuthSession.id == session_id,
                    AuthSession.revoked_at.is_(None),
                    AuthSession.expires_at > datetime.now(UTC),
                )
            )
            return to_session_record(record) if record is not None else None

    def replace_refresh_token(
        self,
        session_id: UUID,
        previous_token_hash: str,
        token_hash: str,
        expires_at: datetime,
    ) -> bool:
        with Session(self._engine) as session, session.begin():
            result = cast(
                CursorResult[Any],
                session.execute(
                    update(AuthSession)
                    .where(
                        AuthSession.id == session_id,
                        AuthSession.refresh_token_hash == previous_token_hash,
                        AuthSession.revoked_at.is_(None),
                        AuthSession.expires_at > datetime.now(UTC),
                    )
                    .values(refresh_token_hash=token_hash, expires_at=expires_at)
                ),
            )
            return result.rowcount == 1

    def revoke_session(self, session_id: UUID) -> None:
        with Session(self._engine) as session, session.begin():
            session.execute(
                update(AuthSession)
                .where(AuthSession.id == session_id, AuthSession.revoked_at.is_(None))
                .values(revoked_at=datetime.now(UTC))
            )

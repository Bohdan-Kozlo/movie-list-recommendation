from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.modules.auth.dependencies import AuthUseCases
from app.modules.auth.domain import (
    DuplicateEmailError,
    GoogleProfile,
    InvalidCredentialsError,
    SessionRecord,
    User,
)
from app.modules.auth.use_cases import (
    GetCurrentUser,
    LoginUser,
    LogoutSession,
    RefreshSession,
    RegisterUser,
    SignInWithGoogle,
)


class FakeRepository:
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}
        self.identities: dict[tuple[str, str], UUID] = {}
        self.sessions: dict[UUID, SessionRecord] = {}

    def user_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    def user_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    def create_user(self, email: str, password_hash: str | None) -> User:
        user = User(id=uuid4(), email=email, password_hash=password_hash)
        self.users[user.id] = user
        return user

    def identity_user_id(self, provider: str, subject: str) -> UUID | None:
        return self.identities.get((provider, subject))

    def identity_exists_for_user(self, provider: str, user_id: UUID) -> bool:
        return any(
            identity_provider == provider and identity_user_id == user_id
            for (identity_provider, _), identity_user_id in self.identities.items()
        )

    def link_identity(self, provider: str, subject: str, user_id: UUID) -> None:
        self.identities[(provider, subject)] = user_id

    def create_session(self, session: SessionRecord) -> None:
        self.sessions[session.id] = session

    def active_session(self, session_id: UUID) -> SessionRecord | None:
        session = self.sessions.get(session_id)
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at <= datetime.now(UTC)
        ):
            return None
        return session

    def replace_refresh_token(
        self,
        session_id: UUID,
        previous_token_hash: str,
        token_hash: str,
        expires_at: datetime,
    ) -> bool:
        session = self.sessions[session_id]
        if session.refresh_token_hash != previous_token_hash:
            return False
        self.sessions[session_id] = SessionRecord(
            id=session.id,
            user_id=session.user_id,
            refresh_token_hash=token_hash,
            expires_at=expires_at,
            revoked_at=None,
        )
        return True

    def revoke_session(self, session_id: UUID) -> None:
        session = self.sessions[session_id]
        self.sessions[session_id] = SessionRecord(
            id=session.id,
            user_id=session.user_id,
            refresh_token_hash=session.refresh_token_hash,
            expires_at=session.expires_at,
            revoked_at=datetime.now(UTC),
        )


class FakePasswords:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash(password)


class FakeTokens:
    def __init__(self) -> None:
        self.refresh_lifetime = timedelta(days=30)
        self.issued = 0

    def issue(self, user_id: UUID, session_id: UUID) -> tuple[str, str, datetime]:
        self.issued += 1
        return (
            f"access:{user_id}:{session_id}:{self.issued}",
            f"refresh:{user_id}:{session_id}:{self.issued}",
            datetime.now(UTC) + self.refresh_lifetime,
        )

    def access_claims(self, token: str) -> tuple[UUID, UUID]:
        _, user_id, session_id, _ = token.split(":")
        return UUID(user_id), UUID(session_id)

    def refresh_claims(self, token: str) -> tuple[UUID, UUID]:
        _, user_id, session_id, _ = token.split(":")
        return UUID(user_id), UUID(session_id)

    @staticmethod
    def hash_refresh(token: str) -> str:
        return f"hash:{token}"


@pytest.fixture
def use_cases() -> AuthUseCases:
    repository = FakeRepository()
    passwords = FakePasswords()
    tokens = FakeTokens()
    return AuthUseCases(
        register_user=RegisterUser(repository, passwords, tokens),
        login_user=LoginUser(repository, passwords, tokens),
        refresh_session=RefreshSession(repository, tokens),
        logout_session=LogoutSession(repository, tokens),
        get_current_user=GetCurrentUser(repository, tokens),
        sign_in_with_google=SignInWithGoogle(repository, tokens),
    )


def test_registers_and_authenticates_an_email_user(use_cases: AuthUseCases) -> None:
    user, tokens = use_cases.register_user.execute("Person@Example.com", "eightchars")

    assert user.email == "person@example.com"
    assert tokens.access_token.startswith("access:")
    assert use_cases.get_current_user.execute(tokens.access_token) == user


def test_rejects_duplicate_email_and_invalid_credentials(use_cases: AuthUseCases) -> None:
    use_cases.register_user.execute("person@example.com", "eightchars")

    with pytest.raises(DuplicateEmailError):
        use_cases.register_user.execute("PERSON@example.com", "anotherpw")
    with pytest.raises(InvalidCredentialsError):
        use_cases.login_user.execute("person@example.com", "incorrect")


def test_rotates_and_revokes_refresh_sessions(use_cases: AuthUseCases) -> None:
    _, original_tokens = use_cases.register_user.execute("person@example.com", "eightchars")

    replacement = use_cases.refresh_session.execute(original_tokens.refresh_token)
    use_cases.logout_session.execute(replacement.access_token, None)

    with pytest.raises(InvalidCredentialsError):
        use_cases.refresh_session.execute(original_tokens.refresh_token)
    with pytest.raises(InvalidCredentialsError):
        use_cases.get_current_user.execute(replacement.access_token)


def test_revokes_a_session_with_its_valid_refresh_token(use_cases: AuthUseCases) -> None:
    _, tokens = use_cases.register_user.execute("person@example.com", "eightchars")

    use_cases.logout_session.execute(None, tokens.refresh_token)

    with pytest.raises(InvalidCredentialsError):
        use_cases.refresh_session.execute(tokens.refresh_token)


def test_links_a_verified_google_identity_to_normalized_email(
    use_cases: AuthUseCases,
) -> None:
    email_user, _ = use_cases.register_user.execute("Person@Example.com", "eightchars")

    linked_user, _ = use_cases.sign_in_with_google.execute(
        GoogleProfile(subject="google-subject", email="PERSON@example.com", email_verified=True)
    )

    assert linked_user == email_user


def test_rejects_unverified_google_email_without_creating_a_user(
    use_cases: AuthUseCases,
) -> None:
    with pytest.raises(InvalidCredentialsError):
        use_cases.sign_in_with_google.execute(
            GoogleProfile(
                subject="google-subject", email="person@example.com", email_verified=False
            )
        )

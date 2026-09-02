from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from app.main import app
from app.modules.auth.api import get_google_provider
from app.modules.auth.dependencies import get_auth_use_cases
from app.modules.auth.domain import (
    DuplicateEmailError,
    GoogleProfile,
    InvalidCredentialsError,
    SessionTokens,
    User,
)
from fastapi import Request, Response
from fastapi.testclient import TestClient


class FakeAuthService:
    def __init__(self) -> None:
        self.user = User(id=uuid4(), email="person@example.com", password_hash="hashed")
        self.logged_out = False

    def register(self, email: str, password: str) -> tuple[User, SessionTokens]:
        if email == "taken@example.com":
            raise DuplicateEmailError
        self.user = User(id=uuid4(), email=email.lower(), password_hash="hashed")
        return self.user, self._tokens()

    def login(self, email: str, password: str) -> tuple[User, SessionTokens]:
        if password != "eightchars":
            raise InvalidCredentialsError
        return self.user, self._tokens()

    def refresh(self, refresh_token: str) -> SessionTokens:
        if refresh_token != "refresh":
            raise InvalidCredentialsError
        return self._tokens()

    def current_user(self, access_token: str) -> User:
        if access_token != "access" or self.logged_out:
            raise InvalidCredentialsError
        return self.user

    def logout(self, access_token: str | None, refresh_token: str | None) -> None:
        if access_token is not None:
            self._logout_with_access_token(access_token)
            return
        if refresh_token is not None:
            self._logout_with_refresh_token(refresh_token)

    def _logout_with_access_token(self, access_token: str) -> None:
        if access_token != "access":
            raise InvalidCredentialsError
        self.logged_out = True

    def _logout_with_refresh_token(self, refresh_token: str) -> None:
        if refresh_token != "refresh":
            raise InvalidCredentialsError
        self.logged_out = True

    def sign_in_with_google(self, profile: GoogleProfile) -> tuple[User, SessionTokens]:
        if not profile.email_verified:
            raise InvalidCredentialsError
        self.user = User(id=uuid4(), email=profile.email.lower(), password_hash=None)
        return self.user, self._tokens()

    @staticmethod
    def _tokens() -> SessionTokens:
        return SessionTokens("access", "refresh", datetime.now(UTC) + timedelta(days=30))


class FakeGoogleProvider:
    async def redirect(self, request: Request, redirect_uri: str) -> Response:
        return Response(status_code=204, headers={"X-Redirect-Uri": redirect_uri})

    async def profile(self, request: Request) -> GoogleProfile:
        return GoogleProfile(
            subject="google-subject", email="person@example.com", email_verified=True
        )


def configured_client(monkeypatch) -> tuple[TestClient, FakeAuthService]:
    monkeypatch.setenv("DATABASE_URL", "postgresql://unused")
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    monkeypatch.setenv("WEB_APP_URL", "http://localhost:5173")
    service = FakeAuthService()
    app.dependency_overrides[get_auth_use_cases] = lambda: SimpleNamespace(
        register_user=SimpleNamespace(execute=service.register),
        login_user=SimpleNamespace(execute=service.login),
        refresh_session=SimpleNamespace(execute=service.refresh),
        logout_session=SimpleNamespace(execute=service.logout),
        get_current_user=SimpleNamespace(execute=service.current_user),
        sign_in_with_google=SimpleNamespace(execute=service.sign_in_with_google),
    )
    app.dependency_overrides[get_google_provider] = FakeGoogleProvider
    return TestClient(app), service


def test_registration_sets_http_only_session_cookies(monkeypatch) -> None:
    client, _ = configured_client(monkeypatch)

    response = client.post(
        "/auth/register", json={"email": "Person@Example.com", "password": "eightchars"}
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["email"] == "person@example.com"
    assert "access_token=access" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=lax" in response.headers["set-cookie"]


def test_login_rejects_invalid_password_and_current_user_requires_a_session(monkeypatch) -> None:
    client, _ = configured_client(monkeypatch)

    invalid_login = client.post(
        "/auth/login", json={"email": "person@example.com", "password": "incorrect"}
    )
    unauthenticated = client.get("/auth/me")

    app.dependency_overrides.clear()
    assert invalid_login.status_code == 401
    assert unauthenticated.status_code == 401


def test_google_callback_sets_cookies_then_returns_to_the_spa(monkeypatch) -> None:
    client, _ = configured_client(monkeypatch)

    response = client.get("/auth/google/callback", follow_redirects=False)

    app.dependency_overrides.clear()
    assert response.status_code == 303
    assert response.headers["location"] == "http://localhost:5173/auth/callback?status=success"
    assert "refresh_token=refresh" in response.headers["set-cookie"]


def test_logout_clears_cookies_and_revokes_the_active_session(monkeypatch) -> None:
    client, service = configured_client(monkeypatch)
    client.cookies.set("access_token", "access")

    response = client.post("/auth/logout")

    app.dependency_overrides.clear()
    assert response.status_code == 204
    assert service.logged_out is True
    assert 'access_token=""' in response.headers["set-cookie"]


def test_logout_revokes_a_session_using_a_valid_refresh_cookie(monkeypatch) -> None:
    client, service = configured_client(monkeypatch)
    client.cookies.set("refresh_token", "refresh")

    response = client.post("/auth/logout")

    app.dependency_overrides.clear()
    assert response.status_code == 204
    assert service.logged_out is True

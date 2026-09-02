"""REST endpoints for account authentication and identity linking."""

from functools import lru_cache
from typing import Annotated, Protocol

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field

from app.adapters.auth_repository import SqlAlchemyAuthRepository
from app.adapters.google_oauth import GoogleOAuthClient
from app.core.config import Settings
from app.core.database import create_database_engine
from app.modules.auth.application import (
    AuthApplicationService,
    DuplicateEmailError,
    GoogleProfile,
    IdentityConflictError,
    InvalidCredentialsError,
    SessionTokens,
    User,
)
from app.modules.auth.security import Argon2PasswordManager, JwtTokenManager

router = APIRouter(prefix="/auth", tags=["auth"])


class CredentialsRequest(BaseModel):
    """Email-password credentials accepted for registration and login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class AuthenticatedUserResponse(BaseModel):
    """The safe account projection returned to the browser."""

    id: str
    email: str


class GoogleProvider(Protocol):
    async def redirect(self, request: Request, redirect_uri: str) -> Response: ...

    async def profile(self, request: Request) -> GoogleProfile: ...


def get_auth_service() -> AuthApplicationService:
    settings = Settings.from_environment()
    return configured_auth_service(settings.database_url, settings.require_auth_jwt_secret())


@lru_cache
def configured_auth_service(database_url: str, jwt_secret: str) -> AuthApplicationService:
    """Reuse configured account infrastructure for the running API process."""
    return AuthApplicationService(
        SqlAlchemyAuthRepository(create_database_engine(database_url)),
        Argon2PasswordManager(),
        JwtTokenManager(jwt_secret),
    )


def get_google_provider() -> GoogleOAuthClient:
    settings = Settings.from_environment()
    return GoogleOAuthClient(
        settings.require_google_client_id(), settings.require_google_client_secret()
    )


def get_current_user(
    service: Annotated[AuthApplicationService, Depends(get_auth_service)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    if access_token is None:
        raise authentication_required()
    try:
        return service.current_user(access_token)
    except InvalidCredentialsError as error:
        raise authentication_required() from error


@router.post(
    "/register", response_model=AuthenticatedUserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    credentials: CredentialsRequest,
    response: Response,
    service: Annotated[AuthApplicationService, Depends(get_auth_service)],
) -> AuthenticatedUserResponse:
    try:
        user, tokens = service.register(str(credentials.email), credentials.password)
    except DuplicateEmailError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already registered."
        ) from error
    set_session_cookies(response, tokens, Settings.from_environment())
    return user_response(user)


@router.post("/login", response_model=AuthenticatedUserResponse)
def login(
    credentials: CredentialsRequest,
    response: Response,
    service: Annotated[AuthApplicationService, Depends(get_auth_service)],
) -> AuthenticatedUserResponse:
    try:
        user, tokens = service.login(str(credentials.email), credentials.password)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password."
        ) from error
    set_session_cookies(response, tokens, Settings.from_environment())
    return user_response(user)


@router.post("/refresh", response_model=AuthenticatedUserResponse)
def refresh(
    response: Response,
    service: Annotated[AuthApplicationService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AuthenticatedUserResponse:
    if refresh_token is None:
        raise authentication_required()
    try:
        tokens = service.refresh(refresh_token)
        user = service.current_user(tokens.access_token)
    except InvalidCredentialsError as error:
        clear_session_cookies(response, Settings.from_environment())
        raise authentication_required() from error
    set_session_cookies(response, tokens, Settings.from_environment())
    return user_response(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    service: Annotated[AuthApplicationService, Depends(get_auth_service)],
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    session_revoked = False
    if access_token is not None:
        try:
            service.logout(access_token)
            session_revoked = True
        except InvalidCredentialsError:
            pass
    if not session_revoked and refresh_token is not None:
        try:
            service.logout_with_refresh(refresh_token)
        except InvalidCredentialsError:
            pass
    clear_session_cookies(response, Settings.from_environment())
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=AuthenticatedUserResponse)
def me(user: Annotated[User, Depends(get_current_user)]) -> AuthenticatedUserResponse:
    return user_response(user)


@router.get("/google/login")
async def google_login(
    request: Request,
    provider: Annotated[GoogleProvider, Depends(get_google_provider)],
) -> Response:
    settings = Settings.from_environment()
    return await provider.redirect(request, settings.require_google_redirect_uri())


@router.get("/google/callback")
async def google_callback(
    request: Request,
    provider: Annotated[GoogleProvider, Depends(get_google_provider)],
    service: Annotated[AuthApplicationService, Depends(get_auth_service)],
) -> RedirectResponse:
    settings = Settings.from_environment()
    try:
        user, tokens = service.sign_in_with_google(await provider.profile(request))
    except (InvalidCredentialsError, IdentityConflictError):
        return RedirectResponse(
            f"{settings.web_app_url}/auth/callback?status=error", status_code=303
        )
    response = RedirectResponse(
        f"{settings.web_app_url}/auth/callback?status=success", status_code=303
    )
    set_session_cookies(response, tokens, settings)
    return response


def user_response(user: User) -> AuthenticatedUserResponse:
    return AuthenticatedUserResponse(id=str(user.id), email=user.email)


def authentication_required() -> HTTPException:
    """Return the uniform response for missing, expired, and invalid sessions."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required."
    )


def set_session_cookies(response: Response, tokens: SessionTokens, settings: Settings) -> None:
    """Write browser-only session JWTs using the configured transport policy."""
    response.set_cookie(
        "access_token",
        tokens.access_token,
        max_age=15 * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookies(response: Response, settings: Settings) -> None:
    """Remove both session cookies with their original scope and security attributes."""
    for cookie_name in ("access_token", "refresh_token"):
        response.delete_cookie(
            cookie_name,
            httponly=True,
            secure=settings.auth_cookie_secure,
            samesite="lax",
            path="/",
        )

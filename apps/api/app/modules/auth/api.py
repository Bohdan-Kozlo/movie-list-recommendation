"""Thin REST transport for independent auth use cases."""

from typing import Annotated, Protocol

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.adapters.oauth.google import GoogleOAuthClient
from app.core.config import Settings
from app.modules.auth.dependencies import (
    AuthUseCases,
    authentication_required,
    get_auth_use_cases,
    get_current_user,
)
from app.modules.auth.domain import (
    DuplicateEmailError,
    GoogleProfile,
    IdentityConflictError,
    InvalidCredentialsError,
    SessionTokens,
    User,
)
from app.modules.auth.dto import (
    AuthenticatedUserResponse,
    CredentialsRequest,
    to_authenticated_user_response,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleProvider(Protocol):
    async def redirect(self, request: Request, redirect_uri: str) -> Response: ...

    async def profile(self, request: Request) -> GoogleProfile: ...


def get_google_provider() -> GoogleOAuthClient:
    settings = Settings.from_environment()
    return GoogleOAuthClient(
        settings.require_google_client_id(), settings.require_google_client_secret()
    )


@router.post(
    "/register", response_model=AuthenticatedUserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    credentials: CredentialsRequest,
    response: Response,
    use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)],
) -> AuthenticatedUserResponse:
    try:
        user, tokens = use_cases.register_user.execute(str(credentials.email), credentials.password)
    except DuplicateEmailError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already registered."
        ) from error
    set_session_cookies(response, tokens, Settings.from_environment())
    return to_authenticated_user_response(user)


@router.post("/login", response_model=AuthenticatedUserResponse)
def login(
    credentials: CredentialsRequest,
    response: Response,
    use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)],
) -> AuthenticatedUserResponse:
    try:
        user, tokens = use_cases.login_user.execute(str(credentials.email), credentials.password)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password."
        ) from error
    set_session_cookies(response, tokens, Settings.from_environment())
    return to_authenticated_user_response(user)


@router.post("/refresh", response_model=AuthenticatedUserResponse)
def refresh(
    response: Response,
    use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AuthenticatedUserResponse:
    if refresh_token is None:
        raise authentication_required()
    try:
        tokens = use_cases.refresh_session.execute(refresh_token)
        user = use_cases.get_current_user.execute(tokens.access_token)
    except InvalidCredentialsError as error:
        clear_session_cookies(response, Settings.from_environment())
        raise authentication_required() from error
    set_session_cookies(response, tokens, Settings.from_environment())
    return to_authenticated_user_response(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)],
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    use_cases.logout_session.execute(access_token, refresh_token)
    clear_session_cookies(response, Settings.from_environment())
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=AuthenticatedUserResponse)
def me(user: Annotated[User, Depends(get_current_user)]) -> AuthenticatedUserResponse:
    return to_authenticated_user_response(user)


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
    use_cases: Annotated[AuthUseCases, Depends(get_auth_use_cases)],
) -> RedirectResponse:
    settings = Settings.from_environment()
    try:
        user, tokens = use_cases.sign_in_with_google.execute(await provider.profile(request))
    except (InvalidCredentialsError, IdentityConflictError):
        return RedirectResponse(
            f"{settings.web_app_url}/auth/callback?status=error", status_code=303
        )
    response = RedirectResponse(
        f"{settings.web_app_url}/auth/callback?status=success", status_code=303
    )
    set_session_cookies(response, tokens, settings)
    return response


def set_session_cookies(response: Response, tokens: SessionTokens, settings: Settings) -> None:
    for name, value, max_age in (
        ("access_token", tokens.access_token, 15 * 60),
        ("refresh_token", tokens.refresh_token, 30 * 24 * 60 * 60),
    ):
        response.set_cookie(
            name,
            value,
            max_age=max_age,
            httponly=True,
            secure=settings.auth_cookie_secure,
            samesite="lax",
            path="/",
        )


def clear_session_cookies(response: Response, settings: Settings) -> None:
    for cookie_name in ("access_token", "refresh_token"):
        response.delete_cookie(
            cookie_name,
            httponly=True,
            secure=settings.auth_cookie_secure,
            samesite="lax",
            path="/",
        )

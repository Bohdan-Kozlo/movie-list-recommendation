"""Google OpenID Connect adapter built with Authlib."""

from secrets import token_urlsafe
from typing import Any

from authlib.integrations.base_client.errors import OAuthError  # type: ignore[import-untyped]
from authlib.integrations.starlette_client import OAuth  # type: ignore[import-untyped]
from fastapi import Request

from app.adapters.oauth.mappers import to_google_profile
from app.modules.auth.domain import GoogleProfile, InvalidCredentialsError


class GoogleOAuthClient:
    """Start and complete the Google OIDC authorization-code exchange."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._oauth = OAuth()
        self._oauth.register(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid profile email"},
        )

    async def redirect(self, request: Request, redirect_uri: str) -> Any:
        return await self._client.authorize_redirect(request, redirect_uri, nonce=token_urlsafe(32))

    async def profile(self, request: Request) -> GoogleProfile:
        try:
            token = await self._client.authorize_access_token(request)
            userinfo = token.get("userinfo")
        except OAuthError as error:
            raise InvalidCredentialsError from error
        if not isinstance(userinfo, dict):
            raise InvalidCredentialsError
        return to_google_profile(userinfo)

    @property
    def _client(self) -> Any:
        client = self._oauth.create_client("google")
        if client is None:
            raise RuntimeError("Google OAuth client is unavailable.")
        return client

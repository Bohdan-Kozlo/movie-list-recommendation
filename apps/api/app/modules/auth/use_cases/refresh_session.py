"""Refresh-token rotation use case."""

from app.modules.auth.domain import InvalidCredentialsError, SessionTokens
from app.modules.auth.ports import AuthRepository, TokenManager
from app.modules.auth.use_cases.get_current_user import GetCurrentUser


class RefreshSession:
    def __init__(self, repository: AuthRepository, tokens: TokenManager) -> None:
        self._repository = repository
        self._tokens = tokens

    def execute(self, refresh_token: str) -> SessionTokens:
        user_id, session_id = GetCurrentUser._claims(self._tokens.refresh_claims, refresh_token)
        session = self._repository.active_session(session_id)
        if session is None or session.user_id != user_id:
            raise InvalidCredentialsError
        previous_token_hash = self._tokens.hash_refresh(refresh_token)
        if session.refresh_token_hash != previous_token_hash:
            raise InvalidCredentialsError
        access_token, replacement, expires_at = self._tokens.issue(user_id, session_id)
        if not self._repository.replace_refresh_token(
            session_id, previous_token_hash, self._tokens.hash_refresh(replacement), expires_at
        ):
            raise InvalidCredentialsError
        return SessionTokens(access_token, replacement, expires_at)

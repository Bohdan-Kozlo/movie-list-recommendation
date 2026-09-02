"""Session revocation use case."""

from app.modules.auth.domain import InvalidCredentialsError
from app.modules.auth.ports import AuthRepository, TokenManager
from app.modules.auth.use_cases.get_current_user import GetCurrentUser


class LogoutSession:
    def __init__(self, repository: AuthRepository, tokens: TokenManager) -> None:
        self._repository = repository
        self._tokens = tokens

    def execute(self, access_token: str | None, refresh_token: str | None) -> None:
        if access_token is not None:
            try:
                self._revoke_with_access_token(access_token)
                return
            except InvalidCredentialsError:
                pass
        if refresh_token is not None:
            try:
                self._revoke_with_refresh_token(refresh_token)
            except InvalidCredentialsError:
                pass

    def _revoke_with_access_token(self, access_token: str) -> None:
        _, session_id = GetCurrentUser._claims(self._tokens.access_claims, access_token)
        self._repository.revoke_session(session_id)

    def _revoke_with_refresh_token(self, refresh_token: str) -> None:
        user_id, session_id = GetCurrentUser._claims(self._tokens.refresh_claims, refresh_token)
        session = self._repository.active_session(session_id)
        if session is None or session.user_id != user_id:
            raise InvalidCredentialsError
        if session.refresh_token_hash != self._tokens.hash_refresh(refresh_token):
            raise InvalidCredentialsError
        self._repository.revoke_session(session_id)

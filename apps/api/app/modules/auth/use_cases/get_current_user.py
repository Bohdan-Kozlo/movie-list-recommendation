"""Access-token authentication use case."""

from typing import Callable
from uuid import UUID

from app.modules.auth.domain import InvalidCredentialsError, User
from app.modules.auth.ports import AuthRepository, TokenManager


class GetCurrentUser:
    def __init__(self, repository: AuthRepository, tokens: TokenManager) -> None:
        self._repository = repository
        self._tokens = tokens

    def execute(self, access_token: str) -> User:
        user_id, session_id = self._claims(self._tokens.access_claims, access_token)
        session = self._repository.active_session(session_id)
        if session is None or session.user_id != user_id:
            raise InvalidCredentialsError
        user = self._repository.user_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError
        return user

    @staticmethod
    def _claims(parser: Callable[[str], tuple[UUID, UUID]], token: str) -> tuple[UUID, UUID]:
        try:
            return parser(token)
        except Exception as error:
            raise InvalidCredentialsError from error

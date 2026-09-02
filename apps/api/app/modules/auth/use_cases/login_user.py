"""Email-password sign-in use case."""

from app.modules.auth.domain import InvalidCredentialsError, SessionTokens, User, normalize_email
from app.modules.auth.ports import AuthRepository, PasswordManager, TokenManager
from app.modules.auth.use_cases._sessions import issue_session


class LoginUser:
    def __init__(
        self, repository: AuthRepository, passwords: PasswordManager, tokens: TokenManager
    ) -> None:
        self._repository = repository
        self._passwords = passwords
        self._tokens = tokens

    def execute(self, email: str, password: str) -> tuple[User, SessionTokens]:
        user = self._repository.user_by_email(normalize_email(email))
        if user is None or user.password_hash is None:
            raise InvalidCredentialsError
        if not self._passwords.verify(password, user.password_hash):
            raise InvalidCredentialsError
        return user, issue_session(self._repository, self._tokens, user)

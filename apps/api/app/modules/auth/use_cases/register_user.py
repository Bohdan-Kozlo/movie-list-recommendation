"""Email-password account registration use case."""

from app.modules.auth.domain import DuplicateEmailError, SessionTokens, User, normalize_email
from app.modules.auth.ports import AuthRepository, PasswordManager, TokenManager
from app.modules.auth.use_cases._sessions import issue_session


class RegisterUser:
    def __init__(
        self, repository: AuthRepository, passwords: PasswordManager, tokens: TokenManager
    ) -> None:
        self._repository = repository
        self._passwords = passwords
        self._tokens = tokens

    def execute(self, email: str, password: str) -> tuple[User, SessionTokens]:
        normalized_email = normalize_email(email)
        if self._repository.user_by_email(normalized_email) is not None:
            raise DuplicateEmailError
        user = self._repository.create_user(normalized_email, self._passwords.hash(password))
        return user, issue_session(self._repository, self._tokens, user)

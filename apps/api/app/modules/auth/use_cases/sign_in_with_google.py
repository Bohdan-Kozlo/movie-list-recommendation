"""Verified Google identity sign-in and linking use case."""

from app.modules.auth.domain import (
    GoogleProfile,
    IdentityConflictError,
    InvalidCredentialsError,
    SessionTokens,
    User,
    normalize_email,
)
from app.modules.auth.ports import AuthRepository, TokenManager
from app.modules.auth.use_cases._sessions import issue_session


class SignInWithGoogle:
    def __init__(self, repository: AuthRepository, tokens: TokenManager) -> None:
        self._repository = repository
        self._tokens = tokens

    def execute(self, profile: GoogleProfile) -> tuple[User, SessionTokens]:
        if not profile.email_verified or not profile.subject or not profile.email:
            raise InvalidCredentialsError
        linked_user_id = self._repository.identity_user_id("google", profile.subject)
        if linked_user_id is not None:
            user = self._repository.user_by_id(linked_user_id)
            if user is None:
                raise InvalidCredentialsError
            return user, issue_session(self._repository, self._tokens, user)
        user = self._repository.user_by_email(normalize_email(profile.email))
        if user is None:
            user = self._repository.create_user(normalize_email(profile.email), None)
        elif self._repository.identity_exists_for_user("google", user.id):
            raise IdentityConflictError
        self._repository.link_identity("google", profile.subject, user.id)
        return user, issue_session(self._repository, self._tokens, user)

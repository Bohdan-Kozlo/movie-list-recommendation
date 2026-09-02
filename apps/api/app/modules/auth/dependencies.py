"""Composition root for auth adapters and independent use cases."""

from dataclasses import dataclass
from functools import lru_cache

from app.adapters.postgres.auth_repository import SqlAlchemyAuthRepository
from app.core.config import Settings
from app.core.database import create_database_engine
from app.modules.auth.security import Argon2PasswordManager, JwtTokenManager
from app.modules.auth.use_cases import (
    GetCurrentUser,
    LoginUser,
    LogoutSession,
    RefreshSession,
    RegisterUser,
    SignInWithGoogle,
)


@dataclass(frozen=True)
class AuthUseCases:
    register_user: RegisterUser
    login_user: LoginUser
    refresh_session: RefreshSession
    logout_session: LogoutSession
    get_current_user: GetCurrentUser
    sign_in_with_google: SignInWithGoogle


def get_auth_use_cases() -> AuthUseCases:
    settings = Settings.from_environment()
    return configured_auth_use_cases(settings.database_url, settings.require_auth_jwt_secret())


@lru_cache
def configured_auth_use_cases(database_url: str, jwt_secret: str) -> AuthUseCases:
    repository = SqlAlchemyAuthRepository(create_database_engine(database_url))
    passwords = Argon2PasswordManager()
    tokens = JwtTokenManager(jwt_secret)
    return AuthUseCases(
        register_user=RegisterUser(repository, passwords, tokens),
        login_user=LoginUser(repository, passwords, tokens),
        refresh_session=RefreshSession(repository, tokens),
        logout_session=LogoutSession(repository, tokens),
        get_current_user=GetCurrentUser(repository, tokens),
        sign_in_with_google=SignInWithGoogle(repository, tokens),
    )

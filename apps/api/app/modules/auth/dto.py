"""HTTP DTOs and centralized mapping for the auth module."""

from pydantic import BaseModel, EmailStr, Field

from app.modules.auth.domain import User


class CredentialsRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class AuthenticatedUserResponse(BaseModel):
    id: str
    email: str


def to_authenticated_user_response(user: User) -> AuthenticatedUserResponse:
    return AuthenticatedUserResponse(id=str(user.id), email=user.email)

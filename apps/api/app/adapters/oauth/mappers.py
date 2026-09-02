"""Mappings from identity-provider payloads to application values."""

from typing import Any

from app.modules.auth.domain import GoogleProfile, InvalidCredentialsError


def to_google_profile(userinfo: dict[str, Any]) -> GoogleProfile:
    subject = userinfo.get("sub")
    email = userinfo.get("email")
    verified = userinfo.get("email_verified")
    if not isinstance(subject, str) or not isinstance(email, str) or not isinstance(verified, bool):
        raise InvalidCredentialsError
    return GoogleProfile(subject=subject, email=email, email_verified=verified)

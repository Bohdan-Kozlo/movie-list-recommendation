"""Password and JWT implementations behind the auth application seam."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash


class Argon2PasswordManager:
    """Hash passwords using pwdlib's recommended Argon2 configuration."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        return self._password_hash.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return self._password_hash.verify(password, password_hash)


class JwtTokenManager:
    """Issue and validate signed access and refresh JWTs for one session."""

    _issuer = "movie-list-recommendation"
    _audience = "movie-list-web"
    _algorithm = "HS256"

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def issue(self, user_id: UUID, session_id: UUID) -> tuple[str, str, datetime]:
        access_expiry = datetime.now(UTC) + timedelta(minutes=15)
        refresh_expiry = datetime.now(UTC) + timedelta(days=30)
        return (
            self._encode("access", user_id, session_id, access_expiry),
            self._encode("refresh", user_id, session_id, refresh_expiry),
            refresh_expiry,
        )

    def access_claims(self, token: str) -> tuple[UUID, UUID]:
        return self._claims(token, "access")

    def refresh_claims(self, token: str) -> tuple[UUID, UUID]:
        return self._claims(token, "refresh")

    @staticmethod
    def hash_refresh(token: str) -> str:
        return sha256(token.encode()).hexdigest()

    def _encode(
        self, token_type: str, user_id: UUID, session_id: UUID, expires_at: datetime
    ) -> str:
        now = datetime.now(UTC)
        return jwt.encode(
            {
                "sub": str(user_id),
                "sid": str(session_id),
                "jti": str(uuid4()),
                "typ": token_type,
                "iss": self._issuer,
                "aud": self._audience,
                "iat": now,
                "exp": expires_at,
            },
            self._secret,
            algorithm=self._algorithm,
        )

    def _claims(self, token: str, expected_type: str) -> tuple[UUID, UUID]:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["sub", "sid", "jti", "typ", "iat", "exp"]},
            )
            if claims["typ"] != expected_type:
                raise InvalidTokenError("Unexpected token type.")
            return UUID(claims["sub"]), UUID(claims["sid"])
        except (InvalidTokenError, KeyError, ValueError) as error:
            raise ValueError("Invalid session token.") from error

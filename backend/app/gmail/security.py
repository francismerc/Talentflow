import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken


class OAuthStateError(ValueError):
    """Raised when an OAuth state token is invalid or expired."""


class TokenEncryptionError(ValueError):
    """Raised when a stored integration token cannot be decrypted."""


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


@dataclass(frozen=True, slots=True)
class OAuthState:
    user_id: UUID
    expires_at: int


class OAuthStateSigner:
    def __init__(self, secret: str, *, ttl_seconds: int = 600) -> None:
        if len(secret) < 32:
            raise ValueError("OAuth state secret must contain at least 32 characters.")
        self._secret = secret.encode("utf-8")
        self._ttl_seconds = ttl_seconds

    def create(self, user_id: UUID, *, now: int | None = None) -> str:
        issued_at = int(time.time()) if now is None else now
        payload = {
            "exp": issued_at + self._ttl_seconds,
            "nonce": secrets.token_urlsafe(24),
            "sub": str(user_id),
        }
        encoded_payload = _base64url_encode(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        signature = hmac.new(
            self._secret,
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return f"{encoded_payload}.{_base64url_encode(signature)}"

    def verify(self, token: str, *, now: int | None = None) -> OAuthState:
        try:
            encoded_payload, encoded_signature = token.split(".", maxsplit=1)
            expected_signature = hmac.new(
                self._secret,
                encoded_payload.encode("ascii"),
                hashlib.sha256,
            ).digest()
            supplied_signature = _base64url_decode(encoded_signature)
            if not hmac.compare_digest(expected_signature, supplied_signature):
                raise OAuthStateError("OAuth state signature is invalid.")

            payload = json.loads(_base64url_decode(encoded_payload))
            expires_at = int(payload["exp"])
            user_id = UUID(payload["sub"])
        except OAuthStateError:
            raise
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exception:
            raise OAuthStateError("OAuth state is invalid.") from exception

        current_time = int(time.time()) if now is None else now
        if expires_at < current_time:
            raise OAuthStateError("OAuth state has expired.")
        return OAuthState(user_id=user_id, expires_at=expires_at)


class TokenCipher:
    def __init__(self, encryption_key: str) -> None:
        try:
            self._fernet = Fernet(encryption_key.encode("ascii"))
        except (ValueError, TypeError) as exception:
            raise ValueError("Google token encryption key is invalid.") from exception

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError) as exception:
            raise TokenEncryptionError(
                "Stored Google token could not be decrypted."
            ) from exception

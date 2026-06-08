from uuid import UUID

import pytest
from cryptography.fernet import Fernet

from app.gmail.security import OAuthStateError, OAuthStateSigner, TokenCipher

USER_ID = UUID("90000000-0000-4000-8000-000000000001")
STATE_SECRET = "state-secret-that-is-long-enough-for-hmac-signing"


def test_oauth_state_round_trip() -> None:
    signer = OAuthStateSigner(STATE_SECRET, ttl_seconds=600)

    state = signer.create(USER_ID, now=1_000)
    result = signer.verify(state, now=1_300)

    assert result.user_id == USER_ID
    assert result.expires_at == 1_600


def test_oauth_state_rejects_tampering() -> None:
    signer = OAuthStateSigner(STATE_SECRET)
    state = signer.create(USER_ID, now=1_000)
    payload, signature = state.split(".")
    tampered = f"{payload[:-1]}A.{signature}"

    with pytest.raises(OAuthStateError, match="signature"):
        signer.verify(tampered, now=1_001)


def test_oauth_state_rejects_expired_token() -> None:
    signer = OAuthStateSigner(STATE_SECRET, ttl_seconds=10)
    state = signer.create(USER_ID, now=1_000)

    with pytest.raises(OAuthStateError, match="expired"):
        signer.verify(state, now=1_011)


def test_token_cipher_round_trip() -> None:
    cipher = TokenCipher(Fernet.generate_key().decode("ascii"))

    encrypted = cipher.encrypt("google-refresh-token")

    assert encrypted != "google-refresh-token"
    assert cipher.decrypt(encrypted) == "google-refresh-token"

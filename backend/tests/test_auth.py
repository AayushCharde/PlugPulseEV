"""Tests for JWT verification (decode_token) using a locally-signed token.

No network / no live Authentik: we generate an RSA keypair, sign tokens, and
verify them against the matching (or a mismatched) public key.
"""

from __future__ import annotations

import time

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth import decode_token

_AUD = "plugpulse-client"
_ISS = "https://auth.example.com/application/o/plugpulse/"


def _keypair() -> tuple[bytes, bytes]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def _token(private_pem: bytes, *, exp_offset: int = 3600, aud: str = _AUD, iss: str = _ISS) -> str:
    now = int(time.time())
    payload = {
        "sub": "user-1",
        "preferred_username": "alice",
        "email": "alice@example.com",
        "aud": aud,
        "iss": iss,
        "iat": now,
        "exp": now + exp_offset,
    }
    return jwt.encode(payload, private_pem, algorithm="RS256")


def test_valid_token_decodes() -> None:
    private_pem, public_pem = _keypair()
    token = _token(private_pem)
    claims = decode_token(token, public_pem, audience=_AUD, issuer=_ISS)
    assert claims["sub"] == "user-1"
    assert claims["preferred_username"] == "alice"


def test_expired_token_rejected() -> None:
    private_pem, public_pem = _keypair()
    token = _token(private_pem, exp_offset=-10)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token, public_pem, audience=_AUD, issuer=_ISS)


def test_wrong_audience_rejected() -> None:
    private_pem, public_pem = _keypair()
    token = _token(private_pem, aud="someone-else")
    with pytest.raises(jwt.InvalidAudienceError):
        decode_token(token, public_pem, audience=_AUD, issuer=_ISS)


def test_bad_signature_rejected() -> None:
    private_pem, _ = _keypair()
    _, other_public_pem = _keypair()  # verify with a different key
    token = _token(private_pem)
    with pytest.raises(jwt.InvalidSignatureError):
        decode_token(token, other_public_pem, audience=_AUD, issuer=_ISS)

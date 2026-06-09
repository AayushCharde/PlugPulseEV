"""OIDC authentication: verify Authentik-issued JWTs and resolve the user.

The backend is a resource server — it does not issue tokens. It validates the
access token's signature against the provider's JWKS and the iss/aud/exp claims,
then upserts the user (keyed on the OIDC ``sub``). Auth is optional: when the
OIDC settings are unset, the protected routes return 503 and the public map is
unaffected.

``decode_token`` is pure (no network) and unit-tested with a locally-signed JWT.
"""

from __future__ import annotations

from typing import Any

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, status
from jwt import PyJWKClient
from pydantic import BaseModel

from app.config import settings
from app.db import db

router = APIRouter()

_ALGORITHMS = ["RS256"]
_jwks_client: PyJWKClient | None = None

_UPSERT_USER_SQL = """
INSERT INTO users (oidc_sub, handle, email)
VALUES ($1, $2, $3)
ON CONFLICT (oidc_sub) DO UPDATE SET handle = EXCLUDED.handle, email = EXCLUDED.email
RETURNING id, handle, email, trust_score
"""


class UserOut(BaseModel):
    id: int
    handle: str | None
    email: str | None
    trust_score: float


def decode_token(
    token: str,
    key: Any,
    *,
    audience: str | None,
    issuer: str | None,
) -> dict[str, Any]:
    """Verify a JWT's signature + standard claims against ``key``. Pure / no I/O.

    Raises a ``jwt.PyJWTError`` subclass on any validation failure.
    """
    claims: dict[str, Any] = jwt.decode(
        token,
        key,
        algorithms=_ALGORITHMS,
        audience=audience,
        issuer=issuer,
        options={"require": ["exp"]},
    )
    return claims


def _jwks() -> PyJWKClient:
    global _jwks_client
    if not settings.oidc_jwks_url:
        raise RuntimeError("OIDC_JWKS_URL is not configured")
    if _jwks_client is None:
        _jwks_client = PyJWKClient(settings.oidc_jwks_url)
    return _jwks_client


def verify_token(token: str) -> dict[str, Any]:
    """Resolve the signing key from the provider's JWKS, then verify the token."""
    signing_key = _jwks().get_signing_key_from_jwt(token)
    return decode_token(
        token,
        signing_key.key,
        audience=settings.oidc_audience,
        issuer=settings.oidc_issuer,
    )


async def get_current_user(authorization: str | None = Header(default=None)) -> UserOut:
    """FastAPI dependency: authenticate the bearer token and upsert the user."""
    if not settings.oidc_jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        )
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        claims = verify_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub")
    handle = claims.get("preferred_username") or claims.get("name")
    email = claims.get("email")

    rows = await db.fetch(_UPSERT_USER_SQL, sub, handle, email)
    row = rows[0]
    return UserOut(
        id=row["id"], handle=row["handle"], email=row["email"], trust_score=row["trust_score"]
    )


@router.get("/me", response_model=UserOut)
async def me(user: UserOut = Depends(get_current_user)) -> UserOut:
    return user

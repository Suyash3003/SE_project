from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_db
from app.models.auth import User


from app.config import JWT_SECRET, ENVIRONMENT

ROLES = {"admin", "dealer", "customer"}
TOKEN_TTL_SECONDS = 60 * 60 * 8
bearer_scheme = HTTPBearer(auto_error=False)


def _secret() -> bytes:
    secret = JWT_SECRET or os.getenv("JWT_SECRET", "")
    if len(secret) < 32:
        if ENVIRONMENT == "development":
            secret = "modern-colours-dev-secret-key-at-least-32-chars-long-2025-secure-demo"
        else:
            raise RuntimeError("JWT_SECRET must be configured with at least 32 characters in production")
    return secret.encode()



def normalize_identifier(value: str) -> str:
    return value.strip().lower()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=64
    )
    return f"scrypt${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(derived).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt_text, expected_text = encoded.split("$")
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(expected_text.encode())
        actual = hashlib.scrypt(
            password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=64
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _encode_part(value: dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")


def create_access_token(user: User) -> str:
    header = _encode_part({"alg": "HS256", "typ": "JWT"})
    payload = _encode_part({
        "sub": user.id,
        "role": user.role,
        "dealer_id": getattr(user, "dealer_id", None),
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    })
    unsigned = f"{header}.{payload}".encode()
    signature = base64.urlsafe_b64encode(hmac.new(_secret(), unsigned, hashlib.sha256).digest()).decode().rstrip("=")
    return f"{header}.{payload}.{signature}"


def _decode_token(token: str) -> dict[str, Any]:
    try:
        header, payload, signature = token.split(".")
        unsigned = f"{header}.{payload}".encode()
        expected = base64.urlsafe_b64encode(
            hmac.new(_secret(), unsigned, hashlib.sha256).digest()
        ).decode().rstrip("=")
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        decoded = json.loads(base64.urlsafe_b64decode(f"{payload}==".encode()))
        if decoded["exp"] <= time.time():
            raise ValueError("expired token")
        return decoded
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db=Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    claims = _decode_token(credentials.credentials)
    user = db.query(User).filter(User.id == claims["sub"]).first()
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="Account is not active")
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission to access this resource")
        return user

    return dependency


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

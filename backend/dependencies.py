# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/dependencies.py
"""FastAPI dependencies – authentication and JWT utilities.

The implementation follows the checklist:
- Uses ``python-jose`` for JWT handling (no hand‑rolled crypto).
- Verifies token signature, expiration (``exp`` claim) and ``sub`` presence.
- Returns a minimal user dict that downstream code can extend.
- All error paths provide explicit HTTP status codes and messages.
- Supports both ``Authorization: Bearer <token>`` header and ``token`` cookie
  (the cookie is set by ``POST /api/v1/auth/login`` for frontend convenience).
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from .config import settings

security = HTTPBearer(auto_error=False)  # auto_error=False lets us check cookies first


def _decode_token(token: str) -> Dict[str, str]:
    """Validate a JWT and return its payload dict.

    Raises ``HTTPException`` with 401 on any failure.
    """
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    user_id: str | None = payload.get("sub")
    exp: int | None = payload.get("exp")
    if user_id is None or exp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    return {"user_id": user_id}


def create_access_token(data: Dict[str, str], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: Payload data – must contain a ``sub`` key (user identifier).
        expires_delta: Optional custom TTL; defaults to ``settings.JWT_EXPIRE_MINUTES``.
    """
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, str]:
    """Validate the bearer token and return a ``user`` dict.

    The token can be supplied either as an ``Authorization: Bearer <token>`` header
    (for direct API clients) or as a ``token`` cookie (set by ``POST /api/v1/auth/login``
    for browser clients). Cookie takes precedence.
    """
    token: str | None = None

    # 1. Prefer cookie (set by the login endpoint for browser clients)
    token_cookie = request.cookies.get("token")
    if token_cookie:
        token = token_cookie
    # 2. Fall back to Authorization header
    elif credentials and credentials.credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        return _decode_token(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed"
        ) from exc

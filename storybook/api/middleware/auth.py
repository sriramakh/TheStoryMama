"""JWT authentication middleware for FastAPI."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import Config
from api.db.engine import get_db
from api.db.models import User

security = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    """Decode and verify a JWT token signed by NextAuth."""
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Require a valid JWT and return the authenticated User."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = _decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def optional_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User | None:
    """Optionally authenticate — returns None if no token provided."""
    if not credentials:
        return None

    try:
        payload = _decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == user_id).first()
    except HTTPException:
        pass

    return None

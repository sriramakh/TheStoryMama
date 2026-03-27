"""Authentication router — register, login, OAuth user upsert."""

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.db.engine import get_db
from api.db.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OAuthUserRequest(BaseModel):
    email: EmailStr
    name: str | None = None
    avatar_url: str | None = None
    provider: str = "google"
    provider_id: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None
    avatar_url: str | None
    provider: str


@router.post("/register", response_model=UserResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email/password."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    password_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()

    user = User(
        email=req.email,
        password_hash=password_hash,
        name=req.name,
        provider="credentials",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        provider=user.provider,
    )


@router.post("/login", response_model=UserResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email/password."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        provider=user.provider,
    )


@router.post("/oauth-user", response_model=UserResponse)
def upsert_oauth_user(req: OAuthUserRequest, db: Session = Depends(get_db)):
    """Create or update a user from OAuth provider (called by NextAuth)."""
    user = db.query(User).filter(User.email == req.email).first()

    if user:
        # Update provider info if needed
        if not user.provider_id:
            user.provider_id = req.provider_id
            user.provider = req.provider
        if req.name and not user.name:
            user.name = req.name
        if req.avatar_url:
            user.avatar_url = req.avatar_url
        db.commit()
        db.refresh(user)
    else:
        user = User(
            email=req.email,
            name=req.name,
            avatar_url=req.avatar_url,
            provider=req.provider,
            provider_id=req.provider_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        provider=user.provider,
    )

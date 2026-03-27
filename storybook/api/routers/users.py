"""User profile and credits router — requires authentication."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.db.engine import get_db
from api.db.models import User, Story, Credit
from api.middleware.auth import require_auth

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me")
def get_profile(user: User = Depends(require_auth)):
    """Get current user profile."""
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "provider": user.provider,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.get("/me/credits")
def get_credits(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Get user's credit balance."""
    now = datetime.now(timezone.utc)

    # Sum all active credits (not expired)
    credits = (
        db.query(Credit)
        .filter(
            Credit.user_id == user.id,
            (Credit.expires_at.is_(None) | (Credit.expires_at > now)),
        )
        .all()
    )

    total = sum(c.total for c in credits)
    used = sum(c.used for c in credits)

    # Find the soonest expiring credit for subscription info
    soonest_expiry = None
    plan_type = None
    for c in credits:
        if c.expires_at:
            if not soonest_expiry or c.expires_at < soonest_expiry:
                soonest_expiry = c.expires_at
        if c.order and c.order.plan_type:
            plan_type = c.order.plan_type

    return {
        "available": total - used,
        "total": total,
        "used": used,
        "plan_type": plan_type,
        "expires_at": soonest_expiry.isoformat() if soonest_expiry else None,
    }


@router.get("/me/stories")
def get_user_stories(
    page: int = 1,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Get stories created by the current user."""
    per_page = 20
    query = db.query(Story).filter(Story.owner_id == user.id)

    total = query.count()
    stories = (
        query.order_by(Story.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "stories": [
            {
                "id": s.folder_name,
                "title": s.title,
                "animation_style": s.animation_style,
                "scene_count": s.scene_count,
                "category": s.category,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "cover_image_url": s.cover_image_url,
            }
            for s in stories
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }

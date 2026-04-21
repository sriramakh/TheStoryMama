"""Avatar router — user-owned character portraits used as image generation references.

Pipeline: user uploads a photo → Grok renders an animation-style avatar →
GPT-4o-mini extracts a visual sheet → stored on disk + DB record.

When generating a story, the user picks 1-N avatars; their portraits are then
passed to Grok images.edit() as references for every scene — exactly the same
flow we use for the Caleb series.
"""

import base64
import io
import os
import uuid
import requests
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from PIL import Image
from openai import OpenAI

from config import Config
from api.db.engine import get_db
from api.db.models import Avatar, User
from api.middleware.auth import require_auth


router = APIRouter(prefix="/api/v1/avatars", tags=["avatars"])

AVATARS_DIR = os.getenv(
    "AVATARS_DIR",
    "/opt/thestorymama/storybook/avatars"
    if os.path.exists("/opt/thestorymama")
    else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "avatars"),
)
os.makedirs(AVATARS_DIR, exist_ok=True)

# Sub-bypass for development: allow free users to create up to 3 avatars
# (the paid quota lives in user.avatar_quota — once payments are wired up,
# free users will get 0 here and unlock via subscription).
DEV_FREE_AVATAR_LIMIT = 3

ANIMATION_STYLE_PROMPT = (
    "3D animated Pixar-style children's book character. "
    "Convert this photograph into a warm, vibrant 3D animated character. "
    "Soft rounded shapes, expressive big eyes, friendly smile, cinematic lighting. "
    "Keep the person's recognizable features (face shape, hair, skin tone) but render "
    "them as a stylized cartoon character. Plain soft cream background. "
    "Full body view if possible, friendly neutral pose."
)


class AvatarOut(BaseModel):
    id: str
    name: str
    type: str
    description: str | None = None
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class AvatarListResponse(BaseModel):
    avatars: list[AvatarOut]
    quota: int  # max avatars allowed
    used: int   # number of avatars currently owned
    can_create: bool


def _get_quota(user: User) -> int:
    """Return the user's avatar quota.
    For development before payments are wired up, every authenticated user
    gets DEV_FREE_AVATAR_LIMIT free avatars."""
    return max(user.avatar_quota or 0, DEV_FREE_AVATAR_LIMIT)


def _grok_render_avatar(source_path: str) -> bytes:
    """Call Grok images.edit() to render the photo as an animation-style avatar."""
    with open(source_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = "png" if source_path.lower().endswith(".png") else "jpeg"
    data_uri = f"data:image/{ext};base64,{b64}"

    body = {
        "model": "grok-imagine-image",
        "prompt": ANIMATION_STYLE_PROMPT,
        "n": 1,
        "response_format": "b64_json",
        "image": {"url": data_uri, "type": "image_url"},
    }
    resp = requests.post(
        "https://api.x.ai/v1/images/edits",
        headers={
            "Authorization": f"Bearer {Config.GROK_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=120,
    )
    resp.raise_for_status()
    return base64.b64decode(resp.json()["data"][0]["b64_json"])


def _extract_visual_sheet(image_bytes: bytes, name: str) -> str:
    """Extract a one-line character description for use in image prompts."""
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": (
                f"Describe this children's book character '{name}' in ONE dense line. "
                "Include: gender, approximate age, skin tone, hair color & style, eye color, "
                "clothing colors and patterns, accessories. Be obsessively precise about colors. "
                "This will be used as a reference to ensure visual consistency across illustrations."
            )},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "low"}},
        ]}],
        max_tokens=200,
    )
    return resp.choices[0].message.content.strip()


@router.get("", response_model=AvatarListResponse)
def list_avatars(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """List the authenticated user's avatars + quota info."""
    avatars = (
        db.query(Avatar)
        .filter(Avatar.user_id == user.id)
        .order_by(Avatar.created_at.desc())
        .all()
    )
    quota = _get_quota(user)
    return AvatarListResponse(
        avatars=[
            AvatarOut(
                id=str(a.id),
                name=a.name,
                type=a.type,
                description=a.description,
                image_url=f"/api/v1/avatars/{a.id}/image",
                created_at=a.created_at,
            )
            for a in avatars
        ],
        quota=quota,
        used=len(avatars),
        can_create=len(avatars) < quota,
    )


@router.post("/create", response_model=AvatarOut)
async def create_avatar(
    name: str = Form(...),
    type: str = Form(...),  # "boy", "girl", "father", "mother", "grandmother", "grandfather", etc.
    photo: UploadFile = File(...),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Create a new avatar from an uploaded photo.

    Steps:
      1. Save uploaded photo
      2. Grok renders it as an animation-style character
      3. GPT-4o-mini extracts visual description for prompt reuse
      4. Store Avatar DB record
    """
    # Quota check
    used = db.query(Avatar).filter(Avatar.user_id == user.id).count()
    quota = _get_quota(user)
    if used >= quota:
        raise HTTPException(
            status_code=402,
            detail=f"Avatar quota exhausted ({used}/{quota}). Purchase more to continue.",
        )

    # Validate inputs
    name = name.strip()
    if not name or len(name) > 100:
        raise HTTPException(400, "Name must be 1-100 characters")
    type = type.strip().lower()
    if not type:
        raise HTTPException(400, "Type is required (e.g. 'boy', 'girl', 'mother', 'grandfather')")

    # Validate file
    content = await photo.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "Photo must be under 10MB")
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
        # Resize to keep API payload reasonable
        if max(img.size) > 1024:
            img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=88)
        content = buf.getvalue()
    except Exception:
        raise HTTPException(400, "Invalid image file")

    avatar_id = uuid.uuid4()
    user_dir = os.path.join(AVATARS_DIR, str(user.id))
    os.makedirs(user_dir, exist_ok=True)

    # Save source photo
    source_path = os.path.join(user_dir, f"{avatar_id}_source.jpg")
    with open(source_path, "wb") as f:
        f.write(content)

    # Render avatar via Grok
    try:
        avatar_bytes = _grok_render_avatar(source_path)
    except Exception as e:
        # Clean up source if render fails
        try:
            os.remove(source_path)
        except OSError:
            pass
        raise HTTPException(502, f"Avatar render failed: {e}")

    # Save rendered avatar
    image_path = os.path.join(user_dir, f"{avatar_id}.png")
    with open(image_path, "wb") as f:
        f.write(avatar_bytes)

    # Extract visual sheet
    try:
        description = _extract_visual_sheet(avatar_bytes, name)
    except Exception:
        description = None

    avatar = Avatar(
        id=avatar_id,
        user_id=user.id,
        name=name,
        type=type,
        description=description,
        image_path=image_path,
        source_path=source_path,
    )
    db.add(avatar)
    db.commit()
    db.refresh(avatar)

    return AvatarOut(
        id=str(avatar.id),
        name=avatar.name,
        type=avatar.type,
        description=avatar.description,
        image_url=f"/api/v1/avatars/{avatar.id}/image",
        created_at=avatar.created_at,
    )


@router.get("/{avatar_id}/image")
def get_avatar_image(
    avatar_id: str,
    db: Session = Depends(get_db),
):
    """Serve the avatar PNG. Public — anyone with the link can view."""
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar or not os.path.exists(avatar.image_path):
        raise HTTPException(404, "Avatar not found")
    return FileResponse(avatar.image_path, media_type="image/png")


@router.delete("/{avatar_id}", status_code=204)
def delete_avatar(
    avatar_id: str,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Delete an avatar (owner only)."""
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(404, "Avatar not found")
    if avatar.user_id != user.id:
        raise HTTPException(403, "Not your avatar")

    # Remove files
    for p in [avatar.image_path, avatar.source_path]:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass

    db.delete(avatar)
    db.commit()
    return None

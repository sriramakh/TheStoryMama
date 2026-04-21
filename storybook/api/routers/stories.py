from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api.schemas.story import (
    StoryGenerateRequest,
    JobStatusResponse,
    JobStatus,
    StoryResponse,
    StoryListResponse,
    StyleResponse,
    StyleListResponse,
)
from api.services.story_service import story_service
from api.services.safety_filter import safety_filter
from api.middleware.auth import optional_auth, require_auth
from api.db.engine import get_db
from api.db.models import Avatar, User

import sys
import os

_STORYBOOK_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _STORYBOOK_ROOT not in sys.path:
    sys.path.insert(0, _STORYBOOK_ROOT)

from config import Config

router = APIRouter(prefix="/api/v1")


@router.post("/stories/generate", response_model=JobStatusResponse)
async def generate_story(
    request: StoryGenerateRequest,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    # Safety check
    if request.description:
        is_safe, reason = safety_filter.is_safe(request.description)
        if not is_safe:
            raise HTTPException(status_code=400, detail=reason)

    # Validate animation style
    if request.animation_style and request.animation_style not in Config.ANIMATION_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid animation style. Available: {list(Config.ANIMATION_STYLES.keys())}",
        )

    # Resolve avatar IDs to character data (name/type/description/portrait_path).
    # Each avatar becomes a story character; its portrait is passed to the image
    # generator as a Grok images.edit() reference (same flow as Caleb series).
    avatars_data = []
    if request.avatar_ids:
        avs = (
            db.query(Avatar)
            .filter(Avatar.id.in_(request.avatar_ids), Avatar.user_id == user.id)
            .all()
        )
        if len(avs) != len(request.avatar_ids):
            raise HTTPException(400, "One or more avatar_ids are invalid or not yours")
        for a in avs:
            avatars_data.append({
                "name": a.name,
                "type": a.type,
                "description": a.description or "",
                "portrait_path": a.image_path,
            })

    job_id = story_service.start_generation(
        description=request.description,
        num_scenes=request.num_scenes,
        animation_style=request.animation_style,
        age_group=request.age_group,
        avatars=avatars_data,
        user_id=str(user.id),
    )

    return JobStatusResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        progress=0.0,
        message="Generation started",
    )


@router.get("/stories/generate/{job_id}", response_model=JobStatusResponse)
async def get_generation_status(job_id: str):
    status = story_service.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=JobStatus(status["status"]),
        progress=status["progress"],
        message=status.get("message"),
        story_id=status.get("story_id"),
    )


@router.get("/stories", response_model=StoryListResponse)
async def list_stories(request: Request, page: int = 1, per_page: int = 20):
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    base_url = str(request.base_url).rstrip("/")
    stories_data, total = story_service.list_stories(page, per_page)

    stories = [
        StoryResponse(**story_service._story_to_response(s, base_url))
        for s in stories_data
    ]

    return StoryListResponse(stories=stories, total=total, page=page, per_page=per_page)


@router.get("/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str, request: Request):
    story = story_service.get_story(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    base_url = str(request.base_url).rstrip("/")
    return StoryResponse(**story_service._story_to_response(story, base_url))


@router.get("/stories/{story_id}/scenes/{scene_num}/image")
async def get_scene_image(story_id: str, scene_num: int):
    path = story_service.get_scene_image_path(story_id, scene_num)
    if path is None:
        raise HTTPException(status_code=404, detail="Scene image not found")
    # Cache images — use file modification time for cache busting
    import os
    mtime = int(os.path.getmtime(path))
    return FileResponse(
        path,
        headers={
            "Cache-Control": "public, max-age=86400",
            "ETag": f'"{mtime}"',
        },
    )


@router.get("/stories/{story_id}/pdf")
async def get_story_pdf(story_id: str):
    path = story_service.get_pdf_path(story_id)
    if path is None:
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=f"{story_id}.pdf")


@router.get("/stories/{story_id}/video")
async def get_story_video(story_id: str):
    """Serve the demo reel video for a story."""
    story_dir = os.path.join(Config.OUTPUT_DIR, story_id)
    # Look for demo_reel.mp4 or any .mp4
    for name in ["demo_reel.mp4", "story.mp4"]:
        path = os.path.join(story_dir, name)
        if os.path.exists(path):
            return FileResponse(path, media_type="video/mp4", filename=f"{story_id}.mp4")
    # Try any mp4
    for f in os.listdir(story_dir) if os.path.exists(story_dir) else []:
        if f.endswith(".mp4"):
            return FileResponse(os.path.join(story_dir, f), media_type="video/mp4")
    raise HTTPException(status_code=404, detail="Video not found")


@router.get("/styles", response_model=StyleListResponse)
async def list_styles():
    styles = [
        StyleResponse(id=key, name=val["name"], description=val["description"])
        for key, val in Config.ANIMATION_STYLES.items()
    ]
    return StyleListResponse(styles=styles)

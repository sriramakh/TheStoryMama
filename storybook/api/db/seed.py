"""Seed the database with existing stories from the filesystem."""

import json
import os
import sys
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.db.engine import SessionLocal, init_db
from api.db.models import Story
from config import Config

# Keywords for auto-categorization
CATEGORY_KEYWORDS = {
    "bedtime": ["sleep", "dream", "night", "moon", "star", "bed", "pillow", "lullaby", "yawn", "cozy"],
    "animals": ["animal", "bear", "rabbit", "fox", "owl", "penguin", "hedgehog", "squirrel", "deer", "mouse", "cat", "dog", "bird", "fish", "turtle", "frog", "butterfly", "bunny"],
    "adventure": ["adventure", "journey", "explore", "discover", "quest", "brave", "travel", "climb", "sail", "fly"],
    "friendship": ["friend", "together", "share", "help", "kind", "play", "team", "buddy"],
    "fantasy": ["magic", "enchant", "fairy", "wizard", "spell", "glow", "mystical", "dragon", "unicorn", "castle"],
    "nature": ["forest", "garden", "flower", "tree", "river", "mountain", "ocean", "rain", "sun", "meadow"],
    "family": ["mama", "papa", "mother", "father", "sister", "brother", "family", "home", "baby", "parent"],
    "seasons": ["spring", "summer", "autumn", "fall", "winter", "snow", "blossom", "harvest", "christmas", "holiday"],
    "funny": ["funny", "silly", "laugh", "giggle", "joke", "clumsy", "oops", "wacky", "goofy"],
    "learning": ["learn", "count", "color", "alphabet", "number", "shape", "word", "read", "school", "lesson"],
}


def categorize_story(story_data: dict) -> str:
    """Auto-categorize a story based on its content."""
    text = " ".join([
        story_data.get("title", ""),
        story_data.get("setting", ""),
        story_data.get("moral", ""),
        " ".join(c.get("type", "") for c in story_data.get("characters", [])),
        " ".join(s.get("text", "") for s in story_data.get("scenes", [])[:3]),
    ]).lower()

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)
    return "adventure"


def seed_stories():
    """Scan the stories directory and import all stories into the database."""
    init_db()
    db = SessionLocal()

    stories_dir = Config.OUTPUT_DIR
    if not os.path.exists(stories_dir):
        print(f"No stories directory found at {stories_dir}")
        return

    imported = 0
    skipped = 0

    for folder_name in sorted(os.listdir(stories_dir)):
        folder_path = os.path.join(stories_dir, folder_name)
        json_path = os.path.join(folder_path, "story_data.json")

        if not os.path.isdir(folder_path) or not os.path.exists(json_path):
            continue

        # Check if already imported
        existing = db.query(Story).filter(Story.folder_name == folder_name).first()
        if existing:
            skipped += 1
            continue

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                story_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  Skipping {folder_name}: {e}")
            continue

        # Auto-categorize
        category = categorize_story(story_data)

        # Build cover image URL
        cover_path = os.path.join(folder_path, "scene_01_raw.png")
        cover_url = f"/api/v1/stories/{folder_name}/scenes/1/image" if os.path.exists(cover_path) else None

        story = Story(
            folder_name=folder_name,
            title=story_data.get("title", "Untitled Story"),
            setting=story_data.get("setting"),
            art_style=story_data.get("art_style"),
            moral=story_data.get("moral"),
            instagram_caption=story_data.get("instagram_caption"),
            animation_style=story_data.get("animation_style"),
            story_data=story_data,
            is_public=True,
            category=category,
            tags=[c.get("type", "") for c in story_data.get("characters", []) if c.get("type")],
            cover_image_url=cover_url,
            scene_count=len(story_data.get("scenes", [])),
            owner_id=None,  # System-generated
        )

        db.add(story)
        imported += 1
        print(f"  Imported: {folder_name} [{category}]")

    db.commit()
    db.close()

    print(f"\nSeed complete: {imported} imported, {skipped} skipped (already exist)")


if __name__ == "__main__":
    seed_stories()

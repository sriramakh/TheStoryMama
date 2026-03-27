"""Public story library router — serves stories from the filesystem with multi-category tagging."""

import os
import json
import re
from collections import Counter

from fastapi import APIRouter, Query

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config import Config

router = APIRouter(prefix="/api/v1/library", tags=["library"])

# ── Category definitions with weighted keyword groups ─────────────────────────
# Each category has "strong" keywords (worth 3 points) and "weak" keywords (1 point).
# A story qualifies for a category if its score >= threshold.

CATEGORIES = {
    "animals": {
        "threshold": 6,
        "strong": [],
        "weak": [],
        # Special: determined by character types, not keywords
    },
    "adventure": {
        "threshold": 3,
        "strong": [
            "adventure", "quest", "treasure hunt", "expedition", "mission",
            "rescue mission",
        ],
        "weak": [
            "treasure", "hunt", "race", "chase", "explore", "journey",
            "rescue", "brave", "search", "mystery", "clue",
        ],
    },
    "friendship": {
        "threshold": 3,
        "strong": [
            "friendship", "best friend", "new friend", "friends",
        ],
        "weak": [
            "friend", "buddy", "together", "teamwork",
        ],
    },
    "fantasy": {
        "threshold": 3,
        "strong": [
            "magical", "enchanted", "wizard", "fairy", "dragon", "unicorn",
            "portal", "kingdom", "potion", "sorcerer", "spell",
        ],
        "weak": [
            "magic", "wish", "transform", "invisible", "shimmer",
            "sparkle", "glow", "mystical", "rainbow",
        ],
    },
    "nature": {
        "threshold": 6,
        "strong": [
            "forest", "garden", "jungle", "savanna", "woodland",
            "ocean", "coral reef",
        ],
        "weak": [
            "meadow", "pond", "river", "mountain", "nature",
        ],
    },
    "family": {
        "threshold": 3,
        "strong": [
            "mama", "papa", "mother", "father", "grandma", "grandpa",
            "grandmother", "grandfather", "family", "sibling", "sister",
            "brother", "parent",
        ],
        "weak": [
            "dad", "mom", "daughter", "son", "baby", "twin",
        ],
    },
    "funny": {
        "threshold": 3,
        "strong": [
            "funny", "hilarious", "mishap", "chaos", "mischief",
        ],
        "weak": [
            "silly", "laugh", "giggle", "oops", "messy",
            "splash", "tumble", "prank",
        ],
    },
    "learning": {
        "threshold": 3,
        "strong": [
            "learn", "lesson", "school", "teach", "curiosity",
        ],
        "weak": [
            "discover", "curious", "practice",
        ],
    },
    "seasons": {
        "threshold": 3,
        "strong": [
            "winter", "summer", "spring", "autumn", "christmas",
            "holiday", "snowflake", "first snow", "snowy",
        ],
        "weak": [
            "snow", "frost", "ice", "harvest",
        ],
    },
    "bedtime": {
        "threshold": 3,
        "strong": [
            "bedtime", "goodnight", "lullaby", "tuck in",
        ],
        "weak": [
            "sleep", "dream", "pillow",
        ],
    },
}


ANIMAL_TYPES = {
    "rabbit", "bear", "fox", "hedgehog", "squirrel", "owl", "penguin",
    "frog", "turtle", "duckling", "otter", "deer", "mouse", "kitten",
    "puppy", "lamb", "piglet", "dragon", "parrot", "monkey", "sloth",
    "chameleon", "toucan", "giraffe", "elephant", "lion", "meerkat",
    "seahorse", "octopus", "dolphin", "whale", "crab", "ladybug",
    "caterpillar", "butterfly", "dragonfly", "firefly", "snail",
    "worm", "cricket", "bumblebee", "gecko", "salamander", "beaver",
    "raccoon", "chipmunk", "porcupine", "badger", "flamingo", "robin",
    "swan", "heron", "puffin", "goat", "donkey", "alpaca", "pony",
    "chick", "bird", "fish", "cub", "pup", "kit", "foal", "calf",
}

HUMAN_TYPES = {
    "girl", "boy", "child", "grandmother", "grandfather", "grandma",
    "grandpa", "baker", "gardener", "little girl", "little boy",
    "human", "man", "woman",
}


def _categorize_story(story_data: dict) -> list[str]:
    """Assign multiple categories based on title, moral, setting, and character types."""
    # Use title + moral + setting + first 3 scenes for keyword matching
    title = story_data.get("title", "").lower()
    moral = (story_data.get("moral", "") or "").lower()
    setting = story_data.get("setting", "").lower()
    # Title and moral get triple weight by repeating
    text = f"{title} {title} {title} {moral} {moral} {moral} {setting}"

    scenes = story_data.get("scenes", [])
    for s in scenes[:3]:
        text += " " + s.get("text", "").lower()
    if len(scenes) > 3:
        text += " " + scenes[-1].get("text", "").lower()

    char_types = [c.get("type", "").lower().strip() for c in story_data.get("characters", [])]

    categories = []

    # 1. Animals: determined by character types
    has_animals = any(
        any(at in ct for at in ANIMAL_TYPES) for ct in char_types
    )
    if has_animals:
        categories.append("animals")

    # 2-10. Keyword-based categories
    for cat_id, cat_config in CATEGORIES.items():
        if cat_id == "animals":
            continue  # Already handled above
        score = 0
        for kw in cat_config["strong"]:
            if kw in text:
                score += 3
        for kw in cat_config["weak"]:
            if kw in text:
                score += 1
        if score >= cat_config["threshold"]:
            categories.append(cat_id)

    # Family: also check character types for family members
    has_family_chars = any(
        any(ft in ct for ft in {"grandmother", "grandfather", "grandma", "grandpa",
                                "mama", "papa", "mother", "father", "sister", "brother"})
        for ct in char_types
    )
    if has_family_chars and "family" not in categories:
        categories.append("family")

    # If no category matched, default to adventure
    if not categories:
        categories = ["adventure"]

    # Cap at 4 categories max per story
    return categories[:4]


def _story_to_dict(folder_name: str, story_data: dict) -> dict:
    """Convert a story JSON + folder name to API response dict."""
    categories = _categorize_story(story_data)

    return {
        "id": folder_name,
        "title": story_data.get("title", "Untitled"),
        "setting": story_data.get("setting"),
        "art_style": story_data.get("art_style"),
        "moral": story_data.get("moral"),
        "animation_style": story_data.get("animation_style"),
        "category": categories[0],  # Primary category (backwards compat)
        "categories": categories,   # All categories
        "tags": categories,         # Tags = categories for filtering
        "cover_image_url": f"/api/v1/stories/{folder_name}/scenes/1/image",
        "scene_count": len(story_data.get("scenes", [])),
        "created_at": None,
        "characters": story_data.get("characters", []),
        "scenes": [
            {
                "scene_number": s.get("scene_number"),
                "text": s.get("text"),
                "background": s.get("background"),
                "image_url": f"/api/v1/stories/{folder_name}/scenes/{s.get('scene_number')}/image",
            }
            for s in story_data.get("scenes", [])
        ],
    }


def _load_all_stories() -> list[dict]:
    """Scan the stories directory and load all story_data.json files."""
    stories_dir = Config.OUTPUT_DIR
    if not os.path.exists(stories_dir):
        return []

    results = []
    for folder_name in sorted(os.listdir(stories_dir), reverse=True):
        folder_path = os.path.join(stories_dir, folder_name)
        json_path = os.path.join(folder_path, "story_data.json")

        if not os.path.isdir(folder_path) or not os.path.exists(json_path):
            continue

        # Only include stories that have at least 1 image generated
        has_images = any(
            f.startswith("scene_") and (f.endswith(".jpg") or f.endswith("_raw.png"))
            for f in os.listdir(folder_path)
        )
        if not has_images:
            continue

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                story_data = json.load(f)
            results.append(_story_to_dict(folder_name, story_data))
        except (json.JSONDecodeError, IOError):
            continue

    return results


@router.get("")
def list_library_stories(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str | None = None,
    style: str | None = None,
    search: str | None = None,
):
    """Browse the public story library with filters."""
    all_stories = _load_all_stories()

    # Apply filters
    filtered = all_stories
    if category:
        # Match stories that have this category in their categories list
        filtered = [s for s in filtered if category in s.get("categories", [])]
    if style:
        filtered = [s for s in filtered if s["animation_style"] == style]
    if search:
        search_lower = search.lower()
        filtered = [s for s in filtered if search_lower in s["title"].lower()
                    or search_lower in (s.get("moral") or "").lower()
                    or search_lower in (s.get("setting") or "").lower()]

    total = len(filtered)

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    page_stories = filtered[start:end]

    return {
        "stories": page_stories,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/categories")
def list_categories():
    """List categories with story counts (a story can appear in multiple categories)."""
    all_stories = _load_all_stories()
    counts = Counter()
    for s in all_stories:
        for cat in s.get("categories", []):
            counts[cat] += 1
    return {
        "categories": [
            {"id": cat, "count": count}
            for cat, count in counts.most_common()
        ]
    }


@router.get("/featured")
def featured_stories():
    """Return featured stories for the homepage — diverse categories and styles."""
    all_stories = _load_all_stories()
    seen_cats = set()
    seen_styles = set()
    featured = []

    # First pass: one per category, different styles
    for s in all_stories:
        primary_cat = s.get("category", "")
        style = s.get("animation_style", "")
        if primary_cat not in seen_cats and style not in seen_styles and len(featured) < 6:
            featured.append(s)
            seen_cats.add(primary_cat)
            seen_styles.add(style)

    # Fill remaining
    for s in all_stories:
        if s not in featured and len(featured) < 6:
            featured.append(s)

    return {"stories": featured}

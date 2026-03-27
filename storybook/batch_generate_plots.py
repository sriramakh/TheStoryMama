#!/usr/bin/env python3
"""
Batch-generate 100 story plots (text only, no images).
Saves each story as a JSON file in stories_plots/ directory.
Cycles through animation styles and scene counts for variety.
"""

import os
import sys
import json
import time
import random
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from story_generator import StoryGenerator

# Output directory for plots only
PLOTS_DIR = "stories_plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

# Animation styles to cycle through
STYLES = list(Config.ANIMATION_STYLES.keys())

# Scene counts to vary
SCENE_COUNTS = [12, 12, 13, 13, 14, 14, 15, 12, 13, 15]

TOTAL_STORIES = 100

generator = StoryGenerator()

def generate_plot(index: int) -> dict | None:
    """Generate a single story plot."""
    style_key = STYLES[index % len(STYLES)]
    style = Config.ANIMATION_STYLES[style_key]
    num_scenes = SCENE_COUNTS[index % len(SCENE_COUNTS)]

    try:
        story = generator.generate_story(
            num_scenes=num_scenes,
            description=None,  # Auto-generate for variety
            art_style_hint=style["story_art_style"],
        )
        story["animation_style"] = style_key
        return story
    except Exception as e:
        print(f"  ERROR: {e}")
        traceback.print_exc()
        return None


def main():
    # Check how many already exist
    existing = set()
    for f in os.listdir(PLOTS_DIR):
        if f.endswith(".json"):
            existing.add(f)

    start_index = len(existing)
    print(f"=" * 60)
    print(f"Batch Story Plot Generator")
    print(f"=" * 60)
    print(f"Target: {TOTAL_STORIES} stories")
    print(f"Already generated: {start_index}")
    print(f"Remaining: {TOTAL_STORIES - start_index}")
    print(f"=" * 60)

    for i in range(start_index, TOTAL_STORIES):
        filename = f"story_{i+1:03d}.json"
        filepath = os.path.join(PLOTS_DIR, filename)

        if os.path.exists(filepath):
            print(f"[{i+1:3d}/{TOTAL_STORIES}] Skipping (already exists)")
            continue

        style_key = STYLES[i % len(STYLES)]
        num_scenes = SCENE_COUNTS[i % len(SCENE_COUNTS)]
        print(f"[{i+1:3d}/{TOTAL_STORIES}] Generating... (style: {style_key}, scenes: {num_scenes})")

        story = generate_plot(i)

        if story:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(story, f, indent=2, ensure_ascii=False)

            chars = ", ".join(f"{c['name']} ({c['type']})" for c in story["characters"])
            print(f"           Title: {story['title']}")
            print(f"           Characters: {chars}")
            print(f"           Scenes: {len(story['scenes'])}")
            if story.get("moral"):
                print(f"           Moral: {story['moral'][:80]}")
        else:
            print(f"           FAILED — will retry on next run")

        # Small delay to avoid rate limits
        time.sleep(1)

    print(f"\n{'=' * 60}")
    print(f"Generation complete! {TOTAL_STORIES} plots saved to {PLOTS_DIR}/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

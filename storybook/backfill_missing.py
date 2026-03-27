#!/usr/bin/env python3
"""Backfill missing story plots."""
import os, json, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from config import Config
from story_generator import StoryGenerator

PLOTS_DIR = "stories_plots"
STYLES = list(Config.ANIMATION_STYLES.keys())
SCENE_COUNTS = [12, 12, 13, 13, 14, 14, 15, 12, 13, 15]
generator = StoryGenerator()

for i in [37, 43, 77]:
    filename = f"story_{i:03d}.json"
    filepath = os.path.join(PLOTS_DIR, filename)
    if os.path.exists(filepath):
        print(f"Already exists: {filename}")
        continue

    style_key = STYLES[(i-1) % len(STYLES)]
    num_scenes = SCENE_COUNTS[(i-1) % len(SCENE_COUNTS)]
    print(f"Generating {filename} (style: {style_key}, scenes: {num_scenes})...")

    for attempt in range(3):
        try:
            story = generator.generate_story(
                num_scenes=num_scenes,
                art_style_hint=Config.ANIMATION_STYLES[style_key]["story_art_style"],
            )
            story["animation_style"] = style_key
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(story, f, indent=2, ensure_ascii=False)
            print(f"  OK: {story['title']}")
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")

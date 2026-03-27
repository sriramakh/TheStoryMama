#!/usr/bin/env python3
"""
Generate 1 sample image per animation style (10 total) using scene 1
from a different story for each style. Saves to style_samples/ directory.
"""

import os
import sys
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from image_generator import ImageGenerator

PLOTS_DIR = "stories_plots"
SAMPLES_DIR = "style_samples"
os.makedirs(SAMPLES_DIR, exist_ok=True)

STYLES = list(Config.ANIMATION_STYLES.keys())

# Pick one story per style (stories are already assigned 1 style each, round-robin)
# story_001 = pixar_3d, story_002 = studio_ghibli, ..., story_010 = soft_pastel_dream
for i, style_key in enumerate(STYLES):
    story_index = i + 1
    story_file = os.path.join(PLOTS_DIR, f"story_{story_index:03d}.json")

    if not os.path.exists(story_file):
        print(f"[{style_key}] Story file not found: {story_file}")
        continue

    output_path = os.path.join(SAMPLES_DIR, f"{style_key}.png")
    if os.path.exists(output_path):
        print(f"[{style_key}] Already exists, skipping")
        continue

    with open(story_file, "r", encoding="utf-8") as f:
        story = json.load(f)

    style = Config.ANIMATION_STYLES[style_key]
    scene = story["scenes"][0]  # Scene 1

    print(f"[{i+1:2d}/10] {style_key}: '{story['title']}'")
    print(f"        Characters: {', '.join(c['name'] + ' (' + c['type'] + ')' for c in story['characters'])}")

    img_gen = ImageGenerator(animation_style=style)

    try:
        img_gen.generate_scene_image(
            story=story,
            scene=scene,
            scene_index=0,
            output_path=output_path,
        )
        size_kb = os.path.getsize(output_path) // 1024
        print(f"        Saved: {output_path} ({size_kb} KB)")
    except Exception as e:
        print(f"        ERROR: {e}")

print(f"\nDone! Samples saved to {SAMPLES_DIR}/")

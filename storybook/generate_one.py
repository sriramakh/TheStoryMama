#!/usr/bin/env python3
"""Generate a single story end-to-end with the claymation theme."""

import os
import sys

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from story_generator import StoryGenerator
from image_generator import ImageGenerator
from text_overlay import TextOverlay
from pdf_compiler import StoryBookPDF
from character_registry import CharacterRegistry
from utils import get_next_story_number, create_story_folder, save_story_json

# Force gpt-image provider
Config.IMAGE_PROVIDER = "gpt-image"

print("=" * 60)
print("TheStoryMama — Story Generator")
print("=" * 60)

# Step 1: Generate story
print("\n[1/5] Generating story text...")
style = Config.ANIMATION_STYLES["claymation"]
generator = StoryGenerator()
story = generator.generate_story(
    num_scenes=12,
    description=None,  # Let AI surprise us
    art_style_hint=style["story_art_style"],
)
story["animation_style"] = "claymation"
print(f"  Title: {story['title']}")
print(f"  Characters: {', '.join(c['name'] for c in story['characters'])}")
print(f"  Scenes: {len(story['scenes'])}")
if story.get("moral"):
    print(f"  Moral: {story['moral']}")

# Step 2: Create output folder
serial = get_next_story_number(Config.OUTPUT_DIR)
folder = create_story_folder(Config.OUTPUT_DIR, serial, story["title"])
save_story_json(story, folder)
print(f"\n  Output folder: {folder}")

# Step 3: Generate images
print("\n[2/5] Generating illustrations (gpt-image-1-mini, claymation)...")
img_gen = ImageGenerator()

def progress_cb(scene_num, total, status=""):
    print(f"  Scene {scene_num}/{total} {status}")

raw_paths = img_gen.generate_all_images(
    story=story,
    output_dir=folder,
    progress_callback=progress_cb,
)
print(f"  Generated {len(raw_paths)} images")

# Step 4: Overlay text
print("\n[3/5] Overlaying story text on images...")
overlay = TextOverlay()
final_paths = overlay.process_all_scenes(
    story=story,
    raw_image_paths=raw_paths,
    output_dir=folder,
)
print(f"  Created {len(final_paths)} final images")

# Step 5: Compile PDF
print("\n[4/5] Compiling PDF storybook...")
pdf = StoryBookPDF()
pdf_path = os.path.join(folder, f"{story['title'].replace(' ', '_')}.pdf")
pdf.compile_pdf(story=story, image_paths=final_paths, output_path=pdf_path)
print(f"  PDF: {pdf_path}")

# Step 6: Update character registry
print("\n[5/5] Updating character registry...")
registry = CharacterRegistry()
registry.load()
registry.update_from_story(story)
print("  Done!")

print("\n" + "=" * 60)
print(f"Story '{story['title']}' generated successfully!")
print(f"Folder: {folder}")
print("=" * 60)

#!/usr/bin/env python3
"""
Batch generate images for all 100 story plots.
Reads from stories_plots/, generates full pipeline (images + text overlay + PDF)
into stories/ directory.
"""

import os
import sys
import json
import time
import traceback
from collections import deque

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from image_generator import ImageGenerator
from text_overlay import TextOverlay
from pdf_compiler import StoryBookPDF
from utils import sanitize_folder_name, get_next_story_number, create_story_folder, save_story_json

PLOTS_DIR = "stories_plots"
OUTPUT_DIR = Config.OUTPUT_DIR

# Track progress
PROGRESS_FILE = "batch_progress.json"

# --------------------------------------------------------------------------- #
#  Rate limiter: 50 images per minute (OpenAI limit)
#  We track timestamps of recent API calls and sleep if we'd exceed the limit.
#  Using 45/min to leave headroom for the review calls.
# --------------------------------------------------------------------------- #
MAX_IMAGES_PER_MINUTE = 45
_api_call_times = deque()


def rate_limit_wait():
    """Sleep if necessary to stay under the images-per-minute limit."""
    now = time.time()
    # Remove timestamps older than 60 seconds
    while _api_call_times and _api_call_times[0] < now - 60:
        _api_call_times.popleft()

    if len(_api_call_times) >= MAX_IMAGES_PER_MINUTE:
        # Wait until the oldest call falls outside the 60-second window
        wait_time = 60 - (now - _api_call_times[0]) + 0.5
        if wait_time > 0:
            print(f"    [Rate limit] {len(_api_call_times)} calls in last 60s, waiting {wait_time:.1f}s...")
            time.sleep(wait_time)

    _api_call_times.append(time.time())


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed": [], "failed": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def process_story(story_index: int, story: dict, progress: dict) -> bool:
    """Process a single story: generate images, overlay text, compile PDF."""
    story_id = f"story_{story_index:03d}"

    if story_id in progress["completed"]:
        return True

    style_key = story.get("animation_style", Config.DEFAULT_ANIMATION_STYLE)
    style = Config.ANIMATION_STYLES.get(style_key, Config.ANIMATION_STYLES[Config.DEFAULT_ANIMATION_STYLE])
    title = story["title"]
    num_scenes = len(story["scenes"])

    # Create output folder
    serial = get_next_story_number(OUTPUT_DIR)
    folder = create_story_folder(OUTPUT_DIR, serial, title)
    save_story_json(story, folder)

    print(f"  Folder: {folder}")
    print(f"  Style: {style_key} | Scenes: {num_scenes} | Characters: {len(story['characters'])}")

    # Step 1: Generate images (with rate limiting)
    print(f"  Generating {num_scenes} images...")
    img_gen = ImageGenerator(animation_style=style)

    def img_progress(scene_num, total, status=""):
        # Rate limit before each image generation call
        if "generating" in status.lower() or status == "":
            rate_limit_wait()
        print(f"    Scene {scene_num}/{total} {status}")

    raw_paths = img_gen.generate_all_images(
        story=story,
        output_dir=folder,
        progress_callback=img_progress,
    )
    print(f"  Generated {len(raw_paths)} images")

    # Step 2: Text overlay
    print(f"  Overlaying text...")
    overlay = TextOverlay()
    final_paths = overlay.process_all_scenes(
        story=story,
        raw_image_paths=raw_paths,
        output_dir=folder,
    )
    print(f"  Created {len(final_paths)} final images")

    # Step 3: Compile PDF
    print(f"  Compiling PDF...")
    pdf_name = sanitize_folder_name(title) + ".pdf"
    pdf_path = os.path.join(folder, pdf_name)
    pdf = StoryBookPDF()
    pdf.compile_pdf(story=story, image_paths=final_paths, output_path=pdf_path)
    print(f"  PDF: {pdf_path}")

    return True


def main():
    progress = load_progress()

    # Count stories
    story_files = sorted([f for f in os.listdir(PLOTS_DIR) if f.endswith(".json")])
    total = len(story_files)
    completed = len(progress["completed"])

    print("=" * 60)
    print("Batch Image Generator")
    print("=" * 60)
    print(f"Total stories: {total}")
    print(f"Already completed: {completed}")
    print(f"Remaining: {total - completed}")
    print("=" * 60)

    for i, filename in enumerate(story_files):
        story_index = int(filename.replace("story_", "").replace(".json", ""))
        story_id = f"story_{story_index:03d}"

        if story_id in progress["completed"]:
            continue

        filepath = os.path.join(PLOTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            story = json.load(f)

        done_count = len(progress["completed"])
        print(f"\n[{done_count + 1}/{total}] {story['title']}")

        try:
            success = process_story(story_index, story, progress)
            if success:
                progress["completed"].append(story_id)
                save_progress(progress)
                print(f"  DONE")
        except Exception as e:
            print(f"  FAILED: {e}")
            traceback.print_exc()
            progress["failed"].append({"id": story_id, "error": str(e)})
            save_progress(progress)

        # Brief pause between stories
        time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"Batch complete!")
    print(f"Completed: {len(progress['completed'])}/{total}")
    print(f"Failed: {len(progress['failed'])}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

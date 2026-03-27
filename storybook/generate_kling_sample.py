#!/usr/bin/env python3
"""
Generate sample story images using Kling AI kling-v1 model.
Uses the same story plot from the Grok sample for comparison.
Kling API: JWT auth, async task-based, returns image URLs.
"""

import os
import sys
import json
import time
import jwt
import requests

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

KLING_ACCESS_KEY = os.getenv("KLING_ACCESS_KEY", "")
KLING_SECRET_KEY = os.getenv("KLING_SECRET_KEY", "")

if not KLING_ACCESS_KEY or not KLING_SECRET_KEY:
    print("ERROR: KLING_ACCESS_KEY or KLING_SECRET_KEY not found in .env")
    sys.exit(1)

API_BASE = "https://api.klingai.com"
OUTPUT_DIR = "stories_kling_sample"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_jwt_token():
    """Generate a JWT token for Kling API auth."""
    now = int(time.time())
    payload = {
        "iss": KLING_ACCESS_KEY,
        "exp": now + 1800,  # 30 min expiry
        "nbf": now - 5,
    }
    token = jwt.encode(payload, KLING_SECRET_KEY, algorithm="HS256",
                       headers={"alg": "HS256", "typ": "JWT"})
    return token


def create_image_task(prompt: str, aspect_ratio: str = "2:3") -> str | None:
    """Submit an image generation task. Returns task_id."""
    token = get_jwt_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = {
        "model_name": "kling-v1",
        "prompt": prompt[:500],  # Max 500 chars
        "negative_prompt": "blurry, low quality, text, words, letters, numbers, watermark",
        "n": 1,
        "aspect_ratio": aspect_ratio,
    }

    resp = requests.post(f"{API_BASE}/v1/images/generations", json=body, headers=headers, timeout=30)
    data = resp.json()

    if data.get("code") != 0:
        print(f"    Create task error: {data}")
        return None

    task_id = data.get("data", {}).get("task_id")
    return task_id


def poll_task(task_id: str, timeout: int = 300) -> dict | None:
    """Poll a task until it succeeds or fails. Returns task result."""
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}

    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{API_BASE}/v1/images/generations/{task_id}", headers=headers, timeout=30)
        data = resp.json()

        if data.get("code") != 0:
            print(f"    Poll error: {data}")
            return None

        task_data = data.get("data", {})
        status = task_data.get("task_status")

        if status == "succeed":
            return task_data.get("task_result", {})
        elif status == "failed":
            print(f"    Task failed: {task_data.get('task_status_msg')}")
            return None

        time.sleep(5)

    print(f"    Timeout after {timeout}s")
    return None


def download_image(url: str, output_path: str) -> bool:
    """Download an image from URL."""
    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception as e:
        print(f"    Download error: {e}")
        return False


def main():
    # Load the Grok sample story
    story_path = "stories_grok_sample/story_data.json"
    if not os.path.exists(story_path):
        print("ERROR: Grok sample story not found. Run generate_grok_sample.py first.")
        sys.exit(1)

    with open(story_path, "r", encoding="utf-8") as f:
        story = json.load(f)

    # Save story to Kling output dir too
    with open(os.path.join(OUTPUT_DIR, "story_data.json"), "w", encoding="utf-8") as f:
        json.dump(story, f, indent=2, ensure_ascii=False)

    style_desc = (
        "Claymation stop-motion style children's picture book illustration. "
        "Visible clay textures on characters and props, handmade miniature sets, "
        "warm stop-motion lighting with soft shadows, charming imperfections."
    )

    character_block = " | ".join(
        f"{c['name']} ({c['type']}): {c['description'][:80]}"
        for c in story["characters"]
    )

    print("=" * 60)
    print("Kling AI (kling-v1) — Story Image Generator")
    print("=" * 60)
    print(f"Story: {story['title']}")
    print(f"Scenes: {len(story['scenes'])}")
    print(f"Cost estimate: {len(story['scenes'])} x $0.003 = ${len(story['scenes']) * 0.003:.3f}")
    print("=" * 60)

    image_paths = []
    for scene in story["scenes"]:
        scene_num = scene["scene_number"]
        output_path = os.path.join(OUTPUT_DIR, f"scene_{scene_num:02d}.png")

        if os.path.exists(output_path):
            print(f"[Scene {scene_num:2d}/{len(story['scenes'])}] Already exists, skipping")
            image_paths.append(output_path)
            continue

        # Build prompt (max 500 chars for Kling)
        prompt = f"{style_desc} {scene['image_description']}"
        if len(prompt) > 500:
            prompt = prompt[:497] + "..."

        print(f"[Scene {scene_num:2d}/{len(story['scenes'])}] Submitting...")

        # Create task
        task_id = create_image_task(prompt, aspect_ratio="2:3")
        if not task_id:
            print(f"  FAILED to create task")
            continue

        print(f"  Task: {task_id} — polling...")

        # Poll for result
        result = poll_task(task_id)
        if not result:
            print(f"  FAILED")
            continue

        # Download image
        images = result.get("images", [])
        if not images:
            print(f"  No images in result")
            continue

        url = images[0].get("url")
        if not url:
            print(f"  No URL in result")
            continue

        if download_image(url, output_path):
            size_kb = os.path.getsize(output_path) // 1024
            print(f"  Done ({size_kb} KB)")
            image_paths.append(output_path)
        else:
            print(f"  Download failed")

    print(f"\n{'=' * 60}")
    print(f"Summary")
    print(f"  Images generated: {len(image_paths)}/{len(story['scenes'])}")
    print(f"  Output: {OUTPUT_DIR}/")
    print(f"  Total cost: ~${len(image_paths) * 0.003:.3f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

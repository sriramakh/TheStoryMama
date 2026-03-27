#!/usr/bin/env python3
"""
Generate a single sample story using Grok models:
- Story text: grok-4-1-fast-reasoning
- Images: grok-imagine-image
"""

import os
import sys
import json
import base64
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY", "")
if not GROK_API_KEY:
    print("ERROR: GROK_API_KEY not found in .env")
    sys.exit(1)

# xAI uses OpenAI-compatible API
client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1",
)

OUTPUT_DIR = "stories_grok_sample"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Step 1: Generate story with grok-4-1-fast-reasoning ─────────────────────

print("=" * 60)
print("Grok Story Generator — Sample")
print("=" * 60)

print("\n[1/3] Generating story with grok-4-1-fast-reasoning...")

story_prompt = """Create a children's story with 12 scenes for toddlers aged 2-4.

Return your response as a JSON object with this EXACT structure:
{
    "title": "The Story Title",
    "characters": [
        {
            "name": "Character Name",
            "type": "exact species",
            "description": "Extremely detailed visual description: species, colors, clothing, accessories"
        }
    ],
    "setting": "The story's world",
    "art_style": "Claymation stop-motion with clay textures and miniature handmade sets",
    "moral": "A gentle moral or null",
    "scenes": [
        {
            "scene_number": 1,
            "background": "Specific location for this scene",
            "text": "2-3 short sentences for a toddler",
            "image_description": "Detailed description of what to draw"
        }
    ]
}

RULES:
- All characters must share the same habitat (no ocean creatures on land)
- 2-4 characters that fit the plot
- Real plot arc with tension and resolution
- Happy ending during DAYTIME (no night/sleep endings)
- Each scene has a different background
- Simple language for 2-4 year olds
- Use woodland forest animals
- Claymation art style

Return ONLY valid JSON, no extra text."""

response = client.chat.completions.create(
    model="grok-4-1-fast-reasoning",
    messages=[
        {"role": "system", "content": "You are a children's picture book author. Respond ONLY with valid JSON."},
        {"role": "user", "content": story_prompt},
    ],
    temperature=0.9,
)

raw = response.choices[0].message.content.strip()

# Extract JSON
import re
try:
    story = json.loads(raw)
except json.JSONDecodeError:
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, re.DOTALL)
    if match:
        story = json.loads(match.group(1))
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        story = json.loads(raw[start:end + 1])

story["animation_style"] = "claymation"

# Save story JSON
with open(os.path.join(OUTPUT_DIR, "story_data.json"), "w", encoding="utf-8") as f:
    json.dump(story, f, indent=2, ensure_ascii=False)

print(f"  Title: {story['title']}")
print(f"  Characters: {', '.join(c['name'] + ' (' + c['type'] + ')' for c in story['characters'])}")
print(f"  Scenes: {len(story['scenes'])}")

# ─── Step 2: Generate images with grok-imagine-image ─────────────────────────

print(f"\n[2/3] Generating {len(story['scenes'])} images with grok-imagine-image...")

style_desc = (
    "Claymation stop-motion style children's picture book illustration. "
    "Visible clay textures on characters and props, handmade miniature sets, "
    "warm stop-motion lighting with soft shadows, charming imperfections, "
    "tactile and cozy feel."
)

character_block = "\n".join(
    f"- {c['name']} ({c['type']}): {c['description']}"
    for c in story["characters"]
)

image_paths = []
for i, scene in enumerate(story["scenes"]):
    scene_num = scene["scene_number"]
    output_path = os.path.join(OUTPUT_DIR, f"scene_{scene_num:02d}.png")

    if os.path.exists(output_path):
        print(f"  Scene {scene_num}/{len(story['scenes'])} — exists, skipping")
        image_paths.append(output_path)
        continue

    print(f"  Scene {scene_num}/{len(story['scenes'])} generating...")

    prompt = f"""{style_desc}

BACKGROUND: {scene.get('background', '')}

CHARACTERS:
{character_block}

SCENE {scene_num} of {len(story['scenes'])}:
{scene['image_description']}

RULES:
- Claymation stop-motion aesthetic
- Warm, friendly, suitable for ages 2-4
- DO NOT include any text, words, letters, or numbers in the image"""

    try:
        import requests as req_lib

        # Grok image API — minimal params, returns URL
        result = client.images.generate(
            model="grok-imagine-image",
            prompt=prompt,
            n=1,
        )

        # Handle both URL and b64 responses
        img_data = result.data[0]
        if hasattr(img_data, 'url') and img_data.url:
            resp = req_lib.get(img_data.url, timeout=120)
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(resp.content)
        elif hasattr(img_data, 'b64_json') and img_data.b64_json:
            image_bytes = base64.b64decode(img_data.b64_json)
            with open(output_path, "wb") as f:
                f.write(image_bytes)
        else:
            print(f"  Scene {scene_num} ERROR: No image data in response")
            print(f"    Response: {result}")
            continue

        size_kb = os.path.getsize(output_path) // 1024
        print(f"  Scene {scene_num}/{len(story['scenes'])} done ({size_kb} KB)")
        image_paths.append(output_path)
    except Exception as e:
        print(f"  Scene {scene_num} ERROR: {e}")

    time.sleep(2)

# ─── Step 3: Summary ─────────────────────────────────────────────────────────

print(f"\n[3/3] Summary")
print(f"  Story: {story['title']}")
print(f"  Images generated: {len(image_paths)}/{len(story['scenes'])}")
print(f"  Output: {OUTPUT_DIR}/")
print("=" * 60)

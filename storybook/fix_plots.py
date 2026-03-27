#!/usr/bin/env python3
"""
Fix problematic story plots by regenerating them with anti-repetition prompts.
Targets: duplicate titles, night endings, overused "The Great..." pattern.
"""

import os
import json
import time
import random
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from story_generator import StoryGenerator, STORY_THEMES, CHARACTER_HABITAT_GROUPS, STORY_STRUCTURES

PLOTS_DIR = "stories_plots"
STYLES = list(Config.ANIMATION_STYLES.keys())
SCENE_COUNTS = [12, 12, 13, 13, 14, 14, 15, 12, 13, 15]

# Load existing titles to avoid
existing_titles = set()
all_stories = {}
for i in range(1, 101):
    filepath = os.path.join(PLOTS_DIR, f"story_{i:03d}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            s = json.load(f)
            all_stories[i] = s
            existing_titles.add(s["title"].lower())

# Identify stories to regenerate
to_fix = set()

# 1. All duplicate titles — keep the first occurrence, regenerate the rest
from collections import Counter
title_counts = Counter()
title_first = {}
for i in sorted(all_stories.keys()):
    t = all_stories[i]["title"].lower()
    title_counts[t] += 1
    if t not in title_first:
        title_first[t] = i
    elif title_counts[t] > 1:
        to_fix.add(i)

# 2. Night/sleep endings
NIGHT_WORDS = ["sleep", "dream", "night", "moon", "star", "bed", "yawn", "snore",
               "lullaby", "pillow", "dark", "firefly", "lantern", "dusk",
               "twilight", "sleepy"]
for i, s in all_stories.items():
    scenes = s.get("scenes", [])
    if not scenes:
        continue
    last_3 = scenes[-3:]
    combined = " ".join(sc.get("text", "") + " " + sc.get("background", "") for sc in last_3).lower()
    # "blanket" is fine if it's a picnic blanket, only flag the real night words
    if any(w in combined for w in NIGHT_WORDS):
        to_fix.add(i)

# 3. Stories with "The Great" in title (too many)
for i, s in all_stories.items():
    if s["title"].lower().startswith("the great "):
        to_fix.add(i)

print(f"Stories to regenerate: {len(to_fix)} out of 100")
print(f"Indices: {sorted(to_fix)}")

# Banned title patterns and words to force diversity
BANNED_TITLE_STARTS = [
    "the great", "the big", "the magical", "the wonderful",
]

BANNED_NAMES = [
    "benny", "milo", "tilly", "pip", "luna", "lila", "cleo",
    "bubbles", "daisy", "lulu", "lola", "coco", "gigi", "freddy", "buzzy",
]

# Title inspiration — diverse, creative alternatives
TITLE_PATTERNS = [
    "Use a title that sounds like a real published children's book. Examples of GOOD titles: "
    "'Rosie Revere, Engineer', 'The Snail and the Whale', 'Where the Wild Things Are', "
    "'Goodnight Moon', 'Corduroy', 'If You Give a Mouse a Cookie', "
    "'The Very Hungry Caterpillar', 'Owl Babies', 'We're Going on a Bear Hunt', "
    "'Room on the Broom', 'The Gruffalo', 'Stellaluna'. "
    "Your title should be UNIQUE, MEMORABLE, and SPECIFIC to your story's plot. "
    "NEVER start with 'The Great'. NEVER use generic titles like 'The [Adjective] [Place] [Activity]'. "
    "Use character names, specific imagery, or intriguing phrases that make a parent want to click.",
]

generator = StoryGenerator()

def regenerate_story(index: int, attempt: int = 0) -> dict | None:
    """Regenerate a story with anti-repetition constraints."""
    style_key = STYLES[(index - 1) % len(STYLES)]
    style = Config.ANIMATION_STYLES[style_key]
    num_scenes = SCENE_COUNTS[(index - 1) % len(SCENE_COUNTS)]

    # Pick a habitat group, cycling to ensure variety
    habitat_keys = list(CHARACTER_HABITAT_GROUPS.keys())
    habitat_name = habitat_keys[(index + attempt) % len(habitat_keys)]
    species_pool = CHARACTER_HABITAT_GROUPS[habitat_name]
    species_sample = random.sample(species_pool, min(8, len(species_pool)))

    # Pick a story structure
    structure = random.choice(STORY_STRUCTURES)

    # Build a custom prompt with anti-repetition rules
    banned_names_str = ", ".join(BANNED_NAMES)

    custom_description = (
        f"Create a COMPLETELY ORIGINAL story. Here are your constraints:\n\n"
        f"TITLE RULES:\n"
        f"- NEVER start the title with 'The Great'\n"
        f"- NEVER use generic titles like 'The [Adjective] [Place] Adventure/Race/Hunt'\n"
        f"- Use the character's name in the title, OR use vivid specific imagery\n"
        f"- Good examples: 'Pebble's Flying Machine', 'The Day It Rained Marshmallows', "
        f"'How Finn Found His Roar', 'A Puddle Full of Stars'\n\n"
        f"CHARACTER NAME RULES:\n"
        f"- Do NOT use any of these overused names: {banned_names_str}\n"
        f"- Invent FRESH, unique names that fit the character\n\n"
        f"PLOT STRUCTURE: {structure}\n\n"
        f"HABITAT: {habitat_name.replace('_', ' ')} — all characters must fit this habitat\n"
        f"Species to choose from: {', '.join(species_sample)}\n\n"
        f"ENDING RULES:\n"
        f"- The story MUST end during bright DAYTIME — morning or afternoon\n"
        f"- ABSOLUTELY NO: sunset, night, stars, moon, sleep, dreams, dusk, twilight, lanterns, fireflies\n"
        f"- End with energy and joy, not wind-down\n"
    )

    try:
        # We'll call generate_story but inject our custom description
        story = generator.generate_story(
            num_scenes=num_scenes,
            description=custom_description,
            art_style_hint=style["story_art_style"],
        )
        story["animation_style"] = style_key

        # Validate: reject if title starts with "The Great"
        if story["title"].lower().startswith("the great"):
            print(f"    Rejected: title starts with 'The Great' — retrying")
            return None

        # Validate: reject if duplicate title
        if story["title"].lower() in existing_titles:
            print(f"    Rejected: duplicate title '{story['title']}' — retrying")
            return None

        # Validate: no night endings
        last_3 = story["scenes"][-3:]
        combined = " ".join(sc.get("text", "") + " " + sc.get("background", "") for sc in last_3).lower()
        if any(w in combined for w in NIGHT_WORDS):
            print(f"    Rejected: night ending detected — retrying")
            return None

        return story
    except Exception as e:
        print(f"    Error: {e}")
        return None


def main():
    fixed = 0
    failed = 0

    for idx in sorted(to_fix):
        filepath = os.path.join(PLOTS_DIR, f"story_{idx:03d}.json")
        old_title = all_stories[idx]["title"]
        style_key = STYLES[(idx - 1) % len(STYLES)]
        print(f"[{idx:3d}] Fixing '{old_title}' (style: {style_key})...")

        success = False
        for attempt in range(5):
            story = regenerate_story(idx, attempt)
            if story:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(story, f, indent=2, ensure_ascii=False)
                existing_titles.add(story["title"].lower())
                print(f"       -> '{story['title']}' (chars: {len(story['characters'])})")
                fixed += 1
                success = True
                break
            time.sleep(1)

        if not success:
            print(f"       FAILED after 5 attempts — keeping original")
            failed += 1

        time.sleep(1)

    print(f"\n{'=' * 60}")
    print(f"Fixed: {fixed} | Failed: {failed} | Total attempted: {len(to_fix)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

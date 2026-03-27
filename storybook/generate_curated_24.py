#!/usr/bin/env python3
"""
Generate 24 curated stories: 12 Family + 12 Fantasy.
Each has a specific description to ensure the theme lands properly.
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
from image_generator import ImageGenerator
from text_overlay import TextOverlay
from pdf_compiler import StoryBookPDF
from utils import sanitize_folder_name, get_next_story_number, create_story_folder, save_story_json

# ── 12 Family stories ─────────────────────────────────────────────────────────

FAMILY_STORIES = [
    {
        "description": "A little girl helps her Papa bake a birthday cake for Mama. They make a huge mess in the kitchen — flour everywhere, eggs on the floor — but the cake turns out beautiful and Mama loves it.",
        "style": "claymation",
        "scenes": 12,
    },
    {
        "description": "A big brother teaches his baby sister how to take her first steps. She keeps falling and he keeps catching her, until she walks all the way across the room to give him a hug.",
        "style": "felt_plushie",
        "scenes": 12,
    },
    {
        "description": "Grandma takes her grandchild to her magical vegetable garden. They plant seeds, water them, pull out funny-shaped carrots, and make soup together in Grandma's cozy kitchen.",
        "style": "toy_diorama",
        "scenes": 13,
    },
    {
        "description": "A family of hedgehogs prepares for a rainy day picnic inside their cozy burrow. Each family member contributes something — Dad makes sandwiches, Mom finds the blanket, the kids draw a pretend sunshine on the wall.",
        "style": "paper_cutout",
        "scenes": 12,
    },
    {
        "description": "A little boy and his Grandpa go on a fishing trip to the pond. They don't catch any fish, but they find a frog, skip stones, share stories, and realize the best catch was spending time together.",
        "style": "animation_movie",
        "scenes": 13,
    },
    {
        "description": "Twin fox cubs have completely different personalities — one is loud and adventurous, the other is quiet and thoughtful. They discover that together they can solve problems neither could alone.",
        "style": "claymation",
        "scenes": 12,
    },
    {
        "description": "A Mama bear and her cub go on a nature walk. The cub asks 'why?' about everything — why is the sky blue, why do birds sing, why do flowers smell nice — and Mama patiently answers each one with wonder.",
        "style": "animation_movie",
        "scenes": 14,
    },
    {
        "description": "A little girl's family moves to a new home. She's scared and sad about leaving her old room, but her family helps her decorate her new room and she discovers the backyard has a treehouse.",
        "style": "felt_plushie",
        "scenes": 12,
    },
    {
        "description": "A Papa penguin carries his egg through a snowstorm to keep it warm. When the egg finally hatches, the tiny chick sees Papa's face first and they waddle together into the sunshine.",
        "style": "toy_diorama",
        "scenes": 13,
    },
    {
        "description": "Three rabbit siblings argue about what game to play — one wants to dig, one wants to hop race, one wants to hide-and-seek. They invent a new game that combines all three and have the best afternoon ever.",
        "style": "paper_cutout",
        "scenes": 12,
    },
    {
        "description": "A little boy makes a handmade card for his Mom on Mother's Day. He gathers flowers from the garden, draws wobbly hearts, and adds glitter everywhere. Mom's tears of joy confuse him until she explains they're happy tears.",
        "style": "animation_movie",
        "scenes": 12,
    },
    {
        "description": "A family of otters builds a dam together in the river. The youngest otter keeps putting sticks in the wrong place, but the family shows patience and encouragement, and the dam works because of everyone's effort.",
        "style": "claymation",
        "scenes": 13,
    },
]

# ── 12 Fantasy stories ────────────────────────────────────────────────────────

FANTASY_STORIES = [
    {
        "description": "A little mouse discovers a tiny door behind the bookshelf that leads to a miniature candy kingdom. The candy people need help fixing their chocolate bridge before the marshmallow river rises.",
        "style": "animation_movie",
        "scenes": 14,
    },
    {
        "description": "A shy caterpillar finds a pair of magical wings in a hollow tree. Before she can use them, she must complete three kind deeds. Each deed is harder than the last, but she earns her wings and transforms into a dazzling butterfly.",
        "style": "glowlight_fantasy",
        "scenes": 13,
    },
    {
        "description": "A little cloud named Puff can't make rain like the other clouds. Instead, everything Puff sprinkles turns into colorful bubbles. The village below has never seen anything so magical.",
        "style": "animation_movie",
        "scenes": 12,
    },
    {
        "description": "A child finds a paintbrush that brings drawings to life. They paint a puppy, a garden, and a rainbow slide — but when they paint a thunderstorm by accident, they must paint sunshine to save the day.",
        "style": "animation_movie",
        "scenes": 13,
    },
    {
        "description": "Every night, the toys in a nursery come to life. Tonight, the teddy bear, the wooden train, and the ragdoll must find the baby's missing pacifier before morning, searching through a bedroom that feels enormous to tiny toys.",
        "style": "felt_plushie",
        "scenes": 14,
    },
    {
        "description": "A little star falls from the sky into a forest pond. A brave frog and a curious firefly must carry the star back up to the sky, climbing the tallest tree in the world together.",
        "style": "glowlight_fantasy",
        "scenes": 12,
    },
    {
        "description": "A magic music box opens a portal to a land where everything is made of flowers. Flower-horses gallop through petal meadows, bees serve honey tea, and the queen is a giant sunflower who grants one wish.",
        "style": "glowlight_fantasy",
        "scenes": 13,
    },
    {
        "description": "A baby dragon who sneezes soap bubbles instead of fire feels different from the other dragons. But when a fire breaks out in the village, only soap bubbles can put it out — making the baby dragon a hero.",
        "style": "animation_movie",
        "scenes": 12,
    },
    {
        "description": "A child shrinks to the size of an ant and discovers the insect world under the garden. Ants are builders, ladybugs are painters, and the spider is a weaver who knits blankets for cold beetles.",
        "style": "toy_diorama",
        "scenes": 14,
    },
    {
        "description": "A puddle after a rainstorm turns out to be a window into an upside-down world where fish fly in the sky and birds swim in the ocean. A brave duckling jumps in and has an adventure before finding the way back.",
        "style": "animation_movie",
        "scenes": 12,
    },
    {
        "description": "The moon drops a silver key into a child's bedroom. The key opens a wardrobe that leads to a cozy cloud kingdom where cloud animals bounce and play, and the child learns to jump from cloud to cloud.",
        "style": "glowlight_fantasy",
        "scenes": 13,
    },
    {
        "description": "A little owl discovers that her hoots have magical powers — different hoots make flowers bloom, rivers sparkle, and snow fall. She must learn to control her gift before the forest gets too confused.",
        "style": "animation_movie",
        "scenes": 12,
    },
]

generator = StoryGenerator()

def process_story(story_spec: dict, label: str, index: int):
    """Generate a full story: text + images + overlay + PDF."""
    desc = story_spec["description"]
    style_key = story_spec["style"]
    num_scenes = story_spec["scenes"]
    style = Config.ANIMATION_STYLES[style_key]

    print(f"\n[{label} {index}] Generating story...")
    print(f"  Theme: {desc[:80]}...")
    print(f"  Style: {style_key} | Scenes: {num_scenes}")

    # Generate story text
    story = generator.generate_story(
        num_scenes=num_scenes,
        description=desc,
        art_style_hint=style["story_art_style"],
    )
    story["animation_style"] = style_key

    print(f"  Title: {story['title']}")
    chars = ", ".join(f"{c['name']} ({c['type']})" for c in story["characters"])
    print(f"  Characters: {chars}")

    # Create output folder
    serial = get_next_story_number(Config.OUTPUT_DIR)
    folder = create_story_folder(Config.OUTPUT_DIR, serial, story["title"])
    save_story_json(story, folder)

    # Generate images (with rate limiting — 1.5s between scenes)
    print(f"  Generating {len(story['scenes'])} images...")
    img_gen = ImageGenerator(animation_style=style)

    def progress_cb(scene_num, total, status=""):
        print(f"    Scene {scene_num}/{total} {status}")

    raw_paths = img_gen.generate_all_images(
        story=story,
        output_dir=folder,
        progress_callback=progress_cb,
    )

    # Text overlay
    print(f"  Overlaying text...")
    overlay = TextOverlay()
    final_paths = overlay.process_all_scenes(
        story=story,
        raw_image_paths=raw_paths,
        output_dir=folder,
    )

    # PDF
    print(f"  Compiling PDF...")
    pdf_name = sanitize_folder_name(story["title"]) + ".pdf"
    pdf_path = os.path.join(folder, pdf_name)
    pdf = StoryBookPDF()
    pdf.compile_pdf(story=story, image_paths=final_paths, output_path=pdf_path)

    print(f"  DONE: {folder}")
    return True


def main():
    print("=" * 60)
    print("Curated Story Generator — 12 Family + 12 Fantasy")
    print("=" * 60)

    # Family stories
    for i, spec in enumerate(FAMILY_STORIES, 1):
        try:
            process_story(spec, "Family", i)
        except Exception as e:
            print(f"  FAILED: {e}")
            traceback.print_exc()
        time.sleep(3)

    # Fantasy stories
    for i, spec in enumerate(FANTASY_STORIES, 1):
        try:
            process_story(spec, "Fantasy", i)
        except Exception as e:
            print(f"  FAILED: {e}")
            traceback.print_exc()
        time.sleep(3)

    print(f"\n{'=' * 60}")
    print("All 24 curated stories complete!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

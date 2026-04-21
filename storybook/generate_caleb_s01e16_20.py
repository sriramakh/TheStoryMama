#!/usr/bin/env python3
"""Generate Caleb's Adventures S01E16–S01E20 with portrait-first pipeline.

Uses the ORIGINAL character portraits and descriptions from episodes 1-15 (VPS)
to ensure visual consistency across the series.

Portraits are loaded from stories/_caleb_portraits/ (copied from VPS originals).
Ravi has no existing portrait — one will be generated on first use.
"""

import os
import sys
import json
import time
import shutil
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from story_generator import StoryGenerator
from image_generator import ImageGenerator
from text_overlay import TextOverlay
from pdf_compiler import StoryBookPDF
from utils import sanitize_folder_name, create_story_folder, save_story_json
from PIL import Image

# ── Style ──────────────────────────────────────────────────────────────
STYLE_KEY = "animation_movie"
STYLE = Config.ANIMATION_STYLES[STYLE_KEY]

# ── Canonical character descriptions (from VPS story_data.json files) ──
# These are the EXACT descriptions used in episodes 1-15.
CALEB_CHARACTERS = [
    {
        "name": "Caleb",
        "type": "toddler boy",
        "description": (
            "A curious 3-year-old boy with light fair skin, big round hazel eyes, "
            "short tousled sandy-brown hair with a slight cowlick, rosy cheeks. "
            "Wearing a signature red explorer vest with gold buttons over a yellow-and-white "
            "striped t-shirt, green cargo shorts, white socks, and little brown lace-up boots. "
            "Always carries a tiny blue backpack with a star keychain."
        ),
    },
    {
        "name": "Lily",
        "type": "young girl",
        "description": (
            "A confident 5-year-old girl with light fair skin matching Caleb, long wavy "
            "sandy-brown hair often in two braids with pink ribbons, bright hazel eyes like "
            "her brother, a small beauty mark on her left cheek. Wearing a coral-pink t-shirt "
            "with a sunflower print, denim overalls with a daisy patch on the pocket, and "
            "yellow rain boots."
        ),
    },
    {
        "name": "Bubbles",
        "type": "golden retriever puppy",
        "description": (
            "A round, fluffy golden retriever puppy with soft golden-cream fur, big soulful "
            "dark brown eyes, a shiny black nose, floppy velvety ears, a spotted pink tongue "
            "that always sticks out, and a constantly wagging tail. Wearing a teal bandana "
            "with white paw prints tied around his neck."
        ),
    },
    {
        "name": "Sarah",
        "type": "mother",
        "description": (
            "A warm, graceful mother with light fair skin, long straight sandy-brown hair "
            "usually in a loose ponytail with a scrunchie, soft hazel eyes, light freckles "
            "across her nose and cheeks. Wearing a teal v-neck wrap top, comfortable cream "
            "joggers, and white slip-on canvas shoes. A small gold locket necklace around "
            "her neck."
        ),
    },
    {
        "name": "Jack",
        "type": "father",
        "description": (
            "A tall, athletic father with light fair skin, short neat sandy-brown hair like "
            "his children, warm hazel eyes, light stubble on his jaw, and a friendly wide "
            "smile. Wearing a navy-blue plaid flannel shirt with rolled-up sleeves, khaki "
            "pants, brown leather belt, and rugged canvas sneakers. Has a pencil tucked "
            "behind his right ear."
        ),
    },
    {
        "name": "Nana Joy",
        "type": "grandmother",
        "description": (
            "A warm, round-faced elderly woman with light fair skin with gentle wrinkles, "
            "soft silver-white hair in a neat bun held by a tortoiseshell clip, kind hazel "
            "eyes behind round gold-rimmed glasses. Wearing a cozy burnt-orange cardigan "
            "with wooden buttons over a cream floral blouse, a long olive-green skirt, and "
            "comfortable tan slip-on shoes. A beaded reading-glasses chain around her neck."
        ),
    },
]

GUEST_CHARACTERS = {
    "Mila": {
        "name": "Mila",
        "type": "little girl",
        "description": (
            "A cheerful 3-year-old girl with warm light skin, straight black hair in a neat "
            "bob cut with a small red bow clip on the left side, almond-shaped dark brown "
            "eyes, round rosy cheeks. Wearing a mint-green smock dress with white daisy "
            "embroidery over a white long-sleeve shirt, white leggings, and light-purple "
            "Mary Jane shoes. Carries a small sketchbook and crayons."
        ),
    },
    "Aiden": {
        "name": "Aiden",
        "type": "boy",
        "description": (
            "An energetic 4-year-old boy with rich dark brown skin, a short neat fade "
            "haircut, big bright dark eyes with long lashes, and an infectious wide grin. "
            "Wearing an orange basketball jersey with number 7, black athletic shorts with "
            "white stripes, and bright green high-top sneakers with velcro straps. A blue "
            "sweatband on his right wrist."
        ),
    },
    "Sofia": {
        "name": "Sofia",
        "type": "little girl",
        "description": (
            "A bubbly 3-year-old girl with warm tan-olive skin, big bouncy curly dark brown "
            "hair held back by a bright yellow headband, large expressive brown eyes, dimples "
            "when she smiles. Wearing a ruffled red polka-dot dress with a white Peter Pan "
            "collar, white ankle socks with lace trim, and shiny red Mary Jane shoes. A tiny "
            "charm bracelet on her wrist."
        ),
    },
    "Ravi": {
        "name": "Ravi",
        "type": "boy",
        "description": (
            "A thoughtful 4-year-old boy with medium-brown skin, messy wavy black hair that "
            "falls across his forehead, large curious dark brown eyes behind small round "
            "blue-framed glasses. Wearing a mustard-yellow henley shirt with three buttons, "
            "navy-blue corduroy pants, and brown leather sandals. Always has a magnifying "
            "glass in his back pocket."
        ),
    },
}

# ── Portrait cache (original portraits from VPS episodes 1-15) ─────────
PORTRAITS_CACHE_DIR = os.path.join(Config.OUTPUT_DIR, "_caleb_portraits")

# ── Episodes S01E16–S01E20 ─────────────────────────────────────────────
EPISODES = [
    {
        "code": "S01E16",
        "story_id": 220,
        "title_hint": "The Camping Night",
        "description": (
            "Caleb's Adventures series episode. "
            "Jack sets up a tent in the backyard for Caleb and Lily's first 'camping trip.' "
            "They roast marshmallows (Bubbles steals one), tell silly made-up ghost stories "
            "that aren't scary at all, spot fireflies, and Jack plays ukulele. Caleb is nervous "
            "about sleeping outside but Lily and Bubbles snuggle close. They fall asleep under "
            "the stars and Sarah sneaks out with blankets and hot chocolate."
        ),
        "guests": [],
        "scenes": 12,
    },
    {
        "code": "S01E17",
        "story_id": 221,
        "title_hint": "Mila's Kite Festival",
        "description": (
            "Caleb's Adventures series episode. "
            "Mila invites Caleb, Lily, and Aiden to fly kites at the park. Caleb's kite keeps "
            "nose-diving, Lily's gets stuck in a tree, and Aiden's string tangles with Mila's. "
            "Bubbles chases every kite shadow on the ground. Nana Joy arrives with a simple "
            "kite she made from newspaper and sticks — it flies the highest of all. Everyone "
            "learns that the best things don't have to be fancy."
        ),
        "guests": ["Mila", "Aiden"],
        "scenes": 12,
    },
    {
        "code": "S01E18",
        "story_id": 222,
        "title_hint": "The Costume Parade",
        "description": (
            "Caleb's Adventures series episode. "
            "The neighborhood kids organize a costume parade. Caleb wants to be a dinosaur but "
            "his cardboard costume keeps falling apart. Lily is a butterfly with tissue paper "
            "wings. Sofia is a princess who keeps tripping on her cape. Ravi is a robot made of "
            "boxes. Bubbles wears a tiny superhero cape. Sarah and Jack are the judges but can't "
            "pick a winner, so everyone wins 'Best Costume' for different funny reasons."
        ),
        "guests": ["Sofia", "Ravi"],
        "scenes": 13,
    },
    {
        "code": "S01E19",
        "story_id": 223,
        "title_hint": "Bubbles Learns a Trick",
        "description": (
            "Caleb's Adventures series episode. "
            "Caleb decides to teach Bubbles to shake hands. Every attempt goes hilariously wrong — "
            "Bubbles rolls over, licks Caleb's face, fetches a shoe, and runs in circles. "
            "Lily tries helping with treats. Jack demonstrates with a 'sit' that Bubbles ignores. "
            "Nana Joy suggests patience. After a whole day of trying, just before bedtime, "
            "Bubbles suddenly offers her paw perfectly — and everyone cheers so loud she runs "
            "under the couch. The moral: good things take patience, and that's okay."
        ),
        "guests": [],
        "scenes": 12,
    },
    {
        "code": "S01E20",
        "story_id": 224,
        "title_hint": "The Thank You Party",
        "description": (
            "Caleb's Adventures series — SEASON FINALE. "
            "Caleb wants to throw a thank-you party for everyone who made his year special. "
            "He and Lily make invitations (covered in glitter and stickers). Sarah helps bake a "
            "huge messy cake. Jack hangs decorations that keep falling down. Nana Joy brings her "
            "famous cookies. All the friends arrive — Mila, Aiden, Sofia, and Ravi. "
            "Caleb gives each person a hand-drawn 'thank you' card (stick figures with big "
            "hearts). Bubbles accidentally knocks over the cake but everyone laughs and eats it "
            "anyway. They end the night dancing in the backyard under string lights. "
            "The moral: the best adventures are the ones you share with people you love."
        ),
        "guests": ["Mila", "Aiden", "Sofia", "Ravi"],
        "scenes": 14,
    },
]

# ── Pipeline ───────────────────────────────────────────────────────────

generator = StoryGenerator()
shared_portrait_paths: dict[str, str] = {}


def get_episode_characters(ep: dict) -> list[dict]:
    """Get the full character list for an episode (core + guests)."""
    chars = list(CALEB_CHARACTERS)
    for guest_name in ep.get("guests", []):
        if guest_name in GUEST_CHARACTERS:
            chars.append(GUEST_CHARACTERS[guest_name])
    return chars


def load_cached_portraits():
    """Load original portraits from the cache directory (copied from VPS)."""
    global shared_portrait_paths
    if not os.path.exists(PORTRAITS_CACHE_DIR):
        print(f"  ERROR: Portrait cache not found at {PORTRAITS_CACHE_DIR}")
        print(f"  Copy original portraits from VPS first!")
        sys.exit(1)

    # Map filenames to character names
    name_map = {
        "caleb.png": "Caleb",
        "lily.png": "Lily",
        "bubbles.png": "Bubbles",
        "jack.png": "Jack",
        "sarah.png": "Sarah",
        "nana_joy.png": "Nana Joy",
        "mila.png": "Mila",
        "aiden.png": "Aiden",
        "sofia.png": "Sofia",
        "ravi.png": "Ravi",
    }

    for fname in os.listdir(PORTRAITS_CACHE_DIR):
        if fname in name_map:
            shared_portrait_paths[name_map[fname]] = os.path.join(PORTRAITS_CACHE_DIR, fname)

    print(f"  Loaded {len(shared_portrait_paths)} original portraits: {', '.join(sorted(shared_portrait_paths.keys()))}")

    # Check for missing essential characters
    missing = [c["name"] for c in CALEB_CHARACTERS if c["name"] not in shared_portrait_paths]
    if missing:
        print(f"  WARNING: Missing portraits for core characters: {', '.join(missing)}")


def ensure_portraits(characters: list[dict], img_gen: ImageGenerator, output_dir: str):
    """Generate portraits only for characters that don't have originals (e.g., Ravi)."""
    global shared_portrait_paths

    missing = [c for c in characters if c["name"] not in shared_portrait_paths]
    if not missing:
        print(f"  All {len(characters)} portraits available from originals.")
        return

    print(f"  Generating {len(missing)} new portraits (no original available): {', '.join(c['name'] for c in missing)}")

    temp_story = {"characters": missing, "scenes": []}
    img_gen.generate_character_portraits(
        temp_story, output_dir,
        progress_callback=lambda s, t, st: print(f"    Portrait {s}/{t}")
    )

    for c in missing:
        name = c["name"]
        if name in img_gen._portrait_paths:
            src = img_gen._portrait_paths[name]
            cache_path = os.path.join(PORTRAITS_CACHE_DIR, f"{name.lower().replace(' ', '_')}.png")
            if not os.path.exists(cache_path):
                shutil.copy2(src, cache_path)
            shared_portrait_paths[name] = cache_path

    time.sleep(2)


def process_episode(ep: dict, index: int, total: int):
    """Generate one Caleb episode using original portraits."""
    code = ep["code"]
    target_id = ep["story_id"]
    desc = ep["description"]
    num_scenes = ep["scenes"]

    print(f"\n{'=' * 60}")
    print(f"[{index}/{total}] {code}: {ep['title_hint']}")
    print(f"{'=' * 60}")

    characters = get_episode_characters(ep)
    char_names = ", ".join(f"{c['name']} ({c['type']})" for c in characters)
    print(f"  Characters: {char_names}")

    # Build character instruction for story generator
    char_instruction = "\n".join(
        f"- {c['name']} ({c['type']}): {c['description']}" for c in characters
    )
    full_desc = (
        f"{desc}\n\n"
        f"IMPORTANT — Use EXACTLY these characters with these descriptions. "
        f"Do NOT rename, add, or remove any characters:\n{char_instruction}"
    )

    print(f"  Generating story text...")
    story = generator.generate_story(
        num_scenes=num_scenes,
        description=full_desc,
        art_style_hint=STYLE["story_art_style"],
    )
    story["animation_style"] = STYLE_KEY
    story["orientation"] = "portrait"
    story["image_model"] = "grok-image"

    # Override characters with our canonical descriptions
    story["characters"] = characters

    print(f"  Title: {story['title']}")

    # Create folder with target story ID
    folder_name = f"{target_id}_{sanitize_folder_name(story['title'])}"
    folder = os.path.join(Config.OUTPUT_DIR, folder_name)
    os.makedirs(folder, exist_ok=True)
    save_story_json(story, folder)

    # Set up image generator with original portraits
    img_gen = ImageGenerator(animation_style=STYLE)
    img_gen.image_provider = "grok-image"

    # Ensure all needed portraits exist (generates only truly missing ones like Ravi)
    ensure_portraits(characters, img_gen, folder)

    # Copy original portraits into episode folder and load into generator
    portraits_dir = os.path.join(folder, "portraits")
    os.makedirs(portraits_dir, exist_ok=True)
    for c in characters:
        name = c["name"]
        if name in shared_portrait_paths:
            dest = os.path.join(portraits_dir, f"{name.lower().replace(' ', '_')}.png")
            if not os.path.exists(dest):
                shutil.copy2(shared_portrait_paths[name], dest)
            img_gen._portrait_paths[name] = dest

    print(f"  Generating {len(story['scenes'])} scene images with original portrait references...")

    def progress_cb(scene_num, total_s, status=""):
        print(f"    Scene {scene_num}/{total_s} {status}")

    raw_paths = img_gen.generate_all_images(
        story=story, output_dir=folder, progress_callback=progress_cb,
    )

    print(f"  Overlaying text...")
    overlay = TextOverlay()
    final_paths = overlay.process_all_scenes(
        story=story, raw_image_paths=raw_paths, output_dir=folder,
    )

    print(f"  Compiling PDF...")
    pdf_name = sanitize_folder_name(story["title"]) + ".pdf"
    pdf_path = os.path.join(folder, pdf_name)
    StoryBookPDF().compile_pdf(story=story, image_paths=final_paths, output_path=pdf_path)

    # Generate web JPEGs
    for raw in raw_paths:
        web_path = raw.replace("_raw.png", "_web.jpg")
        if not os.path.exists(web_path):
            img = Image.open(raw).convert("RGB")
            img.save(web_path, "JPEG", quality=82, optimize=True)

    print(f"  DONE: {folder}")
    return folder


def main():
    skip = 0
    if "--skip" in sys.argv:
        idx = sys.argv.index("--skip")
        if idx + 1 < len(sys.argv):
            skip = int(sys.argv[idx + 1])

    remaining = EPISODES[skip:]

    print("=" * 60)
    print(f"Caleb's Adventures — generating {len(remaining)} episode(s)")
    print(f"Image provider: grok-image | Style: {STYLE_KEY}")
    print(f"Using ORIGINAL portraits from VPS episodes 1-15")
    print("=" * 60)

    load_cached_portraits()

    completed = []
    failed = []

    for i, ep in enumerate(remaining, skip + 1):
        try:
            folder = process_episode(ep, i, len(remaining) + skip)
            completed.append((ep["code"], folder))
        except Exception as e:
            print(f"  FAILED: {e}")
            traceback.print_exc()
            failed.append((ep["code"], str(e)))
        time.sleep(5)

    print(f"\n{'=' * 60}")
    print(f"BATCH COMPLETE")
    print(f"  Completed: {len(completed)}/{len(remaining)}")
    for code, folder in completed:
        print(f"    {code}: {folder}")
    if failed:
        print(f"  Failed: {len(failed)}")
        for code, err in failed:
            print(f"    {code}: {err}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

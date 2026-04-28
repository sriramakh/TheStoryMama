#!/usr/bin/env python3
"""Generate Caleb's Adventures Season 2, S02E06–S02E10.

Uses original character portraits from stories/_caleb_portraits/ (VPS originals).
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
from utils import sanitize_folder_name, save_story_json
from PIL import Image

STYLE_KEY = "animation_movie"
STYLE = Config.ANIMATION_STYLES[STYLE_KEY]

# ── Canonical character descriptions (from VPS episodes S01) ───────────
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

PORTRAITS_CACHE_DIR = os.path.join(Config.OUTPUT_DIR, "_caleb_portraits")

# ── Episodes S02E06–S02E10 ─────────────────────────────────────────────
EPISODES = [
    {
        "code": "S02E06",
        "story_id": 230,
        "title_hint": "The Farmer's Market Mix-Up",
        "description": (
            "Caleb's Adventures series episode. "
            "Sarah takes Caleb and Lily to the farmer's market on a sunny Saturday morning. "
            "Caleb is in charge of the shopping list but can't read yet — he matches the "
            "pictures Sarah drew to the fruits and vegetables. He grabs a dragon fruit "
            "thinking it's a 'dragon egg,' picks the biggest pumpkin they can barely carry "
            "between the three of them, and trades his beloved star keychain for a jar of "
            "honey from a smiling beekeeper (Jack has to come back later and trade it back). "
            "Bubbles sneaks along and steals a carrot from a stand. They come home with "
            "the wrong groceries but the best family memories. "
            "Moral: helping out means trying, even when you're still learning."
        ),
        "guests": [],
        "scenes": 12,
    },
    {
        "code": "S02E07",
        "story_id": 232,
        "title_hint": "Sofia's Dance Recital",
        "description": (
            "Caleb's Adventures series episode. "
            "Sofia is nervous about her first dance recital at the community center. "
            "Caleb and Lily make a giant 'GO SOFIA' banner with glitter, paint, and "
            "stickers — the glitter gets absolutely everywhere, in their hair, on Bubbles, "
            "on Jack's flannel. At the recital, Sofia walks onto the stage in her sparkly "
            "tutu but freezes when she sees the audience. Caleb stands up in the front row "
            "and does a silly wiggle dance with his arms flapping. Sofia laughs, starts "
            "dancing, and doesn't stop — she's the star of the show. Backstage, Sofia "
            "hugs Caleb and says 'you danced with me.' "
            "Moral: a true friend helps you find your courage."
        ),
        "guests": ["Sofia"],
        "scenes": 12,
    },
    {
        "code": "S02E08",
        "story_id": 233,
        "title_hint": "Jack's Fix-It Day",
        "description": (
            "Caleb's Adventures series episode. "
            "Jack announces he's going to fix everything in the house in one day — the "
            "wobbly kitchen shelf, the squeaky hallway door, the dripping bathroom faucet, "
            "and the stuck living room window. Caleb is his 'official assistant' and hands "
            "him tools from the toolbox — except he keeps handing the wrong ones (a spatula "
            "instead of a screwdriver, a sock instead of a rag, a banana instead of a "
            "hammer). Everything Jack fixes breaks again within minutes. Lily keeps score "
            "on a clipboard. Bubbles runs off with the tape measure. That evening, Sarah "
            "quietly fixes everything herself while Jack and Caleb nap on the couch. "
            "Moral: asking for help doesn't mean you failed — it means you're smart."
        ),
        "guests": [],
        "scenes": 12,
    },
    {
        "code": "S02E09",
        "story_id": 234,
        "title_hint": "The Backyard Bird House",
        "description": (
            "Caleb's Adventures series episode. "
            "Mila comes over with her sketchbook full of birdhouse designs — polka dots, "
            "stripes, flowers, and one that looks like a tiny castle. She and Caleb build "
            "a birdhouse from a kit Jack bought. Mila paints it with bright polka dots and "
            "rainbow stripes. Caleb hammers a nail crooked and the roof tilts. Lily adds a "
            "tiny welcome mat made from a popsicle stick and felt. They hang it in the big "
            "oak tree and sit watching, waiting... and waiting. Nothing comes. They check "
            "every hour. Bubbles barks at the tree. That night Caleb is disappointed. But "
            "the next morning he wakes up to chirping — a wren family has moved in. "
            "Moral: patience brings the sweetest rewards."
        ),
        "guests": ["Mila"],
        "scenes": 13,
    },
    {
        "code": "S02E10",
        "story_id": 235,
        "title_hint": "Aiden's Soccer Showdown",
        "description": (
            "Caleb's Adventures series episode. "
            "Aiden arrives at Caleb's backyard with his soccer ball for a 'championship match.' "
            "He teaches Caleb the basics — dribbling, passing, shooting. Caleb kicks the ball "
            "backward on his first try, trips over it on his second, and accidentally scores "
            "on his own goal on his third. Bubbles steals the ball three times and runs in "
            "circles. Lily is the referee and keeps making up rules. They invent their own "
            "version: 'puppy goals count double' and 'falling down means you get a hug.' "
            "The final score is 47 to 52 and nobody knows who won. They collapse on the "
            "grass laughing. Sarah brings orange slices like a real game. "
            "Moral: making your own rules can be more fun than winning."
        ),
        "guests": ["Aiden"],
        "scenes": 12,
    },
]

# ── Pipeline (reused from S01E16-20 script) ────────────────────────────

generator = StoryGenerator()
shared_portrait_paths: dict[str, str] = {}


def get_episode_characters(ep: dict) -> list[dict]:
    chars = list(CALEB_CHARACTERS)
    for guest_name in ep.get("guests", []):
        if guest_name in GUEST_CHARACTERS:
            chars.append(GUEST_CHARACTERS[guest_name])
    return chars


def load_cached_portraits():
    global shared_portrait_paths
    if not os.path.exists(PORTRAITS_CACHE_DIR):
        print(f"  ERROR: Portrait cache not found at {PORTRAITS_CACHE_DIR}")
        sys.exit(1)

    name_map = {
        "caleb.png": "Caleb", "lily.png": "Lily", "bubbles.png": "Bubbles",
        "jack.png": "Jack", "sarah.png": "Sarah", "nana_joy.png": "Nana Joy",
        "mila.png": "Mila", "aiden.png": "Aiden", "sofia.png": "Sofia",
        "ravi.png": "Ravi",
    }
    for fname in os.listdir(PORTRAITS_CACHE_DIR):
        if fname in name_map:
            shared_portrait_paths[name_map[fname]] = os.path.join(PORTRAITS_CACHE_DIR, fname)

    print(f"  Loaded {len(shared_portrait_paths)} portraits: {', '.join(sorted(shared_portrait_paths.keys()))}")


def ensure_portraits(characters: list[dict], img_gen: ImageGenerator, output_dir: str):
    global shared_portrait_paths
    missing = [c for c in characters if c["name"] not in shared_portrait_paths]
    if not missing:
        print(f"  All {len(characters)} portraits available from originals.")
        return

    print(f"  Generating {len(missing)} new portraits: {', '.join(c['name'] for c in missing)}")
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
    code = ep["code"]
    target_id = ep["story_id"]
    num_scenes = ep["scenes"]

    print(f"\n{'=' * 60}")
    print(f"[{index}/{total}] {code}: {ep['title_hint']}")
    print(f"{'=' * 60}")

    characters = get_episode_characters(ep)
    print(f"  Characters: {', '.join(c['name'] + ' (' + c['type'] + ')' for c in characters)}")

    char_instruction = "\n".join(
        f"- {c['name']} ({c['type']}): {c['description']}" for c in characters
    )
    full_desc = (
        f"{ep['description']}\n\n"
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
    story["characters"] = characters

    print(f"  Title: {story['title']}")

    folder_name = f"{target_id}_{sanitize_folder_name(story['title'])}"
    folder = os.path.join(Config.OUTPUT_DIR, folder_name)
    os.makedirs(folder, exist_ok=True)
    save_story_json(story, folder)

    img_gen = ImageGenerator(animation_style=STYLE)
    img_gen.image_provider = "grok-image"

    ensure_portraits(characters, img_gen, folder)

    portraits_dir = os.path.join(folder, "portraits")
    os.makedirs(portraits_dir, exist_ok=True)
    for c in characters:
        name = c["name"]
        if name in shared_portrait_paths:
            dest = os.path.join(portraits_dir, f"{name.lower().replace(' ', '_')}.png")
            if not os.path.exists(dest):
                shutil.copy2(shared_portrait_paths[name], dest)
            img_gen._portrait_paths[name] = dest

    print(f"  Generating {len(story['scenes'])} scene images with portrait references...")

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
    print(f"Caleb's Adventures Season 2 — generating {len(remaining)} episode(s)")
    print(f"Image provider: grok-image | Style: {STYLE_KEY}")
    print(f"Using original portraits from _caleb_portraits/")
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

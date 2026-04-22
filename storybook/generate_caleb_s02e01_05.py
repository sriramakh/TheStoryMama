#!/usr/bin/env python3
"""Generate Caleb's Adventures Season 2, S02E01–S02E05.

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

# ── Episodes S02E01–S02E05 ─────────────────────────────────────────────
EPISODES = [
    {
        "code": "S02E01",
        "story_id": 225,
        "title_hint": "Caleb's First Day Jitters",
        "description": (
            "Caleb's Adventures series — Season 2 premiere. "
            "Caleb starts preschool and is too nervous to let go of Sarah's hand. "
            "Lily walks him to the door and gives him her lucky daisy pin. Inside, "
            "he discovers Mila, Aiden, Sofia, and Ravi are all in his class. They do "
            "arts and crafts, sing songs, and play in the sandbox. By circle time, "
            "Caleb has forgotten he was ever scared. When Sarah picks him up, he asks "
            "if he can go again tomorrow. "
            "Moral: brave doesn't mean not scared — it means going anyway."
        ),
        "guests": ["Mila", "Aiden", "Sofia", "Ravi"],
        "scenes": 12,
    },
    {
        "code": "S02E02",
        "story_id": 226,
        "title_hint": "The Snow Day Surprise",
        "description": (
            "Caleb's Adventures series episode. "
            "The first snowfall of the year. Caleb has never seen snow stick to the ground. "
            "He wakes up and runs to the window — the whole backyard is white. Jack builds "
            "a lopsided snowman, Lily makes snow angels, Bubbles keeps trying to eat snowballs "
            "and sneezing. Sarah makes hot cocoa with marshmallows for everyone on the porch. "
            "Nana Joy arrives and knits tiny scarves for the snowman. Caleb names the snowman "
            "'Mr. Wobble' because his head keeps sliding. By evening the snow starts melting "
            "but Caleb says Mr. Wobble will come back next winter. "
            "Moral: the best surprises come when you least expect them."
        ),
        "guests": [],
        "scenes": 12,
    },
    {
        "code": "S02E03",
        "story_id": 227,
        "title_hint": "Bubbles and the Baby Duckling",
        "description": (
            "Caleb's Adventures series episode. "
            "Bubbles finds a tiny lost duckling cheeping in the backyard. Caleb and Lily "
            "decide they need to reunite it with its family at the park pond. They make a "
            "little leaf-boat for the duckling to ride in. Bubbles carries it gently in his "
            "mouth (everyone holds their breath). Along the way the duckling quacks at a "
            "butterfly, falls asleep in Caleb's hands, and waddles behind Bubbles like he's "
            "the mama duck. At the pond they find the mama duck and six siblings waiting. "
            "The duckling joins them and quacks back at Caleb as if to say thank you. "
            "Bubbles watches from the edge, tail wagging. "
            "Moral: being gentle with someone small is one of the biggest things you can do."
        ),
        "guests": [],
        "scenes": 12,
    },
    {
        "code": "S02E04",
        "story_id": 228,
        "title_hint": "Nana Joy's Mystery Box",
        "description": (
            "Caleb's Adventures series episode. "
            "Nana Joy brings a beautiful old wooden box with a brass lock and says it belonged "
            "to her mother. She's lost the tiny key years ago. Caleb, Lily, and Bubbles turn "
            "Nana Joy's cottage upside down searching — under cushions, inside teapots, behind "
            "picture frames, in the cookie jar. Bubbles digs in the garden. Lily checks the "
            "bookshelves. Caleb finally spots something shiny hanging on a faded ribbon inside "
            "Nana Joy's old gardening hat on the coat rack. It's the key! Inside the box they "
            "find hand-drawn pictures Nana Joy made as a little girl — flowers, her family, "
            "a puppy that looks just like Bubbles. Everyone is moved. "
            "Moral: the most precious treasures are the ones made with love."
        ),
        "guests": [],
        "scenes": 12,
    },
    {
        "code": "S02E05",
        "story_id": 229,
        "title_hint": "Ravi's Bug Safari",
        "description": (
            "Caleb's Adventures series episode. "
            "Ravi arrives at Caleb's house with his magnifying glass and a homemade bug "
            "journal with hand-drawn pages for each type of bug. He and Caleb go on a 'bug "
            "safari' in the backyard. They catalogue ants marching in lines (Ravi counts 47), "
            "a ladybug on a rose leaf, a fat caterpillar on the fence, a beetle under a rock, "
            "and a dragonfly by the sprinkler. Bubbles accidentally destroys the ant highway "
            "by stepping on it. Caleb and Ravi carefully rebuild it with tiny stick bridges "
            "and leaf tunnels. Lily joins and draws portraits of each bug. By the end, Ravi "
            "declares Caleb an 'Official Junior Bug Scientist.' "
            "Moral: every creature matters, no matter how small."
        ),
        "guests": ["Ravi"],
        "scenes": 13,
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

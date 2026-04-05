"""
Image Generator Module for StoryBook Generator.

Pipeline:
  1. Generate ALL images with the configured provider (MiniMax image-01 or CogView-4)
  2. Review ALL images with GPT-4o-mini vision — confidence score per image
  3. For images scoring < 0.7, regenerate with Gemini using prior scene context
"""

import os
import io
import json
import re
import time
import base64
import requests

from openai import OpenAI
from google import genai
from google.genai import types
from PIL import Image
from config import Config


class ImageGenerator:
    """Generates storybook illustrations using a primary generator + GPT-4o-mini review + Gemini fallback pipeline."""

    CONFIDENCE_THRESHOLD = 0.7

    # Map IMAGE_SIZE to Grok aspect_ratio
    SIZE_TO_GROK_ASPECT = {
        "1024x1536": "9:16",
        "1536x1024": "16:9",
        "1024x1024": "1:1",
    }

    def __init__(self, animation_style: dict | None = None):
        self.image_provider = Config.IMAGE_PROVIDER  # "gpt-image", "grok-image", "minimax", "cogview"
        self.size = Config.IMAGE_SIZE

        # Primary image generator — conditional on provider
        if self.image_provider == "cogview":
            self.glm_client = OpenAI(
                api_key=Config.GLM_API_KEY,
                base_url=Config.GLM_BASE_URL,
            )
            self.model = Config.IMAGE_MODEL
        else:
            self.minimax_token = Config.MINIMAX_API_TOKEN
            self.minimax_base_url = Config.MINIMAX_BASE_URL

        # Reviewer: GPT-4o-mini vision via OpenAI
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)

        # Grok image client (xAI — OpenAI-compatible for generate, raw requests for edit)
        self.grok_api_key = Config.GROK_API_KEY
        self.grok_client = OpenAI(api_key=Config.GROK_API_KEY, base_url="https://api.x.ai/v1") if Config.GROK_API_KEY else None

        # Fallback generator: Gemini
        self.gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)

        self.animation_style = animation_style or Config.ANIMATION_STYLES[Config.DEFAULT_ANIMATION_STYLE]

        # MiniMax subject_reference: holds scene 1's base64 image for consistency
        self._reference_image_b64: str | None = None
        # Scene 1 image path — passed as reference to gpt-image for character consistency
        self._reference_image_path: str | None = None
        # Recent scene image paths — last N scenes passed for continuity
        self._recent_scene_paths: list[str] = []
        # Character visual sheet extracted from scene 1's rendered image by GPT-4o-mini
        self._character_visual_sheet: str | None = None
        # Prior scene PIL images for Gemini visual context
        self._prior_scene_images: list = []
        # Character portraits: name -> file path (for portrait-first pipeline)
        self._portrait_paths: dict[str, str] = {}

    # ------------------------------------------------------------------ #
    #  CDN download helper (CogView returns a URL, not raw bytes)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _download_with_retry(url: str, output_path: str, retries: int = 3) -> str:
        """Download an image from a CDN URL with retry logic."""
        for attempt in range(retries):
            try:
                resp = requests.get(url, timeout=60)
                resp.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                return output_path
            except Exception as e:
                if attempt < retries - 1:
                    wait = (attempt + 1) * 3
                    print(f"   Download attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(f"Failed to download image after {retries} attempts: {e}")

    # ------------------------------------------------------------------ #
    #  Prompt builder (shared by both GLM and Gemini)
    # ------------------------------------------------------------------ #

    def _build_image_prompt(self, story: dict, scene: dict, scene_index: int) -> str:
        """Build a focused prompt for image generation."""
        scene_desc = scene["image_description"]
        relevant_chars = [
            c for c in story["characters"]
            if self._char_name_in_text(c["name"], scene_desc)
        ]
        if not relevant_chars:
            relevant_chars = story["characters"]

        character_block = "\n".join(
            f"- {c['name']} [{self._gender_prefix(c)} {c.get('type', '')}]: {c['description']}"
            for c in relevant_chars
        )

        scenes = story["scenes"]
        scene_type = ""
        if scene_index == 0:
            scene_type = "This is the OPENING scene. Make it inviting and introduce the characters clearly."
        elif scene_index == len(scenes) - 1:
            scene_type = "This is the FINAL scene. Show a warm, happy conclusion."

        style = self.animation_style

        background = scene.get("background") or story.get("setting", "")

        prompt = f"""{style['description']}

BACKGROUND: {background}

CHARACTERS (draw EXACTLY as described, {style['name']} rendering):
{character_block}

SCENE {scene['scene_number']} of {len(scenes)}:
{scene['image_description']}

{scene_type}

RULES:
- {style['image_rules']}
- Keep IDENTICAL character designs (same colors, proportions, features, clothing)
- Warm, friendly expressions appropriate for a children's book
- Suitable for a 2-3 year old child
- DO NOT include any text, words, letters, or numbers in the image"""

        return prompt

    # ------------------------------------------------------------------ #
    #  MiniMax helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _image_to_base64(image_path: str) -> str:
        """Read an image file and return a data-URI base64 string."""
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    def _analyze_reference_image(self, image_path: str, characters: list[dict]) -> str:
        """
        Analyze scene 1's rendered image with GPT-4o-mini vision to extract
        a hyper-detailed character visual sheet. This sheet is then embedded
        in every subsequent MiniMax prompt so the text reinforces the
        subject_reference image exactly.
        """
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        char_names = ", ".join(c["name"] for c in characters)
        char_hints = " | ".join(
            f"{c['name']}={c['type']}: {c['description'][:80]}"
            for c in characters
        )

        analysis_prompt = f"""You are a visual consistency expert for a children's picture book.

The characters in this story are: {char_names}
Character details (TRUST THESE for gender/species — the image may have errors): {char_hints}

Analyze this illustration and for EACH character write ONE dense line:
{'{'}Name{'}'}: {'{'}GENDER (boy/girl/male/female) from the hints above — NOT from the image{'}'}, {'{'}species/type{'}'}, {'{'}exact body/fur/skin/feather color{'}'}, {'{'}eye color{'}'}, {'{'}exact clothing colors & patterns{'}'}, {'{'}accessories{'}'}, {'{'}size/build relative to others{'}'}

CRITICAL: Use the CHARACTER DETAILS above as the source of truth for gender and species.
If the hints say "boy" or use a male name (Ethan, Max, Oliver), describe as MALE/BOY.
If the hints say "girl" or use a female name (Lily, Emma), describe as FEMALE/GIRL.
Family members (parent-child, grandparent-grandchild) must have consistent skin tones.

Then write ONE line describing the art style (lighting, color palette, rendering).

Be OBSESSIVELY precise about colors — e.g. "cerulean blue sweater with 3 golden star patches" NOT "blue sweater". Mention EVERY visible detail: spots, stripes, buttons, buckles, bows, whiskers, tail shape, ear shape, hat style.

Total response MUST be under 600 characters. No headers, no bullet points, no extra words."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_b64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=350,
            )
            sheet = response.choices[0].message.content.strip()
            # Safety: hard-cap at 600 chars
            if len(sheet) > 600:
                cut = sheet[:600].rfind(".")
                sheet = sheet[: cut + 1] if cut > 400 else sheet[:600]
            return sheet
        except Exception as e:
            print(f"   Reference image analysis failed ({e}), using story descriptions")
            # Fallback: build a condensed sheet from the story character data
            return "\n".join(
                f"{c['name']}: {c['description'][:120]}"
                for c in characters
            )[:500]

    # ------------------------------------------------------------------ #
    #  Portrait-first pipeline: generate character portraits
    # ------------------------------------------------------------------ #

    def generate_character_portraits(
        self, story: dict, output_dir: str, progress_callback=None,
    ) -> dict[str, str]:
        """Generate isolated character portraits for reference in scene generation.

        Returns dict mapping character name -> portrait file path.
        Portraits are saved to output_dir/portraits/ subfolder.
        """
        style = self.animation_style
        characters = story["characters"]
        portraits_dir = os.path.join(output_dir, "portraits")
        os.makedirs(portraits_dir, exist_ok=True)

        portrait_paths = {}

        for idx, char in enumerate(characters):
            char_name = char["name"]
            safe_name = char_name.lower().replace(" ", "_").replace("'", "")
            portrait_path = os.path.join(portraits_dir, f"{safe_name}.png")

            if progress_callback:
                progress_callback(idx + 1, len(characters), "portrait")

            gender = self._gender_prefix(char)
            if gender:
                gender += " "

            prompt = f"""Children's picture book character design sheet. {style['description']}

This is a character for an illustrated bedtime storybook for toddlers aged 2-4.

Draw this SINGLE character standing in a friendly neutral pose on a plain soft cream background.
Full body view, 3/4 angle. Cheerful, warm expression. Arms relaxed.

Character: {char_name} — {gender}{char['type']}
Appearance: {char['description']}

RULES:
- {style['image_rules']}
- This is for a wholesome children's book — warm, innocent, age-appropriate
- Draw ONLY this ONE character on a plain cream background
- Full body visible from head to feet
- Match the character description precisely
- NO text, words, letters, or numbers in the image"""

            for attempt in range(3):
                try:
                    if self.image_provider == "grok-image" and self.grok_client:
                        result = self.grok_client.images.generate(
                            model="grok-imagine-image",
                            prompt=prompt,
                            n=1,
                            response_format="b64_json",
                            extra_body={"aspect_ratio": "1:1", "resolution": "2k"},
                        )
                    else:
                        result = self.openai_client.images.generate(
                            model="gpt-image-1-mini",
                            prompt=prompt,
                            n=1,
                            size="1024x1024",
                            quality="medium",
                        )
                    image_bytes = base64.b64decode(result.data[0].b64_json)

                    # Validate portrait isn't a black/blank image
                    img = Image.open(io.BytesIO(image_bytes))
                    pixels = list(img.getdata())
                    avg_brightness = sum(sum(p[:3]) / 3 for p in pixels) / len(pixels)
                    if avg_brightness < 10:  # Nearly all-black
                        print(f"   Portrait for {char_name} is black, retrying...")
                        time.sleep(2)
                        continue

                    with open(portrait_path, "wb") as f:
                        f.write(image_bytes)
                    portrait_paths[char_name] = portrait_path
                    print(f"   Portrait: {char_name} ({char['type']}) ✓")
                    break

                except Exception as e:
                    if attempt < 2:
                        print(f"   Portrait for {char_name} failed ({e}), retrying...")
                        time.sleep(3)
                    else:
                        print(f"   Portrait for {char_name} failed after 3 attempts: {e}")

            # Rate limit
            if idx < len(characters) - 1:
                time.sleep(1.5)

        self._portrait_paths = portrait_paths
        return portrait_paths

    def _build_minimax_prompt(self, story: dict, scene: dict, scene_index: int) -> str:
        """
        Build a detail-packed prompt for MiniMax (hard limit: 1500 chars).

        Scene 1: Maximize character descriptions to establish the strongest visual baseline.
        Scenes 2+: Lead with the character visual sheet extracted from scene 1's actual
                    rendered image, then scene-specific action. The text reinforces
                    what the subject_reference image shows.
        """
        style = self.animation_style
        scenes = story["scenes"]
        all_chars = story["characters"]

        background = scene.get("background") or story.get("setting", "")

        if scene_index == 0:
            # ── Scene 1: establish the visual baseline ──
            # Include ALL characters with full descriptions
            character_block = "\n".join(
                f"- {c['name']} [{self._gender_prefix(c)} {c['type']}]: {c['description']}"
                for c in all_chars
            )

            prompt = f"""{style['description']}

BACKGROUND: {background}

CHARACTERS — draw EXACTLY as described, every detail matters:
{character_block}

SCENE 1/{len(scenes)}: {scene['image_description']}

CRITICAL: Each character MUST match their description PRECISELY — correct species, exact colors, exact clothing, exact proportions. {style['image_rules']}. No text/letters in image. Children's book for ages 2-3."""

        else:
            # ── Scenes 2+: consistency-focused, anchored to scene 1 ──
            visual_sheet = self._character_visual_sheet or "\n".join(
                f"{c['name']}: {c['description'][:100]}" for c in all_chars
            )

            scene_type = ""
            if scene_index == len(scenes) - 1:
                scene_type = " This is the FINAL scene — show a warm, happy conclusion."

            prompt = f"""CONTINUITY: Draw the EXACT SAME characters as the reference image. Same species, same colors, same clothing, same proportions, same art style. Do NOT change any character's appearance.

CHARACTER SHEET (match EXACTLY):
{visual_sheet}

SCENE {scene['scene_number']}/{len(scenes)}: {scene['image_description']}{scene_type}

{style['image_rules']}. No text in image. Children's book for ages 2-3."""

        # Hard-truncate at sentence boundary (1500 char API limit)
        if len(prompt) > 1500:
            truncated = prompt[:1500]
            last_period = truncated.rfind(".")
            if last_period > 1000:
                prompt = truncated[: last_period + 1]
            else:
                prompt = truncated

        return prompt

    # ------------------------------------------------------------------ #
    #  Phase 1a: Generate a single scene image with MiniMax image-01
    # ------------------------------------------------------------------ #

    def _generate_with_minimax(
        self,
        story: dict,
        scene: dict,
        scene_index: int,
        output_path: str,
        retry_count: int = 3,
    ) -> str:
        """Generate an illustration for a single scene using MiniMax image-01."""
        prompt = self._build_minimax_prompt(story, scene, scene_index)

        # Map IMAGE_SIZE to MiniMax aspect ratio
        aspect_map = {
            "1024x1024": "1:1",
            "1024x1536": "2:3",
            "1536x1024": "3:2",
            "768x1024": "3:4",
            "1024x768": "4:3",
        }
        aspect_ratio = aspect_map.get(self.size, "2:3")

        url = f"{self.minimax_base_url}/image_generation"
        headers = {
            "Authorization": f"Bearer {self.minimax_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "image-01",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": 1,
        }

        # For scenes after the first, pass scene 1's image as subject_reference
        if scene_index > 0 and self._reference_image_b64:
            payload["subject_reference"] = [
                {"type": "character", "image_file": self._reference_image_b64}
            ]

        for attempt in range(retry_count):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=120)
                resp.raise_for_status()
                data = resp.json()

                status_code = data.get("base_resp", {}).get("status_code", -1)
                if status_code != 0:
                    status_msg = data.get("base_resp", {}).get("status_msg", "unknown error")
                    raise RuntimeError(f"MiniMax API error {status_code}: {status_msg}")

                image_url = data["data"]["image_urls"][0]
                self._download_with_retry(image_url, output_path)

                # After scene 1 succeeds: store reference image + analyze it
                if scene_index == 0:
                    self._reference_image_b64 = self._image_to_base64(output_path)
                    print("   Analyzing scene 1 for character visual consistency...")
                    self._character_visual_sheet = self._analyze_reference_image(
                        output_path, story["characters"]
                    )
                    if self._character_visual_sheet:
                        print(f"   Character sheet extracted ({len(self._character_visual_sheet)} chars)")

                return output_path

            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   MiniMax attempt {attempt+1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(
                        f"Failed to generate image for scene {scene['scene_number']} "
                        f"after {retry_count} attempts: {e}"
                    )

    # ------------------------------------------------------------------ #
    #  Phase 1b: Generate a single scene image with CogView-4 (GLM)
    # ------------------------------------------------------------------ #

    def _generate_with_cogview(
        self,
        story: dict,
        scene: dict,
        scene_index: int,
        output_path: str,
        retry_count: int = 3,
    ) -> str:
        """Generate an illustration for a single scene using CogView-4."""
        prompt = self._build_image_prompt(story, scene, scene_index)

        if len(prompt) > 16000:
            prompt = prompt[:16000] + "..."

        for attempt in range(retry_count):
            try:
                response = self.glm_client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    size=self.size,
                )

                image_url = response.data[0].url
                self._download_with_retry(image_url, output_path)
                return output_path

            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   Attempt {attempt+1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(
                        f"Failed to generate image for scene {scene['scene_number']} "
                        f"after {retry_count} attempts: {e}"
                    )

    # ------------------------------------------------------------------ #
    #  Phase 1c: Generate a single scene image with Gemini Flash
    # ------------------------------------------------------------------ #

    # Map IMAGE_SIZE to Gemini aspect ratio string.
    _GEMINI_ASPECT_MAP = {
        "1024x1024": "1:1",
        "1024x1536": "2:3",
        "1536x1024": "3:2",
        "768x1024": "3:4",
        "1024x768": "4:3",
    }

    _GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"

    def _generate_with_gemini_primary(
        self,
        story: dict,
        scene: dict,
        scene_index: int,
        output_path: str,
        retry_count: int = 3,
    ) -> str:
        """
        Generate an illustration using Gemini Flash with prior scene images
        as visual context for character consistency.
        """
        prompt = self._build_image_prompt(story, scene, scene_index)

        # Build contents: prior images for visual context, then text prompt
        contents = []
        if scene_index > 0 and self._prior_scene_images:
            # Always include scene 1 (character anchor)
            contents.append(self._prior_scene_images[0])
            # Also include the most recent scene if different from scene 1
            if len(self._prior_scene_images) >= 2:
                contents.append(self._prior_scene_images[-1])
            context_prefix = (
                "The images above are previous scenes from this children's storybook. "
                "Generate the next scene with the EXACT SAME character designs — same species, "
                "same colors, same clothing, same proportions, same face shapes, same art style. "
                "Do NOT change any character's appearance.\n\n"
            )
            contents.append(context_prefix + prompt)
        else:
            contents.append(prompt)

        aspect_ratio = self._GEMINI_ASPECT_MAP.get(self.size, "2:3")

        for attempt in range(retry_count):
            try:
                response = self.gemini_client.models.generate_content(
                    model=self._GEMINI_IMAGE_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                        ),
                    ),
                )

                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        image.save(output_path)

                        # Store PIL image for future scene context
                        self._prior_scene_images.append(Image.open(output_path))
                        return output_path

                raise RuntimeError("No image returned in Gemini response")

            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   Gemini attempt {attempt+1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(
                        f"Failed to generate image for scene {scene['scene_number']} "
                        f"after {retry_count} attempts: {e}"
                    )

    # ------------------------------------------------------------------ #
    #  Phase 1d: Generate a single scene image with GPT-image-1
    # ------------------------------------------------------------------ #

    @staticmethod
    def _char_name_in_text(name: str, text: str) -> bool:
        """Check if a character name appears in text using word boundary matching.
        Prevents 'Max' from matching 'maximum' or 'Sam' from matching 'same'."""
        pattern = r'\b' + re.escape(name.lower()) + r'\b'
        return bool(re.search(pattern, text.lower()))

    @staticmethod
    def _gender_prefix(char: dict) -> str:
        """Extract explicit gender prefix from character type/description for image prompts."""
        ctype = char.get("type", "").lower()
        desc = char.get("description", "").lower()
        name = char.get("name", "").lower()

        # Male indicators in type field (word boundary matching)
        male_type_words = ["boy", "male", "man", "father", "dad", "grandfather", "grandpa",
                           "brother", "son", "uncle", "prince", "king", "husband", "toddler boy"]
        female_type_words = ["girl", "female", "woman", "mother", "mom", "grandmother", "grandma",
                             "sister", "daughter", "aunt", "princess", "queen", "wife", "toddler girl"]

        for w in male_type_words:
            if w in ctype:
                return "MALE"
        for w in female_type_words:
            if w in ctype:
                return "FEMALE"

        # Check description for pronoun/gender cues
        male_desc_patterns = [r'\bboy\b', r'\b he \b', r'\bhis \b', r'\bmale\b', r'\bson\b',
                              r'\bfather\b', r'\bdad\b', r'\bbrother\b', r'\bgrandfather\b', r'\bgrandpa\b']
        female_desc_patterns = [r'\bgirl\b', r'\bshe \b', r'\bher \b', r'\bfemale\b', r'\bdaughter\b',
                                r'\bmother\b', r'\bmom\b', r'\bsister\b', r'\bgrandmother\b', r'\bgrandma\b']

        for p in male_desc_patterns:
            if re.search(p, desc):
                return "MALE"
        for p in female_desc_patterns:
            if re.search(p, desc):
                return "FEMALE"

        # Name-based gender detection — only for human-like characters
        animal_indicators = ["puppy", "dog", "cat", "kitten", "bunny", "rabbit", "bear", "fox",
                             "owl", "bird", "fish", "turtle", "mouse", "squirrel", "deer", "frog",
                             "duck", "hen", "rooster", "pig", "cow", "horse", "pony", "otter",
                             "beaver", "hedgehog", "penguin", "parrot", "hamster", "chipmunk",
                             "raccoon", "wolf", "lion", "tiger", "elephant", "monkey", "seal"]
        is_animal = any(a in ctype for a in animal_indicators)
        if is_animal:
            return ""  # Don't assign human gender to animals

        boy_names = {
            "ethan", "max", "oliver", "james", "noah", "liam", "finn", "leo", "jack", "sam",
            "ben", "tom", "lucas", "henry", "alex", "aiden", "mason", "logan", "jacob", "ryan",
            "daniel", "david", "eli", "owen", "caleb", "nathan", "dylan", "connor", "tyler",
            "charlie", "oscar", "felix", "theo", "archie", "teddy", "alfie", "jasper", "ravi",
            "arjun", "kai", "mateo", "miguel", "omar", "yusuf", "adam", "isaac", "peter",
            "luke", "mark", "paul", "sean", "kevin", "josh", "ian", "cole", "blake", "chase",
        }
        girl_names = {
            "lily", "emma", "sophia", "mia", "ella", "chloe", "aria", "luna", "zoe", "ruby",
            "ivy", "lila", "maya", "nora", "eva", "grace", "abby", "bella", "daisy", "rosie",
            "poppy", "willow", "hazel", "violet", "iris", "flora", "stella", "clara", "alice",
            "hannah", "emily", "sarah", "anna", "priya", "aanya", "mei", "sakura", "yuki",
            "olivia", "isabella", "amelia", "charlotte", "harper", "evelyn", "layla", "riley",
            "scarlett", "penelope", "ellie", "lucy", "leah", "quinn", "sage", "fern", "wren",
        }
        if name in boy_names:
            return "MALE"
        if name in girl_names:
            return "FEMALE"
        return ""

    def _build_gpt_image_prompt(self, story: dict, scene: dict, scene_index: int) -> str:
        """
        Build a detailed prompt for gpt-image-1-mini. No character limit,
        so we can include exhaustive character details.
        """
        style = self.animation_style
        scenes = story["scenes"]
        all_chars = story["characters"]

        character_block = "\n".join(
            f"- {c['name']} [{self._gender_prefix(c)} {c['type']}]: {c['description']}"
            for c in all_chars
        )

        scene_type = ""
        if scene_index == 0:
            scene_type = "This is the OPENING scene. Make it inviting and introduce the characters clearly."
        elif scene_index == len(scenes) - 1:
            scene_type = "This is the FINAL scene. Show a warm, happy conclusion."

        background = scene.get("background") or story.get("setting", "")

        # Determine which characters appear in this scene.
        # Only include characters who are EXPLICITLY named in the image_description.
        # For scene 1: include all characters (establishment shot).
        combined_text = scene.get("image_description", "") + " " + scene.get("text", "")

        scene_chars = []
        absent_chars = []

        if scene_index == 0:
            # Scene 1: all characters present for establishment
            scene_chars = list(all_chars)
        else:
            for c in all_chars:
                # Use word-boundary matching to avoid substring false positives
                if self._char_name_in_text(c["name"], combined_text):
                    scene_chars.append(c)
                else:
                    absent_chars.append(c)

            # If no characters detected (generic text like "everyone"), include all
            if not scene_chars:
                scene_chars = list(all_chars)

        num_chars_in_scene = len(scene_chars)

        if scene_index == 0:
            prompt = f"""{style['description']}

BACKGROUND: {background}

CHARACTERS — draw EVERY character listed below EXACTLY as described. Each character's species, body colors, eye color, clothing colors, accessories, and proportions must match their description PRECISELY:
{character_block}

SCENE {scene['scene_number']} of {len(scenes)}:
{scene['image_description']}

{scene_type}

RULES:
- {style['image_rules']}
- Draw EXACTLY {num_chars_in_scene} characters in this scene — no more, no less
- Keep IDENTICAL character designs (same colors, proportions, features, clothing)
- Warm, friendly expressions appropriate for a children's book
- Suitable for a 2-4 year old child
- DO NOT include any text, words, letters, or numbers in the image"""

        else:
            # Scenes 2+: lead with character visual sheet from scene 1 analysis
            visual_sheet = self._character_visual_sheet or ""
            sheet_section = ""
            if visual_sheet:
                sheet_section = f"""
IMPORTANT — CHARACTER VISUAL REFERENCE (how each character ACTUALLY looks — match this EXACTLY):
{visual_sheet}

"""
            # Build a block describing only the characters present in this scene
            present_block = "\n".join(
                f"- {c['name']} [{self._gender_prefix(c)} {c['type']}]: {c['description']}"
                for c in scene_chars
            )

            # Build exclude list
            absent_names = [c["name"] for c in absent_chars]
            exclude_rule = ""
            if absent_names:
                exclude_rule = f"\n- DO NOT draw these characters (they are NOT in this scene): {', '.join(absent_names)}"

            prompt = f"""{style['description']}

{sheet_section}INCLUDE — draw ONLY these characters with IDENTICAL appearance (same face, skin/fur color, clothing):
{present_block}

BACKGROUND: {background}

SCENE {scene['scene_number']} of {len(scenes)}:
{scene['image_description']}

{scene_type}

COMPOSITION — THIS IS CRITICAL:
- Create a UNIQUE composition for this scene — different camera angle, different character positions
- Characters should be in DIFFERENT poses and positions than previous scenes
- Vary character expressions to match the specific action described
- Use dynamic framing: close-up, wide shot, side view, over-the-shoulder — NOT always centered front-facing
- The background MUST be visually distinct and match the specific location described

RULES:
- {style['image_rules']}
- Draw EXACTLY {num_chars_in_scene} characters in this scene — no more, no less{exclude_rule}
- Character APPEARANCE must match the visual reference (same face, colors, clothing)
- But character POSE, POSITION, and EXPRESSION must be unique to THIS scene
- Warm, friendly expressions appropriate for a children's book
- Suitable for a 2-4 year old child
- DO NOT include any text, words, letters, or numbers in the image"""

        return prompt

    def _get_scene_portrait_files(self, story: dict, scene: dict, scene_index: int) -> list[str]:
        """Get portrait file paths for characters present in this scene."""
        if not self._portrait_paths:
            return []

        all_chars = story["characters"]
        combined_text = scene.get("image_description", "") + " " + scene.get("text", "")

        if scene_index == 0:
            scene_chars = all_chars
        else:
            scene_chars = [c for c in all_chars if self._char_name_in_text(c["name"], combined_text)]
            if not scene_chars:
                scene_chars = all_chars

        return [self._portrait_paths[c["name"]] for c in scene_chars if c["name"] in self._portrait_paths]

    def _generate_with_gpt_image(
        self,
        story: dict,
        scene: dict,
        scene_index: int,
        output_path: str,
        retry_count: int = 3,
    ) -> str:
        """Generate an illustration for a single scene using gpt-image-1-mini.
        Uses character portraits as reference via images.edit() for consistency."""
        prompt = self._build_gpt_image_prompt(story, scene, scene_index)

        # Get portrait references for characters in this scene
        portrait_file_paths = self._get_scene_portrait_files(story, scene, scene_index)

        for attempt in range(retry_count):
            portrait_files = []
            try:
                if portrait_file_paths:
                    # Portrait-first pipeline: use images.edit() with character portraits
                    portrait_files = [open(p, "rb") for p in portrait_file_paths]

                    # Prepend children's book context to the prompt for moderation safety
                    safe_prompt = f"Illustrated children's bedtime storybook scene for toddlers aged 2-4.\nThe attached reference images show each character's appearance for this children's book. Match their appearance PRECISELY but draw them in new poses.\n\n{prompt}"

                    result = self.openai_client.images.edit(
                        model="gpt-image-1-mini",
                        image=portrait_files,
                        prompt=safe_prompt,
                        size=self.size,
                        quality="medium",
                    )
                else:
                    # Fallback: no portraits available, use generate()
                    result = self.openai_client.images.generate(
                        model="gpt-image-1-mini",
                        prompt=prompt,
                        n=1,
                        size=self.size,
                        quality="medium",
                    )

                image_bytes = base64.b64decode(result.data[0].b64_json)
                with open(output_path, "wb") as f:
                    f.write(image_bytes)

                # Track recent scene paths for continuity references
                self._recent_scene_paths.append(output_path)

                return output_path

            except Exception as e:
                if "moderation" in str(e).lower() or "safety" in str(e).lower():
                    # Moderation block — retry without portraits as fallback
                    if attempt < retry_count - 1:
                        print(f"   Moderation block on scene {scene['scene_number']}, retrying...")
                        time.sleep(3)
                        continue
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   GPT-image attempt {attempt+1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(
                        f"Failed to generate image for scene {scene['scene_number']} "
                        f"after {retry_count} attempts: {e}"
                    )
            finally:
                for f in portrait_files:
                    f.close()

    # ------------------------------------------------------------------ #
    #  Phase 1e: Generate a single scene with Grok Imagine (xAI Aurora)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _create_portrait_sheet(image_paths: list[str], max_size: int = 512) -> bytes:
        """Combine multiple character portraits into a single reference sheet image.
        Grok edit only supports 1-2 images, so we merge all portraits into one grid."""
        portraits = []
        for p in image_paths:
            img = Image.open(p).convert("RGB")
            # Resize each portrait to fit in grid
            cell_size = max_size // max(2, len(image_paths))
            img = img.resize((cell_size, cell_size), Image.LANCZOS)
            portraits.append(img)

        # Arrange in a row
        total_w = sum(p.width for p in portraits)
        max_h = max(p.height for p in portraits)
        sheet = Image.new("RGB", (total_w, max_h), (245, 237, 224))
        x = 0
        for p in portraits:
            sheet.paste(p, (x, 0))
            x += p.width

        buf = io.BytesIO()
        sheet.save(buf, format="JPEG", quality=80)
        return buf.getvalue()

    def _grok_edit_image(self, prompt: str, image_paths: list[str], aspect_ratio: str = "2:3") -> bytes:
        """Call Grok images/edits endpoint with reference images via raw HTTP.
        Merges all portraits into a single reference sheet (Grok only supports 1-2 images)."""
        if len(image_paths) > 1:
            # Combine all portraits into one reference sheet
            sheet_bytes = self._create_portrait_sheet(image_paths)
            b64 = base64.b64encode(sheet_bytes).decode("utf-8")
            image_data = {"url": f"data:image/jpeg;base64,{b64}", "type": "image_url"}
        else:
            with open(image_paths[0], "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            ext = "png" if image_paths[0].endswith(".png") else "jpeg"
            image_data = {"url": f"data:image/{ext};base64,{b64}", "type": "image_url"}

        body = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "n": 1,
            "response_format": "b64_json",
            "image": image_data,
        }

        resp = requests.post(
            "https://api.x.ai/v1/images/edits",
            headers={
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return base64.b64decode(data["data"][0]["b64_json"])

    def _extract_visual_sheet_from_portraits(self) -> str:
        """Extract a text visual sheet from character portraits using GPT-4o-mini vision.
        Called once after portraits are generated — gives Grok a detailed text reference."""
        if not self._portrait_paths:
            return ""

        sheets = []
        for name, path in self._portrait_paths.items():
            if not os.path.exists(path):
                continue
            try:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                resp = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Describe this children's book character '{name}' in ONE dense line. Include: exact species/type, gender, skin/fur color, eye color, hair style, clothing colors & patterns, accessories, size/build. Be obsessively precise about colors."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "low"}}
                        ]
                    }],
                    max_tokens=150,
                )
                sheets.append(f"{name}: {resp.choices[0].message.content.strip()}")
            except Exception as e:
                print(f"   Visual sheet for {name} failed: {e}")
                continue

        return "\n".join(sheets)

    def _generate_with_grok_image(
        self,
        story: dict,
        scene: dict,
        scene_index: int,
        output_path: str,
        retry_count: int = 3,
    ) -> str:
        """Generate a scene image using Grok Imagine (Aurora) model.
        Always uses images.generate() for native aspect ratio support.
        Character consistency via text visual sheet extracted from portraits."""
        prompt = self._build_gpt_image_prompt(story, scene, scene_index)
        aspect_ratio = self.SIZE_TO_GROK_ASPECT.get(self.size, "9:16")

        # Extract visual sheet from portraits on first scene (one-time cost)
        if scene_index == 0 and self._portrait_paths and not self._character_visual_sheet:
            print("   Extracting visual sheet from portraits...")
            self._character_visual_sheet = self._extract_visual_sheet_from_portraits()
            if self._character_visual_sheet:
                print(f"   Visual sheet ready ({len(self._character_visual_sheet)} chars)")

        # Inject visual sheet into prompt
        sheet_section = ""
        if self._character_visual_sheet:
            sheet_section = f"\nCHARACTER VISUAL REFERENCE (match EXACTLY):\n{self._character_visual_sheet}\n"

        safe_prompt = f"Illustrated children's bedtime storybook scene for toddlers aged 2-4.\n{sheet_section}\n{prompt}"

        for attempt in range(retry_count):
            try:
                result = self.grok_client.images.generate(
                    model="grok-imagine-image",
                    prompt=safe_prompt,
                    n=1,
                    response_format="b64_json",
                    extra_body={"aspect_ratio": aspect_ratio, "resolution": "2k"},
                )
                image_bytes = base64.b64decode(result.data[0].b64_json)

                with open(output_path, "wb") as f:
                    f.write(image_bytes)

                self._recent_scene_paths.append(output_path)
                return output_path

            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   Grok-image attempt {attempt+1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(
                        f"Failed to generate image for scene {scene['scene_number']} "
                        f"after {retry_count} attempts: {e}"
                    )

    # ------------------------------------------------------------------ #
    #  Phase 1: Dispatcher — route to the configured provider
    # ------------------------------------------------------------------ #

    def generate_scene_image(
        self,
        story: dict,
        scene: dict,
        scene_index: int,
        output_path: str,
        retry_count: int = 3,
    ) -> str:
        """Generate an illustration for a single scene using the configured provider."""
        if self.image_provider == "minimax":
            return self._generate_with_minimax(story, scene, scene_index, output_path, retry_count)
        elif self.image_provider == "gemini":
            return self._generate_with_gemini_primary(story, scene, scene_index, output_path, retry_count)
        elif self.image_provider == "grok-image":
            return self._generate_with_grok_image(story, scene, scene_index, output_path, retry_count)
        elif self.image_provider == "gpt-image":
            return self._generate_with_gpt_image(story, scene, scene_index, output_path, retry_count)
        else:
            return self._generate_with_cogview(story, scene, scene_index, output_path, retry_count)

    # ------------------------------------------------------------------ #
    #  Phase 2: Review images with GPT-4o-mini vision
    # ------------------------------------------------------------------ #

    def _review_images(
        self,
        image_scene_pairs: list[tuple[str, dict]],
        characters: list[dict],
    ) -> dict[int, float]:
        """
        Review each generated image with GPT-4o-mini vision.

        Args:
            image_scene_pairs: List of (image_path, scene_dict) tuples
            characters: Full character list from the story

        Returns:
            dict mapping scene_number -> confidence (0.0-1.0)
        """
        character_block = "\n".join(
            f"- {c['name']} ({c['type']}): {c['description']}"
            for c in characters
        )

        scores = {}
        for image_path, scene in image_scene_pairs:
            scene_num = scene["scene_number"]
            try:
                with open(image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")

                review_prompt = f"""You are reviewing an illustration for a children's storybook.

EXPECTED CHARACTERS:
{character_block}

SCENE DESCRIPTION:
{scene['image_description']}

Look at this image and rate your confidence (0.0 to 1.0) that:
1. All expected characters are present with the correct species
2. No unexpected/hallucinated characters dominate the scene
3. The scene matches the description

Respond ONLY with JSON: {{"confidence": 0.85, "reason": "short note"}}"""

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": review_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_b64}",
                                        "detail": "low",
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=150,
                )

                raw = response.choices[0].message.content.strip()
                # Parse JSON from the response (handle markdown fences)
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                result = json.loads(raw)
                confidence = float(result.get("confidence", 1.0))
                reason = result.get("reason", "")
                scores[scene_num] = confidence
                print(f"   Scene {scene_num}: confidence={confidence:.2f} — {reason}")

            except Exception as e:
                # If review fails, don't block — assume it's fine
                print(f"   Scene {scene_num}: review failed ({e}), defaulting to 1.0")
                scores[scene_num] = 1.0

        return scores

    # ------------------------------------------------------------------ #
    #  Phase 3: Regenerate low-confidence images with Gemini
    # ------------------------------------------------------------------ #

    # Map IMAGE_SIZE to a Gemini-compatible aspect ratio string.
    _ASPECT_RATIO_MAP = {
        "1024x1024": "1:1",
        "1024x1536": "2:3",
        "1536x1024": "3:2",
        "768x1024": "3:4",
        "1024x768": "4:3",
    }

    def _regenerate_with_gemini(
        self,
        story: dict,
        scene: dict,
        scene_index: int,
        output_path: str,
        all_image_paths: list[str],
        retry_count: int = 3,
    ) -> str:
        """
        Regenerate an image using Gemini with up to 2 prior scene images as context.

        Args:
            story: Full story data
            scene: The scene to regenerate
            scene_index: Index of this scene (0-based)
            output_path: Where to save the new image
            all_image_paths: List of all current image paths (ordered by scene)
            retry_count: Number of retries

        Returns:
            str: Path to the saved image
        """
        # Collect up to 2 prior scene images for visual context
        prior_images = []
        for offset in [2, 1]:
            idx = scene_index - offset
            if 0 <= idx < len(all_image_paths) and os.path.exists(all_image_paths[idx]):
                try:
                    img = Image.open(all_image_paths[idx])
                    prior_images.append(img)
                except Exception:
                    pass

        # Build the text prompt
        scene_prompt = self._build_image_prompt(story, scene, scene_index)
        context_text = (
            "The images above are previous scenes from this children's storybook. "
            "Generate the next scene matching the SAME character designs and art style.\n\n"
            + scene_prompt
        )

        # Assemble contents: prior images first, then the text prompt
        contents = []
        for img in prior_images:
            contents.append(img)
        contents.append(context_text)

        aspect_ratio = self._ASPECT_RATIO_MAP.get(self.size, "2:3")

        for attempt in range(retry_count):
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                        ),
                    ),
                )

                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        image.save(output_path)
                        return output_path

                raise RuntimeError("No image returned in Gemini response")

            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   Gemini attempt {attempt+1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(
                        f"Gemini fallback failed for scene {scene['scene_number']} "
                        f"after {retry_count} attempts: {e}"
                    )

    # ------------------------------------------------------------------ #
    #  Orchestrator: generate all images with the full pipeline
    # ------------------------------------------------------------------ #

    def generate_all_images(
        self,
        story: dict,
        output_dir: str,
        progress_callback=None,
    ) -> list[str]:
        """
        Generate illustrations for all scenes using the full pipeline:
          1. Generate all with CogView-4
          2. Review all with GPT-4o-mini
          3. Regenerate low-confidence images with Gemini

        Args:
            story: The structured story data
            output_dir: Directory to save images
            progress_callback: Optional callback(scene_num, total, status)

        Returns:
            list[str]: Paths to all generated images in order
        """
        os.makedirs(output_dir, exist_ok=True)
        image_paths = []
        total = len(story["scenes"])

        # Reset per-story state (critical for batch mode — prevent cross-story bleeding)
        self._reference_image_b64 = None
        self._reference_image_path = None
        self._recent_scene_paths = []
        self._character_visual_sheet = None
        self._prior_scene_images = []
        self._portrait_paths = {}

        # ── Phase 0: Generate character portraits (for gpt-image and grok-image providers) ──
        if self.image_provider in ("gpt-image", "grok-image") and story.get("characters"):
            print(f"  Generating {len(story['characters'])} character portraits...")
            self.generate_character_portraits(story, output_dir, progress_callback)

        # ── Phase 1: Generate all images ──
        for i, scene in enumerate(story["scenes"]):
            scene_num = scene["scene_number"]
            filename = f"scene_{scene_num:02d}_raw.png"
            output_path = os.path.join(output_dir, filename)

            if progress_callback:
                progress_callback(scene_num, total, "generating")

            path = self.generate_scene_image(story, scene, i, output_path)
            image_paths.append(path)

            if progress_callback:
                progress_callback(scene_num, total, "done")

            # Rate limit: 50 images/min = 1.2s minimum gap. Use 1.5s for safety.
            if i < total - 1:
                time.sleep(1.5)

        # ── Phase 2: Review all images with GPT-4o-mini ──
        if progress_callback:
            progress_callback(1, total, "reviewing")

        image_scene_pairs = list(zip(image_paths, story["scenes"]))
        scores = self._review_images(image_scene_pairs, story["characters"])

        # ── Phase 3: Enhanced QC — score only, no auto-regeneration ──
        # Scores are saved to qc_scores.json for manual review in the QC studio
        if progress_callback:
            progress_callback(1, total, "quality checking")

        self._qc_score_all(story, image_paths, output_dir, progress_callback)

        return image_paths

    def _qc_score_all(
        self,
        story: dict,
        image_paths: list[str],
        output_dir: str,
        progress_callback=None,
    ) -> None:
        """
        Score every scene for character consistency and background accuracy.
        Saves scores to qc_scores.json in the story directory — no auto-regeneration.
        Low scores can be fixed manually via the QC studio at :8001/qc.
        """
        total = len(story["scenes"])
        characters = story["characters"]

        char_block = "\n".join(
            f"- {c['name']} ({c['type']}): {c['description']}"
            for c in characters
        )

        # Build reference from last 2-3 scenes
        ref_indices = list(range(max(0, total - 3), total))
        ref_descriptions = self._extract_reference_from_scenes(
            [image_paths[i] for i in ref_indices], characters
        )

        qc_results = []

        for i, scene in enumerate(story["scenes"]):
            scene_num = scene["scene_number"]

            if progress_callback:
                progress_callback(scene_num, total, "qc checking")

            score = self._qc_score_scene(
                image_paths[i], scene, char_block, ref_descriptions
            )

            status = "passed" if score >= 0.75 else "needs_review"
            print(f"   Scene {scene_num}: {status} ({score:.2f})")

            qc_results.append({
                "scene_number": scene_num,
                "score": round(score, 2),
                "status": status,
            })

        # Save scores to file for QC studio
        qc_path = os.path.join(output_dir, "qc_scores.json")
        with open(qc_path, "w") as f:
            json.dump({"story": story.get("title", ""), "scores": qc_results}, f, indent=2)

        passed = sum(1 for r in qc_results if r["status"] == "passed")
        needs_review = sum(1 for r in qc_results if r["status"] == "needs_review")
        print(f"\n   QC: {passed} passed, {needs_review} need review (scores saved to qc_scores.json)")

    def _extract_reference_from_scenes(
        self, ref_image_paths: list[str], characters: list[dict]
    ) -> str:
        """Extract character appearance reference from the last 2-3 scene images."""
        descriptions = []
        for path in ref_image_paths:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()

                char_names = ", ".join(c["name"] for c in characters)
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": (
                                f"Describe each character ({char_names}) in this image in ONE line each. "
                                "Include: exact skin/fur color, hair/fur style, eye color, clothing with exact colors, accessories. "
                                "Be extremely precise about colors and features."
                            )},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}", "detail": "low"}}
                        ]
                    }],
                    max_tokens=300,
                )
                descriptions.append(response.choices[0].message.content.strip())
            except Exception as e:
                print(f"   Reference extraction failed for {path}: {e}")

        return "\n---\n".join(descriptions) if descriptions else ""

    def _qc_score_scene(
        self, image_path: str, scene: dict, char_block: str, ref_descriptions: str
    ) -> float:
        """
        Score a scene image on two criteria:
        1. Character consistency (face, dress, appearance vs reference)
        2. Background accuracy (does setting match scene description?)
        Returns average score 0.0-1.0.
        """
        try:
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()

            prompt = f"""You are a strict QC reviewer for a children's picture book.

CHARACTERS IN THIS STORY:
{char_block}

CHARACTER APPEARANCE FROM REFERENCE SCENES (must match exactly):
{ref_descriptions}

SCENE {scene.get('scene_number', '?')} DESCRIPTION:
Background: {scene.get('background', '')}
Action: {scene.get('image_description', '')}
Text: {scene.get('text', '')}

Look at this image and score TWO criteria (0.0 to 1.0 each):

1. CHARACTER_CONSISTENCY: Do the characters match the reference appearance exactly?
   Score 1.0 if skin/fur color, hair, clothing, accessories all match.
   Score 0.5 if minor differences (slightly different shade).
   Score 0.0 if major differences (wrong skin color, wrong species, wrong clothing).

2. BACKGROUND_ACCURACY: Does the background/setting match the scene description?
   Score 1.0 if the setting clearly matches.
   Score 0.5 if partially matches.
   Score 0.0 if completely wrong setting.

Respond ONLY with JSON:
{{"character_consistency": 0.85, "background_accuracy": 0.90, "issues": "brief note or empty string"}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}", "detail": "low"}}
                    ]
                }],
                max_tokens=200,
            )

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            result = json.loads(raw[start:end])

            char_score = float(result.get("character_consistency", 0.5))
            bg_score = float(result.get("background_accuracy", 0.5))
            issues = result.get("issues", "")

            avg = (char_score + bg_score) / 2

            if issues:
                print(f"     char={char_score:.2f} bg={bg_score:.2f} avg={avg:.2f} — {issues}")

            return avg

        except Exception as e:
            print(f"     QC scoring failed: {e}")
            return 0.5  # Don't block on review failure

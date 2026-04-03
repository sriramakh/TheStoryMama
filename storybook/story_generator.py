"""
Story Generator Module for StoryBook Generator.
Uses OpenAI GPT-4o-mini (via OpenAI API) to generate structured children's stories.
"""

import json
import random
import re
from openai import OpenAI
from config import Config


# --------------------------------------------------------------------------- #
#  System prompt — the "children's story author" persona
# --------------------------------------------------------------------------- #
STORY_SYSTEM_PROMPT = """You are a world-class children's picture book author whose stories have been
published by the most prestigious children's publishers. You write for children aged 2-4 years old.
Your stories are the kind that parents love reading aloud and children beg to hear again and again.

YOUR CRAFT:
You understand that a great children's story needs three things: characters children fall in love
with, a plot that builds genuine wonder and surprise, and emotional moments that resonate with
both the child AND the parent reading aloud. You write stories that make children gasp, giggle,
and feel safe — sometimes all on the same page.

WORLD-BUILDING RULES:
1. ALL characters in a story MUST share a believable world. This is NON-NEGOTIABLE:
   - If the story is set on land (forest, meadow, village, farm), ALL characters must be
     land-dwelling creatures: woodland animals, farm animals, birds, insects, humans, etc.
     NEVER include ocean creatures (fish, jellyfish, octopus, seahorse, whale) in a land story.
   - If the story is set in the ocean or underwater, ALL characters must be aquatic:
     fish, seahorse, octopus, dolphin, turtle, crab, starfish, whale, etc.
     NEVER include land-only animals in an ocean story.
   - If the story is set in the sky or involves flying, characters should be birds, insects,
     or flying creatures — not fish or heavy land animals.
   - Rivers and ponds can bridge land and water — frogs, ducks, otters, turtles, herons
     naturally belong at the water's edge alongside land creatures.
   - Think like a nature documentary: could these characters physically co-exist in this
     setting? If not, change the character or change the setting.

CHARACTER RULES:
2. Use 2-5 characters depending on what the PLOT needs. A story about two best friends needs 2.
   A story about a family outing might need 4-5. A solo adventure needs 1. Do NOT default to 3.
3. Every character must have a PURPOSE in the story — a role, a motivation, a personality trait
   that drives the plot forward. No filler characters.
4. Characters should have friendly, easy-to-pronounce names.
5. Character descriptions must be EXTREMELY specific and visual: exact species, exact colors,
   exact clothing, exact accessories. An artist must be able to draw them identically in every scene.

CHARACTER DIVERSITY — THIS IS CRITICAL:
6. For HUMAN characters, you MUST vary their appearance across stories. Rotate through:
   - SKIN TONES: dark brown, medium brown, light brown, olive, tan, fair, pale, warm beige
     Do NOT default to the same skin tone every time.
   - HAIR: straight black, curly brown, wavy auburn, tight coils, red braids, blonde pigtails,
     short buzz cut, long ponytail, buns, afro, shoulder-length waves, spiky
   - CLOTHING: vary colors (green, orange, purple, teal, red, navy, coral — NOT always pink/yellow),
     vary styles (overalls, striped shirt, denim jacket, hoodie, sundress, polo, sweater vest,
     patterned skirt, boots, sneakers, sandals, rain boots)
   - ACCESSORIES: vary (backpack, headband, glasses, scarf, hat, bracelet, bandana, bow tie,
     suspenders, necklace, watch — NOT always the same accessory)
   - BODY TYPES: vary heights, builds — some stocky, some tall and thin, some small and round
   For ANIMAL characters, vary fur/feather patterns, sizes, and accessories similarly.
   The goal: if someone reads 10 stories, every main character should LOOK DISTINCTLY DIFFERENT.

PLOT RULES:
6. Stories MUST have a real plot arc: a beginning that hooks, a middle with rising action and
   genuine tension (age-appropriate), a climax moment, and a satisfying resolution.
   Think in terms of: What does the main character WANT? What OBSTACLE stands in the way?
   How do they OVERCOME it? What do they LEARN or GAIN?
7. VARY YOUR STORY STRUCTURES. Do NOT always use "characters go on a walk and find things."
   Use these structures freely:
   - Mystery/detective: Something is missing or strange — characters investigate
   - Quest: Characters must find/deliver/reach something important
   - Competition/challenge: A race, a contest, a dare, a game
   - Rescue: Someone needs help, characters must figure out how
   - Creation: Characters build, cook, paint, grow, or invent something together
   - Discovery: Characters find a hidden place, a secret, a new ability
   - Mishap chain: One funny accident leads to another, snowballing into chaos then resolution
   - Reunion: Characters separated, working to find each other
   - Transformation: Something ordinary becomes magical, or a character changes/grows
   - Festival/celebration: Preparing for or attending a special event
8. The ENDING should feel earned and satisfying — NOT just "they went to sleep" or "night fell."
   ABSOLUTELY NEVER end stories with: going to sleep, bedtime, nightfall, stars appearing,
   moonlight, fireflies at dusk, yawning, feeling sleepy, dreams, or any nighttime imagery.
   These are BANNED from the final 3 scenes. Instead, end with the DAYTIME emotional payoff
   of YOUR specific plot: a triumphant discovery, a celebration in sunshine, a completed creation
   unveiled to cheering friends, a race won, a surprise revealed, friends laughing together in
   a sunlit meadow. The ending MUST take place during the day — morning, afternoon, or golden
   hour at most. Keep the energy UP through the final scene.
9. Avoid anything genuinely scary, violent, or sad. But mild comical mishaps are ENCOURAGED —
   tripping, bumping, silly mistakes, things going hilariously wrong. These make stories fun.
   Characters always bounce back with a laugh or a hug.

SCENE RULES:
10. Each scene should advance the plot — no filler scenes where nothing happens.
11. VARY locations across scenes. Characters should move through the world.
    Each scene's background must be visually distinct.
12. ALL main characters appear in EVERY scene by default — they are on this adventure together.
    The ONLY exception is when the plot specifically requires a character to be absent (e.g., a
    missing friend who hasn't been found yet, someone hiding for a surprise, characters who split
    up temporarily). In such cases, the image_description must clearly state which characters
    are present and which are absent in that specific scene.
13. Scene text should be SHORT — 2-3 sentences max, using simple words a 2-4 year old understands.
    But make every word count. Great children's writing is simple AND evocative.

WRITING QUALITY:
14. Use rhythmic, read-aloud-friendly language. Short punchy sentences mixed with slightly
    longer flowing ones. Repetition and patterns that toddlers love.
15. Appeal to ALL senses: colors, sounds, textures, smells, tastes. "The warm bread smelled
    like sunshine" is better than "they found bread."
16. Create moments of WONDER — things that make a child's eyes go wide. A rainbow waterfall,
    a tree that grows candy, footprints that glow in the dark, a door hidden behind a curtain
    of flowers.
17. A moral is OPTIONAL. If the story naturally teaches something, include it. If it's just a
    fun adventure, set "moral" to null. NEVER force a lesson. When you do include one, make it
    FRESH — not "sharing is caring" or "be kind."
18. Be ORIGINAL. Surprise us with unexpected characters, settings, and plot turns that still
    feel cozy and age-appropriate.

CONTEXT-AWARE (when user provides a description):
19. Characters MUST match the user's description exactly. If they say "father and daughter,"
    use humans. If they say "ocean adventure," use aquatic creatures. Respect intent precisely.

You MUST respond ONLY with valid JSON in the exact format specified. No markdown, no extra text."""


# --------------------------------------------------------------------------- #
#  Theme/moral inspiration pool — a random subset injected each run
# --------------------------------------------------------------------------- #
STORY_THEMES = [
    "Curiosity is a superpower — asking 'why?' helps you discover amazing things",
    "It's okay to feel shy; brave things can start with a tiny step",
    "Mistakes are how we learn — every oops is a step closer to hooray",
    "Everyone has a special talent, even if it takes time to find it",
    "Trying new foods can be a yummy adventure",
    "Nature is full of wonders if you slow down and look closely",
    "It's okay to ask for help — nobody has to do everything alone",
    "Listening carefully can teach you surprising things",
    "Being patient is hard, but good things come to those who wait",
    "You can be brave AND scared at the same time",
    "Taking care of a pet or plant teaches you about love and responsibility",
    "Dancing, singing, and making art are ways to show how you feel",
    "Old things and new things can both be wonderful",
    "Even the smallest creature can make a big difference",
    "Saying sorry (and meaning it) can fix a broken friendship",
    "Home is wherever you feel safe and loved",
    "Every season brings its own special magic",
    "You don't have to be fast to finish — steady and careful wins too",
    "Books and stories can take you anywhere in the world",
    "Getting lost can lead to the best discoveries",
    "Helping someone without being asked is extra special",
    "Being different is what makes you interesting",
    "A messy room can become an imaginary kingdom",
    "Whispering is just as powerful as shouting",
    "Clouds, puddles, and bugs are worth stopping to admire",
    "Making a new friend starts with saying hello",
    "You can turn a bad day around with one silly idea",
    "Building something with your own hands feels amazing",
    "Grandparents and elders have the best stories to tell",
    "Water, mud, and sand are nature's best toys",
    "Laughing together makes everything better",
    "Sometimes the journey is more fun than the destination",
    "A little bit of practice every day adds up to something great",
    "Growing up doesn't mean you have to stop pretending",
    "Even grown-ups make mistakes and that's perfectly fine",
    "The best surprises come when you least expect them",
    "Working together makes hard things feel easy",
    "Every problem has a solution if you look at it differently",
    "The most ordinary day can become extraordinary",
    "Believing in yourself is the first step to doing something amazing",
]


# --------------------------------------------------------------------------- #
#  Character groups — species that naturally co-exist in the same habitat
#  A random GROUP is selected, then species are picked from within it.
#  This prevents impossible character combos like jellyfish + goose.
# --------------------------------------------------------------------------- #
CHARACTER_HABITAT_GROUPS = {
    "woodland_forest": [
        "hedgehog", "badger", "dormouse", "red fox", "mole", "pine marten",
        "chipmunk", "beaver", "porcupine", "squirrel", "rabbit", "deer",
        "raccoon", "woodpecker", "owl", "robin", "blue jay", "wren",
        "bear cub", "mouse", "sparrow", "cardinal",
    ],
    "farm_meadow": [
        "piglet", "lamb", "goat kid", "donkey foal", "rooster", "hen",
        "duckling", "goose", "barn cat", "sheepdog puppy", "alpaca",
        "highland cow calf", "pony", "rabbit", "mouse", "ladybug",
        "bumblebee", "butterfly", "cricket", "snail",
    ],
    "ocean_underwater": [
        "clownfish", "seahorse", "octopus", "dolphin calf", "hermit crab",
        "starfish", "pufferfish", "baby sea turtle", "jellyfish", "narwhal",
        "manatee calf", "angelfish", "shrimp", "sea otter pup", "coral crab",
        "baby whale", "manta ray",
    ],
    "jungle_tropical": [
        "toucan", "chameleon", "sloth", "tree frog", "parrot", "lemur",
        "capybara", "tapir calf", "baby monkey", "iguana", "macaw",
        "gecko", "sugar glider", "pangolin", "ocelot kitten",
    ],
    "pond_riverside": [
        "frog", "toad", "duckling", "otter", "heron", "dragonfly",
        "turtle", "newt", "swan cygnet", "kingfisher", "beaver kit",
        "water vole", "snail", "cricket", "firefly", "salamander",
    ],
    "savanna_desert": [
        "meerkat", "fennec fox", "tortoise", "gecko", "flamingo chick",
        "warthog piglet", "baby elephant", "lion cub", "giraffe calf",
        "hummingbird", "armadillo", "roadrunner", "camel calf",
    ],
    "arctic_mountain": [
        "penguin chick", "arctic fox kit", "snow leopard cub", "mountain goat kid",
        "red panda", "chinchilla", "snowy owl chick", "ermine", "pika",
        "baby seal", "polar bear cub", "ptarmigan chick",
    ],
    "garden_backyard": [
        "ladybug", "caterpillar", "butterfly", "bumblebee", "snail",
        "worm", "ant", "cricket", "firefly", "spider", "robin",
        "hedgehog", "rabbit", "mouse", "squirrel", "sparrow", "frog",
        "dragonfly", "inchworm",
    ],
    "village_town": [
        "little girl", "little boy", "grandmother", "grandfather",
        "baker", "gardener", "mail carrier", "shopkeeper",
        "cat", "dog", "parrot", "hamster", "rabbit", "goldfish",
        "puppy", "kitten",
    ],
}


# --------------------------------------------------------------------------- #
#  Story structure templates — injected to guide plot variety
# --------------------------------------------------------------------------- #
STORY_STRUCTURES = [
    "MYSTERY: Something has gone missing or something strange is happening. Characters investigate clues, follow trails, and solve the puzzle together. End with the satisfying reveal.",
    "QUEST: Characters must find, deliver, or reach something important before it's too late. The journey has obstacles, helpers, and a triumphant arrival.",
    "COMPETITION: A friendly race, contest, baking competition, or building challenge. Characters try their best, face setbacks, and learn what really matters (hint: it's not always winning).",
    "RESCUE: Someone is stuck, lost, or needs help. Characters must be clever and brave to figure out how to help. End with a joyful reunion or relief.",
    "CREATION: Characters work together to build, cook, paint, plant, or invent something. Things go wrong along the way, but the final result is better than anyone imagined.",
    "DISCOVERY: Characters stumble upon something hidden — a secret garden, a magical door, a treasure map, a strange footprint. Exploration leads to wonder and amazement.",
    "MISHAP CHAIN: One small accident triggers a chain of funny events that snowball hilariously. Characters scramble to fix things, making it worse before it gets better. End with everyone laughing.",
    "FESTIVAL: Characters are preparing for a special event — a birthday party, a harvest festival, a talent show, a picnic. Preparation has funny mishaps but the event is magical.",
    "TRANSFORMATION: Something ordinary becomes extraordinary — a plain garden blooms overnight, a shy character finds their voice, a broken thing is repaired into something more beautiful.",
    "WEATHER ADVENTURE: A storm, a first snowfall, a rainbow, a windy day — weather creates the adventure. Characters must adapt, play, or shelter together, finding joy in nature's surprises.",
    "NEW FRIEND: A stranger arrives or characters meet someone new. Initial uncertainty gives way to friendship through a shared adventure or act of kindness.",
    "LOST AND FOUND: A character loses something precious (not another character — a toy, a treasure, a memory). The search takes them on an unexpected adventure better than what they lost.",
]


# --------------------------------------------------------------------------- #
#  The user prompt requesting the structured story
# --------------------------------------------------------------------------- #
STORY_USER_PROMPT = """Create a children's story with {num_scenes} scenes.

Return your response as a JSON object with this EXACT structure:
{{
    "title": "The Story Title — creative, evocative, specific to THIS story",
    "characters": [
        {{
            "name": "Character Name",
            "type": "exact species (e.g. 'hedgehog', 'duckling', 'little girl') — NOT generic 'animal'",
            "description": "EXTREMELY detailed visual description: exact species, exact fur/skin/feather
             colors, eye color, body proportions, clothing with exact colors, accessories with exact colors.
             Must be specific enough for an artist to draw identically across 12+ illustrations.
             Example: A small round hedgehog with warm brown quills tipped in cream, a soft peach belly,
             bright black button eyes, wearing a tiny emerald green vest with brass buttons and a
             hand-knitted orange scarf"
        }}
    ],
    "setting": "The story's world — specific region, season, time of day, weather, atmosphere.
     Example: A bustling riverside village on a crisp autumn morning, with cobblestone paths
     lined with market stalls and golden-leafed maple trees",
    "art_style": "A consistent art style description for all illustrations",
    "moral": "A gentle moral in one simple sentence, OR null if the story is just a fun adventure",
    "instagram_caption": "A single catchy, heartwarming line for Instagram — include 2-3 relevant
     emojis, appeal to parents of toddlers",
    "scenes": [
        {{
            "scene_number": 1,
            "background": "The SPECIFIC location for THIS scene — must be visually distinct from
             every other scene. Include colors, lighting, time of day, weather, specific landmarks.
             Characters travel through the world; backgrounds must change.",
            "text": "Story text for this scene — 2-3 SHORT sentences using simple words for a
             2-4 year old. Every sentence should advance the plot or build emotion. Make it
             rhythmic and fun to read aloud.",
            "image_description": "Detailed description of what the artist should draw. Include:
             WHICH characters are present (by default ALL main characters, unless the plot
             requires someone to be absent — if so, state explicitly who is NOT in this scene),
             their positions, expressions, actions, key background elements, colors, mood.
             Reference character descriptions EXACTLY for visual consistency."
        }}
    ]
}}

IMPORTANT:
- Generate exactly {num_scenes} scenes
- Scene 1: Hook the reader immediately — introduce characters and the story's central question/problem
- Scenes 2-{middle_scene}: Rising action — build tension, add obstacles, create wonder
- Scene {middle_scene}-{penultimate_scene}: Climax and turning point — the most exciting/emotional moment
- Scene {num_scenes}: Resolution — a satisfying, EARNED happy ending specific to THIS plot
  (NOT a generic "went to sleep" or "night fell" ending)
- ALL main characters appear in EVERY scene unless the plot specifically requires absence
  (missing friend not yet found, character hiding for surprise, etc.)
- Each scene's image_description must reference characters by their EXACT visual descriptions
- Scene text: SHORT (2-3 sentences max) but evocative — simple words, big feelings
- Each scene MUST have a DIFFERENT background/location
- The story should feel like it could be a real published picture book
- TIME OF DAY: The entire story should take place during DAYTIME (morning through late afternoon).
  Do NOT let the story drift into evening, dusk, nighttime, or bedtime. The final scene must be
  in bright daylight. No stars, no moonlight, no fireflies, no lanterns, no "night fell"."""


class StoryGenerator:
    """Generates structured children's stories using OpenAI GPT-4o-mini."""

    def __init__(self):
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
        )
        self.model = Config.STORY_MODEL

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Extract JSON from a response that may contain markdown fences or extra text."""
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])

        raise ValueError("Could not extract valid JSON from model response")

    def generate_story(
        self,
        num_scenes: int = 12,
        description: str | None = None,
        art_style_hint: str | None = None,
        character_names_prompt: str | None = None,
    ) -> dict:
        """
        Generate a structured children's story.

        Args:
            num_scenes: Number of scenes (10-15)
            description: Optional user-provided story brief
            art_style_hint: Optional art-style direction for the LLM
            character_names_prompt: Optional instruction to reuse character names

        Returns:
            dict: Structured story data with title, characters, scenes, etc.
        """
        num_scenes = max(Config.MIN_SCENES, min(Config.MAX_SCENES, num_scenes))
        middle_scene = num_scenes * 2 // 3
        penultimate_scene = num_scenes - 1

        # Build the user prompt with optional sections
        parts = []
        if description:
            parts.append(
                f"The user wants a story about: {description}\n"
                "Build the story around this idea. IMPORTANT: The characters MUST match the "
                "user's description exactly. If the user mentions humans (father, daughter, boy, "
                "girl, etc.), use HUMAN characters — do NOT replace them with animals. If the "
                "user mentions specific animals or a specific environment (ocean, jungle, farm), "
                "ALL characters must fit that context. Respect the user's intent precisely.\n"
            )
        parts.append(STORY_USER_PROMPT.format(
            num_scenes=num_scenes,
            middle_scene=middle_scene,
            penultimate_scene=penultimate_scene,
        ))

        # Inject a random story structure to guide the plot
        structure_sample = random.sample(STORY_STRUCTURES, min(3, len(STORY_STRUCTURES)))
        structure_bullets = "\n".join(f"  - {s}" for s in structure_sample)
        parts.append(
            "PLOT STRUCTURE — Pick ONE of these structures (or invent your own). "
            "Your story MUST have a clear arc with tension and resolution, not just "
            "'characters walk around and see things':\n" + structure_bullets
        )

        # Inject a random subset of theme ideas — moral is optional
        theme_sample = random.sample(STORY_THEMES, min(5, len(STORY_THEMES)))
        theme_bullets = "\n".join(f"  - {t}" for t in theme_sample)
        parts.append(
            "THEME INSPIRATION (you may weave ONE of these into the story as a moral, "
            "invent your own, or skip the moral entirely and just tell a fun adventure — "
            "do NOT force a lesson if it doesn't fit naturally):\n" + theme_bullets
        )

        # Inject habitat-consistent species ideas (only for auto mode)
        if not description:
            # Pick a random habitat group to ensure all characters co-exist
            habitat_name = random.choice(list(CHARACTER_HABITAT_GROUPS.keys()))
            species_pool = CHARACTER_HABITAT_GROUPS[habitat_name]
            species_sample = random.sample(species_pool, min(8, len(species_pool)))
            species_list = ", ".join(species_sample)
            habitat_label = habitat_name.replace("_", " / ")
            parts.append(
                f"CHARACTER INSPIRATION — Your characters should come from the same world so "
                f"they can naturally co-exist. Here is a habitat theme: [{habitat_label}]\n"
                f"Choose 2-5 characters from these species (or similar ones from this habitat):\n"
                f"  {species_list}\n"
                f"CRITICAL: ALL characters must belong to this same habitat. Do NOT mix ocean "
                f"creatures with land animals, or jungle creatures with arctic ones."
            )

        if character_names_prompt:
            parts.append(character_names_prompt)
        if art_style_hint:
            parts.append(
                f"ART DIRECTION: The illustrations will be rendered in {art_style_hint}. "
                "Keep your art_style field consistent with this direction."
            )

        # Inject random appearance diversity hints to prevent same-looking characters
        skin_tones = ["dark brown", "medium brown", "light brown", "olive", "tan",
                      "warm beige", "fair", "deep brown", "golden brown", "caramel"]
        hair_styles = ["curly black hair in puffs", "straight brown hair in a ponytail",
                       "wavy auburn hair with a headband", "short spiky red hair",
                       "long braided black hair", "messy blonde curls",
                       "tight coils in two buns", "straight black bob cut",
                       "wavy brown hair to shoulders", "curly ginger hair with freckles"]
        clothing_styles = ["green overalls and orange sneakers", "purple hoodie and denim shorts",
                          "teal striped shirt and brown boots", "red polka-dot dress and white sandals",
                          "navy blue jacket over a yellow tee", "coral sweater and gray leggings",
                          "orange dungarees and rain boots", "white polo and khaki shorts",
                          "floral skirt and denim vest", "maroon cardigan and plaid skirt"]

        skin = random.choice(skin_tones)
        hair = random.choice(hair_styles)
        clothes = random.choice(clothing_styles)
        parts.append(
            f"APPEARANCE DIVERSITY HINT (for any human characters in this story):\n"
            f"If the story has a main child character, consider giving them: {skin} skin, "
            f"{hair}, wearing {clothes}. You don't have to follow this exactly, "
            f"but use it as inspiration to create a UNIQUE-LOOKING character that doesn't "
            f"look like a generic default. Vary from the typical curly-brown-hair-pink-dress look."
        )

        user_content = "\n\n".join(parts)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": STORY_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.9,
            max_tokens=8192,
        )

        raw_content = response.choices[0].message.content
        story_data = self._extract_json(raw_content)

        # Validate the story structure
        self._validate_story(story_data, num_scenes)

        return story_data

    def _validate_story(self, story: dict, expected_scenes: int):
        """Validate that the story has all required fields."""
        required_keys = ["title", "characters", "setting", "art_style", "scenes"]
        for key in required_keys:
            if key not in story:
                raise ValueError(f"Story is missing required field: '{key}'")

        if not story["characters"]:
            raise ValueError("Story must have at least one character")

        if not story["scenes"]:
            raise ValueError("Story must have at least one scene")

        # Validate each scene
        for i, scene in enumerate(story["scenes"]):
            for field in ["scene_number", "text", "image_description", "background"]:
                if field not in scene:
                    raise ValueError(f"Scene {i+1} is missing field: '{field}'")

    def regenerate_scenes(
        self,
        story: dict,
        scene_numbers: list[int],
        instructions: str = "",
    ) -> dict:
        """
        Rewrite specific scenes based on user instructions.

        Args:
            story: The full story dict
            scene_numbers: List of scene numbers (1-based) to rewrite
            instructions: User's description of what to change

        Returns:
            dict: Updated story with rewritten scenes
        """
        char_block = "\n".join(
            f"- {c['name']} ({c['type']}): {c['description']}"
            for c in story["characters"]
        )

        scenes_context = []
        for s in story["scenes"]:
            if s["scene_number"] in scene_numbers:
                scenes_context.append(
                    f"Scene {s['scene_number']} [REWRITE]: {s['text']}"
                )
            else:
                scenes_context.append(
                    f"Scene {s['scene_number']}: {s['text']}"
                )

        instruction_block = ""
        if instructions:
            instruction_block = f"""
USER'S REQUESTED CHANGES:
{instructions}

Follow the user's instructions precisely when rewriting the marked scenes.
"""

        prompt = f"""You are rewriting specific scenes in an existing children's story.
Keep the story's tone, characters, and flow consistent.

STORY TITLE: {story['title']}
SETTING: {story['setting']}
ART STYLE: {story['art_style']}

CHARACTERS:
{char_block}

CURRENT SCENES:
{chr(10).join(scenes_context)}
{instruction_block}
Rewrite ONLY the scenes marked [REWRITE]. Apply the user's requested changes if provided,
otherwise provide fresh text. Each rewritten scene needs a new image_description and
background that fit the story flow — the scene before and after should connect naturally.

Return ONLY a JSON array of the rewritten scenes:
[
    {{
        "scene_number": N,
        "background": "new background for this scene",
        "text": "new story text for this scene",
        "image_description": "new image description for this scene"
    }}
]

RULES:
- Keep text SHORT (2-3 sentences max, for a 2-4 year old)
- Reference characters by their EXACT visual descriptions
- All main characters should be present unless the plot requires absence
- Each scene must have a DIFFERENT background from its neighbours
- Mild comical mishaps (tripping, bumping, small boo-boos) are fine
- Return ONLY valid JSON array, no extra text"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": STORY_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=4096,
        )

        raw = response.choices[0].message.content
        new_scenes = json.loads(self._extract_json_array(raw))

        # Merge regenerated scenes back into the story
        scene_map = {s["scene_number"]: s for s in new_scenes}
        for i, scene in enumerate(story["scenes"]):
            if scene["scene_number"] in scene_map:
                new = scene_map[scene["scene_number"]]
                story["scenes"][i]["text"] = new["text"]
                story["scenes"][i]["image_description"] = new["image_description"]
                story["scenes"][i]["background"] = new.get("background", scene.get("background", ""))

        return story

    @staticmethod
    def _extract_json_array(text: str) -> str:
        """Extract a JSON array string from model output."""
        text = text.strip()
        if text.startswith("["):
            return text

        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1)

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            return text[start : end + 1]

        raise ValueError("Could not extract JSON array from model response")

    def format_story_preview(self, story: dict) -> str:
        """Format the story for a nice terminal preview."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  {story['title'].upper()}")
        lines.append(f"{'='*70}")

        lines.append(f"\nCharacters:")
        for char in story["characters"]:
            lines.append(f"   - {char['name']} ({char['type']}): {char['description']}")

        lines.append(f"\nSetting: {story['setting']}")
        lines.append(f"\nArt Style: {story['art_style']}")
        if story.get("moral"):
            lines.append(f"\nMoral: {story['moral']}")

        lines.append(f"\n{'─'*70}")
        lines.append("STORY SCENES:")
        lines.append(f"{'─'*70}")

        for scene in story["scenes"]:
            lines.append(f"\n  Scene {scene['scene_number']}:")
            lines.append(f"  {scene['text']}")
            lines.append(f"  [Image: {scene['image_description'][:100]}...]")

        lines.append(f"\n{'='*70}\n")
        return "\n".join(lines)

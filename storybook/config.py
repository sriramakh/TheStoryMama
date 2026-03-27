"""
Configuration module for StoryBook Generator.
Loads settings from .env file and provides defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration loaded from .env file."""

    # OpenAI API (used for story generation)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Google Gemini API (used for image generation)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # GLM / ZhipuAI API (legacy, kept for reference)
    GLM_API_KEY = os.getenv("GLM_API_KEY", "")
    GLM_BASE_URL = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")

    # MiniMax API (used for image generation)
    MINIMAX_API_TOKEN = os.getenv("MINIMAX_API_TOKEN", "")
    MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1")

    # Model settings
    STORY_MODEL = os.getenv("STORY_MODEL", "gpt-4o-mini")
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "cogView-4-250304")
    IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1536")
    IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "gpt-image")  # "gpt-image", "gemini", "minimax", or "cogview"

    # Story settings
    MIN_SCENES = int(os.getenv("MIN_SCENES", "10"))
    MAX_SCENES = int(os.getenv("MAX_SCENES", "15"))

    # Output settings
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "stories")

    # Character registry
    CHARACTER_REGISTRY_PATH = os.getenv(
        "CHARACTER_REGISTRY_PATH", os.path.join(OUTPUT_DIR, "character_registry.json")
    )

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://storymama:storymama@localhost:5432/storymama")

    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # JWT (shared secret with NextAuth)
    JWT_SECRET = os.getenv("NEXTAUTH_SECRET", "dev-secret-change-in-production")

    # Telegram bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "")

    # Animation styles — final 10 production styles
    DEFAULT_ANIMATION_STYLE = "animation_movie"

    ANIMATION_STYLES = {
        "animation_movie": {
            "name": "Animation Movie",
            "description": (
                "Modern 3D animated movie style children's picture book illustration. "
                "Smooth, vibrant CGI with soft volumetric lighting, rich saturated colors, "
                "expressive cartoon eyes with glossy reflections, rounded friendly shapes, "
                "cinematic depth of field, and warm studio-quality rendering."
            ),
            "story_art_style": "Modern 3D animated movie with smooth shapes, expressive eyes, and cinematic lighting",
            "image_rules": "3D animated movie aesthetic throughout — smooth CGI, NOT flat 2D",
        },
        "claymation": {
            "name": "Claymation",
            "description": (
                "Claymation stop-motion style children's picture book illustration. "
                "Visible clay textures on characters and props, handmade miniature sets, "
                "warm stop-motion lighting with soft shadows, charming imperfections, "
                "tactile and cozy feel."
            ),
            "story_art_style": "Claymation stop-motion with clay textures and miniature handmade sets",
            "image_rules": "Claymation stop-motion aesthetic — visible clay textures, miniature sets, handmade feel",
        },
        "paper_cutout": {
            "name": "Paper Cutout",
            "description": (
                "Paper cutout collage children's picture book illustration. "
                "Layered paper textures with visible edges and subtle shadows between layers, "
                "bold flat colors with handmade imperfections, torn and cut paper shapes, "
                "decorative patterns and textures on each paper layer, slight 3D depth "
                "from stacked cutouts, playful and tactile."
            ),
            "story_art_style": "Paper cutout collage with layered textures, bold flat colors, and handmade feel",
            "image_rules": "Paper cutout collage aesthetic — layered paper textures, visible edges, bold flat colors, handmade imperfections",
        },
        "glowlight_fantasy": {
            "name": "Glowlight Fantasy",
            "description": (
                "Glowlight fantasy children's picture book illustration. "
                "Luminous bioluminescent glow on characters and environment, deep twilight "
                "and midnight blue backgrounds, soft neon accents in teal, magenta, and gold, "
                "fireflies and glowing particles floating in the air, enchanted forest atmosphere "
                "with radiant mushrooms, glowing flowers, and shimmering water reflections."
            ),
            "story_art_style": "Glowlight fantasy with bioluminescent glow, twilight hues, and floating light particles",
            "image_rules": "Glowlight fantasy aesthetic — luminous glow effects, deep twilight palette, bioluminescent details, magical atmosphere",
        },
        "felt_plushie": {
            "name": "Felt & Plushie",
            "description": (
                "Handmade felt and plush toy aesthetic children's illustration. "
                "Characters look like they are made from soft felt fabric with visible stitching, "
                "button eyes, embroidered smiles, fabric textures like fleece and corduroy, "
                "backgrounds made of layered felt pieces with blanket-stitch edges, "
                "warm and cozy like a handmade nursery mobile."
            ),
            "story_art_style": "Felt and plushie with fabric textures, button eyes, stitched details, and nursery warmth",
            "image_rules": "Felt & plushie aesthetic — visible stitching, button eyes, fabric textures, handmade nursery feel",
        },
        "stained_glass": {
            "name": "Stained Glass",
            "description": (
                "Colorful stained glass window art style children's illustration. "
                "Bold black outlines separating jewel-toned color segments, "
                "rich saturated colors like ruby red, emerald green, sapphire blue, and amber gold, "
                "light appearing to glow through translucent colored glass panels, "
                "geometric yet organic shapes, ornate and magical like a fairy tale window."
            ),
            "story_art_style": "Stained glass with jewel tones, bold black outlines, and glowing translucent colors",
            "image_rules": "Stained glass aesthetic — bold black outlines, jewel-toned glass segments, glowing translucent colors",
        },
        "toy_diorama": {
            "name": "Toy Diorama",
            "description": (
                "Miniature toy diorama photography style children's illustration. "
                "Characters look like real collectible figurines or wooden toys photographed "
                "in a handmade miniature set, shallow depth of field with bokeh, "
                "tiny detailed props like miniature books and teacups, "
                "warm studio lighting with soft shadows, cozy and magical like a dollhouse scene, "
                "tilt-shift photography aesthetic."
            ),
            "story_art_style": "Toy diorama with miniature figurines, handmade sets, and tilt-shift photography feel",
            "image_rules": "Toy diorama aesthetic — miniature figurines, handmade sets, shallow depth of field, warm studio lighting",
        },
        "crochet_amigurumi": {
            "name": "Crochet Amigurumi",
            "description": (
                "Handmade crochet amigurumi style children's illustration. "
                "Characters look like real crocheted stuffed toys with visible yarn texture, "
                "tight crochet stitches in chunky yarn, safety eyes with black pupils "
                "and white highlights, stuffed round bodies with soft proportions, "
                "yarn hair and accessories, each character a different bright yarn color. "
                "Background is also made of crocheted and knitted textures. "
                "Warm natural lighting like a lifestyle photograph of handmade toys."
            ),
            "story_art_style": "Crochet amigurumi with yarn textures, safety eyes, and handmade warmth",
            "image_rules": "Crochet amigurumi aesthetic — visible yarn stitches, safety eyes, crocheted textures throughout, handmade toy feel",
        },
        "candy_clay": {
            "name": "Candy Clay",
            "description": (
                "Colorful candy-colored polymer clay sculpture style children's illustration. "
                "Characters look like they are sculpted from smooth bright polymer clay — "
                "polished, rounded, and candy-like with a slight matte sheen. "
                "Vivid saturated candy colors — cherry red, tangerine orange, lemon yellow, "
                "lime green, berry purple, cotton candy pink. Smooth sculpted surfaces with "
                "soft rounded edges, miniature handmade details like tiny clay flowers "
                "and mushrooms. Background is a miniature clay world. "
                "Bright cheerful studio lighting with soft shadows."
            ),
            "story_art_style": "Candy clay with smooth polished polymer clay sculptures in vivid candy colors",
            "image_rules": "Candy clay aesthetic — smooth polymer clay surfaces, vivid candy colors, miniature sculpted world, matte sheen",
        },
        "picture_book_collage": {
            "name": "Picture Book Collage",
            "description": (
                "Mixed-media picture book collage style children's illustration. "
                "Characters and scenes built from layered torn paper, painted textures, "
                "fabric scraps, stamped patterns, and hand-painted elements collaged together. "
                "Visible paper edges and layers creating depth. Rich organic textures — "
                "newspaper print, painted watercolor paper, kraft paper, tissue paper, "
                "textured cardstock. Warm earthy tones mixed with pops of bright color — "
                "teal, coral, golden yellow, olive green. Artistic and tactile."
            ),
            "story_art_style": "Picture book collage with torn paper, painted textures, and mixed-media layers",
            "image_rules": "Picture book collage aesthetic — torn paper edges, layered textures, mixed media, visible paper layers",
        },
    }

    # Image text overlay settings
    FONT_SIZE_TITLE = 48
    FONT_SIZE_BODY = 32
    FONT_SIZE_MORAL = 28
    TEXT_PADDING = 40

    # Text band settings (cream band below the image)
    TEXT_BAND_COLOR = (255, 249, 235)        # Warm cream background
    TEXT_BAND_MIN_HEIGHT = 250               # Minimum band height in pixels
    TEXT_COLOR_TITLE = (101, 67, 33)         # Dark brown for title
    TEXT_COLOR_BODY = (80, 55, 30)           # Dark brown for body text
    TEXT_COLOR_MORAL = (139, 90, 43)         # Warm brown for moral

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "❌ OPENAI_API_KEY is not set! Please add your OpenAI API key to the .env file."
            )
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "❌ GEMINI_API_KEY is not set! Please add your Google Gemini API key to the .env file."
            )
        if cls.IMAGE_PROVIDER == "cogview" and not cls.GLM_API_KEY:
            raise ValueError(
                "❌ GLM_API_KEY is not set! Please add your GLM/ZhipuAI API key to the .env file."
            )
        if cls.IMAGE_PROVIDER == "minimax" and not cls.MINIMAX_API_TOKEN:
            raise ValueError(
                "❌ MINIMAX_API_TOKEN is not set! Please add your MiniMax API token to the .env file."
            )
        if cls.IMAGE_PROVIDER == "gpt-image" and not cls.OPENAI_API_KEY:
            raise ValueError(
                "❌ OPENAI_API_KEY is not set! Please add your OpenAI API key to the .env file."
            )
        if cls.IMAGE_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError(
                "❌ GEMINI_API_KEY is not set! Please add your Gemini API key to the .env file."
            )
        return True

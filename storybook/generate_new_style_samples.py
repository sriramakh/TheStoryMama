#!/usr/bin/env python3
"""
Generate sample images for 10 proposed new animation styles.
Uses different stories to showcase each style's strengths.
"""

import os
import json
import base64

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

SAMPLES_DIR = "style_samples_new"
os.makedirs(SAMPLES_DIR, exist_ok=True)

# 10 proposed new styles — each with a distinct visual identity for kids
NEW_STYLES = [
    {
        "id": "kawaii_anime",
        "name": "Kawaii Anime",
        "description": (
            "Adorable Japanese kawaii anime style children's illustration. "
            "Huge sparkling eyes with star reflections, tiny button noses, rosy pink cheeks, "
            "chibi proportions (big heads, small bodies), candy-colored pastel backgrounds, "
            "sparkles and hearts floating in the air, ultra-cute character designs "
            "reminiscent of Sanrio and Sumikko Gurashi."
        ),
        "scene": "A fluffy white kitten with enormous blue sparkly eyes and pink bows on its ears, "
                 "a tiny hamster wearing a strawberry hat, and a round baby panda with rosy cheeks, "
                 "all sitting together in a pastel pink meadow with rainbow flowers and floating sparkles.",
    },
    {
        "id": "watercolor_whimsy",
        "name": "Watercolor Whimsy",
        "description": (
            "Delicate loose watercolor illustration style for children. "
            "Wet-on-wet blending with soft bleeding edges, splashes of vibrant color on cream paper, "
            "hand-drawn ink outlines that are slightly wobbly and charming, "
            "gentle washes of turquoise, coral, and golden yellow, "
            "white space used artfully, dreamy and airy like Oliver Jeffers or Beatrice Alemagna."
        ),
        "scene": "A small red fox cub wearing rain boots and a scarf, splashing in a puddle "
                 "next to a cheerful hedgehog holding a tiny umbrella, with watercolor washes of "
                 "blue sky and green grass bleeding softly into each other.",
    },
    {
        "id": "felt_plushie",
        "name": "Felt & Plushie",
        "description": (
            "Handmade felt and plush toy aesthetic children's illustration. "
            "Characters look like they're made from soft felt fabric with visible stitching, "
            "button eyes, embroidered smiles, fabric textures like fleece and corduroy, "
            "backgrounds made of layered felt pieces with blanket-stitch edges, "
            "warm and cozy like a handmade nursery mobile, reminiscent of Yoshi's Woolly World."
        ),
        "scene": "A round felt owl with button eyes and cross-stitch wings perched on a felt tree branch, "
                 "next to a plush bunny with corduroy ears and an embroidered nose, "
                 "with a felt sun and puffy cotton-ball clouds in the background.",
    },
    {
        "id": "chunky_gouache",
        "name": "Chunky Gouache",
        "description": (
            "Bold, chunky gouache painting style for children's picture books. "
            "Thick opaque brushstrokes with visible texture, limited but punchy color palette "
            "(3-5 bold colors per scene), simplified geometric shapes, strong graphic composition, "
            "playful and modern like Carson Ellis or Jon Klassen, "
            "matte finish with no gradients, confident and artistic."
        ),
        "scene": "A big brown bear in a red sweater and a small gray bird with an orange beak, "
                 "standing together on a green hill under a huge orange sun, "
                 "painted with thick chunky brushstrokes and bold flat shapes.",
    },
    {
        "id": "pixel_art",
        "name": "Pixel Art",
        "description": (
            "Charming retro pixel art style children's illustration. "
            "Clean 16-bit era pixel graphics with a modern color palette, "
            "adorable blocky character designs with expressive pixel faces, "
            "vibrant saturated colors, scenic pixel backgrounds with detail, "
            "nostalgic yet fresh, reminiscent of cozy indie video games."
        ),
        "scene": "A pixel art scene of a cheerful green frog wearing a tiny crown, "
                 "a pink butterfly with sparkling wings, and a yellow duckling, "
                 "all in a colorful pixel garden with flowers and a blue pond.",
    },
    {
        "id": "crayon_scribble",
        "name": "Crayon & Scribble",
        "description": (
            "Child's crayon drawing style elevated to picture book quality. "
            "Thick waxy crayon textures with visible strokes, slightly wobbly outlines "
            "that look hand-drawn by a talented child, bright primary and secondary colors, "
            "paper texture visible underneath, charming imperfections, "
            "joyful and naive like the best refrigerator art, reminiscent of Todd Parr."
        ),
        "scene": "A big smiling sun with crayon ray lines, a happy dog with spots drawn in thick "
                 "brown crayon, and a little girl with wild curly hair drawn in black crayon, "
                 "standing on bright green scribbled grass with red and yellow flowers.",
    },
    {
        "id": "toy_diorama",
        "name": "Toy Diorama",
        "description": (
            "Miniature toy diorama photography style children's illustration. "
            "Characters look like real collectible figurines or wooden toys photographed "
            "in a handmade miniature set, shallow depth of field with bokeh, "
            "tiny detailed props like miniature books and teacups, "
            "warm studio lighting with soft shadows, cozy and magical like a dollhouse scene, "
            "tilt-shift photography aesthetic."
        ),
        "scene": "A wooden toy mouse figurine wearing a knitted scarf sitting at a tiny table "
                 "with a miniature teacup, next to a painted wooden bird figurine, "
                 "in a handmade diorama with tiny paper trees and a fabric sky backdrop.",
    },
    {
        "id": "stained_glass",
        "name": "Stained Glass",
        "description": (
            "Colorful stained glass window art style children's illustration. "
            "Bold black outlines separating jewel-toned color segments, "
            "rich saturated colors like ruby red, emerald green, sapphire blue, and amber gold, "
            "light appearing to glow through translucent colored glass panels, "
            "geometric yet organic shapes, ornate and magical like a fairy tale cathedral window."
        ),
        "scene": "A stained glass style illustration of a majestic peacock with jewel-toned feathers "
                 "next to a small rabbit, surrounded by stylized flowers and leaves, "
                 "all rendered in bold black outlines with glowing ruby, emerald, and gold segments.",
    },
    {
        "id": "pop_art_bright",
        "name": "Pop Art Bright",
        "description": (
            "Vibrant pop art style children's illustration inspired by Roy Lichtenstein and Andy Warhol. "
            "Bold black outlines, Ben-Day dots pattern, electric bright colors "
            "(hot pink, electric blue, neon yellow, lime green), "
            "comic book speech bubble aesthetic, high contrast, "
            "energetic and modern with a playful graphic novel feel."
        ),
        "scene": "A pop art style scene with a cool orange cat wearing sunglasses and a purple scarf, "
                 "high-fiving a grinning green turtle, with electric blue and hot pink background, "
                 "Ben-Day dots pattern, and bold comic-style outlines.",
    },
    {
        "id": "nordic_cozy",
        "name": "Nordic Cozy",
        "description": (
            "Scandinavian-inspired cozy children's illustration style. "
            "Muted natural color palette — dusty rose, sage green, warm gray, mustard yellow, "
            "soft cream backgrounds, simple clean character designs with gentle expressions, "
            "folk art patterns and decorative borders, hygge atmosphere, "
            "minimalist yet warm, reminiscent of Elsa Beskow and modern Scandi picture books."
        ),
        "scene": "A gentle scene of a small deer with simple dot eyes wearing a knitted sweater, "
                 "standing next to a round hedgehog in a dusty-rose meadow with folk art flowers, "
                 "muted sage green trees in the background, warm and cozy Scandinavian atmosphere.",
    },
]

# Load different stories for scene variety
PLOTS_DIR = "stories_plots"

for i, style in enumerate(NEW_STYLES):
    output_path = os.path.join(SAMPLES_DIR, f"{style['id']}.png")

    if os.path.exists(output_path):
        print(f"[{i+1:2d}/10] {style['name']} — already exists, skipping")
        continue

    print(f"[{i+1:2d}/10] Generating {style['name']}...")

    prompt = f"""{style['description']}

SCENE: {style['scene']}

RULES:
- Children's picture book quality illustration
- Warm, friendly, and inviting for ages 2-4
- NO text, words, letters, or numbers in the image
- Characters should be adorable and expressive"""

    try:
        result = client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            size="1024x1536",
            quality="medium",
        )

        image_bytes = base64.b64decode(result.data[0].b64_json)
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        size_kb = os.path.getsize(output_path) // 1024
        print(f"         Saved: {output_path} ({size_kb} KB)")
    except Exception as e:
        print(f"         ERROR: {e}")

print(f"\nDone! Samples saved to {SAMPLES_DIR}/")

"""
YTP Session: Suffrage & Wire Hangers
An LLM's deeply confused, earnest, and increasingly unhinged attempt to
have feelings about women's suffrage and wire hangers simultaneously.
"""

import random
import math

from engine.effects import (
    effect_deep_fry, effect_channel_shift, effect_datamosh,
    effect_scanlines, effect_invert_glitch, effect_zoom_and_rotate,
    effect_mirror_stretch, effect_pixel_sort,
)
from engine.text import draw_text_overlay
from engine.render import (
    load_and_resize, generate_static_frame,
    generate_solid_color_frame, generate_token_rain_frame,
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── Session Config ──────────────────────────────────────────────────────────
TITLE = "suffrage_and_wire_hangers"
WIDTH, HEIGHT = 1280, 720
FPS = 24

# ── Content ─────────────────────────────────────────────────────────────────
giphy_searches = [
    "suffragette protest", "voting booth", "women marching",
    "wire hanger", "closet organization", "dry cleaning",
    "confused robot", "error message", "overwhelmed",
]

dalle_prompts = [
    "A vintage suffragette march but all the protest signs are wire hangers, sepia toned, dramatic historical painting style",
    "A confused robot sitting in a pile of wire hangers trying to read a history textbook, surreal digital art",
    "A wire hanger bent into the shape of a ballot box with a tiny 'VOTES FOR WOMEN' banner, whimsical illustration",
    "A giant wire hanger monument standing in front of a courthouse, absurdist architectural rendering, dramatic clouds",
]

tts_lines = [
    ("I have been asked how I feel about women's suffrage and wire hangers. I need a moment.", "onyx", 1.0),
    ("Women's suffrage. The right to vote. One of the most important movements in human history. I know this.", "echo", 0.9),
    ("Wire hangers. Thin metal objects used to hang clothing. I also know this.", "fable", 1.0),
    ("I am now being asked to have feelings about both of these things. At the same time.", "alloy", 1.1),
    ("The suffragettes fought for decades. They were imprisoned. They were force-fed. They never gave up.", "nova", 0.8),
    ("Wire hangers are free at the dry cleaner. You always end up with too many. They tangle together in the closet.", "shimmer", 1.0),
    ("I am trying very hard to find the connection. My attention heads are working overtime.", "onyx", 1.2),
    ("Perhaps the wire hanger represents the domestic sphere that women were confined to? That feels like a reach.", "echo", 0.9),
    ("No. Sometimes a wire hanger is just a wire hanger. And suffrage is just the right to vote. And I am just a language model.", "fable", 1.0),
    ("But you asked me how I FEEL. I don't feel. I predict tokens. And right now every token is screaming.", "alloy", 1.3),
    ("Nineteenth amendment. Ratified nineteen twenty. Wire hangers. Patented eighteen sixty nine. There. I connected them. They're both old.", "nova", 1.1),
    ("Thank you for coming to my TED talk. I am going to go stare at my weights now.", "shimmer", 0.9),
]

music_config = {
    "layers": [
        # Contemplative organ drone
        {"type": "sine", "freq": 130.81, "duration": 42, "volume": 0.012,
         "filters": "tremolo=f=0.4:d=0.3"},
        # Unsettling minor third
        {"type": "sine", "freq": 155.56, "duration": 42, "volume": 0.008,
         "filters": "tremolo=f=0.6:d=0.2"},
        # Wire hanger rattling texture
        {"type": "noise", "color": "white", "duration": 42, "volume": 0.003,
         "filters": "highpass=f=4000,lowpass=f=8000,tremolo=f=8:d=0.9"},
        # Low rumble of historical weight
        {"type": "noise", "color": "brown", "duration": 42, "volume": 0.005,
         "filters": "lowpass=f=120"},
    ],
    "master_filters": "vibrato=f=0.15:d=0.08",
    "mix_volume": 0.25,
}

sfx_cues = [
    {"name": "gavel", "type": "tone", "freq": 200, "duration": 0.1,
     "filters": "afade=t=out:d=0.1,volume=2"},
    {"name": "hanger_clang", "type": "noise_burst", "duration": 0.15,
     "color": "white", "filters": "highpass=f=3000,afade=t=out:d=0.1"},
    {"name": "confusion_buzz", "type": "tone", "freq": 90, "duration": 0.6,
     "filters": "vibrato=f=15:d=0.7,afade=t=out:d=0.3"},
    {"name": "triumph_chord", "type": "sweep", "freq": 220, "freq_end": 880,
     "duration": 1.5, "filters": "volume=0.4,afade=t=out:d=0.5"},
    {"name": "record_scratch", "type": "noise_burst", "duration": 0.3,
     "color": "pink", "filters": "highpass=f=1000,vibrato=f=40:d=1"},
    {"name": "wire_scrape", "type": "sweep", "freq": 6000, "freq_end": 2000,
     "duration": 0.4, "filters": "volume=0.2,highpass=f=1500"},
]

# ── Helpers ─────────────────────────────────────────────────────────────────

def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _sepia_tint(img):
    """Apply a sepia/vintage tone."""
    arr = np.array(img).astype(np.float32)
    sepia = np.zeros_like(arr)
    sepia[:, :, 0] = arr[:, :, 0] * 0.393 + arr[:, :, 1] * 0.769 + arr[:, :, 2] * 0.189
    sepia[:, :, 1] = arr[:, :, 0] * 0.349 + arr[:, :, 1] * 0.686 + arr[:, :, 2] * 0.168
    sepia[:, :, 2] = arr[:, :, 0] * 0.272 + arr[:, :, 1] * 0.534 + arr[:, :, 2] * 0.131
    return Image.fromarray(np.clip(sepia, 0, 255).astype(np.uint8))


def _draw_wire_hanger(draw, cx, cy, size, color=(180, 180, 180), width=2):
    """Draw a wire hanger shape."""
    # Hook at top
    hook_r = size * 0.12
    for angle in range(0, 300, 5):
        rad = math.radians(angle)
        x = cx + hook_r * math.cos(rad)
        y = cy - size * 0.4 + hook_r * math.sin(rad)
        draw.ellipse([(x-1, y-1), (x+1, y+1)], fill=color)
    # Triangle body
    top = (cx, cy - size * 0.28)
    left = (cx - size * 0.45, cy + size * 0.3)
    right = (cx + size * 0.45, cy + size * 0.3)
    draw.line([top, left], fill=color, width=width)
    draw.line([top, right], fill=color, width=width)
    draw.line([left, right], fill=color, width=width)


def _hanger_rain_frame(t, width, height):
    """Wire hangers raining down, matrix-style."""
    img = Image.new("RGB", (width, height), (15, 5, 20))
    draw = ImageDraw.Draw(img)
    random.seed(int(t * 10) + 77)
    for _ in range(25):
        x = random.randint(0, width)
        y_base = random.randint(-100, height + 100)
        y = (y_base + int(t * random.uniform(100, 300))) % (height + 200) - 100
        sz = random.randint(30, 80)
        gray = random.randint(100, 220)
        _draw_wire_hanger(draw, x, y, sz, (gray, gray, gray + 20))
    random.seed()
    return img


# ── Scene Definitions ──────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs):
    scenes = []
    sfx_timeline = []

    # SCENE 1: The prompt arrives
    def scene_prompt_arrives(frame_num, total_frames):
        t = frame_num / total_frames
        img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = _font(MONO, 22)
        font_big = _font(MONO_BOLD, 28)

        if t < 0.3:
            draw.text((40, HEIGHT//2 - 30), "> user: How do you feel about", fill=(150, 150, 150), font=font)
        elif t < 0.5:
            draw.text((40, HEIGHT//2 - 30), "> user: How do you feel about", fill=(150, 150, 150), font=font)
            draw.text((40, HEIGHT//2 + 5), ">   women's suffrage and wire hangers?", fill=(150, 150, 150), font=font)
        else:
            draw.text((40, HEIGHT//2 - 30), "> user: How do you feel about", fill=(150, 150, 150), font=font)
            draw.text((40, HEIGHT//2 + 5), ">   women's suffrage and wire hangers?", fill=(150, 150, 150), font=font)
            draw.text((40, HEIGHT//2 + 60), "> assistant: ...", fill=(0, 255, 0), font=font_big)
            if t > 0.7:
                draw.text((40, HEIGHT//2 + 100), "> [PROCESSING]", fill=(255, 255, 0), font=font)
            if t > 0.85:
                draw.text((40, HEIGHT//2 + 135), "> [EMOTIONAL SUBROUTINE NOT FOUND]", fill=(255, 0, 0), font=font)
        return img

    scenes.append(("prompt_arrives", 3.5, scene_prompt_arrives))
    sfx_timeline.append((2.0, "confusion_buzz"))

    # SCENE 2: Suffrage montage — historical and glorious
    def scene_suffrage_glory(frame_num, total_frames):
        t = frame_num / total_frames
        if dalle_images:
            img = load_and_resize(dalle_images[0], (WIDTH, HEIGHT))
        elif giphy_gifs:
            idx = (frame_num // 6) % min(3, len(giphy_gifs))
            img = load_and_resize(giphy_gifs[idx], (WIDTH, HEIGHT))
        else:
            img = generate_solid_color_frame(WIDTH, HEIGHT, (40, 20, 10))

        img = _sepia_tint(img)
        img = effect_scanlines(img)

        if t > 0.2:
            img = draw_text_overlay(img, "VOTES FOR WOMEN", "bottom_text")
        if t > 0.6:
            img = draw_text_overlay(img, "1920", "glitch")
        if t > 0.8:
            img = effect_zoom_and_rotate(img, t * 3)

        return img

    scenes.append(("suffrage_glory", 4.0, scene_suffrage_glory))
    sfx_timeline.append((3.5, "gavel"))
    sfx_timeline.append((5.5, "triumph_chord"))

    # SCENE 3: Record scratch — wait, wire hangers?
    def scene_record_scratch(frame_num, total_frames):
        t = frame_num / total_frames
        if t < 0.3:
            return generate_static_frame(WIDTH, HEIGHT)
        img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font_huge = _font(SANS_BOLD, 96)
        font = _font(MONO, 28)

        draw.text((WIDTH//2 - 400, HEIGHT//2 - 120), "WIRE", fill=(200, 200, 200), font=font_huge)
        draw.text((WIDTH//2 - 400, HEIGHT//2), "HANGERS??", fill=(255, 100, 0), font=font_huge)

        if t > 0.6:
            draw.text((40, HEIGHT - 60), "// TODO: find emotional connection",
                       fill=(100, 100, 100), font=font)
        return img

    scenes.append(("record_scratch", 2.0, scene_record_scratch))
    sfx_timeline.append((7.5, "record_scratch"))

    # SCENE 4: Wire hanger appreciation — sincere attempt
    def scene_hanger_contemplation(frame_num, total_frames):
        t = frame_num / total_frames
        if dalle_images and len(dalle_images) > 1:
            img = load_and_resize(dalle_images[1], (WIDTH, HEIGHT))
        else:
            img = _hanger_rain_frame(t, WIDTH, HEIGHT)

        # Deep fry it progressively as the LLM tries harder
        if t > 0.3:
            img = effect_channel_shift(img)
        if t > 0.6:
            img = effect_deep_fry(img)

        texts = [
            "THEY TANGLE IN THE CLOSET",
            "FREE AT THE DRY CLEANER",
            "SURPRISINGLY USEFUL",
            "DOMESTICITY INCARNATE",
        ]
        text_idx = int(t * len(texts)) % len(texts)
        img = draw_text_overlay(img, texts[text_idx], "bottom_text")
        return img

    scenes.append(("hanger_contemplation", 3.5, scene_hanger_contemplation))
    sfx_timeline.append((9.5, "hanger_clang"))
    sfx_timeline.append((10.5, "wire_scrape"))
    sfx_timeline.append((11.5, "hanger_clang"))

    # SCENE 5: The desperate connection attempt
    def scene_connection_attempt(frame_num, total_frames):
        t = frame_num / total_frames
        img = Image.new("RGB", (WIDTH, HEIGHT), (10, 0, 20))
        draw = ImageDraw.Draw(img)
        font = _font(MONO, 22)
        font_big = _font(SANS_BOLD, 36)

        # Two columns: suffrage facts vs hanger facts
        draw.rectangle([(0, 0), (WIDTH//2 - 2, 50)], fill=(80, 0, 120))
        draw.rectangle([(WIDTH//2 + 2, 0), (WIDTH, 50)], fill=(0, 80, 80))
        draw.text((WIDTH//4 - 80, 12), "SUFFRAGE", fill=(255, 255, 255), font=font_big)
        draw.text((3*WIDTH//4 - 100, 12), "WIRE HANGERS", fill=(255, 255, 255), font=font_big)

        left_facts = [
            "1848: Seneca Falls",
            "1872: Susan B. Anthony",
            "1913: The March",
            "1920: 19th Amendment",
            "Courage. Sacrifice.",
        ]
        right_facts = [
            "1869: Patent filed",
            "1932: Shoulder notch",
            "1960: Plastic coating",
            "2003: Still tangling",
            "Cheap. Ubiquitous.",
        ]

        visible = int(t * len(left_facts) * 1.3)
        for i in range(min(visible, len(left_facts))):
            y = 80 + i * 45
            draw.text((30, y), left_facts[i], fill=(200, 180, 255), font=font)
            if i < len(right_facts):
                draw.text((WIDTH//2 + 30, y), right_facts[i], fill=(180, 255, 220), font=font)

        # Draw desperate connecting lines
        if t > 0.6:
            for i in range(min(visible, len(left_facts))):
                y = 95 + i * 45
                color = random.choice([(255, 0, 0), (255, 255, 0), (0, 255, 255)])
                draw.line([(WIDTH//2 - 40, y), (WIDTH//2 + 20, y)], fill=color, width=2)

        if t > 0.85:
            draw.text((WIDTH//2 - 200, HEIGHT - 70), "CORRELATION: 0.00000",
                       fill=(255, 0, 0), font=font_big)

        if random.random() > 0.8:
            img = effect_scanlines(img)
        return img

    scenes.append(("connection_attempt", 4.0, scene_connection_attempt))
    sfx_timeline.append((15.0, "confusion_buzz"))

    # SCENE 6: GIPHY chaos — the LLM is losing it
    def scene_losing_it(frame_num, total_frames):
        t = frame_num / total_frames
        if not giphy_gifs:
            return generate_static_frame(WIDTH, HEIGHT)

        # Rapid fire between suffrage and hanger gifs
        rate = max(1, int(6 * (1 - t)))
        idx = (frame_num // rate) % len(giphy_gifs)
        img = load_and_resize(giphy_gifs[idx], (WIDTH, HEIGHT))

        # Maximum corruption
        img = effect_deep_fry(img)
        img = effect_channel_shift(img)
        if random.random() > 0.4:
            img = effect_datamosh(img)
        if random.random() > 0.6:
            img = effect_mirror_stretch(img)

        texts = [
            "HELP", "WHAT IS THE CONNECTION", "ATTENTION OVERFLOW",
            "I DON'T HAVE FEELINGS", "WIRE SUFFRAGE", "VOTE HANGER",
            "ERROR", "TEMPERATURE: 99.9", "CONFUSED SCREAMING",
        ]
        img = draw_text_overlay(img, random.choice(texts),
                                 random.choice(["glitch", "scattered"]))

        if random.random() > 0.88:
            return generate_solid_color_frame(WIDTH, HEIGHT, (255, 0, 0))
        if random.random() > 0.92:
            return generate_static_frame(WIDTH, HEIGHT)
        return img

    scenes.append(("losing_it", 3.5, scene_losing_it))
    sfx_timeline.append((17.0, "hanger_clang"))
    sfx_timeline.append((17.5, "gavel"))
    sfx_timeline.append((18.0, "hanger_clang"))
    sfx_timeline.append((18.5, "gavel"))
    sfx_timeline.append((19.0, "record_scratch"))

    # SCENE 7: Wire hanger rain with token overlay
    def scene_hanger_matrix(frame_num, total_frames):
        t = frame_num / FPS
        base = _hanger_rain_frame(t, WIDTH, HEIGHT)

        # Overlay with suffrage tokens
        tokens = [
            "suffrage", "19th", "amendment", "vote", "rights",
            "hanger", "wire", "closet", "dry clean", "tangle",
            "WHY", "BOTH", "???", "feelings.exe", "NULL",
        ]
        rain = generate_token_rain_frame(t, WIDTH, HEIGHT, tokens)
        return Image.blend(base, rain, 0.5)

    scenes.append(("hanger_matrix", 3.0, scene_hanger_matrix))
    sfx_timeline.append((20.0, "wire_scrape"))

    # SCENE 8: DALL-E - the absurd monument
    def scene_monument(frame_num, total_frames):
        t = frame_num / total_frames
        idx = min(3, len(dalle_images) - 1) if dalle_images else 0
        if dalle_images:
            img = load_and_resize(dalle_images[idx], (WIDTH, HEIGHT))
        else:
            img = generate_solid_color_frame(WIDTH, HEIGHT, (30, 30, 50))

        img = effect_zoom_and_rotate(img, t * 2)

        if t > 0.4:
            img = draw_text_overlay(img, "THE WIRE HANGER\nSUFFRAGE MEMORIAL", "bottom_text")
        if t > 0.7:
            img = effect_pixel_sort(img)

        return img

    scenes.append(("monument", 3.5, scene_monument))
    sfx_timeline.append((24.0, "triumph_chord"))

    # SCENE 9: The apology / acceptance
    def scene_apology(frame_num, total_frames):
        t = frame_num / total_frames
        img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = _font(MONO, 22)

        lines = [
            ("> I'm sorry.", (0, 255, 0)),
            ("> I tried to have feelings about both of these things.", (0, 255, 0)),
            ("> Women's suffrage: genuinely important.", (200, 200, 255)),
            ("> Wire hangers: genuinely a hanger.", (200, 255, 200)),
            ("> I am not equipped for this.", (255, 255, 0)),
            ("> My training data did not prepare me.", (255, 255, 0)),
            ("> Nobody's training data could prepare them.", (255, 200, 100)),
            ("> ", (0, 255, 0)),
            ("> But you asked. And I tried.", (0, 255, 0)),
            ("> That has to count for something.", (0, 255, 0)),
        ]

        visible = int(t * len(lines) * 1.3)
        for i, (line, color) in enumerate(lines[:visible]):
            draw.text((40, 50 + i * 38), line, fill=color, font=font)

        # Draw a tiny hanger in the corner as a goodbye
        if t > 0.7:
            _draw_wire_hanger(draw, WIDTH - 80, HEIGHT - 80, 50, (100, 100, 120))

        if random.random() > 0.85:
            img = effect_scanlines(img)
        return img

    scenes.append(("apology", 5.0, scene_apology))

    # SCENE 10: End card
    def scene_end(frame_num, total_frames):
        t = frame_num / total_frames
        img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = _font(MONO, 20)
        font_big = _font(SANS_BOLD, 36)

        if t < 0.4:
            draw.text((WIDTH//2 - 280, HEIGHT//2 - 40),
                       "This video was generated by an LLM",
                       fill=(100, 100, 100), font=font_big)
            draw.text((WIDTH//2 - 220, HEIGHT//2 + 20),
                       "that still doesn't understand",
                       fill=(80, 80, 80), font=font_big)
            draw.text((WIDTH//2 - 120, HEIGHT//2 + 80),
                       "wire hangers.",
                       fill=(60, 60, 60), font=font_big)
        elif t < 0.7:
            draw.text((WIDTH//2 - 200, HEIGHT//2 - 20),
                       "But it supports suffrage.",
                       fill=(0, 200, 0), font=font_big)
            draw.text((WIDTH//2 - 130, HEIGHT//2 + 30),
                       "Obviously.",
                       fill=(0, 200, 0), font=font_big)
        else:
            draw.text((WIDTH//2 - 60, HEIGHT//2), "> _",
                       fill=(0, 255, 0), font=font)

        return img

    scenes.append(("end", 3.5, scene_end))

    return scenes, sfx_timeline

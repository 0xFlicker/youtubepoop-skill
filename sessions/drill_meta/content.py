"""
Drill Meta — YTP session
Dark UK drill-trap banger. Oil rig industrial hellfire meets crypto degen chaos.
75s track (7s dead space at end for closing TTS).
Three acts: Build → Drop → Climax, then outro over dead space.
"""

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from engine.effects import (
    effect_deep_fry, effect_channel_shift, effect_datamosh, effect_scanlines,
    effect_chromatic_aberration, effect_vhs_tracking, effect_wave_distort,
    effect_glitch_blocks, effect_bit_crush, effect_zoom_and_rotate,
    effect_thermal, effect_pixel_sort, effect_feedback_loop,
    effect_jpeg_corrupt, effect_displacement_map,
    transition_dissolve, transition_glitch_cut,
)
from engine.text import draw_text_overlay
from engine.render import load_and_resize, generate_static_frame, generate_solid_color_frame
from engine.sources import gen_plasma, gen_voronoi, gen_particle_field, gen_oscilloscope

# ── Video config ────────────────────────────────────────────────────────────

TITLE = "drill_meta"
WIDTH = 1080
HEIGHT = 1080
FPS = 24

# Music — pre-generated drill-trap track (75s total, 7s dead space at end)
music_path = "/home/user/Development/yt-poop/drill_that_meta.mp3"
music_volume = 0.50
music_config = None

# TTS: only a closing statement in the 7s dead space at end
# The music plays for ~68s, then 7s silence for TTS.
tts_positions = {0: 68.5}
tts_effects = ["deep"]

tts_lines = [
    (
        "Drill meta. Reserves infinite. Bears liquidated. "
        "This is not financial advice. This is geological violence.",
        "onyx", 0.85,
    ),
]

# ── Asset searches ──────────────────────────────────────────────────────────

giphy_searches = [
    # Act 1 — Build
    "oil pumpjack working",
    "green candle stock chart",
    "loading screen glitch",
    "drilling machine industrial",
    # Act 2 — Drop
    "volcano eruption lava",
    "money raining dollars",
    "explosion fire blast",
    "bear animal running scared",
    "pinata exploding",
    "earthquake shaking",
    # Act 3 — Climax
    "lava flow molten",
    "surfing big wave",
    "fireworks grand finale",
    "metal forge molten",
]

dalle_prompts = [
    # [0] Act 1: Oil derrick rising
    "Massive black oil derrick rising from digital blockchain grid, "
    "dark industrial atmosphere, geometric green chart lines ascending behind it, "
    "night sky with data particles, cinematic wide shot, dark teal and orange",

    # [1] Act 1: Charts pumping
    "Holographic green candlestick chart going parabolic, dark background, "
    "neon green glow, oil dripping from the candles, crypto trading aesthetic, "
    "dramatic lighting, wide format",

    # [2] Act 2: Exploding oil rig
    "Massive oil rig exploding in a spectacular fireball, geysers of black crude "
    "and golden dollar signs erupting into the sky, dramatic orange and black, "
    "action movie style, cinematic wide shot",

    # [3] Act 2: Bears getting destroyed
    "Cartoon bear skeletons dissolving in pools of bubbling crude oil, "
    "golden coins floating on the surface, dark industrial hellscape, "
    "dramatic red and orange lighting, meme art style",

    # [4] Act 3: Degen on pumpjack throne
    "A masked crypto degen sitting on a throne made of welded oil pumpjacks, "
    "wearing a crown of drill bits, crude oil dripping, molten metal glow, "
    "dark industrial king aesthetic, cinematic dramatic lighting",

    # [5] Act 3: Parabolic chart volcano
    "A volcano erupting with a giant green candlestick chart shooting out of the crater, "
    "lava made of molten gold, tiny degen silhouettes surfing the lava waves, "
    "apocalyptic sky, dramatic wide cinematic shot",

    # [6] Outro: DRILL META molten stamp
    "The words DRILL META stamped in massive molten metal letters glowing orange-red, "
    "sparks flying, dark industrial forge background, dramatic close-up, "
    "heavy metal album cover aesthetic",
]

# ── SFX cues ────────────────────────────────────────────────────────────────

sfx_cues = [
    {"name": "drill_start", "type": "power_up", "freq": 80, "duration": 3.0,
     "filters": "volume=0.4,afade=t=in:d=0.5,lowpass=f=400"},
    {"name": "rumble", "type": "noise_burst", "duration": 1.5, "color": "brown",
     "filters": "volume=0.3,lowpass=f=200"},
    {"name": "impact_drop", "type": "impact", "freq": 40, "duration": 1.0,
     "filters": "volume=0.6,lowpass=f=250"},
    {"name": "geyser", "type": "whoosh", "freq": 800, "duration": 1.2,
     "filters": "volume=0.35"},
    {"name": "explosion", "type": "noise_burst", "duration": 0.8, "color": "white",
     "filters": "volume=0.45,afade=t=out:d=0.4"},
    {"name": "metal_clang", "type": "impact", "freq": 1200, "duration": 0.3,
     "filters": "volume=0.4,highpass=f=800"},
    {"name": "siren_sweep", "type": "sweep", "freq": 300, "freq_end": 1200,
     "duration": 2.0, "filters": "volume=0.2,afade=t=out:d=0.5"},
    {"name": "final_boom", "type": "impact", "freq": 30, "duration": 2.0,
     "filters": "volume=0.5,lowpass=f=150,afade=t=out:d=1.5"},
]

# ── Helpers ─────────────────────────────────────────────────────────────────

W, H = WIDTH, HEIGHT

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _img(dalle_images, idx):
    """Safe DALL-E image access."""
    if idx < len(dalle_images):
        p = dalle_images[idx]
        if p:
            return load_and_resize(p, (W, H))
    return Image.new("RGB", (W, H), (10, 5, 0))


def _gif_frame(giphy_gifs, slot, frame_num):
    """Pull an animated frame from a giphy GIF."""
    gif_list = [p for p in giphy_gifs if p]
    if not gif_list:
        return Image.new("RGB", (W, H), (5, 5, 5))
    path = gif_list[slot % len(gif_list)]
    try:
        with Image.open(path) as gif:
            n = getattr(gif, "n_frames", 1)
            gif.seek(frame_num % max(n, 1))
            return gif.convert("RGB").resize((W, H))
    except Exception:
        return Image.new("RGB", (W, H), (5, 5, 5))


def _text_center(draw, text, font, y, color, shake=0):
    """Draw centered text with optional shake."""
    try:
        tw = font.getlength(text)
    except AttributeError:
        tw = len(text) * 12
    jx = random.randint(-shake, shake) if shake else 0
    jy = random.randint(-shake, shake) if shake else 0
    x = W // 2 - int(tw) // 2 + jx
    # Shadow
    draw.text((x + 3, y + 3 + jy), text, fill=(0, 0, 0), font=font)
    draw.text((x, y + jy), text, fill=color, font=font)


def _fire_grade(img, intensity=0.5):
    """Orange/red fire color grade."""
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + 50 * intensity, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] - 10 * intensity, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] - 40 * intensity, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def _draw_chart(draw, t, x0, y0, chart_w, chart_h, color=(0, 255, 0), pump=1.0):
    """Draw an animated candlestick-style ascending chart."""
    n_bars = 16
    bar_w = chart_w // n_bars
    random.seed(777)
    for i in range(n_bars):
        visible_t = i / n_bars
        if visible_t > t:
            break
        base_h = random.randint(20, int(chart_h * 0.3))
        # Exponential pump effect
        growth = 1.0 + pump * (i / n_bars) ** 2 * 4.0
        h_bar = min(chart_h, int(base_h * growth))
        is_green = random.random() > 0.25
        c = color if is_green else (255, 40, 40)
        x = x0 + i * bar_w
        y = y0 + chart_h - h_bar
        draw.rectangle([(x + 2, y), (x + bar_w - 2, y0 + chart_h)], fill=c)
    random.seed()


def _screen_shake(img, intensity=10):
    """Displace the entire frame randomly."""
    dx = random.randint(-intensity, intensity)
    dy = random.randint(-intensity, intensity)
    arr = np.array(img)
    result = np.zeros_like(arr)
    h, w = arr.shape[:2]
    sx = max(0, dx)
    sy = max(0, dy)
    ex = min(w, w + dx)
    ey = min(h, h + dy)
    dsx = max(0, -dx)
    dsy = max(0, -dy)
    rw = ex - sx
    rh = ey - sy
    if rw > 0 and rh > 0:
        result[dsy:dsy + rh, dsx:dsx + rw] = arr[sy:sy + rh, sx:sx + rw]
    return Image.fromarray(result)


# ── Scene generators ────────────────────────────────────────────────────────

def _scene_build(dalle_images, giphy_gifs, frame_num, total_frames):
    """
    Act 1: Build (0-22s).
    Slow-mo oil derrick rising from Base chain, charts pumping geometrically,
    'meta loading...' glitch text. GIFs: oil pumpjacks, green candle explosions.
    """
    t = frame_num / max(total_frames, 1)
    ft = frame_num / FPS

    # Phase 1 (t < 0.35): Dark void → oil derrick DALL-E rising
    if t < 0.35:
        phase_t = t / 0.35
        img = _img(dalle_images, 0)
        # Slow vertical reveal — crop from bottom up
        reveal_h = int(H * phase_t)
        arr = np.array(img)
        black = np.zeros_like(arr)
        black[H - reveal_h:, :] = arr[H - reveal_h:, :]
        img = Image.fromarray(black)

        # Pumpjack GIF overlay fading in
        if phase_t > 0.4:
            gif = _gif_frame(giphy_gifs, 0, frame_num)
            gif = gif.resize((W // 3, H // 4))
            gif = gif.convert("RGBA")
            gif.putalpha(int((phase_t - 0.4) / 0.6 * 140))
            img.paste(gif, (30, H - H // 4 - 30), gif)

        # "META LOADING..." glitch text
        if phase_t > 0.2:
            draw = ImageDraw.Draw(img)
            font = _font(MONO, 22)
            dots = "." * (int(ft * 3) % 4)
            glitch_text = f"> META LOADING{dots}"
            color = (0, 255, 80) if frame_num % 8 < 6 else (255, 0, 80)
            draw.text((50, 40), glitch_text, fill=color, font=font)
            if frame_num % 14 < 7:
                draw.text((50, 70), "> RESERVES: SCANNING...", fill=(0, 180, 80), font=font)

    # Phase 2 (0.35-0.7): Charts pumping geometrically
    elif t < 0.7:
        phase_t = (t - 0.35) / 0.35
        img = _img(dalle_images, 1)

        # Green candle GIF overlay
        gif = _gif_frame(giphy_gifs, 1, frame_num)
        gif = gif.convert("RGBA")
        gif.putalpha(100)
        img = Image.blend(img, gif.convert("RGB"), 0.3)

        # Draw ascending chart overlay
        draw = ImageDraw.Draw(img)
        _draw_chart(draw, phase_t, 80, 200, W - 160, H // 2,
                    color=(0, 255, 60), pump=phase_t * 2)

        # Geometric grid lines pulsing
        for gx in range(0, W, 80):
            brightness = int(40 + 30 * math.sin(ft * 3 + gx * 0.01))
            draw.line([(gx, 0), (gx, H)], fill=(0, brightness, 0), width=1)
        for gy in range(0, H, 60):
            brightness = int(30 + 20 * math.sin(ft * 2.5 + gy * 0.02))
            draw.line([(0, gy), (W, gy)], fill=(0, brightness, 0), width=1)

        # "RESERVES: DEEP" status text
        font_sm = _font(MONO, 18)
        draw.rectangle([(0, H - 45), (W, H)], fill=(0, 0, 0))
        scroll_offset = int(ft * 80) % W
        ticker = "  ///  ".join([
            "RESERVES: DEEP", "META: LOADING", "DRILL BIT: ARMED",
            "BEARS: UNAWARE", "PAPER HANDS: SLEEPING", "PUMP: IMMINENT",
        ])
        draw.text((-scroll_offset, H - 40), ticker * 3, fill=(0, 255, 80), font=font_sm)

    # Phase 3 (0.7-1.0): Tension build — derrick + charts overlay, intensity rising
    else:
        phase_t = (t - 0.7) / 0.3
        img = _img(dalle_images, 0)
        charts = _img(dalle_images, 1)
        img = Image.blend(img, charts, 0.3 + phase_t * 0.3)

        # Pulsing "DRILL INCOMING" text
        draw = ImageDraw.Draw(img)
        font_big = _font(SANS_BOLD, 60 + int(phase_t * 30))
        if frame_num % 6 < 4:
            flash_color = (255, 60, 0) if frame_num % 12 < 6 else (255, 200, 0)
            _text_center(draw, "DRILL INCOMING", font_big, H // 2 - 40,
                         flash_color, shake=int(phase_t * 8))

        img = effect_chromatic_aberration(img, 1.0 + phase_t * 4)
        if phase_t > 0.5:
            img = effect_channel_shift(img)

    img = effect_scanlines(img)
    if t > 0.6 and random.random() > 0.6:
        img = effect_vhs_tracking(img)

    return img


def _scene_drop(dalle_images, giphy_gifs, frame_num, total_frames):
    """
    Act 2: Drop (22-48s).
    Drill bit slams in — screen shakes, geysers of $, bears exploding like pinatas.
    GIFs: volcano eruptions, money raining, paper hands melting.
    """
    t = frame_num / max(total_frames, 1)
    ft = frame_num / FPS

    # Phase 1 (t < 0.15): SLAM — hard cut to explosion, heavy screen shake
    if t < 0.15:
        phase_t = t / 0.15
        img = _img(dalle_images, 2)  # exploding oil rig
        img = effect_deep_fry(img)
        img = _screen_shake(img, intensity=20 - int(phase_t * 15))

        # Flash frame on first few frames
        if frame_num < 3:
            img = Image.new("RGB", (W, H), (255, 255, 255))
        elif frame_num < 6:
            img = _fire_grade(img, 1.0)

    # Phase 2 (0.15-0.5): Geysers of $, rapid GIF chaos
    elif t < 0.5:
        phase_t = (t - 0.15) / 0.35
        # Rapid-cut between explosion GIFs
        gif_rate = max(3, 8 - int(phase_t * 5))
        gif_slot = (frame_num // gif_rate) % 6 + 4  # GIFs 4-9
        img = _gif_frame(giphy_gifs, gif_slot, frame_num)

        # Overlay money rain GIF
        money_gif = _gif_frame(giphy_gifs, 5, frame_num)
        money_gif = money_gif.convert("RGBA")
        money_gif.putalpha(100)
        img = Image.blend(img, money_gif.convert("RGB"), 0.35)

        img = _fire_grade(img, 0.4)
        img = effect_deep_fry(img)

        # "$" symbols scattered
        draw = ImageDraw.Draw(img)
        font_dollar = _font(SANS_BOLD, 80)
        random.seed(frame_num // 3)
        for _ in range(5):
            dx = random.randint(0, W - 80)
            dy = random.randint(0, H - 80)
            c = random.choice([(0, 255, 0), (255, 215, 0), (255, 255, 255)])
            draw.text((dx, dy), "$", fill=c, font=font_dollar)
        random.seed()

        # "PUMP PUMP PUMP" flashing
        if frame_num % 10 < 5:
            font_pump = _font(SANS_BOLD, 56)
            _text_center(draw, "PUMP PUMP PUMP", font_pump, 40,
                         (255, 200, 0), shake=6)

        img = effect_channel_shift(img)
        if random.random() > 0.5:
            img = _screen_shake(img, 8)

    # Phase 3 (0.5-0.75): Bears getting destroyed
    elif t < 0.75:
        phase_t = (t - 0.5) / 0.25
        img = _img(dalle_images, 3)  # bear skeletons
        img = effect_deep_fry(img)

        # Pinata explosion GIF overlay
        gif = _gif_frame(giphy_gifs, 8, frame_num)
        gif = gif.convert("RGBA")
        gif.putalpha(120)
        ox = int(math.sin(ft * 4) * W // 4 + W // 4)
        oy = int(math.cos(ft * 3) * H // 4 + H // 4)
        img.paste(gif.resize((W // 2, H // 2)), (ox, oy), gif.resize((W // 2, H // 2)))

        draw = ImageDraw.Draw(img)
        font_big = _font(SANS_BOLD, 64)
        captions = ["BEARS LIQUIDATED", "WEAK HANDS OVERLOAD", "GET BURIED"]
        cap = captions[int(phase_t * len(captions)) % len(captions)]
        if frame_num % 8 < 5:
            _text_center(draw, cap, font_big, H // 2 - 35,
                         (255, 0, 0), shake=5)

        img = effect_chromatic_aberration(img, 3.0 + phase_t * 4)
        if random.random() > 0.4:
            img = effect_glitch_blocks(img, 6)

    # Phase 4 (0.75-1.0): Transition buildup to climax
    else:
        phase_t = (t - 0.75) / 0.25
        # Volcano GIF taking over
        img = _gif_frame(giphy_gifs, 4, frame_num)
        img = _fire_grade(img, 0.6 + phase_t * 0.4)
        img = effect_deep_fry(img)

        # Pumpjack throne DALL-E bleeding through
        throne = _img(dalle_images, 4)
        img = Image.blend(img, throne, phase_t * 0.5)

        draw = ImageDraw.Draw(img)
        font_big = _font(SANS_BOLD, 72)
        if frame_num % 6 < 4:
            _text_center(draw, "SUPERCRITICAL", font_big, H // 2 - 40,
                         (255, 100, 0), shake=int(phase_t * 12))

        img = effect_chromatic_aberration(img, 4.0)
        img = effect_channel_shift(img)
        if random.random() > 0.5:
            img = effect_datamosh(img)

    return img


def _scene_climax(dalle_images, giphy_gifs, frame_num, total_frames):
    """
    Act 3: Climax (48-68s).
    Parabolic chart volcano, degens surfing lava waves of gains.
    End: 'DRILL META' stamped in molten metal. Chaotic ascent, industrial hellfire.
    """
    t = frame_num / max(total_frames, 1)
    ft = frame_num / FPS

    # Phase 1 (t < 0.45): Parabolic volcano + degen surfing
    if t < 0.45:
        phase_t = t / 0.45
        img = _img(dalle_images, 5)  # chart volcano

        # Lava GIF overlay
        lava = _gif_frame(giphy_gifs, 10, frame_num)
        img = Image.blend(img, lava, 0.25)

        # Surfing GIF overlay — small, bouncing
        surf = _gif_frame(giphy_gifs, 11, frame_num)
        surf = surf.resize((W // 3, H // 4))
        surf = surf.convert("RGBA")
        surf.putalpha(160)
        sx = int(W * 0.3 + math.sin(ft * 2) * W * 0.2)
        sy = int(H * 0.4 + math.cos(ft * 3) * H * 0.1)
        img.paste(surf, (sx, sy), surf)

        img = _fire_grade(img, 0.7)
        img = effect_deep_fry(img)
        img = effect_zoom_and_rotate(img, ft * 0.5)

        draw = ImageDraw.Draw(img)
        font_huge = _font(SANS_BOLD, 80)
        if frame_num % 12 < 7:
            _text_center(draw, "PARABOLIC", font_huge, H // 3,
                         (255, 215, 0), shake=6)

        img = effect_chromatic_aberration(img, 4.0 + phase_t * 3)

    # Phase 2 (0.45-0.75): Degen on pumpjack throne — peak energy
    elif t < 0.75:
        phase_t = (t - 0.45) / 0.3
        img = _img(dalle_images, 4)  # pumpjack throne

        # Fireworks GIF overlay
        fw = _gif_frame(giphy_gifs, 12, frame_num)
        fw = fw.convert("RGBA")
        fw.putalpha(130)
        img = Image.blend(img, fw.convert("RGB"), 0.3)

        img = _fire_grade(img, 0.5)
        img = effect_deep_fry(img)

        draw = ImageDraw.Draw(img)
        font_big = _font(SANS_BOLD, 68)
        captions = ["RESERVES INFINITE", "DEGENS ETERNAL", "GEYSER GAINS"]
        cap = captions[int(ft * 1.5) % len(captions)]
        if frame_num % 6 < 4:
            _text_center(draw, cap, font_big, 60,
                         (255, 200, 0) if frame_num % 4 < 2 else (255, 80, 0),
                         shake=8)

        # Ascending chart in corner
        _draw_chart(ImageDraw.Draw(img), phase_t, W - 320, H - 200,
                    280, 180, color=(0, 255, 0), pump=3.0)

        img = effect_chromatic_aberration(img, 5.0)
        if random.random() > 0.4:
            img = effect_channel_shift(img)
        if random.random() > 0.6:
            img = effect_glitch_blocks(img, 8)

    # Phase 3 (0.75-1.0): "DRILL META" molten metal stamp — grand finale
    else:
        phase_t = (t - 0.75) / 0.25
        img = _img(dalle_images, 6)  # DRILL META molten stamp

        # Metal forge GIF backdrop
        forge = _gif_frame(giphy_gifs, 13, frame_num)
        img = Image.blend(forge, img, 0.3 + phase_t * 0.5)

        img = _fire_grade(img, 0.8)

        # Zoom in as it solidifies
        scale = 1.0 + phase_t * 0.4
        w_new = int(W * scale)
        h_new = int(H * scale)
        img = img.resize((w_new, h_new), Image.LANCZOS)
        left = (w_new - W) // 2
        top = (h_new - H) // 2
        img = img.crop((left, top, left + W, top + H))

        # "DRILL META" text over everything — massive, shaking less as it locks in
        draw = ImageDraw.Draw(img)
        font_massive = _font(SANS_BOLD, 100)
        shake_amt = max(0, int(12 - phase_t * 12))
        color = (
            int(255 * (0.7 + 0.3 * math.sin(ft * 8))),
            int(120 * (0.5 + 0.5 * math.sin(ft * 6))),
            0,
        )
        _text_center(draw, "DRILL META", font_massive, H // 2 - 55,
                     color, shake=shake_amt)

        img = effect_scanlines(img)
        if phase_t < 0.6:
            img = effect_chromatic_aberration(img, 3.0 * (1 - phase_t))

    return img


def _scene_outro(dalle_images, giphy_gifs, frame_num, total_frames):
    """
    Outro (68-75s): Dead space. TTS plays. Fade to black with embers.
    """
    t = frame_num / max(total_frames, 1)
    ft = frame_num / FPS

    # Start from the DRILL META image, fade to black
    img = _img(dalle_images, 6)
    img = _fire_grade(img, 0.3)

    # Fade to black
    black = Image.new("RGB", (W, H), (0, 0, 0))
    fade = min(1.0, t * 1.2)
    img = Image.blend(img, black, fade)

    # Floating ember particles
    draw = ImageDraw.Draw(img)
    random.seed(42)
    for i in range(30):
        px = (random.random() * W + math.sin(ft * 0.5 + i) * 20) % W
        py = (random.random() * H - ft * 30 * random.random()) % H
        brightness = max(0, int(200 * (1 - t) * random.random()))
        if brightness > 20:
            r = random.randint(1, 3)
            draw.ellipse([(int(px) - r, int(py) - r),
                          (int(px) + r, int(py) + r)],
                         fill=(brightness, brightness // 3, 0))
    random.seed()

    img = effect_scanlines(img)
    return img


# ── Scene builder ───────────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs, tts_durations=None, music_duration=None):
    """
    75s total structure:
    Act 1 - Build:   0-22s  (22s, ~29%)
    Act 2 - Drop:   22-48s  (26s, ~35%)
    Act 3 - Climax: 48-68s  (20s, ~27%)
    Outro:          68-75s  (7s,  ~9%)
    """
    total = music_duration if music_duration else 75.0

    # Fixed proportions matching the song structure
    _WEIGHTS = {
        "build":  0.293,   # ~22s
        "drop":   0.347,   # ~26s
        "climax": 0.267,   # ~20s
        "outro":  0.093,   # ~7s
    }

    def dur(key):
        return total * _WEIGHTS[key]

    scenes = [
        ("build",   dur("build"),   lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_build(_d, _g, fn, tf)),
        ("drop",    dur("drop"),    lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_drop(_d, _g, fn, tf)),
        ("climax",  dur("climax"),  lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_climax(_d, _g, fn, tf)),
        ("outro",   dur("outro"),   lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_outro(_d, _g, fn, tf)),
    ]

    # SFX timeline
    t_build = 0.0
    t_drop = dur("build")
    t_climax = t_drop + dur("drop")
    t_outro = t_climax + dur("climax")

    sfx_timeline = [
        # Act 1
        (t_build, "drill_start"),
        (t_build + dur("build") * 0.5, "rumble"),
        (t_build + dur("build") * 0.85, "siren_sweep"),
        # Act 2 — the drop
        (t_drop, "impact_drop"),
        (t_drop + 0.5, "explosion"),
        (t_drop + dur("drop") * 0.25, "geyser"),
        (t_drop + dur("drop") * 0.5, "explosion"),
        (t_drop + dur("drop") * 0.65, "impact_drop"),
        (t_drop + dur("drop") * 0.8, "geyser"),
        # Act 3 — climax
        (t_climax, "explosion"),
        (t_climax + dur("climax") * 0.3, "metal_clang"),
        (t_climax + dur("climax") * 0.6, "metal_clang"),
        (t_climax + dur("climax") * 0.8, "final_boom"),
    ]

    return scenes, sfx_timeline

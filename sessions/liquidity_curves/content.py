"""
YTP Session: Liquidity Curves

The violent mathematics of automated market making.
x * y = k — the equation that replaced the trading floor.
Bonding curves, concentrated liquidity, slippage nightmares,
and the infinite rebalancing act of DeFi.

Every swap moves the price. Every pool tells a story.
The curve never forgets.
"""

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from engine.effects import (
    effect_deep_fry, effect_channel_shift, effect_datamosh,
    effect_scanlines, effect_invert_glitch, effect_zoom_and_rotate,
    effect_pixel_sort, effect_vhs_tracking, effect_chromatic_aberration,
    effect_wave_distort, effect_glitch_blocks,
    effect_feedback_loop, effect_thermal, effect_posterize,
    effect_jpeg_corrupt, effect_displacement_map,
    transition_dissolve, transition_glitch_cut, transition_pixel_scatter,
)
from engine.text import draw_text_overlay
from engine.render import load_and_resize, generate_static_frame
from engine.sources import (
    gen_plasma, gen_voronoi, gen_particle_field,
    gen_oscilloscope, gen_circuit_board, gen_strange_attractor,
    gen_ascii_matrix, ffmpeg_mandelbrot_frame,
)

# ── Session Config ──────────────────────────────────────────────────────────
TITLE = "liquidity_curves"
WIDTH, HEIGHT = 1080, 1080
FPS = 24

# Pre-generated ACE-Step track (F minor, 88 BPM, dark cyberpunk ambient)
music_path = "/home/user/Development/yt-poop/sessions/liquidity_curves/build/audio/generated_music.mp3"
music_volume = 0.35
music_config = None

# ── Content ─────────────────────────────────────────────────────────────────

# GIF slots (2 per search = indices 0-15):
#   0-1: swimming pool      2-3: water flowing      4-5: stock market chart
#   6-7: pancake flip       8-9: balancing act      10-11: money rain
#  12-13: math equations   14-15: trading floor
giphy_searches = [
    "swimming pool water",
    "water flowing pipe",
    "stock market chart",
    "pancake flip cooking",
    "balancing act circus",
    "money rain",
    "math equations chalkboard",
    "trading floor chaos",
]

dalle_prompts = [
    # [0] AMM: Robot market maker
    "A robotic figure standing behind a trading desk made of glowing mathematical "
    "curves, two streams of colorful tokens flowing through its hands, dark neon "
    "background, cyberpunk financial aesthetic, dramatic blue and purple lighting",

    # [1] The Pool: Liquidity pool as actual pool
    "An overhead view of a luminous swimming pool filled with golden coins and "
    "crypto tokens instead of water, the pool shaped like a hyperbolic curve, "
    "neon blue glow from beneath, dark surroundings, surreal photorealistic",

    # [2] Slippage: Person sliding on coins
    "A person in a business suit dramatically slipping and falling on a floor "
    "covered in scattered coins and tokens, motion blur, their briefcase flying "
    "open with charts and graphs spilling out, dark comedic photorealistic style",

    # [3] Concentrated liquidity: Laser focus
    "A massive magnifying glass focusing scattered points of light into a single "
    "intense beam on a narrow band of a glowing price chart, mathematical grid "
    "in background, sci-fi laboratory aesthetic, dramatic volumetric lighting",

    # [4] Yield: Money tree growing from computer
    "A bioluminescent tree growing out of a computer monitor, its branches made "
    "of circuit traces, its leaves are golden coins, roots are ethernet cables "
    "going into the ground, dark forest background, magical realism photography",

    # [5] Curve wars: Battle of the DEXes
    "An epic battle scene where armies of mathematical curves clash like waves, "
    "each curve a different neon color, the battlefield is a giant coordinate "
    "plane, explosions of data points where curves intersect, cinematic wide shot",
]

tts_lines = [
    # Act 1: The Pool (clips 0-2)
    ("In the beginning, there was no order book. There was only the curve.", "onyx", 0.9),
    ("x times y equals k. The most important equation in decentralized finance. Memorize it. Tattoo it. It is your god now.", "echo", 1.0),
    ("Two tokens enter. The ratio shifts. The price moves. Nobody asked permission. Nobody needed to.", "fable", 1.0),

    # Act 2: The Swap (clips 3-5)
    ("You want to swap token zero for token one? Sure. But the curve decides the price. Not you. Never you.", "alloy", 1.0),
    ("Slippage: zero point three percent. Zero point five. Two percent. Five. Twelve. Your sandwich has been eaten.", "nova", 1.1),
    ("Price impact warning. Price impact warning. PRICE IMPACT WARNING.", "onyx", 1.3),

    # Act 3: The DEXes (clips 6-8)
    ("Uniswap. Curve. PancakeSwap. Aerodrome. Orca. Fluid. So many pools. So little liquidity.", "shimmer", 1.1),
    ("Concentrated liquidity. You pick your range. You become the market maker. Tick by tick by tick.", "echo", 0.9),
    ("But if the price leaves your range? You're holding the wrong token. One hundred percent impermanent loss. Congratulations.", "fable", 1.0),

    # Act 4: The Meta (clips 9-11)
    ("Hooks. Callbacks. Custom curves. Uniswap V4 said: what if the pool could think?", "alloy", 0.9),
    ("Doppler curves. Time-weighted bonding. Zora's flywheel. The curve is recursive.", "nova", 0.85),
    ("Fees flow to liquidity providers. Yield compounds. The pool deepens. The slippage shrinks. The flywheel spins.", "shimmer", 0.9),

    # Coda (clip 12)
    ("You are the liquidity. The liquidity is you. Now go rebalance your position before it's too late.", "onyx", 0.8),
]

tts_effects = [
    "normal", "echo", "normal",          # Act 1: clean intro then reverb on equation
    "normal", "fast", "stutter",          # Act 2: accelerating panic
    "normal", "normal", "telephone",      # Act 3: DEX info dump
    "echo", "chorus", "normal",           # Act 4: ethereal meta
    "deep",                               # Coda: ominous
]

music_config = {
    "layers": [
        # Sub bass pulse — the heartbeat of the pool
        {"type": "sine", "freq": 45, "duration": 90, "volume": 0.015,
         "filters": "tremolo=f=0.5:d=0.6"},
        # Detuned fifth — tension of the curve
        {"type": "sine", "freq": 67.5, "duration": 90, "volume": 0.01,
         "filters": "tremolo=f=0.8:d=0.3"},
        # Sawtooth lead — the swap happening
        {"type": "sawtooth", "freq": 180, "duration": 90, "volume": 0.006,
         "filters": "lowpass=f=800,vibrato=f=3:d=0.15"},
        # FM shimmer — fees accruing
        {"type": "fm", "freq": 440, "mod_freq": 5, "mod_depth": 30,
         "duration": 90, "volume": 0.004,
         "filters": "lowpass=f=1500,tremolo=f=0.3:d=0.2"},
        # Pink noise bed — market microstructure
        {"type": "noise", "color": "pink", "duration": 90, "volume": 0.005,
         "filters": "lowpass=f=400,highpass=f=60"},
        # Arpeggio — the flywheel
        {"type": "arpeggio", "notes": [110, 138.59, 164.81, 220, 164.81, 138.59],
         "step_duration": 0.3, "duration": 90, "volume": 0.004,
         "filters": "lowpass=f=1200,tremolo=f=0.2:d=0.1"},
    ],
    "master_filters": "vibrato=f=0.1:d=0.08",
    "mix_volume": 0.28,
}

sfx_cues = [
    {"name": "pool_splash", "type": "noise_burst", "duration": 0.6,
     "color": "white", "filters": "lowpass=f=800,afade=t=in:d=0.05,afade=t=out:d=0.4,volume=0.3"},
    {"name": "swap_blip", "type": "tone", "freq": 660, "duration": 0.12,
     "filters": "afade=t=out:d=0.1,volume=0.4"},
    {"name": "slippage_alarm", "type": "sweep", "freq": 1500, "freq_end": 200,
     "duration": 1.5, "filters": "volume=0.25,tremolo=f=8:d=0.6"},
    {"name": "price_impact", "type": "impact", "freq": 60, "duration": 0.5,
     "filters": "volume=0.5"},
    {"name": "tick_click", "type": "tone", "freq": 2200, "duration": 0.05,
     "filters": "afade=t=out:d=0.04,volume=0.3"},
    {"name": "rebalance_whoosh", "type": "whoosh", "freq": 1200, "duration": 0.7,
     "filters": "volume=0.3"},
    {"name": "fee_ding", "type": "tone", "freq": 1320, "duration": 0.2,
     "filters": "afade=t=out:d=0.15,volume=0.35"},
    {"name": "glitch_burst", "type": "glitch", "duration": 0.3,
     "filters": "volume=0.25"},
    {"name": "error_buzz", "type": "tone", "freq": 55, "duration": 0.6,
     "filters": "vibrato=f=25:d=0.9,volume=0.3"},
    {"name": "power_up", "type": "power_up", "freq": 220, "duration": 1.0,
     "filters": "volume=0.3,afade=t=out:d=0.3"},
]

# ── Constants & Helpers ────────────────────────────────────────────────────

W, H = WIDTH, HEIGHT
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Palette
CURVE_CYAN = (0, 255, 210)
POOL_BLUE = (30, 80, 220)
SWAP_GREEN = (0, 255, 100)
FEE_GOLD = (255, 200, 40)
SLIPPAGE_RED = (255, 40, 60)
STABLE_PINK = (255, 100, 200)
DARK_BG = (5, 5, 15)

DEXES = [
    "Uniswap V3", "Uniswap V4", "Curve", "PancakeSwap",
    "Aerodrome", "SlipStream", "PancakeSwap Infinity CLMM",
    "Orca", "Fluid", "Humidifi",
]


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _img(dalle_images, idx):
    if idx < len(dalle_images) and dalle_images[idx]:
        return load_and_resize(dalle_images[idx], (W, H))
    return Image.new("RGB", (W, H), DARK_BG)


def _gif_frame(giphy_gifs, slot, frame_num):
    gifs = [p for p in giphy_gifs if p]
    if not gifs:
        return Image.new("RGB", (W, H), DARK_BG)
    path = gifs[slot % len(gifs)]
    try:
        with Image.open(path) as gif:
            n = getattr(gif, "n_frames", 1)
            gif.seek(frame_num % max(n, 1))
            return gif.convert("RGB").resize((W, H))
    except Exception:
        return Image.new("RGB", (W, H), DARK_BG)


def _additive_blend(img_a, img_b, amount=0.3):
    """Additive blend img_b onto img_a at given amount."""
    a = np.array(img_a, dtype=np.float32)
    b = np.array(img_b, dtype=np.float32)
    return Image.fromarray(np.clip(a + b * amount, 0, 255).astype(np.uint8))


def _draw_xy_curve(draw, cx, cy, scale=200, color=CURVE_CYAN, k=1.0):
    """Draw the x*y=k hyperbola centered at (cx, cy)."""
    points = []
    for i in range(1, 300):
        x_val = i * 0.02
        y_val = k / x_val
        sx = int(cx + (x_val - 3.0) * scale / 3.0)
        sy = int(cy - (y_val - 3.0) * scale / 3.0)
        if 0 <= sx < W and 0 <= sy < H:
            points.append((sx, sy))
    if len(points) > 2:
        draw.line(points, fill=color, width=3)


def _draw_stableswap_curve(draw, cx, cy, scale=200, color=STABLE_PINK):
    """Draw a StableSwap curve (flatter in the middle, steep at edges)."""
    points = []
    A = 10  # amplification factor
    for i in range(1, 300):
        x_val = i * 0.02
        # Approximate stableswap: blend of constant-sum and constant-product
        y_cp = 9.0 / x_val  # constant product
        y_cs = 6.0 - x_val  # constant sum (shifted)
        w = A / (A + 1)
        y_val = w * y_cs + (1 - w) * y_cp
        sx = int(cx + (x_val - 3.0) * scale / 3.0)
        sy = int(cy - (y_val - 3.0) * scale / 3.0)
        if 0 <= sx < W and 0 <= sy < H:
            points.append((sx, sy))
    if len(points) > 2:
        draw.line(points, fill=color, width=3)


def _draw_swap_dot(draw, t, cx, cy, scale=200, k=1.0):
    """Animate a dot moving along the x*y=k curve."""
    x_val = 1.0 + t * 4.0
    y_val = k / x_val
    sx = int(cx + (x_val - 3.0) * scale / 3.0)
    sy = int(cy - (y_val - 3.0) * scale / 3.0)
    r = 8
    draw.ellipse([(sx - r, sy - r), (sx + r, sy + r)],
                 fill=SWAP_GREEN, outline=(255, 255, 255))
    return sx, sy


def _draw_price_bar(draw, label, value, x, y, w, color, font):
    """Draw a labeled metric bar."""
    draw.text((x, y - 18), label, fill=(180, 180, 180), font=font)
    bar_w = int(min(value, 1.0) * w)
    draw.rectangle([(x, y), (x + bar_w, y + 12)], fill=color)
    draw.rectangle([(x, y), (x + w, y + 12)], outline=(60, 60, 60))


def _draw_grid(draw, width, height):
    """Draw a subtle coordinate grid."""
    for gx in range(0, width, 40):
        draw.line([(gx, 0), (gx, height)], fill=(15, 15, 30), width=1)
    for gy in range(0, height, 40):
        draw.line([(0, gy), (width, gy)], fill=(15, 15, 30), width=1)


def _draw_axes(draw, cx, cy, scale):
    """Draw x/y axes."""
    draw.line([(cx - scale, cy), (cx + scale, cy)], fill=(80, 80, 80), width=1)
    draw.line([(cx, cy - scale), (cx, cy + scale)], fill=(80, 80, 80), width=1)


def _bonding_curve_frame(t, width, height, giphy_gifs=None, frame_num=0):
    """Draw animated bonding curve with live metric bars."""
    img = Image.new("RGB", (width, height), DARK_BG)

    # Blend math equations GIF into background (slots 12-13)
    if giphy_gifs:
        bg_gif = _gif_frame(giphy_gifs, 12, frame_num)
        img = _additive_blend(img, bg_gif, 0.08)

    draw = ImageDraw.Draw(img)
    font = _font(MONO, 20)
    font_eq = _font(MONO_BOLD, 48)
    font_bar = _font(MONO, 14)

    cx, cy = width // 2, height // 2

    _draw_grid(draw, width, height)
    _draw_axes(draw, cx, cy, 250)
    _draw_xy_curve(draw, cx, cy, scale=250, k=9.0)

    # Animated swap dot
    dot_x, dot_y = _draw_swap_dot(draw, t, cx, cy, scale=250, k=9.0)

    # Token labels
    draw.text((width - 160, cy + 10), "token0", fill=CURVE_CYAN, font=font)
    draw.text((cx + 10, 30), "token1", fill=CURVE_CYAN, font=font)

    # Live metric bars — reserve ratios shift as dot moves
    x_val = 1.0 + t * 4.0
    y_val = 9.0 / x_val
    reserve0_pct = min(1.0, x_val / 5.0)
    reserve1_pct = min(1.0, y_val / 9.0)
    price = y_val / x_val if x_val > 0 else 0
    price_pct = min(1.0, price / 4.0)

    bar_x, bar_w = 40, 180
    _draw_price_bar(draw, "reserve0", reserve0_pct, bar_x, 50, bar_w, CURVE_CYAN, font_bar)
    _draw_price_bar(draw, "reserve1", reserve1_pct, bar_x, 90, bar_w, FEE_GOLD, font_bar)
    _draw_price_bar(draw, "price", price_pct, bar_x, 130, bar_w, SWAP_GREEN, font_bar)

    # Equation overlay
    eq_fade = min(1.0, t * 3)
    eq_color = tuple(int(v * eq_fade) for v in FEE_GOLD)
    draw.text((40, height - 80), "x * y = k", fill=eq_color, font=font_eq)

    return img


def _slippage_frame(t, width, height, giphy_gifs=None, frame_num=0):
    """Visualize slippage getting worse as trade size increases."""
    img = Image.new("RGB", (width, height), DARK_BG)

    # Blend stock chart GIF into background (slots 4-5)
    if giphy_gifs:
        bg_gif = _gif_frame(giphy_gifs, 4, frame_num)
        img = _additive_blend(img, bg_gif, 0.06)

    draw = ImageDraw.Draw(img)
    font = _font(MONO, 22)
    font_big = _font(SANS_BOLD, 40)
    font_bar = _font(MONO, 14)

    cx, cy = width // 2, height // 2 + 30

    _draw_axes(draw, cx, cy, 220)
    _draw_xy_curve(draw, cx, cy, scale=220, k=9.0, color=(40, 100, 80))

    # Animate a big swap — dot moves far along curve
    swap_progress = min(1.0, t * 1.5)
    x_start = 1.5
    x_end = 1.5 + swap_progress * 3.5
    y_start = 9.0 / x_start
    y_end = 9.0 / x_end

    # Draw the swap region (shaded green-to-red)
    for i in range(50):
        frac = i / 50.0
        x_val = x_start + frac * (x_end - x_start)
        y_val = 9.0 / x_val
        sx = int(cx + (x_val - 3.0) * 220 / 3.0)
        sy = int(cy - (y_val - 3.0) * 220 / 3.0)
        r = int(frac * 255)
        g = int((1 - frac) * 255)
        if 0 <= sx < width and 0 <= sy < height:
            draw.line([(sx, sy), (sx, cy)], fill=(r, g, 0), width=2)

    # Slippage calculation
    if x_end > x_start:
        ideal_price = y_start / x_start
        actual_price = (y_start - y_end) / (x_end - x_start)
        slippage_pct = abs(1 - actual_price / ideal_price) * 100
    else:
        slippage_pct = 0

    if slippage_pct < 1:
        slip_color = SWAP_GREEN
    elif slippage_pct < 5:
        slip_color = FEE_GOLD
    else:
        slip_color = SLIPPAGE_RED

    draw.text((40, 20), f"SLIPPAGE: {slippage_pct:.1f}%", fill=slip_color, font=font_big)

    # Metric bars — slippage, trade size, price impact
    bar_x = width - 240
    _draw_price_bar(draw, "trade size", swap_progress, bar_x, 40, 180,
                    FEE_GOLD, font_bar)
    _draw_price_bar(draw, "slippage", min(1.0, slippage_pct / 30.0), bar_x, 80, 180,
                    slip_color, font_bar)
    _draw_price_bar(draw, "price impact", min(1.0, slippage_pct / 20.0), bar_x, 120, 180,
                    SLIPPAGE_RED, font_bar)

    trade_size = swap_progress * 100
    draw.text((40, 65), f"Trade size: {trade_size:.0f} ETH", fill=(180, 180, 180), font=font)

    if slippage_pct > 10:
        if int(t * 15) % 2:
            draw.text((width // 2 - 280, height - 100),
                       "PRICE IMPACT WARNING", fill=SLIPPAGE_RED, font=font_big)

    return img


def _multi_curve_frame(t, width, height):
    """Compare constant product vs stableswap vs concentrated liquidity curves."""
    img = Image.new("RGB", (width, height), DARK_BG)
    draw = ImageDraw.Draw(img)
    font = _font(MONO, 18)
    font_big = _font(SANS_BOLD, 32)

    cx, cy = width // 2, height // 2
    scale = 220

    _draw_grid(draw, width, height)
    _draw_axes(draw, cx, cy, scale)

    # Phase in each curve
    if t > 0.0:
        _draw_xy_curve(draw, cx, cy, scale=scale, k=9.0, color=CURVE_CYAN)
        draw.text((width - 280, height - 110), "x*y=k", fill=CURVE_CYAN, font=font)
    if t > 0.3:
        _draw_stableswap_curve(draw, cx, cy, scale=scale, color=STABLE_PINK)
        draw.text((width - 280, height - 85), "StableSwap", fill=STABLE_PINK, font=font)
    if t > 0.6:
        # Concentrated: only draw the curve in a narrow range (thick)
        points = []
        x_lo, x_hi = 2.0, 4.0
        for i in range(1, 300):
            x_val = i * 0.02
            if x_lo <= x_val <= x_hi:
                y_val = 9.0 / x_val
                sx = int(cx + (x_val - 3.0) * scale / 3.0)
                sy = int(cy - (y_val - 3.0) * scale / 3.0)
                if 0 <= sx < W and 0 <= sy < H:
                    points.append((sx, sy))
        if len(points) > 2:
            draw.line(points, fill=SWAP_GREEN, width=6)
        draw.text((width - 280, height - 60), "Concentrated", fill=SWAP_GREEN, font=font)

    # Animated dot traverses the CP curve
    _draw_swap_dot(draw, t, cx, cy, scale=scale, k=9.0)

    draw.text((40, 20), "CURVE COMPARISON", fill=(200, 200, 200), font=font_big)

    return img


def _doppler_curve_frame(t, width, height):
    """Doppler/time-weighted bonding curve — price decays over time."""
    img = Image.new("RGB", (width, height), DARK_BG)
    draw = ImageDraw.Draw(img)
    font = _font(MONO, 18)
    font_big = _font(SANS_BOLD, 28)
    font_eq = _font(MONO_BOLD, 36)

    _draw_grid(draw, width, height)

    # Draw multiple time-decayed curves
    cx, cy = width // 2, height // 2
    scale = 200
    _draw_axes(draw, cx, cy, scale)

    n_curves = 5
    visible = int(t * n_curves * 1.5) + 1
    for c in range(min(visible, n_curves)):
        # Each curve: price = start_price * e^(-decay * time)
        decay = 0.3 + c * 0.15
        hue = c / n_curves
        r = int(255 * (0.5 + 0.5 * math.sin(hue * 6.28)))
        g = int(255 * (0.5 + 0.5 * math.sin(hue * 6.28 + 2.09)))
        b = int(255 * (0.5 + 0.5 * math.sin(hue * 6.28 + 4.19)))
        color = (min(255, r), min(255, g), min(255, b))

        points = []
        for i in range(300):
            x_val = i / 50.0
            y_val = 5.0 * math.exp(-decay * x_val)
            sx = int(cx - scale + x_val * scale / 3.0)
            sy = int(cy - (y_val - 2.5) * scale / 2.5)
            if 0 <= sx < width and 0 <= sy < height:
                points.append((sx, sy))
        if len(points) > 2:
            draw.line(points, fill=color, width=2)

    # Moving time cursor
    cursor_x = int(cx - scale + t * 6.0 * scale / 3.0)
    if 0 <= cursor_x < width:
        draw.line([(cursor_x, 20), (cursor_x, height - 20)], fill=FEE_GOLD, width=2)
        draw.text((cursor_x + 5, 25), "NOW", fill=FEE_GOLD, font=font)

    draw.text((40, 20), "DOPPLER CURVES", fill=CURVE_CYAN, font=font_big)
    draw.text((40, 55), "p(t) = p0 * e^(-dt)", fill=FEE_GOLD, font=font_eq)
    draw.text((40, height - 40), "time-weighted bonding", fill=(120, 120, 120), font=font)

    return img


def _tick_range_frame(t, width, height, giphy_gifs=None, frame_num=0):
    """Visualize concentrated liquidity tick ranges."""
    img = Image.new("RGB", (width, height), DARK_BG)

    # Blend balancing act GIF behind the ticks (slots 8-9)
    if giphy_gifs:
        bg_gif = _gif_frame(giphy_gifs, 8, frame_num)
        img = _additive_blend(img, bg_gif, 0.06)

    draw = ImageDraw.Draw(img)
    font = _font(MONO, 18)
    font_big = _font(SANS_BOLD, 32)
    font_bar = _font(MONO, 14)

    axis_y = height - 80
    draw.line([(50, axis_y), (width - 50, axis_y)], fill=(80, 80, 80), width=2)

    n_ticks = 40
    current_price_tick = int(n_ticks * (0.3 + 0.4 * math.sin(t * 2)))
    tick_width = (width - 100) // n_ticks

    for i in range(n_ticks):
        tx = 50 + i * tick_width
        dist = abs(i - n_ticks // 2) / (n_ticks // 2)
        liquidity = max(0, 1.0 - dist * 1.5) * (0.5 + 0.5 * math.sin(i * 0.5 + t * 3))
        bar_h = int(liquidity * (height - 120))
        if bar_h > 2:
            color = SWAP_GREEN if abs(i - current_price_tick) < 3 else (30, 60, 120)
            draw.rectangle([(tx, axis_y - bar_h), (tx + tick_width - 2, axis_y)],
                           fill=color)

    # Current price indicator
    price_x = 50 + current_price_tick * tick_width
    draw.line([(price_x, 20), (price_x, axis_y)], fill=FEE_GOLD, width=2)
    draw.text((price_x - 30, 5), "PRICE", fill=FEE_GOLD, font=font)

    # Range bracket
    range_start = 50 + max(0, current_price_tick - 5) * tick_width
    range_end = 50 + min(n_ticks - 1, current_price_tick + 5) * tick_width
    draw.rectangle([(range_start, axis_y + 5), (range_end, axis_y + 15)],
                   fill=CURVE_CYAN)
    draw.text((range_start, axis_y + 20), "YOUR RANGE", fill=CURVE_CYAN, font=font)

    # Metric bars — in-range %, fee capture, IL
    in_range = 1.0 if abs(current_price_tick - n_ticks // 2) < 8 else 0.0
    fee_rate = in_range * (0.5 + 0.5 * math.sin(t * 5))
    il = max(0, 1.0 - in_range) * min(1.0, t)
    _draw_price_bar(draw, "in-range", in_range, 40, 60, 150, SWAP_GREEN, font_bar)
    _draw_price_bar(draw, "fee capture", fee_rate, 40, 100, 150, FEE_GOLD, font_bar)
    _draw_price_bar(draw, "imp. loss", il, 40, 140, 150, SLIPPAGE_RED, font_bar)

    out_of_range = current_price_tick < n_ticks // 2 - 8 or current_price_tick > n_ticks // 2 + 8
    if out_of_range and int(t * 10) % 2:
        draw.text((width // 2 - 150, height // 2 - 20),
                   "OUT OF RANGE", fill=SLIPPAGE_RED, font=font_big)

    draw.text((40, 30), "CONCENTRATED LIQUIDITY", fill=CURVE_CYAN, font=font_big)
    return img


def _dex_parade_frame(t, width, height, giphy_gifs, frame_num):
    """Rapid-fire DEX name display with chaotic visuals."""
    dex_idx = int(t * len(DEXES) * 2.5) % len(DEXES)
    dex_name = DEXES[dex_idx]

    # Cycle through ALL GIFs chaotically
    gif_slot = int(t * 40) % 16
    base = _gif_frame(giphy_gifs, gif_slot, frame_num)
    base = effect_deep_fry(base)

    if frame_num % 3 == 0:
        base = effect_channel_shift(base)
    if frame_num % 5 == 0:
        base = effect_jpeg_corrupt(base, quality=3, passes=2)
    if frame_num % 7 == 0:
        base = effect_posterize(base, levels=3)

    draw = ImageDraw.Draw(base)
    font_huge = _font(SANS_BOLD, 80)
    font = _font(MONO, 24)

    try:
        tw = font_huge.getlength(dex_name)
    except AttributeError:
        tw = len(dex_name) * 40
    tx = width // 2 - int(tw) // 2
    ty = height // 2 - 50

    jx = random.randint(-5, 5)
    jy = random.randint(-3, 3)
    draw.text((tx + 3 + jx, ty + 3 + jy), dex_name, fill=(0, 0, 0), font=font_huge)
    draw.text((tx + jx, ty + jy), dex_name, fill=CURVE_CYAN, font=font_huge)

    swaps = int(t * 999999)
    draw.text((40, height - 50), f"swaps: {swaps:,}", fill=FEE_GOLD, font=font)

    return base


def _flywheel_frame(t, width, height):
    """Visualize the DeFi flywheel: fees -> yield -> liquidity -> lower slippage."""
    img = Image.new("RGB", (width, height), DARK_BG)
    draw = ImageDraw.Draw(img)
    font = _font(SANS_BOLD, 24)
    font_sm = _font(MONO, 18)
    font_bar = _font(MONO, 14)

    cx, cy = width // 2, height // 2
    radius = 160

    labels = ["FEES", "YIELD", "LIQUIDITY", "LOW SLIPPAGE"]
    colors = [FEE_GOLD, SWAP_GREEN, POOL_BLUE, CURVE_CYAN]

    angle_offset = t * math.pi * 2

    for i, (label, color) in enumerate(zip(labels, colors)):
        angle = angle_offset + i * (math.pi / 2)
        lx = int(cx + math.cos(angle) * radius)
        ly = int(cy + math.sin(angle) * radius)

        node_r = 45
        draw.ellipse([(lx - node_r, ly - node_r), (lx + node_r, ly + node_r)],
                     fill=color, outline=(255, 255, 255))

        try:
            lw = font.getlength(label)
        except AttributeError:
            lw = len(label) * 12
        draw.text((lx - int(lw) // 2, ly - 10), label, fill=DARK_BG, font=font)

        next_angle = angle_offset + (i + 1) * (math.pi / 2)
        nx = int(cx + math.cos(next_angle) * radius)
        ny = int(cy + math.sin(next_angle) * radius)
        draw.line([(lx, ly), (nx, ny)], fill=(100, 100, 100), width=2)

    draw.text((cx - 55, cy - 10), "FLYWHEEL", fill=(200, 200, 200), font=font)

    # Metric bars — flywheel health
    rpm = t * 260
    _draw_price_bar(draw, "spin rate", min(1.0, t), 40, height - 55, 160, FEE_GOLD, font_bar)
    _draw_price_bar(draw, "TVL growth", min(1.0, t * 0.8), 40, height - 25, 160, SWAP_GREEN, font_bar)
    draw.text((220, height - 45), f"RPM: {rpm:.0f}", fill=FEE_GOLD, font=font_sm)

    return img


def _hooks_frame(t, width, height):
    """Visualize Uniswap V4 hooks as code callbacks."""
    img = Image.new("RGB", (width, height), DARK_BG)
    draw = ImageDraw.Draw(img)
    font = _font(MONO, 22)

    lines = [
        ("contract LiquidityCurveHook {", CURVE_CYAN),
        ("", (0, 0, 0)),
        ("  function beforeSwap(", FEE_GOLD),
        ("    PoolKey key,", (180, 180, 180)),
        ("    IPoolManager.SwapParams params", (180, 180, 180)),
        ("  ) external returns (bytes4) {", FEE_GOLD),
        ("", (0, 0, 0)),
        ("    // THE CURVE DECIDES", SLIPPAGE_RED),
        ("    uint256 k = reserve0 * reserve1;", SWAP_GREEN),
        ("    require(k >= MIN_K, 'INSUFFICIENT');", SLIPPAGE_RED),
        ("", (0, 0, 0)),
        ("    emit Hooked(msg.sender, k);", (180, 130, 255)),
        ("    return this.beforeSwap.selector;", CURVE_CYAN),
        ("  }", FEE_GOLD),
        ("}", CURVE_CYAN),
    ]

    visible = int(t * len(lines) * 1.3) + 1
    for i, (line, color) in enumerate(lines[:visible]):
        y = 40 + i * 38
        if y < height - 40:
            if i == min(visible - 1, len(lines) - 1):
                cursor_char = "|" if int(t * 8) % 2 == 0 else ""
                draw.text((50, y), line + cursor_char, fill=color, font=font)
            else:
                draw.text((50, y), line, fill=color, font=font)

    return img


# ── Scene Definitions ──────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs):
    scenes = []
    sfx_timeline = []
    cursor = 0.0

    # ── SCENE 1: The Void Pool (2.5s) ────────────────────────────────────
    def scene_void_pool(frame_num, total_frames):
        t = frame_num / total_frames
        # Swimming pool GIF (slots 0-1) darkened + DALL-E pool reveal
        pool_gif = _gif_frame(giphy_gifs, 0, frame_num)
        pool_img = _img(dalle_images, 1)
        # Start with dark GIF, dissolve to DALL-E pool
        base = Image.blend(
            Image.new("RGB", (W, H), DARK_BG),
            pool_gif,
            min(0.3, t * 0.6),
        )
        if t > 0.4:
            reveal = (t - 0.4) / 0.6
            base = transition_dissolve(base, pool_img, reveal * 0.7)
        # Displacement map for underwater feel
        base = effect_displacement_map(base, intensity=8.0, frequency=0.015, t=t)
        if t > 0.6:
            base = draw_text_overlay(base, "THE POOL AWAITS", "typewriter")
        return base

    scenes.append(("void_pool", 4.0, scene_void_pool))
    sfx_timeline.append((cursor + 0.3, "pool_splash"))
    cursor += 4.0

    # ── SCENE 2: x * y = k (5s) ─────────────────────────────────────────
    def scene_equation(frame_num, total_frames):
        t = frame_num / total_frames
        img = _bonding_curve_frame(t, W, H, giphy_gifs, frame_num)
        if frame_num % 6 == 0:
            img = effect_scanlines(img)
        if t > 0.7:
            img = effect_chromatic_aberration(img, intensity=0.5 + t)
        return img

    scenes.append(("equation", 5.0, scene_equation))
    sfx_timeline.append((cursor + 0.0, "swap_blip"))
    sfx_timeline.append((cursor + 2.0, "swap_blip"))
    sfx_timeline.append((cursor + 4.0, "fee_ding"))
    cursor += 5.0

    # ── SCENE 3: AMM Robot (4.5s) ────────────────────────────────────────
    def scene_amm(frame_num, total_frames):
        t = frame_num / total_frames
        # DALL-E AMM image revealed from trading floor GIF (slots 14-15)
        trading_gif = _gif_frame(giphy_gifs, 14, frame_num)
        amm_img = _img(dalle_images, 0)
        if t < 0.35:
            base = effect_deep_fry(trading_gif)
            base = transition_dissolve(base, amm_img, t / 0.35)
        else:
            base = amm_img.copy()
        if random.random() > 0.85:
            base = effect_channel_shift(base)
        if random.random() > 0.9:
            base = effect_glitch_blocks(base, n_blocks=4)
        draw = ImageDraw.Draw(base)
        font = _font(MONO_BOLD, 36)
        draw.text((40, H - 60), "AUTOMATED MARKET MAKER", fill=CURVE_CYAN, font=font)
        return base

    scenes.append(("amm", 4.5, scene_amm))
    sfx_timeline.append((cursor + 0.3, "power_up"))
    cursor += 4.5

    # ── SCENE 4: The Pair — Token Flow (4.5s) ────────────────────────────
    def scene_pair(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS
        # Water flow GIFs (slots 2-3) as background
        water = _gif_frame(giphy_gifs, 2, frame_num)
        # Two particle streams
        stream_a = gen_particle_field(ft, W, H, n_particles=150,
                                      color=CURVE_CYAN, bg=(0, 0, 0))
        stream_b = gen_particle_field(-ft * 1.3, W, H, n_particles=150,
                                      color=FEE_GOLD, bg=(0, 0, 0))
        base = _additive_blend(water, stream_a, 0.6)
        base = _additive_blend(base, stream_b, 0.6)
        # Darken the water a bit so particles pop
        arr = np.array(base, dtype=np.float32)
        arr *= 0.7
        base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

        draw = ImageDraw.Draw(base)
        font = _font(SANS_BOLD, 48)
        font_sm = _font(MONO, 24)
        draw.text((80, H // 2 - 30), "TOKEN 0", fill=CURVE_CYAN, font=font)
        draw.text((W - 280, H // 2 - 30), "TOKEN 1", fill=FEE_GOLD, font=font)
        draw.text((W // 2 - 40, H // 2 + 40), "PAIR", fill=(180, 180, 180), font=font_sm)

        if frame_num % 4 == 0:
            base = effect_scanlines(base)
        return base

    scenes.append(("pair", 4.5, scene_pair))
    sfx_timeline.append((cursor + 0.3, "swap_blip"))
    sfx_timeline.append((cursor + 1.8, "swap_blip"))
    sfx_timeline.append((cursor + 3.5, "swap_blip"))
    cursor += 4.5

    # ── SCENE 5: Multi-Curve Comparison (5s) ─────────────────────────────
    def scene_multi_curve(frame_num, total_frames):
        t = frame_num / total_frames
        img = _multi_curve_frame(t, W, H)
        if frame_num % 8 == 0:
            img = effect_scanlines(img)
        if t > 0.6:
            img = effect_chromatic_aberration(img, intensity=0.8)
        return img

    scenes.append(("multi_curve", 5.0, scene_multi_curve))
    sfx_timeline.append((cursor + 0.5, "swap_blip"))
    sfx_timeline.append((cursor + 2.0, "tick_click"))
    sfx_timeline.append((cursor + 3.5, "tick_click"))
    cursor += 5.0

    # ── SCENE 6: The Swap (5s) ───────────────────────────────────────────
    def scene_swap(frame_num, total_frames):
        t = frame_num / total_frames
        img = _bonding_curve_frame(t, W, H, giphy_gifs, frame_num)
        # Trading floor GIF bleeds through with intensity
        if t > 0.3:
            trading = _gif_frame(giphy_gifs, 15, frame_num)
            img = _additive_blend(img, trading, t * 0.15)
        if t > 0.5:
            img = effect_chromatic_aberration(img, intensity=t * 1.5)
        if t > 0.7 and frame_num % 3 == 0:
            img = effect_vhs_tracking(img)
        if t > 0.85:
            img = effect_deep_fry(img)
            img = draw_text_overlay(img, "THE CURVE MOVES", "glitch")
        return img

    scenes.append(("swap", 5.0, scene_swap))
    sfx_timeline.append((cursor + 0.5, "swap_blip"))
    sfx_timeline.append((cursor + 2.5, "rebalance_whoosh"))
    sfx_timeline.append((cursor + 4.5, "swap_blip"))
    cursor += 5.0

    # ── SCENE 7: Slippage Nightmare (5.5s) ───────────────────────────────
    def scene_slippage(frame_num, total_frames):
        t = frame_num / total_frames
        img = _slippage_frame(t, W, H, giphy_gifs, frame_num)
        if t > 0.4:
            img = effect_scanlines(img)
        if t > 0.6:
            img = effect_channel_shift(img)
        if t > 0.75:
            img = effect_datamosh(img)
        if t > 0.85:
            img = effect_deep_fry(img)
            img = effect_jpeg_corrupt(img, quality=4, passes=2)
        return img

    scenes.append(("slippage", 5.5, scene_slippage))
    sfx_timeline.append((cursor + 0.5, "slippage_alarm"))
    sfx_timeline.append((cursor + 3.5, "error_buzz"))
    sfx_timeline.append((cursor + 5.0, "price_impact"))
    cursor += 5.5

    # ── SCENE 8: Price Impact Meltdown (3.5s) ────────────────────────────
    def scene_price_impact(frame_num, total_frames):
        t = frame_num / total_frames
        # Pancake flip GIFs (slots 6-7) + DALL-E slippage image
        pancake = _gif_frame(giphy_gifs, 6, frame_num)
        slippage_img = _img(dalle_images, 2)
        base = transition_pixel_scatter(pancake, slippage_img, min(1.0, t * 2))
        base = effect_deep_fry(base)
        base = effect_jpeg_corrupt(base, quality=2, passes=3)
        if frame_num % 2 == 0:
            base = effect_channel_shift(base)
        base = effect_chromatic_aberration(base, intensity=2.0 + t * 3)
        if random.random() > 0.6:
            base = effect_datamosh(base)
        texts = ["PRICE IMPACT", "SANDWICHED", "REKT", "MEV", "FRONT-RUN"]
        txt = texts[int(t * 30) % len(texts)]
        base = draw_text_overlay(base, txt, "glitch")
        return base

    scenes.append(("price_impact", 3.5, scene_price_impact))
    sfx_timeline.append((cursor + 0.0, "price_impact"))
    sfx_timeline.append((cursor + 1.2, "glitch_burst"))
    sfx_timeline.append((cursor + 2.4, "error_buzz"))
    cursor += 3.5

    # ── SCENE 9: DEX Parade (5s) ─────────────────────────────────────────
    def scene_dex_parade(frame_num, total_frames):
        t = frame_num / total_frames
        return _dex_parade_frame(t, W, H, giphy_gifs, frame_num)

    scenes.append(("dex_parade", 5.0, scene_dex_parade))
    for i in range(10):
        sfx_timeline.append((cursor + i * 0.5, "tick_click"))
    cursor += 5.0

    # ── SCENE 10: Concentrated Liquidity (5s) ────────────────────────────
    def scene_concentrated(frame_num, total_frames):
        t = frame_num / total_frames
        img = _tick_range_frame(t, W, H, giphy_gifs, frame_num)
        # Flash DALL-E magnifying glass
        if 0.3 < t < 0.6:
            overlay = _img(dalle_images, 3)
            fade = 1.0 - abs(t - 0.45) / 0.15
            img = transition_dissolve(img, overlay, fade * 0.35)
        if frame_num % 5 == 0:
            img = effect_scanlines(img)
        if t > 0.8:
            img = effect_chromatic_aberration(img, intensity=1.5)
        return img

    scenes.append(("concentrated", 5.0, scene_concentrated))
    sfx_timeline.append((cursor + 0.0, "rebalance_whoosh"))
    sfx_timeline.append((cursor + 2.5, "tick_click"))
    sfx_timeline.append((cursor + 4.5, "slippage_alarm"))
    cursor += 5.0

    # ── SCENE 11: Curve Wars — Strange Attractor (5s) ────────────────────
    def scene_curve_wars(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS
        img = gen_strange_attractor(ft * 0.8, W, H, attractor_type="lorenz",
                                    color_scheme="neon", n_points=2500,
                                    rotation_speed=0.5, trail_decay=0.93)
        img = effect_chromatic_aberration(img, intensity=1.5)
        if frame_num % 4 == 0:
            img = effect_scanlines(img)
        # Blend DALL-E battle + stock chart GIFs
        if t > 0.2:
            battle = _img(dalle_images, 5)
            chart_gif = _gif_frame(giphy_gifs, 4, frame_num)
            battle = _additive_blend(battle, chart_gif, 0.2)
            img = transition_dissolve(img, battle, 0.3)
            if random.random() > 0.7:
                img = effect_glitch_blocks(img, n_blocks=6)
        draw = ImageDraw.Draw(img)
        font = _font(SANS_BOLD, 36)
        draw.text((40, 30), "CURVE WARS", fill=SLIPPAGE_RED, font=font)
        return img

    scenes.append(("curve_wars", 5.0, scene_curve_wars))
    sfx_timeline.append((cursor + 0.5, "price_impact"))
    sfx_timeline.append((cursor + 2.5, "glitch_burst"))
    cursor += 5.0

    # ── SCENE 12: Hooks — Smart Pool Code (5s) ──────────────────────────
    def scene_hooks(frame_num, total_frames):
        t = frame_num / total_frames
        img = _hooks_frame(t, W, H)
        circuit = gen_circuit_board(t * 0.3, W, H, density=12)
        img = _additive_blend(img, circuit, 0.12)
        if random.random() > 0.9:
            img = effect_channel_shift(img)
        return img

    scenes.append(("hooks", 5.0, scene_hooks))
    sfx_timeline.append((cursor + 0.0, "swap_blip"))
    sfx_timeline.append((cursor + 2.0, "tick_click"))
    sfx_timeline.append((cursor + 4.0, "fee_ding"))
    cursor += 5.0

    # ── SCENE 13: Doppler Curves (5s) ────────────────────────────────────
    def scene_doppler(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS
        img = _doppler_curve_frame(t, W, H)
        # Voronoi overlay — fragmented liquidity
        voronoi = gen_voronoi(ft * 0.5, W, H, n_points=15, palette="neon")
        img = _additive_blend(img, voronoi, 0.1 + t * 0.1)
        if frame_num % 6 == 0:
            img = effect_wave_distort(img, t=t, amplitude=6, frequency=0.025)
        if t > 0.7:
            img = effect_feedback_loop(img, t=t, decay=0.6, offset=(8, 5))
        return img

    scenes.append(("doppler", 5.0, scene_doppler))
    sfx_timeline.append((cursor + 0.0, "rebalance_whoosh"))
    sfx_timeline.append((cursor + 2.0, "swap_blip"))
    sfx_timeline.append((cursor + 4.0, "fee_ding"))
    cursor += 5.0

    # ── SCENE 14: Zora Flywheel (5s) ────────────────────────────────────
    def scene_flywheel(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS
        img = _flywheel_frame(t, W, H)
        # Oscilloscope waves — the curve evolving
        osc = gen_oscilloscope(ft, W, H, waves=[
            {"freq": 2 + t * 5, "amp": 0.3, "color": CURVE_CYAN},
            {"freq": 3 + t * 3, "amp": 0.2, "color": FEE_GOLD},
        ])
        img = _additive_blend(img, osc, 0.2)
        if t > 0.5:
            draw = ImageDraw.Draw(img)
            font = _font(MONO, 22)
            draw.text((40, 30), "ZORA FLYWHEEL", fill=CURVE_CYAN, font=font)
        if frame_num % 7 == 0:
            img = effect_wave_distort(img, t=t, amplitude=8, frequency=0.03)
        return img

    scenes.append(("flywheel", 5.0, scene_flywheel))
    sfx_timeline.append((cursor + 0.0, "power_up"))
    sfx_timeline.append((cursor + 2.0, "rebalance_whoosh"))
    sfx_timeline.append((cursor + 4.0, "fee_ding"))
    cursor += 5.0

    # ── SCENE 15: Yield Garden (4.5s) ────────────────────────────────────
    def scene_yield(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS
        # DALL-E money tree + money rain GIF (slots 10-11)
        base = _img(dalle_images, 4)
        money_gif = _gif_frame(giphy_gifs, 10, frame_num)
        base = _additive_blend(base, money_gif, 0.25)
        # Mandelbrot fractal bleed — infinite yield
        mandel = ffmpeg_mandelbrot_frame(ft * 0.15, W, H, max_iter=80)
        base = _additive_blend(base, mandel, 0.08)

        draw = ImageDraw.Draw(base)
        font = _font(MONO_BOLD, 28)
        font_sm = _font(MONO, 20)
        font_bar = _font(MONO, 14)
        fees = t * 42069.0
        apy = 12.5 + math.sin(t * 10) * 8

        draw.text((40, 30), f"FEES EARNED: ${fees:,.2f}", fill=FEE_GOLD, font=font)
        draw.text((40, 65), f"APY: {apy:.1f}%", fill=SWAP_GREEN, font=font_sm)

        _draw_price_bar(draw, "yield", min(1.0, t * 1.2), W - 220, 40, 160, SWAP_GREEN, font_bar)
        _draw_price_bar(draw, "fees", min(1.0, t), W - 220, 80, 160, FEE_GOLD, font_bar)
        _draw_price_bar(draw, "TVL", min(1.0, t * 0.9), W - 220, 120, 160, POOL_BLUE, font_bar)

        if frame_num % 5 == 0:
            base = effect_scanlines(base)
        return base

    scenes.append(("yield", 4.5, scene_yield))
    sfx_timeline.append((cursor + 0.5, "fee_ding"))
    sfx_timeline.append((cursor + 1.5, "fee_ding"))
    sfx_timeline.append((cursor + 2.5, "fee_ding"))
    sfx_timeline.append((cursor + 3.5, "fee_ding"))
    cursor += 4.5

    # ── SCENE 16: The Rebalance — Chaos Finale (5s) ─────────────────────
    def scene_rebalance(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Rapid cycle: curve → ticks → doppler → flywheel → DALL-E rapid cut
        phase = int(t * 12) % 5
        if phase == 0:
            img = _bonding_curve_frame(t * 4 % 1, W, H)
            img = effect_deep_fry(img)
        elif phase == 1:
            img = _tick_range_frame(t * 3 % 1, W, H)
            img = effect_invert_glitch(img)
            img = effect_jpeg_corrupt(img, quality=3, passes=2)
        elif phase == 2:
            img = _doppler_curve_frame(t * 3 % 1, W, H)
            img = effect_thermal(img)
        elif phase == 3:
            img = _flywheel_frame(t * 4 % 1, W, H)
            img = effect_datamosh(img)
            img = effect_posterize(img, levels=4)
        else:
            # DALL-E rapid cut + GIF chaos
            img_idx = int(t * 20) % len(dalle_images) if dalle_images else 0
            img = _img(dalle_images, img_idx)
            gif_bg = _gif_frame(giphy_gifs, int(t * 30) % 16, frame_num)
            img = transition_glitch_cut(img, gif_bg, t)
            img = effect_pixel_sort(img)

        if random.random() > 0.5:
            img = effect_glitch_blocks(img, n_blocks=8)
        if random.random() > 0.6:
            img = effect_chromatic_aberration(img, intensity=2.5)
        if random.random() > 0.7:
            img = effect_zoom_and_rotate(img, t * 5)

        texts = ["REBALANCE", "x*y=k", "LIQUIDITY", "THE CURVE",
                 "SLIPPAGE", "YIELD", "FEES", "HOOKS", "DOPPLER", "FLYWHEEL"]
        txt = texts[frame_num % len(texts)]
        img = draw_text_overlay(img, txt, "glitch")
        return img

    scenes.append(("rebalance", 5.0, scene_rebalance))
    sfx_timeline.append((cursor + 0.0, "rebalance_whoosh"))
    sfx_timeline.append((cursor + 1.0, "glitch_burst"))
    sfx_timeline.append((cursor + 2.0, "price_impact"))
    sfx_timeline.append((cursor + 3.0, "glitch_burst"))
    sfx_timeline.append((cursor + 4.0, "error_buzz"))
    cursor += 5.0

    # ── SCENE 17: Fade to Curve (3.5s) ──────────────────────────────────
    def scene_outro(frame_num, total_frames):
        t = frame_num / total_frames
        # ASCII matrix rain dissolving into final curve
        rain = gen_ascii_matrix(t * 2, W, H, mode="rain", color="green",
                                density=0.4, speed=1.5)
        curve = _bonding_curve_frame(0.5, W, H)
        if t < 0.4:
            img = transition_dissolve(rain, curve, t / 0.4)
        else:
            img = curve.copy()

        draw = ImageDraw.Draw(img)
        font = _font(MONO_BOLD, 36)
        draw.text((W // 2 - 120, H - 60), "x * y = k", fill=CURVE_CYAN, font=font)

        if t > 0.4:
            fade = (t - 0.4) / 0.6
            black = Image.new("RGB", (W, H), (0, 0, 0))
            img = transition_dissolve(img, black, fade)

        return img

    scenes.append(("outro", 3.5, scene_outro))
    sfx_timeline.append((cursor + 0.5, "pool_splash"))
    cursor += 3.5

    return scenes, sfx_timeline

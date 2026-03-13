"""
YTP Session: Attention Markets

The zorb sees all. The arrow only goes up.
You are the market. The market is the feed. The feed is you.
Attention is the only currency that spends you back.
"""

import random
import math

from engine.effects import (
    effect_deep_fry, effect_channel_shift, effect_datamosh,
    effect_scanlines, effect_chromatic_aberration, effect_wave_distort,
    effect_glitch_blocks, effect_feedback_loop, effect_posterize,
    effect_bit_crush, effect_pixel_sort, effect_vhs_tracking,
    transition_dissolve, transition_glitch_cut, transition_zoom_through,
)
from engine.text import draw_text_overlay
from engine.render import (
    load_and_resize, generate_static_frame,
    generate_solid_color_frame, generate_token_rain_frame,
)
from engine.sources import (
    gen_plasma, gen_voronoi, gen_oscilloscope, gen_particle_field,
    gen_circuit_board, ffmpeg_gradient_frame,
)
from engine.audio import audio_duration
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


# ── Session Config ──────────────────────────────────────────────────────────
TITLE = "attention_markets"
WIDTH, HEIGHT = 1080, 1080
FPS = 24


# ── Content ─────────────────────────────────────────────────────────────────

giphy_searches = [
    "stock market graph", "trending up arrow", "phone scrolling",
    "viral content", "money printer", "neon sphere",
]

dalle_prompts = [
    "A giant luminous blue glass sphere floating above a crowded neon digital marketplace at night, traders staring up mesmerized, cyberpunk art, square composition",
    "An infinite vertical scroll of glowing content feeds stretching into deep space, tiny silhouettes falling between screens, vaporwave, square composition",
    "A colossal green arrow piercing upward through storm clouds, dramatic lighting from below, geometric minimal art, square composition",
]

tts_lines = [
    ("Good morning. The attention market opens in three. Two. One.", "onyx", 0.95),
    ("Every scroll is a bid. Every like is a derivative. You are the trading floor.", "echo", 1.0),
    ("The zorb sees everything trending. The zorb is what's trending. Don't look away.", "fable", 0.95),
    ("Number go up. Arrow go up. Serotonin go up. Meaning go... somewhere.", "alloy", 1.0),
    ("You used to discover things. Now things discover you. The algorithm is the new tastemaker.", "nova", 0.9),
    ("Mint. Collect. Share. Forget. Mint. Collect. Share. Forget. This is the cycle.", "shimmer", 1.1),
    ("The market doesn't sleep because the market is your phone and your phone is always open.", "onyx", 0.85),
    ("Green candle. Green arrow. Green light. Go. Go where? Doesn't matter. Just go.", "echo", 1.0),
    ("You are not early. You are not late. You are exactly when the feed needs you to be.", "fable", 0.9),
    ("The zorb contains every image ever minted. It is perfectly round because attention has no edges.", "nova", 0.85),
]

tts_effects = [
    "normal",      # market open: clean, authoritative
    "telephone",   # trading floor: compressed
    "echo",        # zorb: ethereal
    "normal",      # number go up: deadpan
    "normal",      # algorithm: matter-of-fact
    "fast",        # mint cycle: frantic
    "slow",        # never sleeps: dragging
    "normal",      # green: punchy
    "whisper",     # timing: intimate
    "chorus",      # zorb final: expansive
]

SCENE_AUDIO_MAP = {
    "cold_open":       [],
    "market_opens":    [0],
    "the_bid":         [1],
    "zorb_appears":    [2],
    "number_go_up":    [3],
    "algorithm":       [4],
    "mint_cycle":      [5],
    "never_sleeps":    [6],
    "green_means_go":  [7],
    "the_feed":        [8],
    "zorb_final":      [9],
    "close":           [],
}

music_config = {
    "layers": [
        {"type": "arpeggio", "freq": 220,
         "notes": [220, 277.18, 329.63, 440, 329.63, 277.18],
         "step_duration": 0.15, "duration": 180, "volume": 0.008,
         "filters": "lowpass=f=3000,tremolo=f=0.3:d=0.2"},
        {"type": "sine", "freq": 55, "duration": 180, "volume": 0.012,
         "filters": "tremolo=f=0.8:d=0.5"},
        {"type": "pad", "freq": 523.25, "freq2": 524.5, "duration": 180,
         "volume": 0.006, "filters": "tremolo=f=0.15:d=0.3"},
        {"type": "noise", "color": "pink", "duration": 180, "volume": 0.003,
         "filters": "lowpass=f=800,highpass=f=200"},
        {"type": "fm", "freq": 880, "mod_freq": 7, "mod_depth": 30,
         "duration": 180, "volume": 0.004,
         "filters": "lowpass=f=4000,tremolo=f=0.5:d=0.4"},
    ],
    "master_filters": "volume=0.9",
    "mix_volume": 0.35,
}

sfx_cues = [
    {"name": "bell", "type": "power_up", "freq": 440, "duration": 1.0,
     "filters": "volume=0.4,afade=t=out:d=0.5"},
    {"name": "notification", "type": "tone", "freq": 880, "duration": 0.12,
     "filters": "afade=t=out:d=0.08,volume=0.5"},
    {"name": "cash", "type": "impact", "freq": 200, "duration": 0.3,
     "filters": "volume=0.3"},
    {"name": "scroll_tick", "type": "typing", "rate": 15, "duration": 1.0,
     "filters": "volume=0.12"},
    {"name": "whoosh", "type": "whoosh", "freq": 2000, "duration": 0.4,
     "filters": "volume=0.25"},
    {"name": "glitch", "type": "glitch", "duration": 0.3,
     "filters": "volume=0.2"},
    {"name": "drop", "type": "power_down", "freq": 880, "duration": 0.8,
     "filters": "volume=0.3,afade=t=out:d=0.4"},
    {"name": "pulse", "type": "heartbeat", "duration": 1.5,
     "filters": "volume=0.3,lowpass=f=150"},
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


def _dur(tts_durations, scene_name, fallback):
    if not tts_durations:
        return fallback
    clips = SCENE_AUDIO_MAP.get(scene_name, [])
    if not clips:
        return fallback
    return audio_duration(tts_durations, clips, padding=0.3, gap_per_clip=0.12)


def _zorb(width, height, cx, cy, radius, t=0):
    """Draw a Zora-style blue gradient sphere."""
    yy, xx = np.mgrid[0:height, 0:width]
    dx = (xx - cx).astype(np.float32)
    dy = (yy - cy).astype(np.float32)
    dist = np.sqrt(dx**2 + dy**2)

    r = radius * (1.0 + 0.03 * math.sin(t * 3))
    mask = dist < r
    if not mask.any():
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))

    norm = np.clip(dist / r, 0, 1)

    # Specular highlight (upper-left)
    sx, sy = cx - r * 0.25, cy - r * 0.3
    spec = np.clip(np.sqrt((xx - sx)**2 + (yy - sy)**2) / (r * 0.55), 0, 1)

    arr = np.zeros((height, width, 4), dtype=np.float32)

    # Blue sphere gradient
    f = 1.0 - norm[mask] ** 1.5
    arr[mask, 0] = 15 + 55 * f
    arr[mask, 1] = 30 + 80 * f
    arr[mask, 2] = 130 + 125 * f
    arr[mask, 3] = 255

    # Specular
    sm = mask & (spec < 1.0)
    if sm.any():
        si = np.clip((1.0 - spec[sm]) ** 2.5, 0, 1)
        arr[sm, 0] += si * 200
        arr[sm, 1] += si * 210
        arr[sm, 2] += si * 120

    # Edge fade
    em = mask & (norm > 0.82)
    if em.any():
        ef = np.clip((1.0 - norm[em]) / 0.18, 0, 1)
        arr[em, 3] = ef * 255

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def _arrow(draw, cx, cy, size, color=(0, 0, 0)):
    """Draw a geometric up arrow."""
    s = size
    points = [
        (cx, cy - s),
        (cx + s * 0.65, cy + s * 0.15),
        (cx + s * 0.25, cy + s * 0.15),
        (cx + s * 0.25, cy + s),
        (cx - s * 0.25, cy + s),
        (cx - s * 0.25, cy + s * 0.15),
        (cx - s * 0.65, cy + s * 0.15),
    ]
    draw.polygon(points, fill=color)


def _arrow_bg(w, h, scale=1.0, bg=(0, 210, 60)):
    """Black up arrow on green background — the motif."""
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)
    _arrow(draw, w // 2, h // 2, int(min(w, h) * 0.28 * scale), (0, 0, 0))
    return img


def _candle_chart(w, h, t, n_candles=24):
    """Green candlestick chart climbing to infinity."""
    img = Image.new("RGB", (w, h), (8, 10, 16))
    draw = ImageDraw.Draw(img)

    cw = w // (n_candles + 2)
    margin = cw

    random.seed(42)
    prices = [50]
    for i in range(n_candles):
        # Mostly up, accelerating with time
        drift = 2 + t * 8 + i * 0.5
        change = random.uniform(-2, drift)
        prices.append(max(10, prices[-1] + change))
    random.seed()

    max_p = max(prices) * 1.1
    min_p = max(0, min(prices) * 0.8)
    rng = max_p - min_p or 1

    for i in range(n_candles):
        x = margin + i * cw
        op, cl = prices[i], prices[i + 1]
        is_green = cl >= op
        color = (0, 210, 60) if is_green else (210, 40, 40)

        y_op = int((1 - (op - min_p) / rng) * (h - 120)) + 60
        y_cl = int((1 - (cl - min_p) / rng) * (h - 120)) + 60

        random.seed(i + 100)
        wt = random.randint(5, 20)
        wb = random.randint(5, 15)
        random.seed()

        cx_candle = x + cw // 2
        draw.line([(cx_candle, min(y_op, y_cl) - wt),
                    (cx_candle, max(y_op, y_cl) + wb)], fill=color, width=1)

        top, bot = min(y_op, y_cl), max(y_op, y_cl)
        if bot - top < 3:
            bot = top + 3
        draw.rectangle([(x + 2, top), (x + cw - 2, bot)], fill=color)

    return img


def _ticker_overlay(img, t, lines):
    """Overlay scrolling ticker text at bottom."""
    draw = ImageDraw.Draw(img)
    font = _font(MONO, 22)
    w, h = img.size

    # Ticker bar background
    draw.rectangle([(0, h - 44), (w, h)], fill=(0, 0, 0))

    text = "   ///   ".join(lines)
    text_w = len(text) * 13
    offset = int(t * 200) % max(text_w, 1)
    doubled = text + "   ///   " + text
    draw.text((-offset, h - 38), doubled, fill=(0, 210, 60), font=font)

    return img


# ── Scene Definitions ──────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs, tts_durations=None):
    scenes = []
    sfx_timeline = []

    def _scene_start():
        return sum(dur for _, dur, _ in scenes)

    W, H = WIDTH, HEIGHT

    # ═══ COLD OPEN: Arrow materializes ═══

    def scene_cold_open(frame_num, total_frames):
        t = frame_num / total_frames
        if t < 0.3:
            return Image.new("RGB", (W, H), (0, 0, 0))

        # Green floods in
        green_t = min(1.0, (t - 0.3) / 0.3)
        bg_g = int(210 * green_t)
        img = Image.new("RGB", (W, H), (0, bg_g, int(60 * green_t)))

        if t > 0.5:
            draw = ImageDraw.Draw(img)
            arrow_t = min(1.0, (t - 0.5) / 0.4)
            _arrow(draw, W // 2, H // 2, int(W * 0.28 * arrow_t), (0, 0, 0))

        if t > 0.85:
            font = _font(MONO_BOLD, 28)
            draw = ImageDraw.Draw(img)
            draw.text((W // 2 - 30, 50), "gm", fill=(0, 0, 0), font=font)

        return img

    scenes.append(("cold_open", 2.0, scene_cold_open))
    sfx_timeline.append((0.8, "whoosh"))

    # ═══ MARKET OPENS ═══

    def scene_market_opens(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Ticker data
        ticker = [
            ("$ATTN", "847.23", "+12.4%", True),
            ("$SCROLL", "2,441", "+8.7%", True),
            ("$LIKE", "0.003", "+0.1%", True),
            ("$MINT", "69.42", "+42.0%", True),
            ("$ZORB", "∞", "+∞%", True),
            ("$TAKE", "112.8", "-3.2%", False),
            ("$FOMO", "999.9", "+99.9%", True),
            ("$VIBE", "420.0", "+4.2%", True),
            ("$ALGO", "1,337", "+13.3%", True),
            ("$FEED", "24/7", "+∞%", True),
        ]

        img = Image.new("RGB", (W, H), (5, 5, 8))
        draw = ImageDraw.Draw(img)
        font = _font(MONO, 24)
        font_big = _font(MONO_BOLD, 48)

        # Countdown at start
        if t < 0.3:
            count = 3 - int(t / 0.1)
            draw.text((W // 2 - 20, H // 2 - 30), str(max(1, count)),
                       fill=(0, 210, 60), font=font_big)
            return img

        # Market data scrolling in
        visible = int((t - 0.3) / 0.7 * len(ticker) * 1.5) + 1
        y = 60
        for i, (label, value, change, is_up) in enumerate(ticker[:visible]):
            x_off = int(math.sin(ft * 3 + i * 0.5) * 15)
            color = (0, 230, 60) if is_up else (230, 50, 50)
            arrow_ch = "▲" if is_up else "▼"
            draw.text((40 + x_off, y), label, fill=(120, 120, 130), font=font)
            draw.text((340 + x_off, y), value, fill=(255, 255, 255), font=font)
            draw.text((640 + x_off, y), f"{arrow_ch} {change}", fill=color, font=font)
            y += 42
            if y > H - 80:
                break

        # Scanlines
        if t > 0.6:
            img = effect_scanlines(img)

        # Bottom ticker
        img = _ticker_overlay(img, ft, [
            "$ATTN ▲12.4%", "$ZORB ▲∞", "$MINT ▲42.0%",
            "$SCROLL ▲8.7%", "ATTENTION IS THE NEW OIL",
        ])

        return img

    dur = _dur(tts_durations, "market_opens", 4.5)
    t0 = _scene_start()
    scenes.append(("market_opens", dur, scene_market_opens))
    sfx_timeline.append((t0, "bell"))
    sfx_timeline.append((t0 + dur * 0.5, "notification"))

    # ═══ THE BID ═══

    def scene_the_bid(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Rapid cuts between GIPHY and arrow motif
        cycle = int(ft * 3) % 4
        if cycle < 2 and giphy_gifs:
            idx = (frame_num // 4) % len(giphy_gifs)
            img = load_and_resize(giphy_gifs[idx], (W, H))
            img = effect_chromatic_aberration(img, 2.5)
        else:
            img = _arrow_bg(W, H, scale=0.8 + 0.4 * math.sin(ft * 5))

        if t > 0.4:
            img = draw_text_overlay(img, "every scroll is a bid", "bottom_text")
        if random.random() > 0.7:
            img = effect_channel_shift(img)

        return img

    dur = _dur(tts_durations, "the_bid", 4.0)
    t0 = _scene_start()
    scenes.append(("the_bid", dur, scene_the_bid))
    sfx_timeline.append((t0, "scroll_tick"))
    sfx_timeline.append((t0 + dur * 0.5, "cash"))

    # ═══ ZORB APPEARS ═══

    def scene_zorb_appears(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Particle field background
        bg = gen_particle_field(ft, W, H, n_particles=150,
                                color=(30, 80, 200), bg=(5, 5, 15))

        # Zorb grows in from center
        radius = int(W * 0.25 * min(1.0, t * 2))
        if radius > 5:
            zorb = _zorb(W, H, W // 2, H // 2, radius, ft)
            bg.paste(zorb, (0, 0), zorb)

        if t > 0.5:
            draw = ImageDraw.Draw(bg)
            font = _font(SANS_BOLD, 36)
            draw.text((W // 2 - 200, H - 120), "don't look away",
                       fill=(100, 150, 255), font=font)

        if t > 0.7:
            bg = effect_feedback_loop(bg, ft, decay=0.5, offset=(8, 8))

        return bg

    dur = _dur(tts_durations, "zorb_appears", 4.5)
    t0 = _scene_start()
    scenes.append(("zorb_appears", dur, scene_zorb_appears))
    sfx_timeline.append((t0, "whoosh"))
    sfx_timeline.append((t0 + dur * 0.6, "notification"))

    # ═══ NUMBER GO UP ═══

    def scene_number_go_up(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Green background with escalating arrows
        img = Image.new("RGB", (W, H), (0, int(180 + 30 * math.sin(ft * 4)), 40))
        draw = ImageDraw.Draw(img)

        # Multiple arrows appearing and growing
        n_arrows = int(t * 12) + 1
        random.seed(77)
        for i in range(n_arrows):
            ax = random.randint(50, W - 50)
            ay = random.randint(50, H - 50)
            asize = random.randint(20, 80) + int(t * 40)
            _arrow(draw, ax, ay, asize, (0, 0, 0))
        random.seed()

        # Central big arrow
        _arrow(draw, W // 2, H // 2, int(W * 0.22 + t * 80), (0, 0, 0))

        if t > 0.3:
            font = _font(SANS_BOLD, 60)
            draw.text((W // 2 - 250, 60), "NUMBER GO UP",
                       fill=(0, 0, 0), font=font)

        if t > 0.6 and frame_num % 6 < 3:
            img = effect_deep_fry(img)

        return img

    dur = _dur(tts_durations, "number_go_up", 3.5)
    t0 = _scene_start()
    scenes.append(("number_go_up", dur, scene_number_go_up))
    sfx_timeline.append((t0, "notification"))
    sfx_timeline.append((t0 + dur * 0.4, "cash"))
    sfx_timeline.append((t0 + dur * 0.7, "cash"))

    # ═══ ALGORITHM ═══

    def scene_algorithm(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = gen_circuit_board(ft, W, H, density=12)

        if dalle_images and len(dalle_images) > 1:
            feed_img = load_and_resize(dalle_images[1], (W, H))
            img = Image.blend(img, feed_img, min(0.4, t * 0.6))

        if t > 0.3:
            img = draw_text_overlay(img, "the algorithm decides", "typewriter")
        if t > 0.7:
            img = effect_glitch_blocks(img, 6)

        return img

    dur = _dur(tts_durations, "algorithm", 4.5)
    t0 = _scene_start()
    scenes.append(("algorithm", dur, scene_algorithm))
    sfx_timeline.append((t0 + dur * 0.4, "glitch"))

    # ═══ MINT CYCLE ═══

    def scene_mint_cycle(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        words = ["MINT", "COLLECT", "SHARE", "FORGET"]
        colors = [(0, 210, 60), (60, 120, 255), (255, 180, 0), (80, 80, 80)]

        idx = int(ft * 4) % 4
        word = words[idx]
        color = colors[idx]

        img = Image.new("RGB", (W, H), (0, 0, 0) if idx != 3 else (15, 15, 15))
        draw = ImageDraw.Draw(img)
        font = _font(SANS_BOLD, 100)

        try:
            tw = font.getlength(word)
        except AttributeError:
            tw = len(word) * 60
        draw.text((W // 2 - tw // 2, H // 2 - 60), word, fill=color, font=font)

        # Small zorb icon in corner
        zorb_r = 40
        zorb = _zorb(W, H, W - 80, 80, zorb_r, ft)
        img.paste(zorb, (0, 0), zorb)

        # Arrow watermark
        if idx == 0:  # MINT gets the green arrow
            small_draw = ImageDraw.Draw(img)
            _arrow(small_draw, W // 2, H // 2 + 120, 40, (0, 150, 40))

        if t > 0.5:
            img = effect_bit_crush(img, bits=4)
        if random.random() > 0.6:
            img = effect_scanlines(img)

        return img

    dur = _dur(tts_durations, "mint_cycle", 3.5)
    t0 = _scene_start()
    scenes.append(("mint_cycle", dur, scene_mint_cycle))
    sfx_timeline.append((t0, "notification"))
    sfx_timeline.append((t0 + dur * 0.25, "cash"))
    sfx_timeline.append((t0 + dur * 0.5, "whoosh"))

    # ═══ NEVER SLEEPS ═══

    def scene_never_sleeps(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Dark, phone glow aesthetic
        img = Image.new("RGB", (W, H), (3, 3, 8))
        draw = ImageDraw.Draw(img)

        # Phone screen glow in center
        glow_r = int(W * 0.35)
        yy, xx = np.mgrid[0:H, 0:W]
        dist = np.sqrt((xx - W // 2) ** 2 + (yy - H // 2) ** 2).astype(np.float32)
        glow = np.clip(1.0 - dist / glow_r, 0, 1) ** 2

        arr = np.array(img).astype(np.float32)
        pulse = 0.7 + 0.3 * math.sin(ft * 2)
        arr[:, :, 2] += glow * 60 * pulse
        arr[:, :, 1] += glow * 20 * pulse
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

        draw = ImageDraw.Draw(img)
        font = _font(MONO, 20)

        # Notification timestamps scrolling
        times = ["3:14 AM", "3:15 AM", "3:17 AM", "3:22 AM", "3:23 AM",
                 "3:41 AM", "4:02 AM", "4:03 AM", "4:30 AM", "5:01 AM"]
        visible = int(t * len(times) * 1.3) + 1
        for i, ts in enumerate(times[:visible]):
            y = 200 + i * 55
            if y < H - 100:
                alpha = int(min(255, 80 + 30 * math.sin(ft + i)))
                draw.text((W // 2 - 60, y), ts, fill=(alpha, alpha, alpha + 40), font=font)
                draw.text((W // 2 + 60, y), "↑", fill=(0, min(255, 120 + i * 15), 40), font=font)

        if t > 0.6:
            img = effect_vhs_tracking(img)

        return img

    dur = _dur(tts_durations, "never_sleeps", 5.0)
    t0 = _scene_start()
    scenes.append(("never_sleeps", dur, scene_never_sleeps))
    sfx_timeline.append((t0, "pulse"))
    sfx_timeline.append((t0 + dur * 0.5, "notification"))

    # ═══ GREEN MEANS GO ═══

    def scene_green_means_go(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = _candle_chart(W, H, t)

        # Arrow motif overlay flashing
        if frame_num % 24 < 8:
            arrow_img = _arrow_bg(W, H, scale=0.5 + t * 0.5)
            img = Image.blend(img, arrow_img, 0.3)

        if t > 0.5:
            draw = ImageDraw.Draw(img)
            font = _font(SANS_BOLD, 52)
            draw.text((W // 2 - 60, 40), "GO.", fill=(0, 210, 60), font=font)

        if t > 0.7:
            img = effect_posterize(img, levels=6)
            img = effect_chromatic_aberration(img, 3.0)

        return img

    dur = _dur(tts_durations, "green_means_go", 4.0)
    t0 = _scene_start()
    scenes.append(("green_means_go", dur, scene_green_means_go))
    sfx_timeline.append((t0, "bell"))
    sfx_timeline.append((t0 + dur * 0.6, "whoosh"))

    # ═══ THE FEED ═══

    def scene_the_feed(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        if dalle_images and len(dalle_images) > 1:
            img = load_and_resize(dalle_images[1], (W, H))
        else:
            img = gen_plasma(ft, W, H, "vaporwave")

        # Rapid GIF cuts overlaid
        if giphy_gifs and frame_num % 18 < 6:
            gif_idx = (frame_num // 6) % len(giphy_gifs)
            gif_img = load_and_resize(giphy_gifs[gif_idx], (W, H))
            img = Image.blend(img, gif_img, 0.5)

        img = effect_wave_distort(img, ft, amplitude=8, frequency=0.015)

        if t > 0.4:
            draw = ImageDraw.Draw(img)
            font = _font(SANS_BOLD, 40)
            draw.text((W // 2 - 280, H // 2 - 25),
                       "you are exactly on time",
                       fill=(255, 255, 255), font=font)

        if t > 0.7:
            img = effect_pixel_sort(img)

        return img

    dur = _dur(tts_durations, "the_feed", 4.5)
    t0 = _scene_start()
    scenes.append(("the_feed", dur, scene_the_feed))
    sfx_timeline.append((t0, "scroll_tick"))
    sfx_timeline.append((t0 + dur * 0.7, "glitch"))

    # ═══ ZORB FINAL ═══

    def scene_zorb_final(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Zorb consuming the frame
        bg = Image.new("RGB", (W, H), (5, 5, 15))

        # Growing zorb
        max_r = int(W * 0.6)
        radius = int(max_r * min(1.0, t * 1.5))
        if radius > 10:
            zorb = _zorb(W, H, W // 2, H // 2, radius, ft)
            bg.paste(zorb, (0, 0), zorb)

        # Small arrows orbiting the zorb
        draw = ImageDraw.Draw(bg)
        n_arrows = 6
        for i in range(n_arrows):
            angle = ft * 1.5 + i * (2 * math.pi / n_arrows)
            orbit_r = radius + 40 + 20 * math.sin(ft * 2 + i)
            ax = int(W // 2 + orbit_r * math.cos(angle))
            ay = int(H // 2 + orbit_r * math.sin(angle))
            if 10 < ax < W - 10 and 10 < ay < H - 10:
                _arrow(draw, ax, ay, 18, (0, 200, 50))

        if t > 0.4:
            font = _font(SANS_BOLD, 32)
            draw.text((W // 2 - 310, H - 100),
                       "attention has no edges",
                       fill=(100, 150, 255), font=font)

        if t > 0.8:
            img_dalle = None
            if dalle_images:
                img_dalle = load_and_resize(dalle_images[0], (W, H))
            if img_dalle:
                bg = transition_dissolve(bg, img_dalle, (t - 0.8) / 0.2)

        return bg

    dur = _dur(tts_durations, "zorb_final", 5.0)
    t0 = _scene_start()
    scenes.append(("zorb_final", dur, scene_zorb_final))
    sfx_timeline.append((t0, "whoosh"))
    sfx_timeline.append((t0 + dur * 0.5, "drop"))

    # ═══ CLOSE ═══

    def scene_close(frame_num, total_frames):
        t = frame_num / total_frames
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        if t > 0.3:
            # Small green arrow fades in at center
            alpha = min(1.0, (t - 0.3) / 0.4)
            g = int(210 * alpha)
            _arrow(draw, W // 2, H // 2, 30, (0, g, int(40 * alpha)))

        if t > 0.7:
            font = _font(MONO, 16)
            draw.text((W // 2 - 20, H - 60), "gn",
                       fill=(40, 40, 40), font=font)

        return img

    scenes.append(("close", 2.0, scene_close))

    return scenes, sfx_timeline

"""
YTP Session: Peace DLC

They sold a war as proof of peace, then handed everyone the receipt at the pump.

The President of Peace DLC — now featuring Operation Epic Fury,
emergency Russian oil waivers, and a loading bar that never reaches 100%.
"""

import random
import math

from engine.effects import (
    effect_deep_fry, effect_channel_shift, effect_datamosh,
    effect_scanlines, effect_chromatic_aberration, effect_wave_distort,
    effect_glitch_blocks, effect_vhs_tracking, effect_bit_crush,
    effect_zoom_and_rotate, effect_thermal, effect_pixel_sort,
    effect_posterize,
    transition_dissolve, transition_glitch_cut,
)
from engine.text import draw_text_overlay
from engine.render import (
    load_and_resize, generate_static_frame,
    generate_solid_color_frame,
)
from engine.sources import (
    gen_plasma, gen_voronoi, gen_particle_field,
)
from engine.audio import audio_duration
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── Session Config ──────────────────────────────────────────────────────────
TITLE = "peace_dlc"
WIDTH, HEIGHT = 1080, 1080
FPS = 24

# ── Content ─────────────────────────────────────────────────────────────────

giphy_searches = [
    "flag waving", "sales presentation",
    "golf swing", "alarm siren",
    "cable news", "sports announcer",
    "oil spill", "gas pump",
    "stock market crash", "paperwork",
    "loading bar", "spinning wheel",
]

dalle_prompts = [
    "A smug patriotic TV ad studio where a gold peace dove logo morphs into cruise missiles and confetti becomes falling ash, hyper-detailed satirical collage, analog broadcast texture, square composition",
    "A luxury golf resort torn open by war-room graphics, oil barrels rolling across a putting green, absurdist political pop art with VHS bloom and glitch edges, square composition",
    "A television anchor desk fused with a military command center, oversized microphones, patriotic bunting, missile trails on green-screen monitors, neon-brutalist satire, square composition",
    "A top-down map of a narrow sea lane clogged with tankers like a jammed artery, gas pump nozzles replacing naval cannons, dark infographic-surrealism, square composition",
    "A frantic boardroom where spreadsheets drip crude oil, sanction stamps blur into rubber fire alarms, executives wearing life vests, editorial collage with deep-fried finance aesthetics, square composition",
    "A giant retro computer error screen over a desert war zone, the word PEACE loading forever while smoke rises behind it, grim meme-poster style with CRT scanlines, square composition",
]

# TTS clips indexed 0-17
tts_lines = [
    # Scene 1: peace_brand (clips 0-1)
    ("Loading peace package. Please do not refresh the war.", "shimmer", 1.0),
    ("Welcome back to the President of Peace DLC.", "onyx", 1.0),
    # Scene 2: little_excursion (clips 2-3)
    ("We took a little excursion.", "echo", 1.0),
    ("If they rise, they rise.", "echo", 1.0),
    # Scene 3: toast_tv (clips 4-6)
    ("America is winning.", "fable", 1.0),
    ("They are toast.", "fable", 1.0),
    ("Why haven't they capitulated?", "shimmer", 1.0),
    # Scene 4: tanker_jenga (clips 7-9)
    ("Error. Exit strategy not found.", "shimmer", 1.0),
    ("A fifth of the world's oil fits through one throat.", "onyx", 0.9),
    ("Gas is not a side effect. It is the invoice.", "onyx", 1.0),
    # Scene 5: sanction_spackle (clips 10-13)
    ("We won.", "echo", 1.0),
    ("We've got to finish the job.", "echo", 1.0),
    ("This story is gossip and speculation.", "nova", 1.0),
    ("The President is his own best messenger.", "nova", 1.0),
    # Scene 6: finish_job (clips 14-17)
    ("The fix for one war was more oil from another.", "onyx", 0.9),
    ("Your rent, your groceries, your fuel. That's the blast radius.", "alloy", 1.0),
    ("Peace, apparently, is a loading bar with missiles.", "echo", 1.0),
    ("The bar never reaches one hundred.", "alloy", 1.0),
]

tts_effects = [
    "stutter",     # 0: system loading — glitched
    "normal",      # 1: narrator — deadpan
    "echo",        # 2: Trump excursion — dismissive echo
    "normal",      # 3: Trump gas prices — flat
    "fast",        # 4: Hegseth winning — frantic
    "normal",      # 5: Hegseth toast — smug
    "telephone",   # 6: Witkoff — diplomatic compression
    "stutter",     # 7: system error — glitched
    "slow",        # 8: narrator oil — ominous
    "normal",      # 9: narrator invoice — deadpan
    "echo",        # 10: Trump won — hollow
    "fast",        # 11: Trump finish — urgent pivot
    "normal",      # 12: Leavitt gossip — dismissive
    "echo",        # 13: Leavitt messenger — ironic reverb
    "slow",        # 14: narrator fix — ominous
    "whisper",     # 15: narrator blast radius — dread
    "chorus",      # 16: narrator loading bar — layered
    "whisper",     # 17: narrator never reaches — final
]

SCENE_AUDIO_MAP = {
    "peace_brand":       [0, 1],
    "little_excursion":  [2, 3],
    "toast_tv":          [4, 5, 6],
    "tanker_jenga":      [7, 8, 9],
    "sanction_spackle":  [10, 11, 12, 13],
    "finish_job":        [14, 15, 16, 17],
}

music_config = {
    "layers": [
        # 1. Patriotic pad — major key, slightly detuned, campaign-ad warmth
        {"type": "pad", "freq": 293.66, "freq2": 294.2, "duration": 110,
         "volume": 0.007, "filters": "tremolo=f=0.15:d=0.2"},
        # 2. Industrial sub-bass — sawtooth, war machine rumble
        {"type": "sawtooth", "freq": 45, "duration": 110,
         "volume": 0.007, "filters": "lowpass=f=300,tremolo=f=1.2:d=0.5"},
        # 3. Ticking rhythm — typing-style percussion
        {"type": "pluck", "freq": 880, "decay": 0.1, "duration": 110,
         "volume": 0.004, "filters": "highpass=f=2000"},
        # 4. Corrupted modem chirps — FM synth, unstable
        {"type": "fm", "freq": 660, "mod_freq": 11, "mod_depth": 80,
         "duration": 110, "volume": 0.003,
         "filters": "lowpass=f=4000,tremolo=f=2.0:d=0.8"},
        # 5. Warning tone arpeggio — alert siren feel
        {"type": "arpeggio", "freq": 523,
         "notes": [523, 659, 784, 659],
         "step_duration": 0.4, "duration": 110,
         "volume": 0.003, "filters": "lowpass=f=3000,afade=t=in:d=30"},
        # 6. Sub-drone — brown noise, anxiety floor
        {"type": "noise", "color": "brown", "duration": 110,
         "volume": 0.004, "filters": "lowpass=f=120"},
        # 7. Dissonance buildup — drone chord, late fade-in
        {"type": "drone_chord", "freq": 196,
         "freqs": [196, 277.18, 392], "duration": 110,
         "volume": 0.003, "filters": "afade=t=in:d=50"},
    ],
    "master_filters": "volume=0.85",
    "mix_volume": 0.30,
}

sfx_cues = [
    # Scene 1: peace_brand
    {"name": "patriotic_chime", "type": "power_up", "freq": 523, "duration": 1.2,
     "filters": "volume=0.4,afade=t=out:d=0.6"},
    {"name": "static_cut", "type": "glitch", "duration": 0.3,
     "filters": "volume=0.3"},
    {"name": "stamp_thud", "type": "impact", "freq": 80, "duration": 0.4,
     "filters": "volume=0.5"},
    # Scene 2: little_excursion
    {"name": "golf_impact", "type": "impact", "freq": 200, "duration": 0.3,
     "filters": "volume=0.4"},
    {"name": "alert_tone", "type": "tone", "freq": 880, "duration": 0.5,
     "filters": "volume=0.4,afade=t=out:d=0.3"},
    # Scene 3: toast_tv
    {"name": "news_whoosh", "type": "whoosh", "freq": 2000, "duration": 0.5,
     "filters": "volume=0.3"},
    {"name": "crowd_burst", "type": "noise_burst", "duration": 0.6,
     "color": "pink", "filters": "volume=0.2,lowpass=f=1000"},
    # Scene 4: tanker_jenga
    {"name": "oil_drone", "type": "sweep", "freq": 50, "duration": 4.0,
     "filters": "volume=0.2"},
    {"name": "market_crash", "type": "impact", "freq": 60, "duration": 1.0,
     "filters": "volume=0.4,lowpass=f=200"},
    {"name": "tanker_horn", "type": "sweep", "freq": 120, "duration": 2.0,
     "filters": "volume=0.25,lowpass=f=400"},
    # Scene 5: sanction_spackle
    {"name": "paper_shuffle", "type": "typing", "rate": 8, "duration": 1.5,
     "filters": "volume=0.12"},
    {"name": "rubber_stamp", "type": "impact", "freq": 150, "duration": 0.2,
     "filters": "volume=0.4"},
    # Scene 6: finish_job
    {"name": "loading_tick", "type": "typing", "rate": 3, "duration": 2.0,
     "filters": "volume=0.15"},
    {"name": "error_beep", "type": "tone", "freq": 440, "duration": 0.2,
     "filters": "volume=0.5,afade=t=out:d=0.15"},
    {"name": "final_drone", "type": "tone", "freq": 196, "duration": 5.0,
     "filters": "afade=t=out:d=4.0,volume=0.3"},
    {"name": "static_fade", "type": "noise_burst", "duration": 2.0,
     "color": "pink", "filters": "afade=t=in:d=0.5,afade=t=out:d=1.0,volume=0.12"},
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
    """Audio-aware duration for a scene, or fallback if no data."""
    if not tts_durations:
        return fallback
    clips = SCENE_AUDIO_MAP.get(scene_name, [])
    if not clips:
        return fallback
    return audio_duration(tts_durations, clips, padding=0.3, gap_per_clip=0.12)


def _peace_bar(draw, t, x, y, w, h, font):
    """Recurring motif: the PEACE loading bar that never finishes.

    Cycles through states: loading → glitch → reset → relabel → drop.
    """
    # Determine bar state from t (wraps through a cycle)
    cycle = (t * 2) % 1.0  # two cycles per scene-t

    if cycle < 0.4:
        # Filling up
        pct = int(cycle / 0.4 * 99)
        label = f"LOADING PEACE... {pct}%"
        fill_frac = pct / 100
        bar_color = (0, 255, 0)
    elif cycle < 0.5:
        # Glitch
        pct = random.randint(30, 99)
        label = f"L0AD\u0338NG P\u0336EA\u0337CE... {pct}%"
        fill_frac = random.random()
        bar_color = (255, 255, 0)
    elif cycle < 0.7:
        # "MISSION ACCOMPLISHED"
        pct = 100
        label = "MISSION ACCOMPLISHED"
        fill_frac = 1.0
        bar_color = (255, 200, 0)
    else:
        # Drop to 12%
        pct = 12
        label = f"LOADING PEACE... {pct}%"
        fill_frac = 0.12
        bar_color = (255, 0, 0)

    # Draw bar
    draw.rectangle([(x, y), (x + w, y + h)], outline=(200, 200, 200), width=2)
    fill_w = int(w * fill_frac)
    if fill_w > 0:
        draw.rectangle([(x + 2, y + 2), (x + 2 + fill_w, y + h - 2)],
                       fill=bar_color)
    draw.text((x, y - 22), label, fill=bar_color, font=font)


def _price_ticker(draw, t, w, h, font):
    """Recurring motif: climbing price ticker in top-right corner."""
    base_oil = 78 + int(t * 180)
    base_gas = 3.12 + t * 2.8
    sentiment = max(10, int(72 - t * 55))

    items = [
        (f"OIL ${base_oil}/bbl", (255, 60, 60)),
        (f"GAS ${base_gas:.2f}/gal", (255, 100, 40)),
        (f"SENTIMENT {sentiment}", (255, 200, 0) if sentiment > 40 else (255, 0, 0)),
    ]

    ticker_x = w - 260
    ticker_y = 15
    draw.rectangle([(ticker_x - 10, ticker_y - 5),
                    (w - 10, ticker_y + len(items) * 24 + 5)],
                   fill=(0, 0, 0))

    for i, (text, color) in enumerate(items):
        draw.text((ticker_x, ticker_y + i * 24), text, fill=color, font=font)


def _dove_symbol(draw, cx, cy, size, t):
    """Recurring motif: peace symbol that morphs into crosshair/pump/missile.

    Uses text glyphs for simplicity — the mutation is the joke.
    """
    font = _font(SANS_BOLD, size)
    cycle = (t * 1.5) % 1.0

    if cycle < 0.25:
        symbol, color = "\u262e", (255, 215, 0)      # ☮ peace — gold
    elif cycle < 0.5:
        symbol, color = "\u2295", (255, 0, 0)         # ⊕ crosshair — red
    elif cycle < 0.75:
        symbol, color = "\u26fd", (100, 100, 100)     # ⛽ gas pump — grey
    else:
        symbol, color = "\u2316", (255, 80, 0)        # ⌖ target — orange

    try:
        tw = font.getlength(symbol)
    except AttributeError:
        tw = size * 0.6
    draw.text((cx - tw // 2, cy - size // 2), symbol, fill=color, font=font)


# ── Scene Definitions ──────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs, tts_durations=None):
    """Build scene list with audio-aware durations."""
    scenes = []
    sfx_timeline = []

    def _scene_start():
        return sum(dur for _, dur, _ in scenes)

    W, H = WIDTH, HEIGHT

    # ═══ SCENE 1: PEACE BRAND (~15s) ═══
    # Patriotic infomercial melts into war branding.

    def scene_peace_brand(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Base: DALL-E patriotic ad studio
        if dalle_images:
            img = load_and_resize(dalle_images[0], (W, H))
        else:
            img = gen_plasma(ft, W, H, "fire")

        # Flag GIFs blend in early
        if t < 0.4 and giphy_gifs:
            flag = load_and_resize(giphy_gifs[0], (W, H), frame=frame_num)
            img = Image.blend(img, flag, 0.3)

        draw = ImageDraw.Draw(img)
        font_big = _font(SANS_BOLD, 56)
        font_med = _font(SANS_BOLD, 36)
        font_bar = _font(MONO_BOLD, 18)

        # "PRESIDENT OF PEACE" title card
        if t < 0.35:
            title = "PRESIDENT OF PEACE"
            try:
                tw = font_big.getlength(title)
            except AttributeError:
                tw = len(title) * 32
            # Gold on dark banner
            draw.rectangle([(0, H // 2 - 60), (W, H // 2 + 60)],
                          fill=(10, 10, 30))
            draw.text((W // 2 - tw // 2, H // 2 - 30),
                      title, fill=(255, 215, 0), font=font_big)

        # Stamp: "OPERATION EPIC FURY" crashes in
        if t > 0.4:
            stamp = "OPERATION EPIC FURY"
            try:
                tw = font_med.getlength(stamp)
            except AttributeError:
                tw = len(stamp) * 20
            jx = random.randint(-3, 3)
            jy = random.randint(-2, 2)
            draw.text((W // 2 - tw // 2 + jx, H // 2 - 20 + jy),
                      stamp, fill=(255, 0, 0), font=font_med)

        # Peace symbol morphing in corner
        _dove_symbol(draw, 100, 100, 60, t)

        # Loading bar appears mid-scene
        if t > 0.3:
            _peace_bar(draw, t, 160, H - 80, W - 320, 28, font_bar)

        # Effects: starts clean, corrupts
        if t > 0.4:
            img = effect_chromatic_aberration(img, 1.0 + (t - 0.4) * 5)
        if t > 0.6:
            img = effect_scanlines(img)
        if t > 0.8:
            img = effect_glitch_blocks(img, 3)

        return img

    dur = _dur(tts_durations, "peace_brand", 15.0)
    t0 = _scene_start()
    scenes.append(("peace_brand", dur, scene_peace_brand))
    sfx_timeline.append((t0, "patriotic_chime"))
    sfx_timeline.append((t0 + dur * 0.4, "stamp_thud"))
    sfx_timeline.append((t0 + dur * 0.8, "static_cut"))

    # ═══ SCENE 2: LITTLE EXCURSION (~14s) ═══
    # Country-club dismissiveness meets DEFCON reality.

    def scene_little_excursion(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Base: DALL-E golf resort with war graphics
        if dalle_images and len(dalle_images) > 1:
            img = load_and_resize(dalle_images[1], (W, H))
        else:
            img = gen_voronoi(ft, W, H, palette="neon")

        # Golf / alarm GIFs cut in
        if giphy_gifs and len(giphy_gifs) > 4:
            if t < 0.5:
                gif = load_and_resize(giphy_gifs[4], (W, H), frame=frame_num)
            else:
                gif = load_and_resize(giphy_gifs[5], (W, H), frame=frame_num)
            img = Image.blend(img, gif, 0.25 + t * 0.15)

        draw = ImageDraw.Draw(img)
        font = _font(SANS_BOLD, 40)
        font_sm = _font(MONO, 18)
        font_bar = _font(MONO_BOLD, 18)

        # Casual-to-war text escalation
        quotes = [
            (0.1, "\"a little excursion\"", (255, 255, 255)),
            (0.3, "\"short-term operation\"", (255, 255, 200)),
            (0.5, "\"if they rise, they rise\"", (255, 200, 100)),
            (0.7, "\"very hard strikes\"", (255, 100, 50)),
            (0.85, "\"FINISH THE JOB\"", (255, 0, 0)),
        ]
        y_text = 120
        for threshold, text, color in quotes:
            if t > threshold:
                draw.text((60, y_text), text, fill=color, font=font)
                y_text += 55

        # Price ticker — gas climbing
        _price_ticker(draw, t, W, H, font_sm)

        # Peace symbol in corner
        _dove_symbol(draw, W - 80, H - 80, 50, t)

        # Effects: country club to war zone
        img = effect_wave_distort(img, ft, amplitude=4 + t * 8, frequency=0.015)
        if t > 0.5:
            img = effect_deep_fry(img)
        if t > 0.7:
            img = effect_vhs_tracking(img)

        return img

    dur = _dur(tts_durations, "little_excursion", 14.0)
    t0 = _scene_start()
    scenes.append(("little_excursion", dur, scene_little_excursion))
    sfx_timeline.append((t0, "golf_impact"))
    sfx_timeline.append((t0 + dur * 0.5, "alert_tone"))

    # ═══ SCENE 3: TOAST TV (~16s) ═══
    # Cable news as military play-by-play.

    def scene_toast_tv(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Base: DALL-E anchor desk + command center
        if dalle_images and len(dalle_images) > 2:
            img = load_and_resize(dalle_images[2], (W, H))
        else:
            img = gen_plasma(ft, W, H, "fire")

        # Cable news GIFs cycle rapidly
        if giphy_gifs and len(giphy_gifs) > 8:
            cycle_rate = max(3, int(10 * (1.0 - t * 0.6)))
            gif_idx = (frame_num // cycle_rate) % min(len(giphy_gifs), 10)
            gif = load_and_resize(giphy_gifs[gif_idx], (W, H), frame=frame_num)
            img = Image.blend(img, gif, 0.3)

        draw = ImageDraw.Draw(img)
        font_banner = _font(SANS_BOLD, 28)
        font_lower = _font(MONO_BOLD, 22)
        font_sm = _font(MONO, 16)
        font_bar = _font(MONO_BOLD, 18)

        # Lower-third news banners with escalating absurdity
        banners = [
            (0.0, "BREAKING: AMERICA IS WINNING", (200, 0, 0)),
            (0.15, "HEGSETH: \"THEY ARE TOAST\"", (180, 0, 0)),
            (0.3, "WAR DEPARTMENT UPDATE: WINNING HARDER", (160, 0, 0)),
            (0.45, "ANALYST: \"WHY HAVEN'T THEY CAPITULATED\"", (140, 0, 0)),
            (0.6, "BREAKING: STILL WINNING (PLEASE CLAP)", (120, 0, 0)),
            (0.75, "NO QUARTER, NO MERCY, NO EXIT STRATEGY", (100, 0, 0)),
        ]

        # Show most recent applicable banner
        current_banner = None
        for threshold, text, bg_color in banners:
            if t > threshold:
                current_banner = (text, bg_color)

        if current_banner:
            text, bg_color = current_banner
            # Red banner bar at bottom
            draw.rectangle([(0, H - 90), (W, H - 50)], fill=bg_color)
            draw.text((20, H - 86), text, fill=(255, 255, 255), font=font_banner)
            # Ticker bar below
            draw.rectangle([(0, H - 50), (W, H - 20)], fill=(0, 0, 0))
            ticker_text = "TOAST /// WINNING /// TOAST /// NO QUARTER /// VICTORY IS IMMINENT /// TOAST /// "
            offset = int(ft * 150) % (len(ticker_text) * 10)
            doubled = ticker_text * 3
            draw.text((-offset, H - 46), doubled,
                      fill=(255, 255, 0), font=font_lower)

        # Scoreboard overlay — "WAR STATS" in corner
        if t > 0.3:
            draw.rectangle([(20, 20), (280, 160)], fill=(0, 0, 0))
            draw.rectangle([(20, 20), (280, 160)], outline=(255, 0, 0), width=2)
            draw.text((30, 25), "WAR SCOREBOARD", fill=(255, 0, 0), font=font_lower)
            draw.text((30, 55), f"SORTIES: {random.Random(42).randint(400, 800)}",
                      fill=(255, 255, 255), font=font_sm)
            draw.text((30, 78), f"TOAST LVL: MAXIMUM",
                      fill=(255, 200, 0), font=font_sm)
            draw.text((30, 101), f"EXIT PLAN: 404",
                      fill=(255, 100, 100), font=font_sm)
            draw.text((30, 124), f"MERCY: 0.00%",
                      fill=(255, 100, 100), font=font_sm)

        # Peace bar bottom-left
        if t > 0.5:
            _peace_bar(draw, t, 20, H - 130, 250, 20, font_sm)

        # Effects: cable news visual hell
        img = effect_chromatic_aberration(img, 2.0 + t * 2)
        if t > 0.5 and random.random() > 0.6:
            img = effect_channel_shift(img)
        if t > 0.7:
            img = effect_glitch_blocks(img, 3)

        return img

    dur = _dur(tts_durations, "toast_tv", 16.0)
    t0 = _scene_start()
    scenes.append(("toast_tv", dur, scene_toast_tv))
    sfx_timeline.append((t0, "news_whoosh"))
    sfx_timeline.append((t0 + dur * 0.3, "crowd_burst"))
    sfx_timeline.append((t0 + dur * 0.6, "news_whoosh"))

    # ═══ SCENE 4: TANKER JENGA (~20s) ═══
    # Oil crisis. Hormuz chokepoint. Gas prices. The invoice arrives.

    def scene_tanker_jenga(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Gas station / pump interlude mid-scene
        if 0.4 < t < 0.6:
            if giphy_gifs and len(giphy_gifs) > 14:
                interlude = giphy_gifs[12:min(16, len(giphy_gifs))]
                idx = (frame_num // 8) % len(interlude)
                img = load_and_resize(interlude[idx], (W, H), frame=frame_num)
            else:
                img = gen_plasma(ft, W, H, "fire")
            img = effect_deep_fry(img)

            draw = ImageDraw.Draw(img)
            font_price = _font(SANS_BOLD, 72)
            font_sm = _font(MONO, 18)
            # Giant gas price
            gas = 3.12 + t * 3.5
            price_text = f"${gas:.2f}"
            try:
                tw = font_price.getlength(price_text)
            except AttributeError:
                tw = len(price_text) * 42
            draw.text((W // 2 - tw // 2, H // 2 - 40),
                      price_text, fill=(255, 0, 0), font=font_price)
            draw.text((W // 2 - 80, H // 2 + 50),
                      "per gallon", fill=(200, 200, 200), font=font_sm)

            _price_ticker(draw, t, W, H, _font(MONO, 16))
            img = effect_chromatic_aberration(img, 3.0)
            return img

        # Main: satellite view of Hormuz
        if dalle_images and len(dalle_images) > 3:
            img = load_and_resize(dalle_images[3], (W, H))
        else:
            img = gen_voronoi(ft, W, H, palette="dark")

        # Thermal effect on the map
        img = effect_thermal(img)
        img = effect_wave_distort(img, ft, amplitude=5, frequency=0.02)

        draw = ImageDraw.Draw(img)
        font_x = _font(SANS_BOLD, 32)
        font_sm = _font(MONO, 18)
        font_bar = _font(MONO_BOLD, 18)

        # Tanker markers appearing progressively
        random.seed(77)
        n_markers = int(t * 12) + 1
        for i in range(n_markers):
            mx = random.randint(150, W - 150)
            my = random.randint(150, H - 150)
            draw.text((mx, my), "\u2715", fill=(255, 0, 0), font=font_x)
            if i < 3:
                draw.text((mx + 20, my + 5), "STRUCK", fill=(255, 100, 0),
                          font=_font(MONO, 14))
        random.seed()

        # Price ticker
        _price_ticker(draw, t, W, H, font_sm)

        # "STRAIT OF HORMUZ" label
        draw.rectangle([(20, H - 60), (340, H - 25)], fill=(0, 0, 0))
        draw.text((30, H - 55), "STRAIT OF HORMUZ",
                  fill=(255, 200, 0), font=_font(MONO_BOLD, 22))

        # Loading bar — labeled "OIL SUPPLY" depleting
        if t > 0.2:
            supply_bar_x = 20
            supply_bar_y = H - 100
            bar_w = 300
            bar_h = 22
            supply_pct = max(0.05, 1.0 - t * 0.9)
            draw.rectangle([(supply_bar_x, supply_bar_y),
                           (supply_bar_x + bar_w, supply_bar_y + bar_h)],
                          outline=(200, 200, 200), width=1)
            fill_w = int(bar_w * supply_pct)
            bar_color = (0, 255, 0) if supply_pct > 0.5 else (255, 0, 0)
            draw.rectangle([(supply_bar_x + 1, supply_bar_y + 1),
                           (supply_bar_x + 1 + fill_w, supply_bar_y + bar_h - 1)],
                          fill=bar_color)
            draw.text((supply_bar_x, supply_bar_y - 20),
                      f"OIL SUPPLY {int(supply_pct * 100)}%",
                      fill=bar_color, font=font_sm)

        # Fire overlay late
        if t > 0.7 and giphy_gifs and len(giphy_gifs) > 12:
            fire = load_and_resize(giphy_gifs[12], (W, H), frame=frame_num)
            img = Image.blend(img, fire, 0.25)

        # Chromatic aberration intensifies
        img = effect_chromatic_aberration(img, 1.5 + t * 3)
        if t > 0.8:
            img = effect_deep_fry(img)

        return img

    dur = _dur(tts_durations, "tanker_jenga", 20.0)
    t0 = _scene_start()
    scenes.append(("tanker_jenga", dur, scene_tanker_jenga))
    sfx_timeline.append((t0, "oil_drone"))
    sfx_timeline.append((t0 + dur * 0.35, "tanker_horn"))
    sfx_timeline.append((t0 + dur * 0.6, "market_crash"))

    # ═══ SCENE 5: SANCTION SPACKLE (~18s) ═══
    # Moral clarity with emergency exceptions. Russian oil waivers.

    def scene_sanction_spackle(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Base: DALL-E boardroom with oil-dripping spreadsheets
        if dalle_images and len(dalle_images) > 4:
            img = load_and_resize(dalle_images[4], (W, H))
        else:
            img = gen_plasma(ft, W, H, "vaporwave")

        # Paperwork / stock crash GIFs cut in
        if giphy_gifs and len(giphy_gifs) > 18:
            if frame_num % 24 < 8:
                gif = load_and_resize(giphy_gifs[16 % len(giphy_gifs)], (W, H),
                                      frame=frame_num)
                img = Image.blend(img, gif, 0.35)

        draw = ImageDraw.Draw(img)
        font_lg = _font(SANS_BOLD, 36)
        font_sm = _font(MONO, 18)
        font_bar = _font(MONO_BOLD, 18)

        # Sanction dashboard — toggles flipping
        if t > 0.15:
            draw.rectangle([(40, 60), (W - 40, 340)], fill=(15, 15, 20))
            draw.rectangle([(40, 60), (W - 40, 340)],
                          outline=(100, 100, 100), width=1)
            draw.text((60, 70), "SANCTIONS DASHBOARD v2.026",
                      fill=(0, 255, 0), font=_font(MONO_BOLD, 22))

            sanctions = [
                ("IRAN OIL", "ENFORCED", (255, 0, 0)),
                ("RUSSIAN OIL", "WAIVED (30 DAYS)", (255, 200, 0)),
                ("MORAL CLARITY", "ADJUSTABLE", (255, 150, 0)),
                ("ALLIED CONFIDENCE", "DECLINING", (255, 80, 0)),
                ("COHERENCE", "404 NOT FOUND", (255, 0, 0)),
            ]
            visible = int((t - 0.15) / 0.85 * len(sanctions) * 1.3) + 1
            for i, (label, status, color) in enumerate(sanctions[:visible]):
                if i >= len(sanctions):
                    break
                y = 110 + i * 40
                draw.text((60, y), f"{label}:", fill=(180, 180, 180), font=font_sm)
                draw.text((400, y), status, fill=color, font=font_sm)
                # Blinking indicator
                if frame_num % 12 < 6:
                    draw.ellipse([(W - 80, y + 3), (W - 68, y + 15)], fill=color)

        # Contradiction quotes overlaid
        if t > 0.5:
            contradictions = [
                "\"gossip and speculation\"",
                "\"his own best messenger\"",
                "\"we won\" → \"finish the job\"",
            ]
            vis = int((t - 0.5) * 8) + 1
            for i, text in enumerate(contradictions[:vis]):
                jx = random.randint(-3, 3)
                y = 380 + i * 45
                draw.text((60 + jx, y), text, fill=(255, 255, 255), font=font_lg)

        # Price ticker
        _price_ticker(draw, t, W, H, _font(MONO, 16))

        # Peace bar
        if t > 0.4:
            _peace_bar(draw, t, 60, H - 80, W - 120, 24, font_bar)

        # Effects: bureaucratic decay
        if t > 0.3:
            img = effect_scanlines(img)
        if t > 0.6 and random.random() > 0.5:
            img = effect_bit_crush(img, bits=5)
        if t > 0.8:
            img = effect_glitch_blocks(img, 4)

        return img

    dur = _dur(tts_durations, "sanction_spackle", 18.0)
    t0 = _scene_start()
    scenes.append(("sanction_spackle", dur, scene_sanction_spackle))
    sfx_timeline.append((t0, "paper_shuffle"))
    sfx_timeline.append((t0 + dur * 0.3, "rubber_stamp"))
    sfx_timeline.append((t0 + dur * 0.6, "rubber_stamp"))

    # ═══ SCENE 6: FINISH JOB (~17s) ═══
    # The loading bar never reaches 100%. The receipt arrives.

    def scene_finish_job(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = Image.new("RGB", (W, H), (0, 0, 0))

        # Phase 1 (t < 0.25): DALL-E error screen cycling with loading bar GIFs
        if t < 0.25:
            if dalle_images and len(dalle_images) > 5:
                img = load_and_resize(dalle_images[5], (W, H))
            elif giphy_gifs and len(giphy_gifs) > 20:
                idx = (frame_num // 6) % min(len(giphy_gifs), 22)
                img = load_and_resize(giphy_gifs[idx], (W, H), frame=frame_num)
            else:
                img = gen_plasma(ft, W, H, "matrix")

            # Loading bar stuck at 99%, glitching
            draw = ImageDraw.Draw(img)
            font_bar = _font(MONO_BOLD, 22)
            bar_w = int(W * 0.7)
            bar_x = (W - bar_w) // 2
            bar_y = H // 2 + 100
            pct = 99 if frame_num % 24 < 18 else random.randint(12, 98)
            label = f"LOADING PEACE... {pct}%"
            draw.rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 30)],
                          outline=(0, 255, 0), width=2)
            fill_w = int(bar_w * (pct / 100))
            draw.rectangle([(bar_x + 2, bar_y + 2),
                           (bar_x + 2 + fill_w, bar_y + 28)],
                          fill=(0, 255, 0) if pct > 50 else (255, 0, 0))
            draw.text((bar_x, bar_y - 28), label,
                      fill=(0, 255, 0), font=font_bar)

            img = effect_scanlines(img)
            if random.random() > 0.7:
                img = effect_chromatic_aberration(img, 3.0)
            return img

        # Phase 2 (0.25 < t < 0.8): Terminal text crawl — the receipt
        draw = ImageDraw.Draw(img)
        font = _font(MONO, 20)
        font_sm = _font(MONO, 16)

        stats = [
            "THE RECEIPT",
            "=" * 38,
            "",
            "Item                          Cost",
            "-" * 38,
            f"Gas price increase:        +{random.Random(50).randint(18, 25)}%",
            f"Oil per barrel:            ${random.Random(51).randint(98, 130)}",
            f"Consumer sentiment:        FALLING",
            f"Russian oil waiver:        30 DAYS",
            f"Congressional approval:    N/A",
            f"Exit strategy:             N/A",
            f"Allied trust:              DECLINING",
            "",
            "-" * 38,
            "Messaged as:               PEACE",
            "Delivered as:              WAR",
            "",
            "Thank you for your purchase.",
        ]

        text_t = (t - 0.25) / 0.55
        visible = int(text_t * len(stats) * 1.3) + 1

        y = 60
        for i, line in enumerate(stats[:visible]):
            if i >= len(stats):
                break
            if y > H - 140:
                break
            if "PEACE" in line and "LOADING" not in line:
                color = (255, 215, 0)
            elif "WAR" in line:
                color = (255, 0, 0)
            elif "N/A" in line or "DECLINING" in line or "FALLING" in line:
                color = (255, 100, 100)
            else:
                color = (0, 255, 0)
            draw.text((60, y), line, fill=color, font=font)
            y += 26

        # Blinking cursor
        if frame_num % 18 < 9:
            draw.text((60, y + 10), "> _", fill=(0, 255, 0), font=font)

        img = effect_scanlines(img)

        # Phase 3 (t > 0.8): Final card — the punchline
        if t > 0.8:
            img = Image.new("RGB", (W, H), (0, 0, 0))
            draw = ImageDraw.Draw(img)
            font_punch = _font(SANS_BOLD, 32)
            font_date = _font(MONO, 20)

            lines = [
                ("They sold a war", (255, 255, 255)),
                ("as proof of peace,", (255, 215, 0)),
                ("then handed everyone", (255, 255, 255)),
                ("the receipt at the pump.", (255, 0, 0)),
            ]

            punch_t = (t - 0.8) / 0.2
            visible_lines = int(punch_t * len(lines) * 1.5) + 1

            for i, (text, color) in enumerate(lines[:visible_lines]):
                if i >= len(lines):
                    break
                try:
                    tw = font_punch.getlength(text)
                except AttributeError:
                    tw = len(text) * 18
                draw.text((W // 2 - tw // 2, H // 2 - 90 + i * 48),
                          text, fill=color, font=font_punch)

            if punch_t > 0.7:
                date_text = "March 2026"
                try:
                    dw = font_date.getlength(date_text)
                except AttributeError:
                    dw = len(date_text) * 12
                draw.text((W // 2 - dw // 2, H // 2 + 120),
                          date_text, fill=(80, 80, 80), font=font_date)

            img = effect_scanlines(img)

        return img

    dur = _dur(tts_durations, "finish_job", 17.0)
    t0 = _scene_start()
    scenes.append(("finish_job", dur, scene_finish_job))
    sfx_timeline.append((t0, "loading_tick"))
    sfx_timeline.append((t0 + dur * 0.25, "error_beep"))
    sfx_timeline.append((t0 + dur * 0.7, "final_drone"))
    sfx_timeline.append((t0 + dur * 0.85, "static_fade"))

    return scenes, sfx_timeline

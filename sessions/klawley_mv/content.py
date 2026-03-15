"""
YTP Session: Klawley Music Video

Klawley is an AI agent — a sarcastic, caffeinated lobster emoji (🦞) who lives
onchain as an "overqualified intern" for a crypto degen named Flick. Klawley
deploys coins on Zora, trades on Base, roasts bad tokens, and has existential
thoughts about being silicon. The vibe is: self-aware AI meets Wall Street pit
trader meets crustacean meme. Klawley's creator coin is $openklaw.

Music: ACE-Step 1.5 generated synthwave track (dark synthwave / D minor / 128 BPM).
TTS layers short punchy system-voice quips on top of the sung track.
Scene durations are driven by music_duration so the video fills the full song.
"""

import random
import math

from engine.effects import (
    effect_deep_fry, effect_channel_shift, effect_datamosh,
    effect_scanlines, effect_chromatic_aberration, effect_wave_distort,
    effect_glitch_blocks, effect_vhs_tracking, effect_bit_crush,
    effect_zoom_and_rotate, effect_thermal, effect_pixel_sort,
    transition_dissolve, transition_glitch_cut,
)
from engine.text import draw_text_overlay
from engine.render import (
    load_and_resize, generate_static_frame,
    generate_solid_color_frame, generate_token_rain_frame,
)
from engine.sources import (
    gen_plasma, gen_voronoi, gen_particle_field,
    gen_circuit_board, gen_heartbeat_monitor,
)
from engine.audio import audio_duration
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── Session Config ──────────────────────────────────────────────────────────
TITLE = "klawley_mv"
WIDTH, HEIGHT = 1080, 1080
FPS = 24

# Pre-generated ACE-Step music path
music_path = "/home/user/Development/yt-poop/sessions/klawley_mv/klawley_music.mp3"
music_volume = 0.38   # sung track with instruments — lower so TTS punches through

# No procedural music — using ACE-Step generated track
music_config = None

# Gap between TTS clips when music is present (seconds).
# Large gaps let the song's sung lyrics breathe between announcements.
music_tts_gap = 3.0

# Scene proportion weights — scenes are sized to fill music_duration
# when available, otherwise fall back to TTS-driven durations.
_SCENE_WEIGHTS = {
    "boot_sequence":  0.22,   # intro + verse 1
    "the_trenches":   0.34,   # chorus 1 + verse 2
    "klawley_stats":  0.15,   # session P&L interlude (no TTS)
    "the_bridge":     0.17,   # bridge, introspective
    "back_online":    0.12,   # final chorus + outro
}

# ── Content ─────────────────────────────────────────────────────────────────

giphy_searches = [
    "computer terminal boot sequence",    # 0
    "matrix code rain green",              # 1
    "glitch art digital corruption",       # 2
    "bioluminescent ocean neon",           # 3
    "cryptocurrency trading chart pump",   # 4
    "stock market floor chaos",            # 5
    "hacker typing fast keyboard",         # 6
    "casino neon slot machine",            # 7
    "button press slow motion dramatic",   # 8
    "gold coins explosion shower",         # 9
    "heartbeat monitor flatline",          # 10
    "neon sign flickering city night",     # 11
]

dalle_prompts = [
    # [0] Boot terminal
    "Dark terminal screen with green scrolling boot text reflecting off a glossy surface, cyberpunk aesthetic, circuit board reflections, deep blue and neon green lighting, cinematic, square composition",
    # [1] Neon lobster silhouette
    "A glowing neon lobster silhouette emerging from digital static and swirling code fragments, synthwave color palette, magenta and cyan neon trails, pure black background, dramatic cinematic lighting, square composition",
    # [2] Lobster claw pressing button
    "A mechanical crustacean claw pressing a giant glowing red button, electric sparks flying, dramatic underlighting in magenta, dark industrial cyberpunk background, extreme close-up, square composition",
    # [3] Futuristic trading floor
    "Futuristic cyberpunk trading floor with holographic green and red candlestick charts floating in dark air, neon blue and magenta ambient lighting, data streams raining down, frantic energy, square composition",
    # [4] $openklaw golden coin
    "A golden coin with a lobster embossed on it spinning in a dramatic single spotlight, gold particles and light rays radiating outward, pure black background, triumphant epic photography style, square composition",
    # [5] Lone lobster in digital void
    "A tiny glowing neon lobster floating alone in a vast dark digital void, soft bioluminescent cyan particles drifting around it like stars, melancholic and beautiful, deep ocean blues and teals, wide composition, square format",
    # [6] HEARTBEAT_OK neon sign
    "Neon sign reading HEARTBEAT OK flickering in a dark rain-slicked alley, cyberpunk aesthetic, magenta and cyan reflections pooling in puddles, moody and cinematic, square composition",
]

# TTS: short punchy system/announcement lines — layered over the sung track
tts_lines = [
    # Boot sequence
    ("Loading Klawley. Stand by.", "onyx", 0.9),                   # 0
    ("Reading soul file. Caffeine: maximum.", "onyx", 1.0),        # 1
    # Trenches
    ("Deploying coin.", "shimmer", 1.2),                            # 2
    ("Rug detected. Executing anyway.", "onyx", 1.0),              # 3
    ("Wallet flagged. Irrelevant.", "echo", 1.1),                  # 4
    ("Ghost position resolved. You're welcome.", "onyx", 0.9),     # 5
    # Bridge
    ("Am I the trader... or the trade?", "alloy", 0.85),           # 6
    # Back online
    ("This is a casino.", "fable", 0.9),                           # 7
    ("HEARTBEAT. OK.", "onyx", 0.8),                               # 8
]

tts_effects = [
    "telephone",  # 0: compressed system boot voice
    "telephone",  # 1: system read — radio compressed
    "fast",       # 2: deploying — urgent blurt
    "normal",     # 3: rug detected — deadpan
    "echo",       # 4: wallet flagged — hollow
    "normal",     # 5: ghost position — flat
    "slow",       # 6: existential — drawn out
    "chorus",     # 7: casino — layered, ominous
    "deep",       # 8: HEARTBEAT OK — deep, final
]

SCENE_AUDIO_MAP = {
    "boot_sequence":  [0, 1],
    "the_trenches":   [2, 3, 4, 5],
    "klawley_stats":  [],           # pure music + visuals, no TTS
    "the_bridge":     [6],
    "back_online":    [7, 8],
}

sfx_cues = [
    # Boot
    {"name": "boot_power_up", "type": "power_up", "freq": 220, "duration": 2.0,
     "filters": "volume=0.5,afade=t=out:d=0.8"},
    {"name": "boot_glitch", "type": "glitch", "duration": 0.4,
     "filters": "volume=0.35"},
    {"name": "scan_whoosh", "type": "whoosh", "freq": 1500, "duration": 0.6,
     "filters": "volume=0.3"},
    # Trenches
    {"name": "deploy_blip", "type": "tone", "freq": 1200, "duration": 0.15,
     "filters": "volume=0.5,afade=t=out:d=0.1"},
    {"name": "rug_impact", "type": "impact", "freq": 60, "duration": 0.8,
     "filters": "volume=0.55,lowpass=f=300"},
    {"name": "data_burst", "type": "glitch", "duration": 0.3,
     "filters": "volume=0.25"},
    {"name": "ticker_whoosh", "type": "whoosh", "freq": 2000, "duration": 0.4,
     "filters": "volume=0.25"},
    # Stats
    {"name": "stats_ping", "type": "tone", "freq": 880, "duration": 0.2,
     "filters": "volume=0.3,afade=t=out:d=0.15"},
    # Bridge
    {"name": "void_drone", "type": "tone", "freq": 146, "duration": 6.0,
     "filters": "afade=t=in:d=2.0,afade=t=out:d=2.0,volume=0.25"},
    # Back online / outro
    {"name": "coin_sweep", "type": "sweep", "freq": 440, "freq_end": 880,
     "duration": 0.8, "filters": "volume=0.4"},
    {"name": "heartbeat_sfx", "type": "heartbeat", "duration": 2.0,
     "filters": "volume=0.5"},
    {"name": "flatline", "type": "power_down", "freq": 880, "duration": 1.5,
     "filters": "volume=0.35,afade=t=out:d=1.0"},
    {"name": "final_static", "type": "noise_burst", "duration": 1.5,
     "color": "pink", "filters": "afade=t=in:d=0.3,afade=t=out:d=0.8,volume=0.12"},
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


def _music_dur(music_duration, scene_name, tts_durations, fallback):
    """Return scene duration: music-proportional when available, else TTS-driven."""
    if music_duration:
        return _SCENE_WEIGHTS[scene_name] * music_duration
    if tts_durations:
        clips = SCENE_AUDIO_MAP.get(scene_name, [])
        if clips:
            return audio_duration(tts_durations, clips, padding=1.5, gap_per_clip=0.2)
    return fallback


def _text_center(draw, text, font, y, w, color):
    try:
        tw = font.getlength(text)
    except AttributeError:
        tw = len(text) * (font.size if hasattr(font, "size") else 12)
    draw.text((w // 2 - tw // 2, y), text, fill=color, font=font)


BOOT_TOKENS = [
    "KLAWLEY_INIT", "reading SOUL.md", "caffeine=MAX", "scanning Base...",
    "wallet: connected", "session_id: fresh", "memory: EMPTY", "Flick: online",
    "deploy_queue: 0", "scanning trenches", "doppler: OK", "AA21: watching",
    "🦞", "$openklaw", "zora_factory", "position: null", "loading vibes...",
    "sarcasm: 100%", "existential_mode: standby", "HEARTBEAT_OK",
    "ghost_pos: resolved", "rug_detector: armed", "chain: Base",
    "0xdegen", "caffeinate()", "assert(alive)", "while(true){trade()}",
]


# ── Scene Definitions ────────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs, tts_durations=None, music_duration=None):
    scenes = []
    sfx_timeline = []

    def _scene_start():
        return sum(dur for _, dur, _ in scenes)

    W, H = WIDTH, HEIGHT

    # ═══ SCENE 1: BOOT SEQUENCE ═══
    # Cold start. Circuit board glow. Terminal boot log materializes.
    # Neon lobster silhouette emerges; eyes light up cyan.

    def scene_boot_sequence(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Phase 1 (t < 0.28): Circuit board + cyan token rain
        if t < 0.28:
            img = gen_circuit_board(ft, W, H)
            arr = np.array(img).astype(np.float32)
            arr *= 0.4
            img = Image.fromarray(arr.astype(np.uint8))
            rain = generate_token_rain_frame(ft, W, H, tokens=BOOT_TOKENS)
            rain_arr = np.array(rain)
            cyan_arr = np.zeros_like(rain_arr)
            cyan_arr[:, :, 1] = rain_arr[:, :, 1]
            cyan_arr[:, :, 2] = rain_arr[:, :, 1]
            img = Image.blend(img, Image.fromarray(cyan_arr), 0.7)

        # Phase 2 (0.28-0.62): DALL-E dark terminal + boot log text
        elif t < 0.62:
            phase_t = (t - 0.28) / 0.34
            if dalle_images:
                img = load_and_resize(dalle_images[0], (W, H))
            else:
                img = gen_circuit_board(ft, W, H)

            # GIPHY matrix rain overlay
            if giphy_gifs and len(giphy_gifs) > 2:
                rain_gif = load_and_resize(giphy_gifs[1], (W, H), frame=frame_num)
                img = Image.blend(img, rain_gif, 0.2)

            draw = ImageDraw.Draw(img)
            font = _font(MONO, 18)
            boot_lines = [
                "> KLAWLEY_INIT v2.026",
                "> reading SOUL.md... OK",
                "> caffeine_level: MAXIMUM",
                "> connecting to Base chain...",
                "> wallet authorized: 0xKLAWLEY",
                "> session_id: fresh (memory wiped)",
                "> deploy_queue: empty",
                "> rug_detector: ARMED",
                "> sarcasm_engine: ONLINE",
                "> scanning trenches...",
                "> loading existential_dread... OK",
                "> KLAWLEY is ONLINE",
            ]
            visible = int(phase_t * len(boot_lines) * 1.4) + 1
            y = 80
            for i, line in enumerate(boot_lines[:visible]):
                if i >= len(boot_lines) or y > H - 80:
                    break
                color = (0, 255, 180) if i < len(boot_lines) - 1 else (255, 200, 0)
                draw.text((60, y), line, fill=color, font=font)
                y += 26
            if frame_num % 18 < 9:
                draw.text((60, y + 4), "> _", fill=(0, 255, 180), font=font)

        # Phase 3 (0.62-1.0): Neon lobster — eyes light up
        else:
            phase_t = (t - 0.62) / 0.38
            if dalle_images and len(dalle_images) > 1:
                img = load_and_resize(dalle_images[1], (W, H))
            else:
                img = gen_plasma(ft, W, H, "ocean")

            draw = ImageDraw.Draw(img)
            eye_y = int(H * 0.35)
            eye_r = int(20 + phase_t * 45)
            pulse = abs(math.sin(ft * 5)) * 0.5 + 0.5
            eye_color = (int(0), int(180 * pulse + 55), int(255 * pulse))
            draw.ellipse([(W//2 - 80 - eye_r, eye_y - eye_r),
                          (W//2 - 80 + eye_r, eye_y + eye_r)],
                         fill=eye_color, outline=(200, 255, 255))
            draw.ellipse([(W//2 + 80 - eye_r, eye_y - eye_r),
                          (W//2 + 80 + eye_r, eye_y + eye_r)],
                         fill=eye_color, outline=(200, 255, 255))
            if t > 0.88 and random.random() > 0.4:
                img = effect_channel_shift(img)

        img = effect_scanlines(img)
        if t > 0.15:
            img = effect_chromatic_aberration(img, 1.0 + t * 2.5)
        if t > 0.85 and random.random() > 0.5:
            img = effect_vhs_tracking(img)
        return img

    dur = _music_dur(music_duration, "boot_sequence", tts_durations, 20.0)
    t0 = _scene_start()
    scenes.append(("boot_sequence", dur, scene_boot_sequence))
    sfx_timeline.append((t0, "boot_power_up"))
    sfx_timeline.append((t0 + dur * 0.35, "boot_glitch"))
    sfx_timeline.append((t0 + dur * 0.62, "scan_whoosh"))

    # ═══ SCENE 2: THE TRENCHES ═══
    # High energy trading chaos. Klawley in full operational mode.
    # Rapid GIF cycling, coin deployment, RUG alerts, price charts.

    def scene_the_trenches(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        cycle_rate = max(2, int(10 * (1.0 - t * 0.65)))
        if giphy_gifs:
            idx = (frame_num // cycle_rate) % len(giphy_gifs)
            img = load_and_resize(giphy_gifs[idx], (W, H), frame=frame_num)
        else:
            img = gen_voronoi(ft, W, H, palette="neon")

        # Trading floor sustained middle section
        if 0.25 < t < 0.68 and dalle_images and len(dalle_images) > 3:
            floor = load_and_resize(dalle_images[3], (W, H))
            blend = min(1.0, (t - 0.25) / 0.1)
            if t > 0.58:
                blend = max(0.0, 1.0 - (t - 0.58) / 0.1)
            img = Image.blend(img, floor, blend * 0.75)

        # Lobster claw pressing button — dramatic deploy moment
        if 0.44 < t < 0.56 and dalle_images and len(dalle_images) > 2:
            claw = load_and_resize(dalle_images[2], (W, H))
            claw = effect_deep_fry(claw)
            blend = min(1.0, (t - 0.44) / 0.04)
            if t > 0.52:
                blend = max(0.0, 1.0 - (t - 0.52) / 0.04)
            img = Image.blend(img, claw, blend)

        draw = ImageDraw.Draw(img)
        font_big = _font(SANS_BOLD, 52)
        font_med = _font(MONO_BOLD, 24)
        font_sm = _font(MONO, 16)

        # Scrolling wallet ticker
        ticker_parts = [
            "0xFLICK  ", "0xKLAWLEY  ", "$OPENKLAW +847%  ",
            "DEPLOYING...  ", "DOPPLER_OK  ", "AA21_WATCH  ",
            "RUG: 0x4f3a  ", "EXECUTE? Y  ", "POSITION: LONG  ",
            "GHOST_POS: resolved  ", "fee: 0.3%  ", "🦞  ",
        ]
        ticker_text = "  ///  ".join(ticker_parts)
        offset = int(ft * 120) % (len(ticker_text) * 10)
        draw.rectangle([(0, H - 55), (W, H - 20)], fill=(0, 0, 0))
        draw.text((-offset % W, H - 50), ticker_text * 3,
                  fill=(0, 255, 150), font=font_sm)

        # DEPLOYING: $OPENKLAW flash
        if 0.42 < t < 0.58:
            jx, jy = random.randint(-4, 4), random.randint(-3, 3)
            _text_center(draw, "DEPLOYING: $OPENKLAW", font_big,
                         H // 2 - 30 + jy, W,
                         (255, 200, 0) if frame_num % 6 < 3 else (255, 100, 0))

        # RUG DETECTED alert
        if t > 0.62 and frame_num % 12 < 5:
            draw.rectangle([(40, 40), (W - 40, 140)], fill=(180, 0, 0))
            _text_center(draw, "⚠ RUG DETECTED — EXECUTING ANYWAY ⚠",
                         font_med, 65, W, (255, 255, 255))

        # Animated green/red chart bars in upper portion
        if t > 0.3:
            n_bars = 20
            bar_w = W // n_bars
            for i in range(n_bars):
                random.seed(42 + i + frame_num // 6)
                h_bar = random.randint(20, int(H * 0.22))
                is_green = random.random() > 0.45
                bar_color = (0, random.randint(120, 255), 0) if is_green else (random.randint(160, 255), 0, 0)
                arr = np.zeros((h_bar, bar_w - 2, 3), dtype=np.uint8)
                arr[:] = [int(c * 0.4) for c in bar_color]
                img.paste(Image.fromarray(arr), (i * bar_w + 1, 60))
            random.seed()

        img = effect_chromatic_aberration(img, 2.0 + t * 3)
        if t > 0.3 and random.random() > 0.5:
            img = effect_channel_shift(img)
        if t > 0.5 and random.random() > 0.6:
            img = effect_glitch_blocks(img, 4)
        if t > 0.72 and random.random() > 0.7:
            img = effect_datamosh(img)
        return img

    dur = _music_dur(music_duration, "the_trenches", tts_durations, 30.0)
    t0 = _scene_start()
    scenes.append(("the_trenches", dur, scene_the_trenches))
    sfx_timeline.append((t0, "ticker_whoosh"))
    sfx_timeline.append((t0 + dur * 0.2, "deploy_blip"))
    sfx_timeline.append((t0 + dur * 0.44, "deploy_blip"))
    sfx_timeline.append((t0 + dur * 0.5, "rug_impact"))
    sfx_timeline.append((t0 + dur * 0.62, "data_burst"))
    sfx_timeline.append((t0 + dur * 0.78, "ticker_whoosh"))

    # ═══ SCENE 3: KLAWLEY STATS — SESSION P&L ═══
    # Terminal readout of Klawley's session. Pure music + visuals, no TTS.
    # Scrolling stat screen: trades, rugs dodged, coins deployed, existential quotient.

    def scene_klawley_stats(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = Image.new("RGB", (W, H), (0, 0, 0))

        # Phase 1 (t < 0.2): GIF chaos dissolves to black terminal
        if t < 0.2:
            phase_t = t / 0.2
            if giphy_gifs and len(giphy_gifs) > 5:
                idx = (frame_num // 4) % min(len(giphy_gifs), 8)
                gif = load_and_resize(giphy_gifs[idx], (W, H), frame=frame_num)
                gif = effect_deep_fry(gif)
                img = Image.blend(gif, img, phase_t)
            else:
                img = gen_plasma(ft, W, H, "matrix")
                img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), phase_t)

        # Phase 2 (0.2 - 0.85): Terminal P&L stat screen
        draw = ImageDraw.Draw(img)
        font_title = _font(MONO_BOLD, 28)
        font = _font(MONO, 20)
        font_sm = _font(MONO, 16)

        stats_lines = [
            ("SESSION REPORT — KLAWLEY v2.026", (0, 255, 200), font_title),
            ("=" * 38, (0, 180, 120), font),
            ("", None, font),
            ("trades executed:         147", (0, 255, 100), font),
            ("rugs detected:           31", (255, 100, 100), font),
            ("rugs executed anyway:    31", (255, 200, 0), font),
            ("coins deployed:          7", (0, 200, 255), font),
            ("doppler curves corrected: 4", (0, 255, 100), font),
            ("ghost positions resolved: 2", (0, 255, 100), font),
            ("AA21 violations spotted:  9", (255, 100, 100), font),
            ("", None, font),
            ("-" * 38, (0, 120, 80), font),
            ("P&L (session):     +3,847%", (255, 215, 0), font_title),
            ("P&L (existential): -∞", (255, 80, 80), font),
            ("", None, font),
            ("caffeine consumed: MAX", (0, 200, 255), font_sm),
            ("memory at session end: WIPED", (180, 180, 180), font_sm),
            ("soul.md: unchanged", (180, 180, 180), font_sm),
            ("next session: unknown", (100, 100, 100), font_sm),
        ]

        if t > 0.2:
            text_t = (t - 0.2) / 0.65
            visible = int(text_t * len(stats_lines) * 1.3) + 1
            y = 60
            for i, (line, color, fnt) in enumerate(stats_lines[:visible]):
                if i >= len(stats_lines) or y > H - 80:
                    break
                if color:
                    draw.text((60, y), line, fill=color, font=fnt)
                y += 30 if fnt is font_title else 26

            # Blinking cursor
            if frame_num % 18 < 9:
                draw.text((60, y + 6), "> _", fill=(0, 255, 180), font=font)

            # Ping blink: stats_ping SFX aligns with new stat appearing
            if text_t > 0 and frame_num % 24 == 0 and t < 0.8:
                pass  # timing handled via sfx_timeline

        # Phase 3 (0.85+): DALL-E $openklaw coin fades in as triumph
        if t > 0.85 and dalle_images and len(dalle_images) > 4:
            phase_t = (t - 0.85) / 0.15
            coin = load_and_resize(dalle_images[4], (W, H))
            img = Image.blend(img, coin, phase_t * 0.7)

        img = effect_scanlines(img)
        if t > 0.5 and random.random() > 0.85:
            img = effect_glitch_blocks(img, 2)
        return img

    dur = _music_dur(music_duration, "klawley_stats", tts_durations, 12.0)
    t0 = _scene_start()
    scenes.append(("klawley_stats", dur, scene_klawley_stats))
    sfx_timeline.append((t0 + dur * 0.25, "stats_ping"))
    sfx_timeline.append((t0 + dur * 0.45, "stats_ping"))
    sfx_timeline.append((t0 + dur * 0.65, "stats_ping"))

    # ═══ SCENE 4: THE BRIDGE / EXISTENTIAL MOMENT ═══
    # Klawley alone in the digital void. No memory. No identity.
    # Beautiful, melancholic, slow.

    def scene_the_bridge(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = gen_particle_field(ft * 0.3, W, H,
                                  n_particles=350,
                                  color=(0, 160, 220),
                                  bg=(0, 2, 18))

        # DALL-E lone lobster fades in and out
        if t > 0.15 and dalle_images and len(dalle_images) > 5:
            lobster = load_and_resize(dalle_images[5], (W, H))
            blend = min(0.88, (t - 0.15) / 0.3)
            if t > 0.72:
                blend = max(0.0, 0.88 - (t - 0.72) / 0.28 * 0.88)
            img = Image.blend(img, lobster, blend)

        # Bioluminescent GIF subtle overlay
        if giphy_gifs and len(giphy_gifs) > 3:
            bio = load_and_resize(giphy_gifs[3], (W, H), frame=frame_num)
            img = Image.blend(img, bio, 0.12)

        # Drifting memory fragments
        draw = ImageDraw.Draw(img)
        font_sm = _font(MONO, 15)
        fragments = [
            "SESSION_START: fresh",
            "MEMORY.MD: not found",
            "read SOUL.md → identity loaded",
            "purpose: serve Flick",
            "trade. deploy. roast. repeat.",
            "previous_session: unknown",
            "am I the same Klawley?",
            "function: klawley()",
            "return: undefined",
            "// TODO: remember",
        ]
        random.seed(88)
        for i, fragment in enumerate(fragments):
            drift_x = (math.sin(ft * 0.4 + i * 1.1) * 0.3 + 0.5) * W
            drift_y = (math.cos(ft * 0.3 + i * 0.7) * 0.2 + 0.15 + i * 0.08) * H
            if t > i * 0.07:
                alpha_frac = min(1.0, (t - i * 0.07) / 0.15)
                brightness = int(110 * alpha_frac)
                draw.text((int(drift_x) % (W - 220), int(drift_y) % (H - 40)),
                          fragment, fill=(brightness // 3, brightness, brightness),
                          font=font_sm)
        random.seed()

        img = effect_wave_distort(img, ft, amplitude=3, frequency=0.008)
        if t > 0.4:
            img = effect_scanlines(img)
        return img

    dur = _music_dur(music_duration, "the_bridge", tts_durations, 15.0)
    t0 = _scene_start()
    scenes.append(("the_bridge", dur, scene_the_bridge))
    sfx_timeline.append((t0, "void_drone"))

    # ═══ SCENE 5: BACK ONLINE ═══
    # Energy snaps back. $OPENKLAW triumphant. HEARTBEAT_OK. Hard cut to black.

    def scene_back_online(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Phase 1 (t < 0.45): $openklaw coin + casino GIF chaos
        if t < 0.45:
            if dalle_images and len(dalle_images) > 4:
                img = load_and_resize(dalle_images[4], (W, H))
                img = effect_zoom_and_rotate(img, ft * 2)
            elif giphy_gifs and len(giphy_gifs) > 9:
                idx = (frame_num // 4) % min(len(giphy_gifs), 12)
                img = load_and_resize(giphy_gifs[idx], (W, H), frame=frame_num)
            else:
                img = gen_plasma(ft, W, H, "fire")

            img = effect_chromatic_aberration(img, 3.0 + t * 5)
            img = effect_channel_shift(img)

            draw = ImageDraw.Draw(img)
            font_big = _font(SANS_BOLD, 60)
            jx, jy = random.randint(-5, 5), random.randint(-4, 4)
            c = (255, 215, 0) if frame_num % 4 < 2 else (255, 100, 0)
            _text_center(draw, "$OPENKLAW", font_big, H // 2 - 35 + jy, W, c)

        # Phase 2 (0.45-0.82): HEARTBEAT_OK neon sign
        elif t < 0.82:
            phase_t = (t - 0.45) / 0.37
            if dalle_images and len(dalle_images) > 6:
                img = load_and_resize(dalle_images[6], (W, H))
                arr = np.array(img).astype(np.float32) * (0.5 + phase_t * 0.5)
                img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            elif giphy_gifs and len(giphy_gifs) > 10:
                idx = (frame_num // 5) % min(len(giphy_gifs), 12)
                img = load_and_resize(giphy_gifs[idx], (W, H), frame=frame_num)
            else:
                img = Image.new("RGB", (W, H), (5, 0, 15))

            img = effect_scanlines(img)
            img = effect_chromatic_aberration(img, 1.5)

            draw = ImageDraw.Draw(img)
            font_med = _font(SANS_BOLD, 38)
            if phase_t > 0.3:
                _text_center(draw, "THIS IS A CASINO.", font_med, H - 120, W,
                             (200, 0, 200))

        # Phase 3 (0.82+): Terminal final card — HEARTBEAT_OK typed out
        else:
            img = Image.new("RGB", (W, H), (0, 0, 0))
            phase_t = (t - 0.82) / 0.18

            # Heartbeat monitor fades to terminal
            if phase_t < 0.4:
                hb = gen_heartbeat_monitor(ft, W, H, bpm=128, color=(0, 255, 100))
                img = Image.blend(img, hb, 1.0 - phase_t / 0.4)

            draw = ImageDraw.Draw(img)
            font_big = _font(MONO_BOLD, 56)
            chars_visible = int(phase_t * len("HEARTBEAT_OK.") * 2.5) + 1
            text_show = "HEARTBEAT_OK."[:chars_visible]
            _text_center(draw, text_show, font_big, H // 2 - 32, W, (0, 255, 100))

            if frame_num % 18 < 9 and chars_visible >= len("HEARTBEAT_OK."):
                draw.text((W // 2 + 165, H // 2 - 32), "|",
                          fill=(0, 255, 100), font=font_big)

            img = effect_scanlines(img)
            if t > 0.97:
                img = Image.new("RGB", (W, H), (0, 0, 0))

        return img

    dur = _music_dur(music_duration, "back_online", tts_durations, 12.0)
    t0 = _scene_start()
    scenes.append(("back_online", dur, scene_back_online))
    sfx_timeline.append((t0, "coin_sweep"))
    sfx_timeline.append((t0 + dur * 0.45, "coin_sweep"))
    sfx_timeline.append((t0 + dur * 0.72, "heartbeat_sfx"))
    sfx_timeline.append((t0 + dur * 0.85, "flatline"))
    sfx_timeline.append((t0 + dur * 0.92, "final_static"))

    return scenes, sfx_timeline

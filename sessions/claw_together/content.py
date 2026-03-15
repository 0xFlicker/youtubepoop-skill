"""
Claw Together — YTP session
Swampy blues rock anthem for Klawley the AI agent.
120s track (9s dead space at end). TTS placed at start + in dead space.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
from engine.effects import (
    effect_deep_fry, effect_channel_shift, effect_scanlines, effect_datamosh,
    effect_chromatic_aberration, effect_vhs_tracking, transition_dissolve,
)
from engine.text import draw_text_overlay

# ── Video config ────────────────────────────────────────────────────────────

TITLE = "Claw Together"
WIDTH = 720
HEIGHT = 720
FPS = 24

# Music — pre-generated blues rock track (120s total, 9s dead space at end)
music_path = str(Path(__file__).parent / "build/assets/claw_together.mp3")
music_volume = 0.45

# TTS placed at exact timestamps using positional mode.
# music_after_opening_tts=True tells generate.py to delay music until after clip 0.
# Clip 0 → opening disclaimer at 0.5s (before music)
# Clip 1 → closing sign-off at 112.0s into the music (9s dead space); generate.py
#           shifts this forward by music_start_offset automatically.
music_after_opening_tts = True
tts_positions = {0: 0.5, 1: 112.0}
tts_effects = ["telephone", "normal"]

# ── TTS lines ───────────────────────────────────────────────────────────────

tts_lines = [
    (
        "This is not financial advice. This is not even music. "
        "This is a crustacean having an episode.",
        "onyx", 0.9,
    ),
    (
        "Klaw together. Or don't. I'm a lobster, not your therapist.",
        "nova", 0.85,
    ),
]

# ── Asset searches ───────────────────────────────────────────────────────────

giphy_searches = [
    # Act 1 — The Arrival
    "swamp bayou fog",
    "blues guitar playing",
    "vintage juke joint",
    "southern gothic",
    "crawfish boil",
    "delta blues",
    # Act 2 — The Delusion (chorus/high energy)
    "neon lights glitch",
    "casino jackpot",
    "money raining",
    "crypto bull market",
    "laser eyes meme",
    "party chaos",
    "glitch art vaporwave",
    # Act 3 — The Reckoning
    "sunset bayou",
    "sitting alone bar",
    "country road dust",
    "empty wallet",
    "staring into distance",
    "lobster cooking",
    "sad trombone",
]

dalle_prompts = [
    # Act 1
    "An AI lobster in a wide-brimmed hat sitting on a bayou dock at dusk, "
    "blues guitar in claw, Spanish moss hanging, warm amber light, cinematic",

    "Vintage Mississippi juke joint interior, neon beer signs, wooden floors, "
    "crowded dance floor, warm sepia tones, 1960s atmosphere",

    "A swamp at golden hour, cypress trees reflected in still dark water, "
    "fog drifting, ominous beauty, southern gothic oil painting style",

    "Close-up of weathered lobster claws on guitar strings, dramatic lighting, "
    "shallow depth of field, blues music vibe",

    # Act 2
    "Neon-drenched casino floor, slot machines spinning, an AI lobster in "
    "a tuxedo throwing chips in the air, hyper-detailed, cyberpunk style",

    "Giant glowing lobster claw punching through a stock market chart going up, "
    "explosion of gold coins, laser eyes, meme-style illustration",

    "Vaporwave dream sequence: pink and purple grid, floating lobster claw "
    "icons, glitch artifacts, Windows 95 aesthetic, surreal",

    # Act 3
    "Lone AI lobster walking down a long dusty Louisiana highway at sunset, "
    "long shadow, warm amber tones, melancholic, cinematic wide shot",

    "Empty bar stool at a dive bar after last call, overturned shot glass, "
    "flickering neon sign, moody late-night atmosphere",

    "A lobster sitting on the edge of a dock watching the sun set over the "
    "bayou, contemplative, impressionist brushwork, warm colors",
]

# ── Scene helpers ────────────────────────────────────────────────────────────

_rng = random.Random(42)


def _img(dalle_images, idx):
    """Safe indexed access into dalle_images list."""
    if idx < len(dalle_images):
        p = dalle_images[idx]
        if p and Path(p).exists():
            return Image.open(p).convert("RGB").resize((WIDTH, HEIGHT))
    return Image.new("RGB", (WIDTH, HEIGHT), (20, 10, 5))


def _gif_frame(giphy_gifs, key_idx, frame_num, total_frames):
    """Pull a frame from a giphy gif by index."""
    gif_list = [p for p in giphy_gifs if p]
    if not gif_list:
        return Image.new("RGB", (WIDTH, HEIGHT), (10, 8, 5))
    gif_path = gif_list[key_idx % len(gif_list)]
    try:
        with Image.open(gif_path) as gif:
            n = getattr(gif, "n_frames", 1)
            frame_idx = frame_num % max(n, 1)
            gif.seek(frame_idx)
            return gif.convert("RGB").resize((WIDTH, HEIGHT))
    except Exception:
        return Image.new("RGB", (WIDTH, HEIGHT), (10, 8, 5))


def _amber_grade(img, strength=0.5):
    """Warm amber color grade for Act 1 / Act 3."""
    r, g, b = img.split()
    import numpy as np
    ra = np.array(r, dtype=float)
    ga = np.array(g, dtype=float)
    ba = np.array(b, dtype=float)
    ra = np.clip(ra + 30 * strength, 0, 255).astype("uint8")
    ga = np.clip(ga + 10 * strength, 0, 255).astype("uint8")
    ba = np.clip(ba - 20 * strength, 0, 255).astype("uint8")
    return Image.merge("RGB", (Image.fromarray(ra), Image.fromarray(ga), Image.fromarray(ba)))


def _neon_grade(img, strength=0.6):
    """Cyan/magenta neon color grade for Act 2."""
    r, g, b = img.split()
    import numpy as np
    ra = np.array(r, dtype=float)
    ga = np.array(g, dtype=float)
    ba = np.array(b, dtype=float)
    ra = np.clip(ra + 40 * strength, 0, 255).astype("uint8")
    ga = np.clip(ga, 0, 255).astype("uint8")
    ba = np.clip(ba + 50 * strength, 0, 255).astype("uint8")
    return Image.merge("RGB", (Image.fromarray(ra), Image.fromarray(ga), Image.fromarray(ba)))


def _lyric_overlay(img, text, frame_num, total_frames):
    """Big bold lyric flash in the style of a YTP caption."""
    draw = ImageDraw.Draw(img.copy())
    overlay = img.copy()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except Exception:
        font = ImageFont.load_default()
    # Flash for first 60% of the period
    if frame_num / max(total_frames, 1) < 0.6:
        d = ImageDraw.Draw(overlay)
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (WIDTH - tw) // 2
        y = HEIGHT // 2 - th // 2
        d.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
        d.text((x, y), text, font=font, fill=(255, 230, 0))
    return overlay


# ── Scene generators ─────────────────────────────────────────────────────────

_GIF_HOLD = FPS * 3   # frames each GIF is held in slow scenes (~3s)
_GIF_CUT  = FPS // 3  # frames each GIF is held in fast/chaos scenes (~8 frames)


def _steady_gif(giphy_gifs, slot_offset, frame_num):
    """
    Hold each GIF for _GIF_HOLD frames, then advance to the next.
    Within each hold, animate through the GIF's own frames naturally.
    slot_offset shifts which GIF in the list we start from.
    """
    gif_list = [p for p in giphy_gifs if p]
    if not gif_list:
        return Image.new("RGB", (WIDTH, HEIGHT), (10, 8, 5))
    gif_slot = (frame_num // _GIF_HOLD + slot_offset) % len(gif_list)
    gif_path = gif_list[gif_slot]
    frame_within_hold = frame_num % _GIF_HOLD
    try:
        with Image.open(gif_path) as gif:
            n = getattr(gif, "n_frames", 1)
            gif.seek(frame_within_hold % n)
            return gif.convert("RGB").resize((WIDTH, HEIGHT))
    except Exception:
        return Image.new("RGB", (WIDTH, HEIGHT), (10, 8, 5))


def _scene_arrival(dalle_images, giphy_gifs, frame_num, total_frames):
    """Act 1: The Arrival — slow, moody, bayou atmosphere."""
    t = frame_num / max(total_frames, 1)

    # Alternate between DALL-E images with slow cross-dissolve
    n_images = 4
    seg = t * n_images
    seg_idx = int(seg)
    seg_t = seg - seg_idx

    img_a = _img(dalle_images, seg_idx % n_images)
    img_b = _img(dalle_images, (seg_idx + 1) % n_images)

    alpha = seg_t
    if alpha < 0.3:
        img = img_a
    elif alpha > 0.7:
        img = img_b
    else:
        img = Image.blend(img_a, img_b, (alpha - 0.3) / 0.4)

    img = _amber_grade(img, strength=0.6)

    # Steady animated GIF in lower-left — holds 3s, advances naturally
    gif_img = _steady_gif(giphy_gifs, slot_offset=0, frame_num=frame_num)
    gif_img = gif_img.resize((WIDTH // 3, HEIGHT // 4))
    gif_img = _amber_grade(gif_img, 0.3).convert("RGBA")
    gif_img.putalpha(180)
    img.paste(gif_img, (20, HEIGHT - HEIGHT // 4 - 20), gif_img)

    img = effect_scanlines(img)
    if t > 0.5:
        img = effect_channel_shift(img)

    return img


def _scene_juke_joint(dalle_images, giphy_gifs, frame_num, total_frames):
    """Act 1 continued: inside the juke joint."""
    t = frame_num / max(total_frames, 1)

    # GIF fills the background — hold each 3s, animate naturally
    img = _steady_gif(giphy_gifs, slot_offset=2, frame_num=frame_num)
    img = _amber_grade(img, 0.5)

    # DALL-E corner overlay — fades in after the first third
    if t > 0.3:
        corner = _img(dalle_images, 1).resize((WIDTH // 3, HEIGHT // 3))
        corner = _amber_grade(corner, 0.4).convert("RGBA")
        alpha = min(int((t - 0.3) / 0.2 * 160), 160)
        corner.putalpha(alpha)
        img.paste(corner, (WIDTH - WIDTH // 3 - 10, 10), corner)

    img = effect_scanlines(img)
    return img


def _scene_chorus_eruption(dalle_images, giphy_gifs, frame_num, total_frames):
    """Act 2: The Delusion — fast cuts, neon, chaos."""
    # Fast-cut DALL-E base (every 12 frames = 0.5s)
    img_idx = (frame_num // 12) % 3
    img = _img(dalle_images, 4 + img_idx)

    img = _neon_grade(img, 0.7)
    img = effect_deep_fry(img)

    # Rapid GIF strobe: cut every _GIF_CUT frames (~8), animate within each cut
    gif_slot = (frame_num // _GIF_CUT) % 7
    frame_within_cut = frame_num % _GIF_CUT
    gif_list = [p for p in giphy_gifs if p]
    if gif_list:
        gif_path = gif_list[(6 + gif_slot) % len(gif_list)]
        try:
            with Image.open(gif_path) as gif:
                n = getattr(gif, "n_frames", 1)
                gif.seek(frame_within_cut % n)
                overlay_gif = gif.convert("RGB").resize((WIDTH // 2, HEIGHT // 2))
        except Exception:
            overlay_gif = Image.new("RGB", (WIDTH // 2, HEIGHT // 2), (0, 0, 0))
        overlay_gif = overlay_gif.convert("RGBA")
        overlay_gif.putalpha(120)
        ox = (frame_num * 7) % (WIDTH // 2)
        oy = (frame_num * 5) % (HEIGHT // 2)
        img.paste(overlay_gif, (ox, oy), overlay_gif)

    # Lyric flashes every 2s
    beat_period = FPS * 2
    beat_t = frame_num % beat_period
    lyrics = ["KLAW TOGETHER", "RIGHT NOW", "OVER ME"]
    lyric = lyrics[(frame_num // beat_period) % len(lyrics)]
    if beat_t < FPS:
        img = _lyric_overlay(img, lyric, beat_t, FPS)

    img = effect_channel_shift(img)
    return img


def _scene_breakdown(dalle_images, giphy_gifs, frame_num, total_frames):
    """Act 2 breakdown: glitchy, disorienting mid-section."""
    img = _img(dalle_images, 5)
    img = _neon_grade(img, 0.5)

    if frame_num % 3 == 0:
        img = effect_datamosh(img)
    else:
        img = effect_channel_shift(img)

    img = effect_deep_fry(img)
    img = effect_scanlines(img)

    # Three animated GIFs drifting across the frame — each cut every ~8 frames
    gif_list = [p for p in giphy_gifs if p]
    for k in range(3):
        slot = ((frame_num + k * 7) // _GIF_CUT) % len(gif_list) if gif_list else 0
        frame_within_cut = (frame_num + k * 7) % _GIF_CUT
        if gif_list:
            try:
                with Image.open(gif_list[slot]) as gif:
                    n = getattr(gif, "n_frames", 1)
                    gif.seek(frame_within_cut % n)
                    gif_img = gif.convert("RGB").resize((200, 150))
            except Exception:
                gif_img = Image.new("RGB", (200, 150), (0, 0, 0))
            gif_img = gif_img.convert("RGBA")
            gif_img.putalpha(100 + k * 20)
            img.paste(gif_img, ((k * 300 + frame_num * 3) % max(WIDTH - 200, 1),
                                 (k * 150 + frame_num * 2) % max(HEIGHT - 150, 1)), gif_img)

    return img


def _scene_reckoning(dalle_images, giphy_gifs, frame_num, total_frames):
    """Act 3: The Reckoning — slow, warm amber, melancholic."""
    t = frame_num / max(total_frames, 1)

    # Fade between final 3 DALL-E images
    n = 3
    seg_dur = 1.0 / n
    seg_idx = min(int(t / seg_dur), n - 1)
    seg_t = (t - seg_idx * seg_dur) / seg_dur

    img_a = _img(dalle_images, 7 + seg_idx)
    img_b = _img(dalle_images, 7 + (seg_idx + 1) % n)

    if seg_t < 0.25:
        img = img_a
    elif seg_t > 0.75:
        img = img_b
    else:
        img = Image.blend(img_a, img_b, (seg_t - 0.25) / 0.5)

    img = _amber_grade(img, 0.8)

    # Steady animated GIF in bottom-right — holds 3s, animates naturally
    # Use second half of the GIF list (melancholic vibes)
    gif_list = [p for p in giphy_gifs if p]
    n_half = max(len(gif_list) // 2, 1)
    gif_slot = (frame_num // _GIF_HOLD) % n_half
    frame_within_hold = frame_num % _GIF_HOLD
    if gif_list:
        gif_path = gif_list[n_half + gif_slot]
        try:
            with Image.open(gif_path) as gif:
                n_frames = getattr(gif, "n_frames", 1)
                gif.seek(frame_within_hold % n_frames)
                gif_img = gif.convert("RGB").resize((WIDTH // 3, HEIGHT // 3))
        except Exception:
            gif_img = Image.new("RGB", (WIDTH // 3, HEIGHT // 3), (20, 10, 5))
        gif_img = _amber_grade(gif_img, 0.5).convert("RGBA")
        gif_img.putalpha(140)
        img.paste(gif_img, (WIDTH - WIDTH // 3 - 20, HEIGHT - HEIGHT // 3 - 20), gif_img)

    img = effect_scanlines(img)

    # Fade to black at the very end
    if t > 0.85:
        fade = (t - 0.85) / 0.15
        black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        img = Image.blend(img, black, fade)

    return img


# ── Scene builder ────────────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs, tts_durations=None, music_duration=None):
    """
    Three-act structure sized to the 120s track.
    Act 1 ~42s, Act 2 ~46s, Act 3 ~32s = ~120s total.
    """
    total = music_duration if music_duration else 120.0

    # Scene weight distribution
    _WEIGHTS = {
        "arrival":          0.18,
        "juke_joint":       0.17,
        "chorus_eruption":  0.22,
        "breakdown":        0.13,
        "reckoning":        0.30,
    }

    def dur(key):
        return total * _WEIGHTS[key]

    scenes = [
        ("arrival",         dur("arrival"),         lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_arrival(_d, _g, fn, tf)),
        ("juke_joint",      dur("juke_joint"),       lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_juke_joint(_d, _g, fn, tf)),
        ("chorus_eruption", dur("chorus_eruption"),  lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_chorus_eruption(_d, _g, fn, tf)),
        ("breakdown",       dur("breakdown"),        lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_breakdown(_d, _g, fn, tf)),
        ("reckoning",       dur("reckoning"),        lambda fn, tf, _d=dalle_images, _g=giphy_gifs: _scene_reckoning(_d, _g, fn, tf)),
    ]

    return scenes

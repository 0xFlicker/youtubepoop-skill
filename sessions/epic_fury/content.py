"""
YTP Session: Epic Fury

Operation Epic Fury — the US/Israel strikes on Iran, February 28, 2026.
The Department of Defense became the Department of War and nobody blinked.
The peace president started a war and the loading bar hit 100%.
Fox News is a Pentagon internship program.
Oil is $200 a barrel and your commute costs more than your rent.
War is peace. Freedom is slavery. Ignorance is strength.
Your mom.
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
    generate_solid_color_frame,
)
from engine.sources import (
    gen_plasma, gen_voronoi, gen_particle_field,
)
from engine.audio import audio_duration
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── Session Config ──────────────────────────────────────────────────────────
TITLE = "epic_fury"
WIDTH, HEIGHT = 1080, 1080
FPS = 24

# ── Content ─────────────────────────────────────────────────────────────────

giphy_searches = [
    "pentagon building", "label maker sticker",
    "aircraft carrier fleet", "military explosion",
    "campaign rally crowd", "loading bar progress",
    "fox news studio", "conspiracy board yarn",
    "oil tanker ship", "gas station pump",
    "slot machine spinning", "talking heads news panel",
]

dalle_prompts = [
    "The Pentagon building at night with a giant label maker pressing the word WAR onto its facade, bureaucratic horror, dark cinematic lighting, square composition",
    "The words OPERATION EPIC FURY in burning steel letters floating over a dark ocean at night, sparks and embers falling, military propaganda poster style, square composition",
    "Split-screen image: left side is a Fox News studio couch, right side is a Pentagon press podium, connected by red conspiracy yarn threads, surveillance camera aesthetic, square composition",
    "Satellite photograph of the Strait of Hormuz with oil-black water and tiny cargo ships, military thermal imaging style, square composition",
    "A 3x3 grid of podium silhouettes each speaking simultaneously, security camera grainy aesthetic, Orwellian surveillance art, square composition",
    "A pure black void with a single white pixel in the exact center, minimalist digital art, square composition",
]

# TTS clips indexed 0-15
tts_lines = [
    # Scene 1: naming_ceremony (clip 0)
    ("We are not the woke department anymore.", "onyx", 1.0),
    # Scene 2: peace_president (clips 1-4)
    ("I will be the greatest peace president God has ever created.", "echo", 1.0),
    ("Combat operations have commenced.", "onyx", 1.0),
    ("We didn't start this war. We're finishing it.", "fable", 1.0),
    ("At what point does this become a betrayal of everything he promised?", "alloy", 1.0),
    # Scene 3: fox_pipeline (clips 5-7)
    ("No stupid rules. We're changing everything.", "onyx", 1.0),
    ("This operation has been designated Operation Your Mom.", "nova", 1.0),
    ("Windows XP has encountered a fatal error.", "shimmer", 1.0),
    # Scene 4: hormuz_experience (clips 8-11)
    ("Two hundred dollars a barrel. Maybe more.", "fable", 1.0),
    ("We have great safety. Tremendous safety.", "echo", 1.0),
    ("The tanker was struck at oh three hundred.", "onyx", 1.0),
    ("That tweet has been deleted.", "nova", 1.0),
    # Scene 5: war_is_peace (clips 12-15)
    ("This operation is very complete. Very thorough.", "echo", 1.0),
    ("This is only the beginning.", "onyx", 1.0),
    ("We are just getting started.", "fable", 1.0),
    ("It is going to get so much worse.", "alloy", 1.0),
]

tts_effects = [
    "normal",      # 0: Hegseth naming — flat, matter-of-fact
    "echo",        # 1: Trump 2024 promise — ghostly
    "telephone",   # 2: Trump 2026 order — compressed, military comms
    "normal",      # 3: Hegseth justification
    "deep",        # 4: Rogan question — low, serious
    "normal",      # 5: Hegseth rules
    "normal",      # 6: Soldier joke
    "stutter",     # 7: XP error — glitched
    "slow",        # 8: Iran oil — ominous
    "echo",        # 9: Trump safety — hollow
    "telephone",   # 10: Military report — radio
    "fast",        # 11: Correction — quick deletion
    "chorus",      # 12: Trump thorough — layered
    "echo",        # 13: Hegseth beginning — reverberating
    "echo",        # 14: Hegseth getting started — reverberating
    "whisper",     # 15: Warren warning — quiet dread
]

SCENE_AUDIO_MAP = {
    "naming_ceremony":    [0],
    "peace_president":    [1, 2, 3, 4],
    "fox_pipeline":       [5, 6, 7],
    "hormuz_experience":  [8, 9, 10, 11],
    "war_is_peace":       [12, 13, 14, 15],
    "outro_your_mom":     [],
}

music_config = {
    "layers": [
        # 1. Peace Muzak — detuned pad, slow tremolo
        {"type": "pad", "freq": 261.63, "freq2": 262.5, "duration": 105,
         "volume": 0.006, "filters": "tremolo=f=0.2:d=0.3"},
        # 2. War.gov Industrial — sawtooth bass
        {"type": "sawtooth", "freq": 55, "duration": 105,
         "volume": 0.008, "filters": "lowpass=f=400,tremolo=f=1.5:d=0.6"},
        # 3. Oil Drone — FM synth
        {"type": "fm", "freq": 80, "mod_freq": 3, "mod_depth": 40,
         "duration": 105, "volume": 0.005,
         "filters": "lowpass=f=600"},
        # 4. Sub-bass — brown noise, low rumble
        {"type": "noise", "color": "brown", "duration": 105,
         "volume": 0.005, "filters": "lowpass=f=100"},
        # 5. Piano motif — pluck
        {"type": "pluck", "freq": 261.63, "decay": 3.0, "duration": 105,
         "volume": 0.010},
        # 6. Dissonance — drone chord, slow fade-in
        {"type": "drone_chord", "freq": 220,
         "freqs": [220, 311.13, 440], "duration": 105,
         "volume": 0.003, "filters": "afade=t=in:d=60"},
        # 7. Air raid arpeggio
        {"type": "arpeggio", "freq": 440,
         "notes": [440, 554, 659, 880],
         "step_duration": 0.5, "duration": 105,
         "volume": 0.003, "filters": "lowpass=f=3000"},
    ],
    "master_filters": "volume=0.85",
    "mix_volume": 0.30,
}

sfx_cues = [
    # Scene 1
    {"name": "piano_note", "type": "tone", "freq": 261, "duration": 2.0,
     "filters": "afade=t=out:d=1.5,volume=0.4"},
    {"name": "synth_stab", "type": "impact", "freq": 55, "duration": 0.6,
     "filters": "volume=0.5"},
    {"name": "vhs_click", "type": "noise_burst", "duration": 0.08,
     "filters": "volume=0.3"},
    # Scene 2
    {"name": "air_raid_siren", "type": "sweep", "freq": 400, "duration": 3.0,
     "filters": "volume=0.25"},
    {"name": "loading_tick", "type": "typing", "rate": 4, "duration": 2.0,
     "filters": "volume=0.15"},
    # Scene 3
    {"name": "xp_error", "type": "tone", "freq": 600, "duration": 0.3,
     "filters": "volume=0.5,afade=t=out:d=0.2"},
    {"name": "cable_news_whoosh", "type": "whoosh", "freq": 2000, "duration": 0.5,
     "filters": "volume=0.3"},
    {"name": "typewriter_sfx", "type": "typing", "rate": 12, "duration": 1.5,
     "filters": "volume=0.15"},
    # Scene 4
    {"name": "oil_drone_rise", "type": "sweep", "freq": 60, "duration": 5.0,
     "filters": "volume=0.2"},
    {"name": "cash_register", "type": "impact", "freq": 300, "duration": 0.2,
     "filters": "volume=0.4"},
    {"name": "ship_explosion", "type": "impact", "freq": 40, "duration": 1.5,
     "filters": "volume=0.5,lowpass=f=200"},
    {"name": "tweet_delete", "type": "power_down", "freq": 880, "duration": 0.5,
     "filters": "volume=0.3,afade=t=out:d=0.3"},
    # Scene 5
    {"name": "dissonance_chord", "type": "tone", "freq": 311, "duration": 3.0,
     "filters": "volume=0.3,afade=t=in:d=1.0,afade=t=out:d=1.0"},
    {"name": "glitch_burst", "type": "glitch", "duration": 0.4,
     "filters": "volume=0.25"},
    # Scene 6
    {"name": "final_piano", "type": "tone", "freq": 261, "duration": 4.0,
     "filters": "afade=t=out:d=3.0,volume=0.35"},
    {"name": "static_fade", "type": "noise_burst", "duration": 2.0,
     "color": "pink", "filters": "afade=t=in:d=0.5,afade=t=out:d=1.0,volume=0.15"},
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


# ── Scene Definitions ──────────────────────────────────────────────────────

def build_scenes(dalle_images, giphy_gifs, tts_durations=None):
    """Build scene list with audio-aware durations."""
    scenes = []
    sfx_timeline = []

    def _scene_start():
        return sum(dur for _, dur, _ in scenes)

    W, H = WIDTH, HEIGHT

    # ═══ SCENE 1: NAMING CEREMONY (~12s) ═══
    # Pentagon → Department of War. Label maker. Scanlines. Glitch text.

    def scene_naming_ceremony(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Base: DALL-E pentagon with label maker, or fallback plasma
        if dalle_images:
            img = load_and_resize(dalle_images[0], (W, H))
        else:
            img = gen_plasma(ft, W, H, "dark")

        # Dark scanline overlay from the start
        img = effect_scanlines(img)

        # Chromatic aberration builds over time
        if t > 0.1:
            img = effect_chromatic_aberration(img, 1.5 + t * 3)

        # Glitch text: "W̸A̸R̸.G̸O̸V̸" appears and corrupts
        if t > 0.25:
            draw = ImageDraw.Draw(img)
            font = _font(SANS_BOLD, 80)
            glitch_text = "W\u0338A\u0338R\u0338.\u0338G\u0338O\u0338V\u0338"
            # Jitter position
            jx = random.randint(-5, 5)
            jy = random.randint(-3, 3)
            draw.text((W // 2 - 200 + jx, H // 2 - 50 + jy),
                      glitch_text, fill=(255, 0, 0), font=font)

        # Typewriter namespace errors
        if 0.45 < t < 0.75:
            draw = ImageDraw.Draw(img)
            font_sm = _font(MONO, 20)
            errors = [
                "namespace DoD → DoW",
                "err: PEACE.dll not found",
                "renaming defense.exe → war.exe",
                "WARNING: label printer jammed",
            ]
            visible = int((t - 0.45) / 0.3 * len(errors)) + 1
            for i, err in enumerate(errors[:visible]):
                y = H // 2 + 60 + i * 28
                draw.text((80, y), f"> {err}", fill=(0, 255, 0), font=font_sm)

        # Channel shift in late scene
        if t > 0.6:
            img = effect_channel_shift(img)

        # VHS tracking artifacts
        if t > 0.7 and random.random() > 0.5:
            img = effect_vhs_tracking(img)

        # Glitch blocks near end
        if t > 0.8:
            img = effect_glitch_blocks(img, 4)

        # Hard cut to black at the very end + synth stab moment
        if t > 0.92:
            img = Image.new("RGB", (W, H), (0, 0, 0))

        return img

    dur = _dur(tts_durations, "naming_ceremony", 12.0)
    t0 = _scene_start()
    scenes.append(("naming_ceremony", dur, scene_naming_ceremony))
    sfx_timeline.append((t0, "piano_note"))
    sfx_timeline.append((t0 + dur * 0.85, "synth_stab"))
    sfx_timeline.append((t0 + dur * 0.92, "vhs_click"))

    # ═══ SCENE 2: PEACE PRESIDENT (~18s) ═══
    # The promise vs the reality. Rapid montage. Loading bar. Terms & conditions.

    def scene_peace_president(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Rapid montage: cycle through GIFs with increasing speed
        if giphy_gifs:
            # Cycle rate increases over time (every N frames → fewer frames)
            cycle_rate = max(2, int(12 * (1.0 - t * 0.7)))
            idx = (frame_num // cycle_rate) % len(giphy_gifs)
            img = load_and_resize(giphy_gifs[idx], (W, H), frame=frame_num)
        else:
            img = gen_voronoi(ft, W, H, palette="neon")

        # DALL-E "EPIC FURY" on fire in middle section
        if 0.3 < t < 0.6 and dalle_images and len(dalle_images) > 1:
            fury_img = load_and_resize(dalle_images[1], (W, H))
            fury_img = effect_deep_fry(fury_img)
            fury_img = effect_zoom_and_rotate(fury_img, ft)
            blend = min(1.0, (t - 0.3) / 0.1)
            if t > 0.5:
                blend = max(0.0, 1.0 - (t - 0.5) / 0.1)
            img = Image.blend(img, fury_img, blend * 0.8)

        # Chromatic aberration throughout
        img = effect_chromatic_aberration(img, 2.0 + t * 2)

        # Loading bar overlay: "LOADING WAR... 78%"
        if 0.15 < t < 0.85:
            draw = ImageDraw.Draw(img)
            font = _font(MONO_BOLD, 24)
            bar_w = int(W * 0.6)
            bar_h = 30
            bar_x = (W - bar_w) // 2
            bar_y = H - 120
            progress_pct = min(100, int(t * 130))
            fill_w = int(bar_w * (progress_pct / 100))

            # Bar background
            draw.rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)],
                          outline=(0, 255, 0), width=2)
            # Bar fill
            if fill_w > 0:
                draw.rectangle([(bar_x + 2, bar_y + 2),
                               (bar_x + 2 + fill_w, bar_y + bar_h - 2)],
                              fill=(0, 255, 0))
            # Label
            label = f"LOADING WAR... {progress_pct}%"
            draw.text((bar_x, bar_y - 30), label,
                      fill=(0, 255, 0), font=font)

        # Terms and conditions popup in late section
        if t > 0.6:
            draw = ImageDraw.Draw(img)
            font_sm = _font(MONO, 14)
            popup_x, popup_y = 60, 60
            popup_w, popup_h = W - 120, 200
            # Semi-dark popup background
            overlay = Image.new("RGB", (popup_w, popup_h), (20, 20, 20))
            img.paste(overlay, (popup_x, popup_y))
            draw.rectangle([(popup_x, popup_y),
                           (popup_x + popup_w, popup_y + popup_h)],
                          outline=(0, 255, 0), width=1)
            terms = [
                "TERMS & CONDITIONS OF WAR (v2.026)",
                "",
                "By continuing to exist in this country you agree to:",
                "  - Unlimited military action without congressional approval",
                "  - Gas prices determined by vibes",
                "  - The word 'peace' now means 'war'",
                "  - Your taxes fund this, you're welcome",
                "",
                "[  OK  ]  [  ALSO OK  ]  [  OK BUT SADDER  ]",
            ]
            for i, line in enumerate(terms):
                draw.text((popup_x + 15, popup_y + 12 + i * 20),
                          line, fill=(0, 255, 0), font=font_sm)

        # Datamosh effect near cuts
        if t > 0.85:
            img = effect_datamosh(img)

        return img

    dur = _dur(tts_durations, "peace_president", 18.0)
    t0 = _scene_start()
    scenes.append(("peace_president", dur, scene_peace_president))
    sfx_timeline.append((t0, "air_raid_siren"))
    sfx_timeline.append((t0 + dur * 0.3, "loading_tick"))

    # ═══ SCENE 3: FOX PIPELINE (~18s) ═══
    # Fox News couch → Pentagon podium. Red yarn conspiracy. Career trajectory.

    def scene_fox_pipeline(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = Image.new("RGB", (W, H), (10, 10, 15))

        # Split screen: left fox, right pentagon
        left_img = None
        right_img = None

        if giphy_gifs and len(giphy_gifs) > 12:
            left_img = load_and_resize(giphy_gifs[12], (W // 2, H), frame=frame_num)
        if dalle_images and len(dalle_images) > 2:
            right_img = load_and_resize(dalle_images[2], (W // 2, H))

        # Swap sides at t > 0.5
        if t > 0.5:
            left_img, right_img = right_img, left_img

        if left_img:
            img.paste(left_img, (0, 0))
        else:
            left_fill = gen_plasma(ft, W // 2, H, "fire")
            img.paste(left_fill, (0, 0))

        if right_img:
            img.paste(right_img, (W // 2, 0))
        else:
            right_fill = gen_voronoi(ft, W // 2, H, palette="dark")
            img.paste(right_fill, (W // 2, 0))

        # Divider line
        draw = ImageDraw.Draw(img)
        draw.line([(W // 2, 0), (W // 2, H)], fill=(255, 0, 0), width=3)

        # Red conspiracy yarn lines connecting sides
        random.seed(42)
        n_lines = int(t * 8) + 1
        for i in range(n_lines):
            x1 = random.randint(50, W // 2 - 50)
            y1 = random.randint(100, H - 100)
            x2 = random.randint(W // 2 + 50, W - 50)
            y2 = random.randint(100, H - 100)
            draw.line([(x1, y1), (x2, y2)], fill=(255, 0, 0), width=2)
            # Pin dots at endpoints
            draw.ellipse([(x1 - 4, y1 - 4), (x1 + 4, y1 + 4)], fill=(255, 50, 50))
            draw.ellipse([(x2 - 4, y2 - 4), (x2 + 4, y2 + 4)], fill=(255, 50, 50))
        random.seed()

        # Career trajectory typewriter text
        if t > 0.2:
            font_sm = _font(MONO, 18)
            trajectory = [
                "Fox & Friends weekend host",
                "→ Fox & Friends co-host",
                "→ National Guard deployment (yes really)",
                "→ Secretary of Defense",
                "→ Secretary of W̸a̸r̸",
            ]
            visible = int((t - 0.2) / 0.8 * len(trajectory)) + 1
            for i, step in enumerate(trajectory[:visible]):
                # Progressive corruption
                if i >= 3 and random.random() > 0.6:
                    step = ''.join(
                        c if random.random() > 0.2 else random.choice('█▓▒░')
                        for c in step
                    )
                y = H - 200 + i * 28
                draw.text((40, y), step, fill=(255, 255, 255), font=font_sm)

        # Effects
        img = effect_chromatic_aberration(img, 1.5)
        if t > 0.6 and random.random() > 0.5:
            img = effect_glitch_blocks(img, 3)
        if t > 0.8:
            img = effect_scanlines(img)

        return img

    dur = _dur(tts_durations, "fox_pipeline", 18.0)
    t0 = _scene_start()
    scenes.append(("fox_pipeline", dur, scene_fox_pipeline))
    sfx_timeline.append((t0, "cable_news_whoosh"))
    sfx_timeline.append((t0 + dur * 0.3, "typewriter_sfx"))
    sfx_timeline.append((t0 + dur * 0.7, "xp_error"))

    # ═══ SCENE 4: HORMUZ EXPERIENCE (~20s) ═══
    # Oil crisis. Satellite view. Price ticker. Gas station interlude. Fire.

    def scene_hormuz_experience(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        # Gas station / slot machine interlude in mid-section
        if 0.4 < t < 0.6:
            if giphy_gifs and len(giphy_gifs) > 18:
                interlude_gifs = giphy_gifs[18:min(22, len(giphy_gifs))]
                idx = (frame_num // 8) % len(interlude_gifs)
                img = load_and_resize(interlude_gifs[idx], (W, H), frame=frame_num)
            else:
                img = gen_plasma(ft, W, H, "fire")
            img = effect_deep_fry(img)
            img = effect_chromatic_aberration(img, 3.0)
            # Still show price ticker during interlude
            draw = ImageDraw.Draw(img)
            font_price = _font(MONO_BOLD, 28)
            price = 89 + int((t - 0.0) * 250)
            draw.rectangle([(W - 280, 20), (W - 20, 70)], fill=(0, 0, 0))
            color = (255, 0, 0) if price > 150 else (255, 200, 0)
            draw.text((W - 270, 28), f"BRENT ${price}/bbl",
                      fill=color, font=font_price)
            return img

        # Main: satellite view of Strait of Hormuz
        if dalle_images and len(dalle_images) > 3:
            img = load_and_resize(dalle_images[3], (W, H))
        else:
            img = gen_voronoi(ft, W, H, palette="dark")

        # Thermal effect
        img = effect_thermal(img)

        # Wave distortion
        img = effect_wave_distort(img, ft, amplitude=6, frequency=0.02)

        draw = ImageDraw.Draw(img)

        # Red X ship markers appearing progressively
        random.seed(99)
        n_markers = int(t * 10) + 1
        font_x = _font(SANS_BOLD, 36)
        for i in range(n_markers):
            mx = random.randint(200, W - 200)
            my = random.randint(200, H - 200)
            draw.text((mx, my), "✕", fill=(255, 0, 0), font=font_x)
        random.seed()

        # Oil price ticker top-right corner
        font_price = _font(MONO_BOLD, 28)
        price = 89 + int(t * 250)
        draw.rectangle([(W - 280, 20), (W - 20, 70)], fill=(0, 0, 0))
        color = (255, 0, 0) if price > 150 else (255, 200, 0)
        draw.text((W - 270, 28), f"BRENT ${price}/bbl",
                  fill=color, font=font_price)

        # Fire GIF overlay in late section
        if t > 0.7 and giphy_gifs and len(giphy_gifs) > 3:
            fire = load_and_resize(giphy_gifs[3], (W, H), frame=frame_num)
            img = Image.blend(img, fire, 0.3)

        # Chromatic aberration intensifies
        img = effect_chromatic_aberration(img, 1.0 + t * 4)

        # Deep fry in final stretch
        if t > 0.8:
            img = effect_deep_fry(img)

        return img

    dur = _dur(tts_durations, "hormuz_experience", 20.0)
    t0 = _scene_start()
    scenes.append(("hormuz_experience", dur, scene_hormuz_experience))
    sfx_timeline.append((t0, "oil_drone_rise"))
    sfx_timeline.append((t0 + dur * 0.3, "cash_register"))
    sfx_timeline.append((t0 + dur * 0.6, "ship_explosion"))
    sfx_timeline.append((t0 + dur * 0.85, "tweet_delete"))

    # ═══ SCENE 5: WAR IS PEACE (~20s) ═══
    # Brady Bunch grid. Orwell quotes. "PEACE THROUGH STRENGTH". Dissolve.

    def scene_war_is_peace(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = Image.new("RGB", (W, H), (0, 0, 0))
        cell_w = W // 3
        cell_h = H // 3

        # Color tints for each cell
        tints = [
            (1.2, 0.8, 0.8), (0.8, 1.2, 0.8), (0.8, 0.8, 1.2),
            (1.2, 1.2, 0.8), (0.8, 1.2, 1.2), (1.2, 0.8, 1.2),
            (1.0, 0.7, 0.7), (0.7, 1.0, 0.7), (0.7, 0.7, 1.0),
        ]

        for row in range(3):
            for col in range(3):
                cell_idx = row * 3 + col
                cx, cy = col * cell_w, row * cell_h

                # Each cell from a different source
                if giphy_gifs and cell_idx < len(giphy_gifs):
                    gif_idx = (cell_idx + frame_num // 12) % len(giphy_gifs)
                    cell_img = load_and_resize(giphy_gifs[gif_idx], (cell_w, cell_h), frame=frame_num)
                elif dalle_images and cell_idx < len(dalle_images):
                    cell_img = load_and_resize(dalle_images[cell_idx % len(dalle_images)],
                                               (cell_w, cell_h))
                else:
                    cell_img = gen_plasma(ft + cell_idx, cell_w, cell_h, "vaporwave")

                # Apply unique color tint
                arr = np.array(cell_img).astype(np.float32)
                r_mult, g_mult, b_mult = tints[cell_idx]
                arr[:, :, 0] = np.clip(arr[:, :, 0] * r_mult, 0, 255)
                arr[:, :, 1] = np.clip(arr[:, :, 1] * g_mult, 0, 255)
                arr[:, :, 2] = np.clip(arr[:, :, 2] * b_mult, 0, 255)
                cell_img = Image.fromarray(arr.astype(np.uint8))

                # Glitch individual cells at t > 0.7
                if t > 0.7 and random.random() > 0.5:
                    cell_img = effect_channel_shift(cell_img)
                if t > 0.8 and random.random() > 0.6:
                    cell_img = effect_datamosh(cell_img)

                img.paste(cell_img, (cx, cy))

        # Grid lines
        draw = ImageDraw.Draw(img)
        for i in range(1, 3):
            draw.line([(i * cell_w, 0), (i * cell_w, H)],
                      fill=(40, 40, 40), width=2)
            draw.line([(0, i * cell_h), (W, i * cell_h)],
                      fill=(40, 40, 40), width=2)

        # Orwell quote materializes at t > 0.3
        if t > 0.3:
            font = _font(SANS_BOLD, 44)
            # Semi-transparent dark overlay for readability
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(W // 2 - 320, H // 2 - 90), (W // 2 + 320, H // 2 + 90)],
                fill=(0, 0, 0, 160))
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, overlay)
            img = img.convert("RGB")

            draw = ImageDraw.Draw(img)
            quote_lines = [
                ("WAR IS PEACE", (255, 0, 0)),
                ("FREEDOM IS SLAVERY", (255, 100, 0)),
                ("IGNORANCE IS STRENGTH", (255, 200, 0)),
            ]
            visible_lines = int((t - 0.3) / 0.2 * len(quote_lines)) + 1
            for i, (text, color) in enumerate(quote_lines[:visible_lines]):
                try:
                    tw = font.getlength(text)
                except AttributeError:
                    tw = len(text) * 26
                draw.text((W // 2 - tw // 2, H // 2 - 70 + i * 55),
                          text, fill=color, font=font)

        # "PEACE THROUGH STRENGTH" scattered at t > 0.5
        if t > 0.5:
            draw = ImageDraw.Draw(img)
            font_scatter = _font(MONO_BOLD, 20)
            random.seed(123)
            for _ in range(int((t - 0.5) * 20) + 1):
                sx = random.randint(20, W - 300)
                sy = random.randint(20, H - 40)
                angle_text = "PEACE THROUGH STRENGTH"
                alpha = int(80 + random.random() * 100)
                draw.text((sx, sy), angle_text,
                          fill=(alpha, alpha // 2, alpha // 4), font=font_scatter)
            random.seed()

        # Dissolve to black at t > 0.9
        if t > 0.9:
            black = Image.new("RGB", (W, H), (0, 0, 0))
            blend = (t - 0.9) / 0.1
            img = transition_dissolve(img, black, blend)

        return img

    dur = _dur(tts_durations, "war_is_peace", 20.0)
    t0 = _scene_start()
    scenes.append(("war_is_peace", dur, scene_war_is_peace))
    sfx_timeline.append((t0 + dur * 0.3, "dissonance_chord"))
    sfx_timeline.append((t0 + dur * 0.7, "glitch_burst"))

    # ═══ SCENE 6: OUTRO — YOUR MOM (~17s) ═══
    # Shrink to pixel. Terminal crawl. Statistics. Blinking cursor. Final card.

    def scene_outro_your_mom(frame_num, total_frames):
        t = frame_num / total_frames
        ft = frame_num / FPS

        img = Image.new("RGB", (W, H), (0, 0, 0))

        # Phase 1 (t < 0.3): DALL-E images cycling, shrinking to center pixel
        if t < 0.3:
            if dalle_images:
                cycle_rate = max(2, int(8 * (1.0 - t * 3)))
                idx = (frame_num // cycle_rate) % len(dalle_images)
                src = load_and_resize(dalle_images[idx], (W, H))
            else:
                src = gen_plasma(ft, W, H, "vaporwave")

            # Shrink toward center
            shrink = max(0.02, 1.0 - (t / 0.3))
            new_w = max(2, int(W * shrink))
            new_h = max(2, int(H * shrink))
            src_small = src.resize((new_w, new_h), Image.LANCZOS)
            paste_x = (W - new_w) // 2
            paste_y = (H - new_h) // 2
            img.paste(src_small, (paste_x, paste_y))

            # Bit crush effect during shrink
            img = effect_bit_crush(img, bits=max(2, int(8 * shrink)))

            return img

        # Phase 2 (0.3 < t < 0.85): Terminal text crawl
        draw = ImageDraw.Draw(img)
        font = _font(MONO, 20)
        font_sm = _font(MONO, 16)

        stats = [
            "OPERATION EPIC FURY — AFTER ACTION REPORT",
            "==========================================",
            "",
            f"Sorties flown: {random.Random(42).randint(800, 1200)}",
            f"Tomahawks launched: {random.Random(43).randint(200, 400)}",
            f"Pentagon press briefings: {random.Random(44).randint(3, 8)}",
            f"Congressional votes held: 0",
            f"Oil price increase: +{random.Random(45).randint(100, 200)}%",
            f"Fox News hosts promoted: {random.Random(46).randint(2, 5)}",
            f"Tweets deleted: {random.Random(47).randint(12, 30)}",
            "",
            "Wars started by peace presidents: 1",
            "Departments renamed for honesty: also 1",
            "Operations named after your mom: also 1",
            "",
            "Loading peace...... ERROR: FILE NOT FOUND",
        ]

        text_t = (t - 0.3) / 0.55
        visible = int(text_t * len(stats) * 1.3) + 1

        y = 80
        for i, line in enumerate(stats[:visible]):
            if i >= len(stats):
                break
            if y > H - 120:
                break
            # Green terminal text, typewriter reveal
            color = (0, 255, 0) if "ERROR" not in line else (255, 0, 0)
            if "your mom" in line:
                color = (255, 255, 0)
            draw.text((60, y), line, fill=color, font=font)
            y += 28

        # Blinking cursor
        if frame_num % 18 < 9:
            draw.text((60, y + 10), "> _", fill=(0, 255, 0), font=font)

        # Scanlines on terminal
        img = effect_scanlines(img)

        # Phase 3 (t > 0.85): Final card
        if t > 0.85:
            img = Image.new("RGB", (W, H), (0, 0, 0))
            draw = ImageDraw.Draw(img)
            font_title = _font(SANS_BOLD, 48)
            font_date = _font(MONO, 24)

            # Zalgo title in red
            title = "E\u0335P\u0336I\u0337C\u0334 F\u0338U\u0335R\u0337Y\u0335"
            try:
                tw = font_title.getlength(title)
            except AttributeError:
                tw = len(title) * 28
            draw.text((W // 2 - tw // 2, H // 2 - 50),
                      title, fill=(255, 0, 0), font=font_title)

            # Date
            date_text = "est. February 28, 2026"
            try:
                dw = font_date.getlength(date_text)
            except AttributeError:
                dw = len(date_text) * 14
            draw.text((W // 2 - dw // 2, H // 2 + 20),
                      date_text, fill=(180, 0, 0), font=font_date)

            # Subtle scanlines
            img = effect_scanlines(img)

        return img

    dur = _dur(tts_durations, "outro_your_mom", 17.0)
    t0 = _scene_start()
    scenes.append(("outro_your_mom", dur, scene_outro_your_mom))
    sfx_timeline.append((t0, "final_piano"))
    sfx_timeline.append((t0 + dur * 0.8, "static_fade"))

    return scenes, sfx_timeline

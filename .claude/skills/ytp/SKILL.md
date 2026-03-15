---
name: ytp
description: Create or manage YouTube Poop video sessions. Use when the user wants to generate a new YTP video, iterate on an existing session, add scenes, or re-render.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
argument-hint: <new|render|list> [session_name] [description]
---

# YTP Video Generator

You are managing a YouTube Poop video generator. The project lives at `/home/user/Development/yt-poop`.

## Architecture

```
engine/           # Reusable generation capabilities
  effects.py      # Visual effects + transitions (see Effects Reference below)
  text.py         # Text overlays (glitch, bottom_text, scattered, typewriter)
  audio.py        # TTS, procedural music (sine/sawtooth/square/noise layers), SFX, mixing
  assets.py       # GIPHY fetching, DALL-E image generation
  render.py       # Frame rendering + ffmpeg encoding
  progress.py     # ProgressTracker for resumability
sessions/         # Each video is a session
  <name>/
    content.py    # Content definition (scenes, prompts, TTS lines, music, SFX)
    build/        # Cached assets, frames, audio (auto-created)
    *.mp4         # Output video
generate.py       # CLI: python generate.py <session_name>
```

## Commands

### `/ytp new <session_name> <description>`
Create a new session. Write `sessions/<session_name>/content.py` with:
- `TITLE`, `WIDTH=1280`, `HEIGHT=720`, `FPS=24`
- `giphy_searches` — list of GIPHY search terms for source material
- `dalle_prompts` — list of DALL-E image prompts
- `tts_lines` — list of `(text, voice, speed)` tuples. Voices: alloy, echo, fable, onyx, nova, shimmer
- `music_config` — `{"layers": [...], "master_filters": "...", "mix_volume": 0.3}`
  - Layer types: `sine`, `sawtooth`, `square` (need `freq`), `noise` (needs `color`: pink/white/brown)
  - Each layer: `{"type", "freq", "duration", "volume", "filters"}`
- `sfx_cues` — list of `{"name", "type": "tone"|"noise_burst"|"sweep", "freq", "duration", "filters"}`
- `build_scenes(dalle_images, giphy_gifs)` — returns `(scenes, sfx_timeline)` or just `scenes`
  - Scene: `(name, duration_secs, gen_func)` where `gen_func(frame_num, total_frames) -> PIL.Image`
  - SFX timeline: `[(timestamp_secs, sfx_name), ...]`

Import effects/text/render from the engine. Use `$ARGUMENTS` for the session name and theme.

### `/ytp render [session_name]`
Run `python generate.py <session_name>` to render. The pipeline is fully resumable — cached steps are skipped.
If no session name given, list available sessions and ask which to render.

### `/ytp list`
List available sessions under `sessions/` and their status (has output video? progress state?).

### `/ytp iterate <session_name>`
Read the session's `content.py`, discuss changes with the user, edit it, then invalidate affected cache steps:
- Changed `giphy_searches` → delete `build/progress.json` entry for "giphy"
- Changed `dalle_prompts` → delete "dalle" entry
- Changed `tts_lines` → delete "tts" entry
- Changed `music_config` → delete "music" entry
- Changed `sfx_cues` → delete "sfx" entry
- Changed `build_scenes` → delete "frames" and "audio" entries
Then re-render.

## Effects Reference (`engine/effects.py`)

### Core Effects
- `effect_deep_fry(img)` — oversaturate, sharpen, add noise
- `effect_channel_shift(img)` — shift RGB channels apart
- `effect_datamosh(img)` — corrupt random rectangular regions
- `effect_scanlines(img)` — VHS-style scanlines
- `effect_invert_glitch(img)` — invert a random horizontal band
- `effect_zoom_and_rotate(img, t)` — animated Ken Burns on acid
- `effect_mirror_stretch(img)` — mirror half the image
- `effect_pixel_sort(img)` — sort pixels by brightness in random rows
- `effect_vhs_tracking(img)` — horizontal band shifts with noise bars
- `effect_chromatic_aberration(img, intensity=1.0)` — radial channel scaling
- `effect_posterize(img, levels=4)` — reduce color depth
- `effect_wave_distort(img, t=0, amplitude=15, frequency=0.02)` — sinusoidal row shifting
- `effect_glitch_blocks(img, n_blocks=8)` — displace/recolor/duplicate random blocks
- `effect_bit_crush(img, bits=3)` — reduce bit depth per channel
- `effect_feedback_loop(img, t=0, decay=0.7, offset=(10,10))` — video feedback blend
- `effect_color_halftone(img, dot_size=6)` — CMYK halftone dots
- `effect_thermal(img)` — thermal camera colormap
- `effect_jpeg_corrupt(img, quality=2, passes=3)` — repeated JPEG compression for authentic deep-fry artifacts (quality 1-20, passes 1-5)
- `effect_slit_scan(img, history=None, band_height=4, direction="horizontal")` — temporal slit-scan; caller passes `collections.deque(maxlen=N)` of recent frames as `history`
- `effect_displacement_map(img, intensity=15.0, frequency=0.02, t=0.0, axis="both")` — multi-octave sine displacement for liquify/melting/underwater distortion; `axis` can be "both", "x", or "y"

### Transitions
- `transition_dissolve(img_a, img_b, t)` — cross-dissolve
- `transition_wipe_horizontal(img_a, img_b, t)` — left-to-right wipe
- `transition_wipe_vertical(img_a, img_b, t)` — top-to-bottom wipe
- `transition_glitch_cut(img_a, img_b, t)` — random blocks swap
- `transition_pixel_scatter(img_a, img_b, t)` — pixels randomly switch
- `transition_zoom_through(img_a, img_b, t)` — zoom into A, dissolve to B

## Generators Reference (`engine/sources.py`)

### FFmpeg lavfi sources
- `ffmpeg_mandelbrot_frame(t, width, height, max_iter)` — mandelbrot zoom
- `ffmpeg_life_frame(frame_num, width, height, rule, fill_ratio)` — Game of Life
- `ffmpeg_gradient_frame(width, height, c0, c1, duration, t)` — color gradient
- `ffmpeg_test_pattern(width, height, pattern)` — test pattern (testsrc2, smptebars, etc.)

### Python generative sources
- `gen_plasma(t, width, height, palette)` — sine interference plasma; palettes: vaporwave, fire, matrix, ocean
- `gen_voronoi(t, width, height, n_points, palette)` — animated Voronoi diagram; palettes: neon, dark
- `gen_oscilloscope(t, width, height, waves)` — oscilloscope waveforms
- `gen_particle_field(t, width, height, n_particles, color, bg)` — drifting particles with orbital attraction
- `gen_circuit_board(t, width, height, density)` — animated PCB trace pattern
- `gen_heartbeat_monitor(t, width, height, bpm, color)` — ECG heart rate display
- `gen_reaction_diffusion(t, width, height, feed_rate=0.04, kill_rate=0.06, palette="alien", speed=10, sim_scale=4)` — Gray-Scott organic patterns (spots, stripes, coral); palettes: alien, coral, void, electric. Stateful — evolves over calls.
- `gen_strange_attractor(t, width, height, attractor_type="lorenz", n_points=2000, rotation_speed=0.3, color_scheme="default", trail_decay=0.95)` — chaotic particle traces with 3D rotation; types: lorenz, rossler, aizawa; colors: default, fire, neon, ice. Stateful — trails accumulate.
- `gen_ascii_matrix(t, width, height, mode="rain", char_size=14, color="green", density=0.6, speed=1.0)` — ASCII art renderer; modes: rain (Matrix digital rain), static (noise-to-ASCII), morph (flowing sine interference); colors: green, amber, white, rainbow

## Important Notes
- API keys come from `doppler` in the project directory: `OPENAI_API_KEY` and `GIPHY_API_KEY`
- Everything is resumable. Never re-generate assets that already exist.
- The content/engine separation is critical — never put content-specific logic in `engine/`
- YTP style: chaotic, glitchy, absurdist humor, rapid cuts, deep-fried effects, stuttering, channel shifting

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
  - **OR** `ace_music` — ACE-Step music generation config (see Music Generation below)
- `sfx_cues` — list of `{"name", "type": "tone"|"noise_burst"|"sweep", "freq", "duration", "filters"}`
- `build_scenes(dalle_images, giphy_gifs)` — returns `(scenes, sfx_timeline)` or just `scenes`
  - Scene: `(name, duration_secs, gen_func)` where `gen_func(frame_num, total_frames) -> PIL.Image`
  - SFX timeline: `[(timestamp_secs, sfx_name), ...]`

Import effects/text/render from the engine. Use `$ARGUMENTS` for the session name and theme.

## Music Generation (ACE-Step 1.5)

When a session needs a real song (not just procedural synth), use the ACE-Step 1.5 model via ComfyUI at `http://172.20.0.1:8000`.

### When to use
- The content calls for an actual song with lyrics, melody, or specific genre
- Procedural sine/sawtooth/noise layers won't cut it for the vibe
- The user requests a song or music track

### content.py config
Add an `ace_music` dict to the session's `content.py`:

```python
ace_music = {
    "tags": "dark synthwave with distorted bassline, arpeggiating synths, cinematic pads, 808 drums",
    "lyrics": "[Verse 1]\nLines here\n[Chorus]\nChorus lines",
    "key": "D minor",
    "bpm": 128,
    "duration": 70,  # seconds — request ~8s MORE than you need (see Tail Padding below)
    "seed": 42,
    "filename": "session_music",  # output filename prefix (no extension)
}
```

### Tail Padding
ACE-Step produces audio exactly the requested length, but the **last 7–9 seconds are typically silent/blank**. Handle this one of three ways:
1. **Trim**: Request `desired_duration + 8` seconds, then trim the silent tail with ffmpeg: `ffmpeg -i song.mp3 -t <desired_duration> -c copy trimmed.mp3`
2. **Fill**: Use the silent tail for TTS lines, SFX hits, or a fade-out transition
3. **Ignore**: If the video is shorter than the music, `-shortest` in the final encode handles it

**Default approach: Trim.** Request 8s extra, trim to desired length after download.

### Generation workflow
1. **Start music generation early** — submit the ComfyUI prompt as the first step (it takes 1–3 minutes)
2. **Work on other assets in parallel** — fetch GIPHY, generate DALL-E images, write TTS while music generates
3. **Poll for completion** before frame rendering begins (music duration determines video timing)
4. **Download and trim** the result to the session's `build/audio/` directory

### ComfyUI submission
POST to `http://172.20.0.1:8000/prompt` with this node graph:

```json
{
  "prompt": {
    "104": { "class_type": "UNETLoader", "inputs": { "unet_name": "acestep_v1.5_turbo.safetensors", "weight_dtype": "default" } },
    "105": { "class_type": "DualCLIPLoader", "inputs": { "clip_name1": "qwen_0.6b_ace15.safetensors", "clip_name2": "qwen_1.7b_ace15.safetensors", "type": "ace", "device": "default" } },
    "98":  { "class_type": "EmptyAceStep1.5LatentAudio", "inputs": { "seconds": DURATION, "batch_size": 1 } },
    "94":  { "class_type": "TextEncodeAceStepAudio1.5", "inputs": {
               "clip": ["105", 0], "tags": "TAGS", "lyrics": "LYRICS",
               "seed": SEED, "bpm": BPM, "duration": DURATION,
               "timesignature": "4", "language": "en", "keyscale": "KEY",
               "generate_audio_codes": true, "cfg_scale": 3,
               "temperature": 0.8, "top_p": 0.9, "top_k": 0, "min_p": 0 } },
    "47":  { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["94", 0] } },
    "78":  { "class_type": "ModelSamplingAuraFlow", "inputs": { "model": ["104", 0], "shift": 5 } },
    "3":   { "class_type": "KSampler", "inputs": {
               "model": ["78", 0], "positive": ["94", 0], "negative": ["47", 0],
               "latent_image": ["98", 0], "seed": SEED,
               "steps": 8, "cfg": 1, "sampler_name": "euler", "scheduler": "simple", "denoise": 1 } },
    "18":  { "class_type": "VAEDecodeAudio", "inputs": { "samples": ["3", 0], "vae": ["106", 0] } },
    "106": { "class_type": "VAELoader", "inputs": { "vae_name": "ace_1.5_vae.safetensors" } },
    "107": { "class_type": "SaveAudioMP3", "inputs": {
               "audio": ["18", 0], "filename_prefix": "audio/FILENAME", "quality": "V0" } }
  }
}
```

### Polling and download
```bash
# Poll every 5s until .status.status_str == "success" (timeout 5 min)
curl -s "http://172.20.0.1:8000/history/{prompt_id}"

# Extract filename from .outputs["107"].audio[0]
# Download and trim:
curl -s "http://172.20.0.1:8000/view?filename=FILENAME&type=output&subfolder=SUBFOLDER" -o build/audio/raw_music.mp3
ffmpeg -y -i build/audio/raw_music.mp3 -t DESIRED_DURATION -c copy build/audio/music.mp3
```

### Mixing with other audio
The downloaded music file replaces or supplements the procedural `music_config`. In `generate.py`, the audio mixing step should use this file as the music bed. Layer TTS and SFX on top as usual.

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

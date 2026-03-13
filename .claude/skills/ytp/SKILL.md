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
  effects.py      # Visual effects (deep_fry, channel_shift, datamosh, scanlines, etc.)
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

## Important Notes
- API keys come from `doppler` in the project directory: `OPENAI_API_KEY` and `GIPHY_API_KEY`
- Everything is resumable. Never re-generate assets that already exist.
- The content/engine separation is critical — never put content-specific logic in `engine/`
- YTP style: chaotic, glitchy, absurdist humor, rapid cuts, deep-fried effects, stuttering, channel shifting

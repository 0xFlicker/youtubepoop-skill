#!/usr/bin/env python3
"""
YTP Generator — CLI entrypoint.
Usage: python generate.py <session_name>

Sessions live in sessions/<name>/content.py.
Each session is independently resumable — cached steps are skipped.
"""

import sys
import subprocess
import importlib
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))


def main():
    if len(sys.argv) < 2:
        # List available sessions
        sessions_dir = PROJECT_DIR / "sessions"
        available = [
            d.name for d in sessions_dir.iterdir()
            if d.is_dir() and (d / "content.py").exists()
        ]
        print("Usage: python generate.py <session_name>")
        print(f"\nAvailable sessions: {', '.join(sorted(available))}")
        sys.exit(1)

    session_name = sys.argv[1]
    session_dir = PROJECT_DIR / "sessions" / session_name

    if not (session_dir / "content.py").exists():
        print(f"Session '{session_name}' not found.")
        sys.exit(1)

    # Import session content
    content = importlib.import_module(f"sessions.{session_name}.content")

    # Set up build dirs inside the session
    build_dir = session_dir / "build"
    assets_dir = build_dir / "assets"
    frames_dir = build_dir / "frames"
    audio_dir = build_dir / "audio"
    for d in [assets_dir, frames_dir, audio_dir]:
        d.mkdir(parents=True, exist_ok=True)

    output_path = session_dir / f"{content.TITLE}.mp4"

    # Progress tracker (per-session)
    from engine.progress import ProgressTracker
    progress = ProgressTracker(build_dir / "progress.json")

    # API keys
    from engine import get_key
    openai_key = get_key("OPENAI_API_KEY")
    xai_key = get_key("XAI_API_KEY")
    giphy_key = get_key("GIPHY_API_KEY")

    print("=" * 60)
    print(f"  YTP: '{content.TITLE}'")
    print(f"  Session: {session_name}")
    print(f"  (resumable — cached steps will be skipped)")
    print("=" * 60)

    # 1. GIPHY
    from engine.assets import fetch_giphy_gifs, generate_dalle_images
    print(f"\n[1/7] GIPHY assets...")
    giphy_gifs = fetch_giphy_gifs(content.giphy_searches, assets_dir, giphy_key, progress)
    print(f"  Total: {len(giphy_gifs)} GIFs")

    # 2. Grok Imagine (xAI)
    print(f"\n[2/7] Grok Imagine images...")
    dalle_images = generate_dalle_images(content.dalle_prompts, assets_dir, xai_key, progress)
    print(f"  Total: {len(dalle_images)} images")

    # 3. TTS
    from engine.audio import (
        generate_tts_clips, generate_music_track, generate_sfx, build_audio,
        measure_tts_durations, estimate_processed_durations, audio_duration,
        measure_clip_duration,
    )
    print(f"\n[3/7] TTS voiceover...")
    tts_clips = generate_tts_clips(content.tts_lines, audio_dir, openai_key, progress)
    print(f"  Total: {len(tts_clips)} clips")

    # 3b. Measure TTS durations for audio-aware scene sizing
    tts_fx = getattr(content, "tts_effects", None)
    if tts_clips:
        print(f"\n  Measuring TTS durations...")
        raw_durations = measure_tts_durations(tts_clips)
        processed_durations = estimate_processed_durations(raw_durations, tts_fx)
        total_tts = sum(processed_durations)
        print(f"  Raw TTS: {sum(raw_durations):.1f}s -> Processed: {total_tts:.1f}s")
    else:
        processed_durations = []

    # 4. Music
    print(f"\n[4/7] Music track...")
    music_track = None
    if hasattr(content, "music_path") and content.music_path:
        src = Path(content.music_path)
        dst = audio_dir / "music.wav"
        if src.exists():
            if not dst.exists():
                vol = getattr(content, "music_volume", 0.4)
                print(f"  Converting pre-generated music (volume={vol})...")
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(src),
                    "-af", f"volume={vol}",
                    "-ar", "44100", "-ac", "2", str(dst),
                ], capture_output=True)
            music_track = dst if dst.exists() else None
            print(f"  {'Using pre-generated track' if music_track else 'Conversion failed'}")
        else:
            print(f"  Warning: music_path not found: {src}")
    elif hasattr(content, "music_config") and content.music_config:
        music_track = generate_music_track(content.music_config, audio_dir, progress)
        print(f"  {'Generated' if music_track else 'None'}")
    else:
        print("  Skipped (no music_config or music_path)")
    music_duration = None
    if music_track:
        music_duration = measure_clip_duration(music_track)
        print(f"  Music duration: {music_duration:.1f}s")

    # 5. SFX
    print(f"\n[5/7] Sound effects...")
    sfx_clips = {}
    if hasattr(content, "sfx_cues") and content.sfx_cues:
        sfx_clips = generate_sfx(content.sfx_cues, audio_dir, progress)
        print(f"  Total: {len(sfx_clips)} SFX clips")
    else:
        print("  Skipped (no sfx_cues)")

    # Compute music start offset for "opening TTS before music" pattern
    tts_positions = getattr(content, "tts_positions", None)
    music_start_offset = 0.0
    if (tts_positions is not None
            and 0 in tts_positions
            and processed_durations
            and getattr(content, "music_after_opening_tts", False)):
        music_start_offset = tts_positions[0] + processed_durations[0]
        # Shift all non-opening TTS positions forward by the offset
        tts_positions = {
            idx: (pos if idx == 0 else pos + music_start_offset)
            for idx, pos in tts_positions.items()
        }
        print(f"  Music delayed by {music_start_offset:.1f}s (after opening TTS)")

    # 6. Render frames — pass TTS durations so scenes can size to audio
    from engine.render import render_frames, encode_video
    print(f"\n[6/7] Rendering frames...")
    import inspect
    # Check if build_scenes accepts tts_durations / music_duration (backward compatible)
    sig = inspect.signature(content.build_scenes)
    kwargs = {}
    if "tts_durations" in sig.parameters:
        kwargs["tts_durations"] = processed_durations
    if "music_duration" in sig.parameters:
        # Extend music_duration to include the pre-music TTS gap
        effective_music_duration = (
            (music_duration + music_start_offset) if music_duration else None
        )
        kwargs["music_duration"] = effective_music_duration
    scene_result = content.build_scenes(dalle_images, giphy_gifs, **kwargs)

    # build_scenes can return just scenes or (scenes, sfx_timeline)
    if isinstance(scene_result, tuple):
        scenes, sfx_timeline_names = scene_result
    else:
        scenes, sfx_timeline_names = scene_result, []

    total_duration, total_frames = render_frames(
        scenes, content.FPS, frames_dir, progress
    )

    # Resolve SFX timeline names to paths
    sfx_timeline = []
    for timestamp, name in sfx_timeline_names:
        if name in sfx_clips:
            sfx_timeline.append((timestamp, sfx_clips[name]))

    # 7. Audio + encode
    print(f"\n[7/7] Building audio & encoding...")
    music_gap = getattr(content, "music_tts_gap", None) if music_track else None
    final_audio = build_audio(
        tts_clips, total_duration, audio_dir, progress,
        music_track=music_track, sfx_timeline=sfx_timeline,
        tts_effects=tts_fx, music_gap=music_gap,
        tts_positions=tts_positions,
        music_start_offset=music_start_offset,
    )

    success = encode_video(frames_dir, final_audio, output_path, content.FPS)

    if success:
        print(f"\n{'=' * 60}")
        print(f"  DONE: {output_path}")
        print(f"  Duration: {total_duration:.1f}s")
        print(f"  Re-run to resume from cache if interrupted!")
        print(f"{'=' * 60}")
    else:
        print("\n  FAILED — see errors above. Re-run to resume.")
        sys.exit(1)


if __name__ == "__main__":
    main()

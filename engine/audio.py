"""Audio generation — TTS, procedural music, SFX, and mixing."""

import subprocess
import shutil
from pathlib import Path


# ── Duration measurement ────────────────────────────────────────────────────

# Effect duration multipliers — how each TTS effect changes clip length
_EFFECT_MULTIPLIERS = {
    "normal": 1.0,
    "echo": 1.05,       # adds a short tail
    "fast": 1.0 / 1.4,  # atempo=1.4
    "slow": 1.0 / 0.8,  # atempo=0.8
    "deep": 1.0 / 0.7,  # asetrate * 0.7
    "high": 1.0 / 1.3,  # asetrate * 1.3
    "whisper": 1.0,
    "telephone": 1.0,
    "chorus": 1.05,
    "reverse": 1.0,
    "stutter": None,     # special: replaces with ~1.6s regardless
}
_STUTTER_FIXED_DURATION = 1.6  # 0.4s x 4 loops


def measure_clip_duration(path):
    """Measure duration of an audio file in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 3.0  # fallback estimate


def measure_tts_durations(tts_clips):
    """Measure raw durations of all TTS clips. Returns list of floats."""
    return [measure_clip_duration(path) for path, _ in tts_clips]


def estimate_processed_durations(raw_durations, tts_effects=None):
    """
    Estimate post-processing durations based on which effects will be applied.
    Returns list of estimated durations in seconds.
    """
    if tts_effects is None:
        tts_effects = [
            "normal", "echo", "fast", "normal", "whisper", "telephone",
            "normal", "chorus", "slow", "normal", "stutter", "normal",
        ]

    result = []
    for i, raw_dur in enumerate(raw_durations):
        effect = tts_effects[i % len(tts_effects)]
        mult = _EFFECT_MULTIPLIERS.get(effect, 1.0)
        if mult is None:  # stutter
            result.append(_STUTTER_FIXED_DURATION)
        else:
            result.append(raw_dur * mult)
    return result


def audio_duration(tts_durations, clip_indices, padding=1.5, gap_per_clip=0.25):
    """
    Helper for content.py: compute scene duration to fit specific TTS clips.

    Args:
        tts_durations: list of all clip durations (from estimate_processed_durations)
        clip_indices: list of TTS clip indices that play during this scene
        padding: extra seconds added at end for breathing room
        gap_per_clip: estimated inter-clip gap time

    Returns:
        float: recommended scene duration in seconds
    """
    if not clip_indices or not tts_durations:
        return 4.0  # sensible default
    total = sum(tts_durations[i] for i in clip_indices if i < len(tts_durations))
    total += gap_per_clip * max(0, len(clip_indices) - 1)
    return total + padding


def generate_tts_clips(lines, audio_dir, api_key, progress, step_key="tts"):
    """
    Generate TTS clips with OpenAI.
    lines: list of (text, voice, speed)
    Returns: list of (path, text) for clips that exist.
    """
    from openai import OpenAI
    audio_dir = Path(audio_dir)

    if progress.is_done(step_key):
        print(f"  [cached] TTS clips")
        clips = []
        for i, (text, _, _) in enumerate(lines):
            path = audio_dir / f"tts_{i}.mp3"
            if path.exists():
                clips.append((path, text))
        return clips

    client = OpenAI(api_key=api_key)
    clips = []

    for i, (text, voice, speed) in enumerate(lines):
        path = audio_dir / f"tts_{i}.mp3"
        if path.exists():
            print(f"  [cached] TTS clip {i+1}/{len(lines)}")
            clips.append((path, text))
            continue

        print(f"  Generating TTS clip {i+1}/{len(lines)} (voice={voice})...")
        try:
            response = client.audio.speech.create(
                model="tts-1", voice=voice, input=text, speed=speed,
            )
            response.stream_to_file(str(path))
            clips.append((path, text))
        except Exception as e:
            print(f"    Warning: {e}")

    progress.mark_done(step_key)
    return clips


def generate_music_track(config, audio_dir, progress, step_key="music"):
    """
    Generate procedural music/drone using ffmpeg lavfi synthesis.

    config: {
        "layers": [
            {"type": "sine"|"sawtooth"|"square"|"noise"|"pluck"|"fm"|"pad",
             "freq": 110, "duration": 30, "volume": 0.02,
             "filters": "optional,extra,filters",
             # pluck-specific:
             "decay": 2.0,
             # fm-specific:
             "mod_freq": 5, "mod_depth": 50,
             # pad-specific:
             "freq2": 165, "beat_freq": 0.5,
            },
            ...
        ],
        "master_filters": "optional,master,filters",
        "mix_volume": 0.3,
    }
    """
    audio_dir = Path(audio_dir)
    output = audio_dir / "music.wav"

    if progress.is_done(step_key) and output.exists():
        print(f"  [cached] Music track")
        return output

    layers = config.get("layers", [])
    if not layers:
        return None

    layer_paths = []
    for i, layer in enumerate(layers):
        layer_path = audio_dir / f"music_layer_{i}.wav"
        if layer_path.exists():
            layer_paths.append(layer_path)
            continue

        ltype = layer["type"]
        dur = layer["duration"]
        vol = layer.get("volume", 0.02)
        freq = layer.get("freq", 110)
        filters = layer.get("filters", "")

        if ltype == "sine":
            src = f"sine=frequency={freq}:duration={dur}"
        elif ltype == "sawtooth":
            src = f"aevalsrc='(1-2*mod({freq}*t\\,1))*{vol}':d={dur}:s=44100"
        elif ltype == "square":
            src = f"aevalsrc='(mod({freq}*t\\,1)>0.5)*2*{vol}-{vol}':d={dur}:s=44100"
        elif ltype == "noise":
            color = layer.get("color", "pink")
            src = f"anoisesrc=d={dur}:c={color}:a={vol}"
        elif ltype == "pluck":
            # Plucked string — sine with exponential decay, repeated
            decay = layer.get("decay", 2.0)
            src = (f"aevalsrc='sin(2*PI*{freq}*t)*{vol}"
                   f"*exp(-t*{1.0/decay})*(1+0.3*sin(2*PI*{freq*2.01}*t))'"
                   f":d={dur}:s=44100")
        elif ltype == "fm":
            # FM synthesis — carrier + modulator
            mod_freq = layer.get("mod_freq", 5)
            mod_depth = layer.get("mod_depth", 50)
            src = (f"aevalsrc='sin(2*PI*({freq}+{mod_depth}"
                   f"*sin(2*PI*{mod_freq}*t))*t)*{vol}':d={dur}:s=44100")
        elif ltype == "pad":
            # Two detuned sines for a warm pad sound
            freq2 = layer.get("freq2", freq * 1.005)
            src = (f"aevalsrc='(sin(2*PI*{freq}*t)+sin(2*PI*{freq2}*t))"
                   f"*0.5*{vol}':d={dur}:s=44100")
        elif ltype == "arpeggio":
            # Stepped frequency pattern
            notes = layer.get("notes", [freq, freq*1.25, freq*1.5, freq*2])
            step_dur = layer.get("step_duration", 0.25)
            notes_str = "+".join(
                f"sin(2*PI*{n}*t)*(between(mod(t\\,{step_dur*len(notes)})\\,"
                f"{j*step_dur}\\,{(j+1)*step_dur}))"
                for j, n in enumerate(notes)
            )
            src = f"aevalsrc='{notes_str}*{vol}':d={dur}:s=44100"
        elif ltype == "drone_chord":
            # Multiple stacked frequencies for a rich drone
            freqs = layer.get("freqs", [freq, freq*1.5, freq*2])
            expr = "+".join(f"sin(2*PI*{f}*t)" for f in freqs)
            src = f"aevalsrc='({expr})*{vol}/{len(freqs)}':d={dur}:s=44100"
        else:
            continue

        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", src]

        af_parts = []
        if ltype in ("sine",):
            af_parts.append(f"volume={vol}")
        if filters:
            af_parts.append(filters)
        if af_parts:
            cmd += ["-af", ",".join(af_parts)]

        cmd += ["-ar", "44100", "-ac", "2", str(layer_path)]

        print(f"  Generating music layer {i+1}/{len(layers)} ({ltype})...")
        subprocess.run(cmd, capture_output=True)
        if layer_path.exists():
            layer_paths.append(layer_path)

    if not layer_paths:
        return None

    if len(layer_paths) == 1:
        shutil.copy(layer_paths[0], output)
    else:
        cmd = ["ffmpeg", "-y"]
        for p in layer_paths:
            cmd += ["-i", str(p)]
        mix_filter = f"amix=inputs={len(layer_paths)}:duration=longest"
        master_filters = config.get("master_filters", "")
        if master_filters:
            mix_filter += f",{master_filters}"
        cmd += ["-filter_complex", mix_filter, "-ar", "44100", "-ac", "2", str(output)]
        subprocess.run(cmd, capture_output=True)

    progress.mark_done(step_key)
    return output if output.exists() else None


def generate_sfx(cues, audio_dir, progress, step_key="sfx"):
    """
    Generate sound effect clips using ffmpeg lavfi.

    cue types:
      noise_burst  — burst of colored noise
      tone         — pure sine tone
      sweep        — frequency sweep
      impact       — layered noise + tone for punchy hit
      glitch       — rapid random tones for digital glitch
      whoosh       — filtered noise sweep for transitions
      heartbeat    — low thump pattern
      typing       — rapid clicking pattern
      power_up     — ascending tone cascade
      power_down   — descending tone cascade
    """
    audio_dir = Path(audio_dir)

    if progress.is_done(step_key):
        print(f"  [cached] SFX clips")
        result = {}
        for cue in cues:
            p = audio_dir / f"sfx_{cue['name']}.wav"
            if p.exists():
                result[cue["name"]] = p
        return result

    result = {}
    for cue in cues:
        name = cue["name"]
        path = audio_dir / f"sfx_{name}.wav"
        if path.exists():
            result[name] = path
            continue

        stype = cue["type"]
        dur = cue.get("duration", 0.5)
        freq = cue.get("freq", 440)
        filters = cue.get("filters", "")

        src = None
        extra_filters = ""

        if stype == "noise_burst":
            color = cue.get("color", "white")
            src = f"anoisesrc=d={dur}:c={color}:a=0.5"

        elif stype == "tone":
            src = f"sine=frequency={freq}:duration={dur}"

        elif stype == "sweep":
            freq_end = cue.get("freq_end", freq // 2)
            src = (f"aevalsrc='sin(2*PI*({freq}+({freq_end}-{freq})*t/{dur})*t)'"
                   f":d={dur}:s=44100")

        elif stype == "impact":
            # Low thump + noise transient
            src = (f"aevalsrc='(sin(2*PI*{freq}*t)*exp(-t*8)"
                   f"+random(0)*exp(-t*20)*0.5)':d={dur}:s=44100")

        elif stype == "glitch":
            # Rapid random frequency bursts
            src = (f"aevalsrc='sin(2*PI*(200+800*random(0))*t)"
                   f"*(mod(t*20\\,1)<0.3)':d={dur}:s=44100")

        elif stype == "whoosh":
            # Filtered noise sweep for transitions
            src = f"anoisesrc=d={dur}:c=pink:a=0.4"
            center = cue.get("freq", 1000)
            extra_filters = f"bandpass=f={center}:width_type=h:w=500"

        elif stype == "heartbeat":
            # Double thump
            gap = 0.15
            src = (f"aevalsrc='(sin(2*PI*50*t)*exp(-t*10)"
                   f"+sin(2*PI*50*(t-{gap}))*exp(-(t-{gap})*10)"
                   f"*(t>{gap}))':d={dur}:s=44100")

        elif stype == "typing":
            # Rapid clicks
            rate = cue.get("rate", 8)
            src = (f"aevalsrc='(mod(t*{rate}\\,1)<0.05)"
                   f"*sin(2*PI*4000*t)*exp(-mod(t*{rate}\\,1)*100)"
                   f"':d={dur}:s=44100")

        elif stype == "power_up":
            src = (f"aevalsrc='sin(2*PI*({freq}*pow(2\\,t/{dur}*2))*t)"
                   f"*0.5':d={dur}:s=44100")

        elif stype == "power_down":
            src = (f"aevalsrc='sin(2*PI*({freq}*pow(2\\,(1-t/{dur})*2))*t)"
                   f"*0.5':d={dur}:s=44100")

        else:
            continue

        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", src]
        all_filters = ",".join(f for f in [extra_filters, filters] if f)
        if all_filters:
            cmd += ["-af", all_filters]
        cmd += ["-ar", "44100", "-ac", "2", str(path)]

        print(f"  Generating SFX: {name} ({stype})...")
        subprocess.run(cmd, capture_output=True)
        if path.exists():
            result[name] = path

    progress.mark_done(step_key)
    return result


def build_audio(tts_clips, total_duration, audio_dir, progress,
                music_track=None, sfx_timeline=None,
                tts_effects=None, step_key="audio",
                music_gap=None, tts_positions=None,
                music_start_offset=0.0):
    """
    Assemble final audio track.

    tts_effects: optional list of effect names per TTS clip.
        Values: "normal", "echo", "fast", "slow", "deep", "high",
                "whisper", "stutter", "telephone", "reverse", "chorus"
        If None, uses a sensible default sequence (reverse is rare).
    """
    audio_dir = Path(audio_dir)
    final_audio = audio_dir / "final_audio.wav"

    if progress.is_done(step_key) and final_audio.exists():
        print(f"  [cached] Final audio mix")
        return final_audio

    # Default effects: reverse is rare, used only at specific dramatic moments
    if tts_effects is None:
        tts_effects = [
            "normal", "echo", "fast", "normal", "whisper", "telephone",
            "normal", "chorus", "slow", "normal", "stutter", "normal",
        ]

    processed_clips = []   # sequential mode: ordered list for concat
    positional_clips = {}  # positional mode: {clip_index: proc_path}

    for i, (clip_path, text) in enumerate(tts_clips):
        if not clip_path.exists():
            continue

        out_path = audio_dir / f"proc_{i}.wav"
        if not out_path.exists():
            effect = tts_effects[i % len(tts_effects)]
            filters = []

            if effect == "reverse":
                filters.append("areverse")
            elif effect == "fast":
                filters.append("atempo=1.4")
            elif effect == "slow":
                filters.append("atempo=0.8")
            elif effect == "stutter":
                filters.append("atrim=0:0.4,aloop=3:17640")
            elif effect == "echo":
                filters.append("aecho=0.8:0.88:60:0.4")
            elif effect == "deep":
                filters.append("asetrate=44100*0.7,aresample=44100")
            elif effect == "high":
                filters.append("asetrate=44100*1.3,aresample=44100")
            elif effect == "whisper":
                filters.append("highpass=f=300,aecho=0.6:0.3:40:0.3,volume=1.8")
            elif effect == "telephone":
                filters.append("highpass=f=300,lowpass=f=3400,volume=1.5")
            elif effect == "chorus":
                filters.append("chorus=0.5:0.9:50|60:0.4|0.32:0.25|0.4:2|2.3")
            # "normal" = no effect

            # Subtle per-clip variation (less aggressive than before)
            if i % 5 == 0 and effect == "normal":
                filters.append("highpass=f=100")

            # Loudness normalization — ensures no clip is too quiet
            filters.append("loudnorm=I=-18:TP=-1.5:LRA=11")
            filter_str = ",".join(filters)
            subprocess.run([
                "ffmpeg", "-y", "-i", str(clip_path),
                "-af", filter_str, "-ar", "44100", "-ac", "2",
                str(out_path)
            ], capture_output=True)

        if out_path.exists():
            if tts_positions is not None:
                # Positional mode: track by index, no gaps needed
                positional_clips[i] = out_path
            else:
                processed_clips.append(out_path)

                # Gaps between clips — much larger when music is driving the track
                gap_path = audio_dir / f"gap_{i}.wav"
                if not gap_path.exists():
                    if music_gap is not None:
                        # With music: spread TTS out so the song has breathing room
                        import random as _random
                        gap_dur = music_gap + _random.uniform(-0.3, 0.8)
                        gap_dur = max(0.5, gap_dur)
                        subprocess.run([
                            "ffmpeg", "-y", "-f", "lavfi", "-i",
                            "anullsrc=r=44100:cl=stereo",
                            "-t", str(gap_dur), str(gap_path)
                        ], capture_output=True)
                    elif i % 2 == 0:
                        gap_dur = 0.15 + (i % 3) * 0.1
                        if i % 4 == 0:
                            subprocess.run([
                                "ffmpeg", "-y", "-f", "lavfi", "-i",
                                f"anoisesrc=d={gap_dur}:c=pink:a=0.02",
                                "-ar", "44100", "-ac", "2", str(gap_path)
                            ], capture_output=True)
                        else:
                            subprocess.run([
                                "ffmpeg", "-y", "-f", "lavfi", "-i",
                                "anullsrc=r=44100:cl=stereo",
                                "-t", str(gap_dur), str(gap_path)
                            ], capture_output=True)
                if gap_path.exists():
                    processed_clips.append(gap_path)

    # Concat TTS clips (sequential mode only)
    raw_audio = audio_dir / "raw_combined.wav"
    if tts_positions is None and processed_clips:
        parts_file = audio_dir / "parts.txt"
        with open(parts_file, "w") as f:
            for clip in processed_clips:
                f.write(f"file '{clip}'\n")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(parts_file), "-c", "copy", str(raw_audio)
        ], capture_output=True)

    # Build the final mix
    inputs = []
    filter_parts = []
    input_idx = 0
    mix_inputs = []

    if tts_positions is not None:
        # Positional mode: each TTS clip gets its own adelay-placed input
        for clip_idx in sorted(positional_clips):
            proc_path = positional_clips[clip_idx]
            pos_secs = tts_positions.get(clip_idx, 0.0)
            delay_ms = int(pos_secs * 1000)
            label = f"speech{clip_idx}"
            inputs += ["-i", str(proc_path)]
            filter_parts.append(
                f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},"
                f"apad=whole_dur={total_duration}[{label}]"
            )
            input_idx += 1
            mix_inputs.append(f"[{label}]")
    elif raw_audio.exists():
        inputs += ["-i", str(raw_audio)]
        filter_parts.append(
            f"[{input_idx}:a]apad=whole_dur={total_duration},"
            f"atrim=0:{total_duration}[speech]"
        )
        input_idx += 1
        mix_inputs.append("[speech]")

    if music_track and Path(music_track).exists():
        inputs += ["-i", str(music_track)]
        if music_start_offset > 0:
            delay_ms = int(music_start_offset * 1000)
            filter_parts.append(
                f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},"
                f"apad=whole_dur={total_duration}[music]"
            )
        else:
            filter_parts.append(
                f"[{input_idx}:a]atrim=0:{total_duration},"
                f"apad=whole_dur={total_duration}[music]"
            )
        input_idx += 1
        mix_inputs.append("[music]")

    if sfx_timeline:
        for si, (timestamp, sfx_path) in enumerate(sfx_timeline):
            if not Path(sfx_path).exists():
                continue
            inputs += ["-i", str(sfx_path)]
            delay_ms = int(timestamp * 1000)
            filter_parts.append(
                f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},"
                f"apad=whole_dur={total_duration}[sfx{si}]"
            )
            input_idx += 1
            mix_inputs.append(f"[sfx{si}]")

    if not mix_inputs:
        print("  No audio sources, generating noise-only track...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            f"anoisesrc=d={total_duration}:c=pink:a=0.015",
            "-af", "lowpass=f=400,highpass=f=40",
            "-ar", "44100", "-ac", "2", str(final_audio)
        ], capture_output=True)
        progress.mark_done(step_key)
        return final_audio

    n_inputs = len(mix_inputs)
    mix_labels = "".join(mix_inputs)
    filter_parts.append(
        f"{mix_labels}amix=inputs={n_inputs}:duration=longest[out]"
    )
    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[out]", "-ar", "44100", "-ac", "2",
        str(final_audio)
    ]
    subprocess.run(cmd, capture_output=True)

    if not final_audio.exists():
        if raw_audio.exists():
            shutil.copy(raw_audio, final_audio)
        elif music_track and Path(music_track).exists():
            shutil.copy(music_track, final_audio)

    progress.mark_done(step_key)
    return final_audio

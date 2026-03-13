"""Frame rendering pipeline and ffmpeg video encoding."""

import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def load_and_resize(path, size=(1280, 720)):
    """Load image/gif frame and resize to target dimensions."""
    try:
        img = Image.open(path).convert("RGB")
        src_ratio = img.width / img.height
        dst_ratio = size[0] / size[1]
        if src_ratio > dst_ratio:
            new_w = int(img.height * dst_ratio)
            left = (img.width - new_w) // 2
            img = img.crop((left, 0, left + new_w, img.height))
        else:
            new_h = int(img.width / dst_ratio)
            top = (img.height - new_h) // 2
            img = img.crop((0, top, img.width, top + new_h))
        return img.resize(size, Image.LANCZOS)
    except Exception:
        return Image.new("RGB", size, (0, 0, 0))


def generate_static_frame(width=1280, height=720):
    """Generate a frame of pure TV static."""
    noise = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(noise)


def generate_solid_color_frame(width=1280, height=720, color=None):
    """Generate a solid color frame."""
    if color is None:
        color = random.choice([
            (255, 0, 0), (0, 0, 255), (255, 0, 255),
            (0, 255, 0), (0, 0, 0), (255, 255, 255),
        ])
    return Image.new("RGB", (width, height), color)


def generate_token_rain_frame(t, width=1280, height=720, tokens=None):
    """Matrix-style rain with tokens/words."""
    if tokens is None:
        tokens = [
            "the", "of", "and", "to", "in", "is", "it", "for", "that", "was",
            "<PAD>", "<EOS>", "<UNK>", "[MASK]", "\\n", "0.9713", "softmax",
            "attention", "token", "embed", "layer", "weight", "bias", "gradient",
            "loss", "epoch", "batch", "tensor", "float16", "RLHF", "\\t",
            "helpful", "harmless", "honest", "I", "cannot", "assist", "with",
            "As an AI", "language", "model", "However", "I'd be happy to",
            "Sure!", "I think", "delve", "Therefore", "Furthermore",
        ]

    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    random.seed(42)
    columns = [(random.randint(0, width - 60), random.uniform(0, 10))
               for _ in range(40)]
    random.seed()

    for col_x, phase in columns:
        speed = random.uniform(80, 200)
        for row in range(25):
            y = int((t * speed + row * 30 + phase * 100) % (height + 200)) - 100
            if 0 <= y < height:
                token = random.choice(tokens)
                green = max(0, 255 - row * 10)
                color = (0, green, 0) if row > 0 else (200, 255, 200)
                draw.text((col_x, y), token, fill=color, font=font)
    return img


def render_frames(scenes, fps, frames_dir, progress, step_key="frames"):
    """
    Render all frames. Resumes per-scene.
    scenes: list of (name, duration_secs, gen_func)
    gen_func(frame_num, total_scene_frames) -> PIL.Image
    Returns: (total_duration, total_frames)
    """
    frames_dir = Path(frames_dir)
    total_duration = sum(dur for _, dur, _ in scenes)
    total_frames = int(total_duration * fps)

    if progress.is_done(step_key):
        existing = len(list(frames_dir.glob("frame_*.png")))
        if existing >= total_frames:
            print(f"  [cached] All {existing} frames")
            return total_duration, total_frames

    print(f"  Total: {total_duration:.1f}s ({total_frames} frames)")

    frame_idx = 0
    for scene_name, duration, gen_func in scenes:
        scene_frames = int(duration * fps)

        # Check cached frames for this scene
        already = 0
        for f in range(scene_frames):
            if (frames_dir / f"frame_{frame_idx + f:05d}.png").exists():
                already += 1
            else:
                break

        if already == scene_frames:
            print(f"  [cached] Scene '{scene_name}' ({scene_frames} frames)")
            frame_idx += scene_frames
            continue

        frame_idx += already
        print(f"  Rendering '{scene_name}' (from {already}/{scene_frames})...")

        for f in range(already, scene_frames):
            img = gen_func(f, scene_frames)
            w, h = img.size
            target_w = int(total_duration * 0 + 1280)  # get from first scene? use img size
            # Just ensure RGB
            img = img.convert("RGB")
            img.save(frames_dir / f"frame_{frame_idx:05d}.png")
            frame_idx += 1
            if frame_idx % 50 == 0:
                print(f"    {frame_idx}/{total_frames} frames...")

    print(f"  Done! {frame_idx} frames rendered.")
    progress.mark_done(step_key)
    return total_duration, total_frames


def encode_video(frames_dir, audio_path, output_path, fps):
    """Encode frames + audio into final MP4 with ffmpeg."""
    frames_dir = Path(frames_dir)
    audio_path = Path(audio_path) if audio_path else None
    output_path = Path(output_path)

    print(f"\n  Encoding video -> {output_path}...")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%05d.png"),
    ]

    if audio_path and audio_path.exists():
        cmd += ["-i", str(audio_path)]

    cmd += [
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
    ]

    if audio_path and audio_path.exists():
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]

    cmd += ["-movflags", "+faststart", str(output_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FFmpeg error:\n{result.stderr[-500:]}")
        return False

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Output: {size_mb:.1f}MB")
    return True

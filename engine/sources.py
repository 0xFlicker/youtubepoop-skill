"""
Generative video sources — ffmpeg lavfi and Python canvas generators.
These produce frames procedurally without external assets.
"""

import math
import random
import subprocess
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ── FFmpeg lavfi sources (rendered to temp PNGs) ────────────────────────────

def ffmpeg_mandelbrot_frame(t, width=1280, height=720, max_iter=80):
    """Render a mandelbrot zoom frame via ffmpeg lavfi."""
    # Zoom into an interesting region over time
    zoom_rate = 1.0 + t * 0.5
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"mandelbrot=size={width}x{height}:maxiter={max_iter}"
        f":start_scale={3.0/zoom_rate}:start_x=-0.743643:start_y=0.131826",
        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode == 0 and len(r.stdout) == width * height * 3:
        arr = np.frombuffer(r.stdout, dtype=np.uint8).reshape((height, width, 3))
        return Image.fromarray(arr)
    return Image.new("RGB", (width, height), (0, 0, 0))


def ffmpeg_life_frame(frame_num, width=1280, height=720, rule="S23/B3", fill_ratio=0.3):
    """Render a Game of Life frame via ffmpeg lavfi."""
    # Generate a specific frame by seeking
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"life=size={width}x{height}:rule={rule}:random_fill_ratio={fill_ratio}"
        f":stitch=1:mold=10:life_color=white:death_color=#001100:mold_color=#00FF44",
        "-vf", f"select=eq(n\\,{frame_num})",
        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=10)
    if r.returncode == 0 and len(r.stdout) == width * height * 3:
        arr = np.frombuffer(r.stdout, dtype=np.uint8).reshape((height, width, 3))
        return Image.fromarray(arr)
    return Image.new("RGB", (width, height), (0, 20, 0))


def ffmpeg_gradient_frame(width=1280, height=720,
                          c0="random", c1="random", duration=1, t=0):
    """Render a color gradient frame."""
    if c0 == "random":
        c0 = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    if c1 == "random":
        c1 = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    speed = max(1, int(t * 10))
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"gradients=size={width}x{height}:c0={c0}:c1={c1}"
        f":speed={speed}:duration=0.1",
        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=5)
    if r.returncode == 0 and len(r.stdout) == width * height * 3:
        arr = np.frombuffer(r.stdout, dtype=np.uint8).reshape((height, width, 3))
        return Image.fromarray(arr)
    return Image.new("RGB", (width, height), (0, 0, 0))


def ffmpeg_test_pattern(width=1280, height=720, pattern="testsrc2"):
    """Generate a test pattern frame (testsrc, testsrc2, smptebars, etc)."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"{pattern}=size={width}x{height}:duration=0.1",
        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=5)
    if r.returncode == 0 and len(r.stdout) == width * height * 3:
        arr = np.frombuffer(r.stdout, dtype=np.uint8).reshape((height, width, 3))
        return Image.fromarray(arr)
    return Image.new("RGB", (width, height), (128, 128, 128))


# ── Python generative canvas sources ───────────────────────────────────────

def gen_plasma(t, width=1280, height=720, palette="vaporwave"):
    """Generate a plasma/lava lamp frame using sine interference."""
    x = np.linspace(0, 4 * math.pi, width)
    y = np.linspace(0, 4 * math.pi, height)
    xx, yy = np.meshgrid(x, y)

    v1 = np.sin(xx + t * 2)
    v2 = np.sin(yy + t * 1.5)
    v3 = np.sin(xx + yy + t * 3)
    v4 = np.sin(np.sqrt(xx**2 + yy**2 + 1) + t * 2.5)
    v = (v1 + v2 + v3 + v4) / 4.0  # -1 to 1

    norm = ((v + 1) / 2 * 255).astype(np.uint8)

    arr = np.zeros((height, width, 3), dtype=np.uint8)
    if palette == "vaporwave":
        arr[:, :, 0] = norm
        arr[:, :, 1] = ((np.sin(v * math.pi) + 1) / 2 * 180).astype(np.uint8)
        arr[:, :, 2] = (255 - norm)
    elif palette == "fire":
        arr[:, :, 0] = np.minimum(255, norm * 2)
        arr[:, :, 1] = np.maximum(0, norm - 80)
        arr[:, :, 2] = np.maximum(0, norm - 200)
    elif palette == "matrix":
        arr[:, :, 0] = 0
        arr[:, :, 1] = norm
        arr[:, :, 2] = norm // 4
    elif palette == "ocean":
        arr[:, :, 0] = norm // 4
        arr[:, :, 1] = norm // 2
        arr[:, :, 2] = norm
    else:
        arr[:, :, 0] = norm
        arr[:, :, 1] = norm
        arr[:, :, 2] = norm

    return Image.fromarray(arr)


def gen_voronoi(t, width=1280, height=720, n_points=20, palette="neon"):
    """Generate a Voronoi diagram frame with moving points."""
    random.seed(42)
    base_points = [(random.random(), random.random()) for _ in range(n_points)]
    random.seed()

    # Animate points
    points = []
    for i, (bx, by) in enumerate(base_points):
        px = (bx + 0.1 * math.sin(t * 2 + i * 1.3)) % 1.0
        py = (by + 0.1 * math.cos(t * 1.7 + i * 0.9)) % 1.0
        points.append((int(px * width), int(py * height)))

    # Build distance field
    yy, xx = np.mgrid[0:height, 0:width]
    min_dist = np.full((height, width), 1e9)
    min_idx = np.zeros((height, width), dtype=np.int32)

    for i, (px, py) in enumerate(points):
        dist = (xx - px) ** 2 + (yy - py) ** 2
        mask = dist < min_dist
        min_dist[mask] = dist[mask]
        min_idx[mask] = i

    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(n_points):
        mask = min_idx == i
        if palette == "neon":
            hue = (i / n_points + t * 0.1) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 0.8)
            arr[mask] = [int(r * 255), int(g * 255), int(b * 255)]
        elif palette == "dark":
            v = ((i * 37) % 100 + 30)
            arr[mask] = [v, v // 2, v * 2 % 256]

    # Draw cell borders
    edge_x = np.abs(np.diff(min_idx, axis=1, prepend=min_idx[:, :1]))
    edge_y = np.abs(np.diff(min_idx, axis=0, prepend=min_idx[:1, :]))
    edges = (edge_x > 0) | (edge_y > 0)
    arr[edges] = [255, 255, 255]

    return Image.fromarray(arr)


def gen_oscilloscope(t, width=1280, height=720, waves=None):
    """Generate an oscilloscope-like display with multiple waveforms."""
    img = Image.new("RGB", (width, height), (0, 5, 0))
    draw = ImageDraw.Draw(img)

    # Grid
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(0, 30, 0))
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(0, 30, 0))

    if waves is None:
        waves = [
            {"freq": 2, "amp": 0.3, "color": (0, 255, 0), "phase_speed": 3},
            {"freq": 5, "amp": 0.15, "color": (0, 200, 255), "phase_speed": 5},
            {"freq": 0.5, "amp": 0.4, "color": (255, 100, 0), "phase_speed": 1},
        ]

    for wave in waves:
        freq = wave["freq"]
        amp = wave["amp"]
        color = wave["color"]
        ps = wave.get("phase_speed", 3)
        points = []
        for x in range(width):
            nx = x / width * freq * 2 * math.pi
            y = height // 2 + int(amp * height * math.sin(nx + t * ps))
            y += int(amp * height * 0.3 * math.sin(nx * 3 + t * ps * 2))
            points.append((x, max(0, min(height - 1, y))))
        if len(points) > 1:
            draw.line(points, fill=color, width=2)

    return img


def gen_particle_field(t, width=1280, height=720, n_particles=200,
                       color=(0, 255, 100), bg=(0, 0, 0)):
    """Generate a field of particles drifting with subtle attraction."""
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    random.seed(99)
    particles = [(random.random(), random.random(), random.uniform(1, 4))
                 for _ in range(n_particles)]
    random.seed()

    cx, cy = 0.5 + 0.2 * math.sin(t), 0.5 + 0.2 * math.cos(t * 0.7)

    for bx, by, size in particles:
        # Drift toward center with orbital motion
        dx = cx - bx
        dy = cy - by
        dist = math.sqrt(dx*dx + dy*dy) + 0.01
        angle = math.atan2(dy, dx) + math.pi / 3  # orbital offset
        speed = 0.05 / dist

        px = (bx + math.cos(angle) * speed * t) % 1.0
        py = (by + math.sin(angle) * speed * t) % 1.0

        sx = int(px * width)
        sy = int(py * height)
        brightness = max(0.3, 1.0 - dist)
        c = tuple(int(v * brightness) for v in color)
        r = int(size * brightness)
        draw.ellipse([(sx-r, sy-r), (sx+r, sy+r)], fill=c)

    return img


def gen_circuit_board(t, width=1280, height=720, density=15):
    """Generate an animated circuit board / PCB trace pattern."""
    img = Image.new("RGB", (width, height), (0, 15, 5))
    draw = ImageDraw.Draw(img)

    cell_w = width // density
    cell_h = height // density

    random.seed(42)
    for cy in range(density + 1):
        for cx in range(density + 1):
            x = cx * cell_w
            y = cy * cell_h

            # Deterministic pattern based on position
            pattern = (cx * 7 + cy * 13) % 8

            brightness = int(40 + 30 * math.sin(t * 2 + cx * 0.5 + cy * 0.3))
            color = (0, brightness + 40, brightness // 2)
            active_color = (0, 255, 100)

            # Pulse activation wave
            dist_from_wave = abs((cx + cy) - int(t * 8) % (density * 2))
            is_active = dist_from_wave < 3

            c = active_color if is_active else color
            w_line = 2 if is_active else 1

            if pattern < 2:  # Horizontal trace
                draw.line([(x, y + cell_h//2), (x + cell_w, y + cell_h//2)],
                          fill=c, width=w_line)
            elif pattern < 4:  # Vertical trace
                draw.line([(x + cell_w//2, y), (x + cell_w//2, y + cell_h)],
                          fill=c, width=w_line)
            elif pattern < 6:  # Corner
                draw.line([(x, y + cell_h//2), (x + cell_w//2, y + cell_h//2)],
                          fill=c, width=w_line)
                draw.line([(x + cell_w//2, y + cell_h//2), (x + cell_w//2, y + cell_h)],
                          fill=c, width=w_line)
            # Node dots
            if pattern % 3 == 0:
                r = 4 if is_active else 2
                draw.ellipse([(x + cell_w//2 - r, y + cell_h//2 - r),
                              (x + cell_w//2 + r, y + cell_h//2 + r)],
                             fill=c)
    random.seed()

    return img


def gen_heartbeat_monitor(t, width=1280, height=720, bpm=72, color=(0, 255, 0)):
    """Generate a heart rate monitor display."""
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Grid
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(0, 25, 0))
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(0, 25, 0))

    # ECG waveform
    baseline_y = height // 2
    points = []
    beat_period = 60.0 / bpm  # seconds per beat
    pixels_per_sec = width / 4  # 4 seconds visible

    for x in range(width):
        time_at_x = (x / pixels_per_sec + t) % (beat_period * 4)
        phase = (time_at_x % beat_period) / beat_period

        # ECG shape
        if 0.1 < phase < 0.15:  # P wave
            y_off = -20 * math.sin((phase - 0.1) / 0.05 * math.pi)
        elif 0.2 < phase < 0.22:  # Q dip
            y_off = 15
        elif 0.22 < phase < 0.28:  # R spike
            y_off = -180 * math.sin((phase - 0.22) / 0.06 * math.pi)
        elif 0.28 < phase < 0.32:  # S dip
            y_off = 30
        elif 0.35 < phase < 0.45:  # T wave
            y_off = -40 * math.sin((phase - 0.35) / 0.1 * math.pi)
        else:
            y_off = 0

        points.append((x, baseline_y + int(y_off)))

    if len(points) > 1:
        draw.line(points, fill=color, width=2)

    # BPM display
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text((width - 200, 30), f"BPM: {bpm}", fill=color, font=font)

    return img

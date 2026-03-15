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


# ── Organic / Chaotic generative sources ────────────────────────────────────

# --- Reaction-Diffusion ---

class _RDState:
    """Gray-Scott reaction-diffusion simulation state."""

    def __init__(self, w, h, feed_rate, kill_rate):
        self.U = np.ones((h, w), dtype=np.float64)
        self.V = np.zeros((h, w), dtype=np.float64)
        # Seed a small square of V at center
        ch, cw = h // 2, w // 2
        s = max(2, min(w, h) // 10)
        self.V[ch - s:ch + s, cw - s:cw + s] = 0.5 + 0.1 * np.random.random((2 * s, 2 * s))

_rd_cache = {}

def _rd_laplacian(grid):
    """Compute Laplacian via np.roll (periodic boundaries)."""
    return (np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0)
            + np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1)
            - 4.0 * grid)

def gen_reaction_diffusion(t, width=1280, height=720, feed_rate=0.04,
                           kill_rate=0.06, palette="alien", speed=10,
                           sim_scale=4):
    """Gray-Scott reaction-diffusion — organic evolving spots, stripes, coral."""
    sim_w = width // sim_scale
    sim_h = height // sim_scale
    cache_key = (sim_w, sim_h, feed_rate, kill_rate)

    if cache_key not in _rd_cache:
        _rd_cache[cache_key] = _RDState(sim_w, sim_h, feed_rate, kill_rate)
    state = _rd_cache[cache_key]

    Du, Dv = 0.16, 0.08
    dt = 1.0
    F, k = feed_rate, kill_rate

    for _ in range(speed):
        lu = _rd_laplacian(state.U)
        lv = _rd_laplacian(state.V)
        uvv = state.U * state.V * state.V
        state.U += dt * (Du * lu - uvv + F * (1.0 - state.U))
        state.V += dt * (Dv * lv + uvv - (F + k) * state.V)
        state.U = np.clip(state.U, 0, 1)
        state.V = np.clip(state.V, 0, 1)

    v = state.V
    arr = np.zeros((sim_h, sim_w, 3), dtype=np.uint8)

    if palette == "alien":
        arr[:, :, 0] = (v * 50).astype(np.uint8)
        arr[:, :, 1] = (v * 255).astype(np.uint8)
        arr[:, :, 2] = (v * 200).astype(np.uint8)
    elif palette == "coral":
        arr[:, :, 0] = (v * 255).astype(np.uint8)
        arr[:, :, 1] = (v * 120).astype(np.uint8)
        arr[:, :, 2] = (v * 80).astype(np.uint8)
    elif palette == "void":
        arr[:, :, 0] = (v * 130).astype(np.uint8)
        arr[:, :, 1] = (v * 50).astype(np.uint8)
        arr[:, :, 2] = (v * 255).astype(np.uint8)
    elif palette == "electric":
        arr[:, :, 0] = (v * 255).astype(np.uint8)
        arr[:, :, 1] = (v * 80).astype(np.uint8)
        arr[:, :, 2] = (v * 255).astype(np.uint8)
    else:  # grayscale fallback
        g = (v * 255).astype(np.uint8)
        arr[:, :, 0] = g
        arr[:, :, 1] = g
        arr[:, :, 2] = g

    img = Image.fromarray(arr)
    if sim_scale != 1:
        img = img.resize((width, height), Image.LANCZOS)
    return img


# --- Strange Attractor ---

class _AttractorState:
    """Particle state for strange attractor rendering."""

    def __init__(self, n_points, attractor_type, width, height):
        self.width = width
        self.height = height
        self.attractor_type = attractor_type
        # Initialize particles near attractor center
        if attractor_type == "rossler":
            self.points = np.random.randn(n_points, 3) * 0.5
        elif attractor_type == "aizawa":
            self.points = np.random.randn(n_points, 3) * 0.1
        else:  # lorenz
            self.points = np.random.randn(n_points, 3) * 0.5
            self.points[:, 2] += 25  # near Lorenz center
        self.trail = np.zeros((height, width), dtype=np.float64)

_attractor_cache = {}

def _attractor_derivatives(pts, atype):
    """Compute dx/dt, dy/dt, dz/dt for all particles simultaneously."""
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    if atype == "lorenz":
        sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
    elif atype == "rossler":
        a, b, c = 0.2, 0.2, 5.7
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
    elif atype == "aizawa":
        a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
        dx = (z - b) * x - d * y
        dy = d * x + (z - b) * y
        dz = c + a * z - z ** 3 / 3.0 - (x ** 2 + y ** 2) * (1 + e * z) + f * z * x ** 3
    else:
        dx = dy = dz = np.zeros_like(x)
    return np.column_stack([dx, dy, dz])

def gen_strange_attractor(t, width=1280, height=720, attractor_type="lorenz",
                          n_points=2000, rotation_speed=0.3, color_scheme="default",
                          trail_decay=0.95):
    """Render chaotic strange attractors as luminous particle traces."""
    cache_key = (attractor_type, n_points, width, height)

    if cache_key not in _attractor_cache:
        _attractor_cache[cache_key] = _AttractorState(n_points, attractor_type, width, height)
    state = _attractor_cache[cache_key]

    # Integration substeps
    dt = 0.005
    for _ in range(10):
        deriv = _attractor_derivatives(state.points, attractor_type)
        state.points += deriv * dt

    # Reset escaped particles
    norms = np.linalg.norm(state.points, axis=1)
    escaped = norms > 200
    if np.any(escaped):
        n_esc = escaped.sum()
        if attractor_type == "lorenz":
            state.points[escaped] = np.random.randn(n_esc, 3) * 0.5
            state.points[escaped, 2] += 25
        else:
            state.points[escaped] = np.random.randn(n_esc, 3) * 0.5

    # 3D rotation around Y axis
    angle = rotation_speed * t
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    x_rot = state.points[:, 0] * cos_a + state.points[:, 2] * sin_a
    y_rot = state.points[:, 1]
    z_rot = -state.points[:, 0] * sin_a + state.points[:, 2] * cos_a

    # Perspective projection
    fov = 400.0
    z_offset = 60.0
    denom = z_rot + z_offset
    denom = np.where(np.abs(denom) < 1.0, 1.0, denom)
    sx = (x_rot * fov / denom + width / 2).astype(np.int32)
    sy = (y_rot * fov / denom + height / 2).astype(np.int32)

    # Decay trail
    state.trail *= trail_decay

    # Plot points on trail
    valid = (sx >= 0) & (sx < width) & (sy >= 0) & (sy < height)
    state.trail[sy[valid], sx[valid]] = 1.0

    # Colorize
    trail = np.clip(state.trail, 0, 1)
    arr = np.zeros((height, width, 3), dtype=np.uint8)

    if color_scheme == "fire":
        arr[:, :, 0] = (trail * 255).astype(np.uint8)
        arr[:, :, 1] = (trail ** 2 * 180).astype(np.uint8)
        arr[:, :, 2] = (trail ** 3 * 80).astype(np.uint8)
    elif color_scheme == "neon":
        hue_shift = t * 0.2
        arr[:, :, 0] = (trail * 255 * (0.5 + 0.5 * math.sin(hue_shift))).astype(np.uint8)
        arr[:, :, 1] = (trail * 255 * (0.5 + 0.5 * math.sin(hue_shift + 2.1))).astype(np.uint8)
        arr[:, :, 2] = (trail * 255 * (0.5 + 0.5 * math.sin(hue_shift + 4.2))).astype(np.uint8)
    elif color_scheme == "ice":
        arr[:, :, 0] = (trail ** 3 * 150).astype(np.uint8)
        arr[:, :, 1] = (trail * 230).astype(np.uint8)
        arr[:, :, 2] = (trail * 255).astype(np.uint8)
    else:  # default — white/blue
        arr[:, :, 0] = (trail * 180).astype(np.uint8)
        arr[:, :, 1] = (trail * 200).astype(np.uint8)
        arr[:, :, 2] = (trail * 255).astype(np.uint8)

    return Image.fromarray(arr)


# --- ASCII Matrix ---

_ascii_tile_cache = {}
_ascii_rain_state = {}

def gen_ascii_matrix(t, width=1280, height=720, mode="rain", char_size=14,
                     color="green", density=0.6, speed=1.0):
    """ASCII art renderer — digital rain, static noise, or morphing sine fields."""
    chars = ' .:-=+*#%@'
    n_chars = len(chars)

    cols = width // max(4, char_size)
    rows = height // max(4, char_size)

    # Pre-render character tiles
    cache_key = (char_size, color)
    if cache_key not in _ascii_tile_cache:
        color_map = {
            "green": (0, 255, 65),
            "amber": (255, 176, 0),
            "white": (220, 220, 220),
        }
        base_color = color_map.get(color, (0, 255, 65))
        tiles = {}
        for ch in chars:
            tile = Image.new("RGB", (char_size, char_size), (0, 0, 0))
            d = ImageDraw.Draw(tile)
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                    max(6, char_size - 2))
            except Exception:
                font = ImageFont.load_default()
            d.text((1, 0), ch, fill=base_color, font=font)
            tiles[ch] = tile
        _ascii_tile_cache[cache_key] = tiles

    tiles = _ascii_tile_cache[cache_key]

    # Build character grid
    grid = [[' '] * cols for _ in range(rows)]

    if mode == "rain":
        rain_key = (cols, rows, color)
        if rain_key not in _ascii_rain_state:
            # Initialize column drop positions and speeds
            _ascii_rain_state[rain_key] = {
                'heads': [random.randint(-rows, 0) for _ in range(cols)],
                'speeds': [random.uniform(0.3, 1.5) for _ in range(cols)],
                'last_t': t,
            }
        rs = _ascii_rain_state[rain_key]
        dt = (t - rs['last_t']) * speed * 10
        rs['last_t'] = t

        for c in range(cols):
            rs['heads'][c] += rs['speeds'][c] * dt
            head = int(rs['heads'][c])
            # Reset column when fully off screen
            if head - rows > rows:
                rs['heads'][c] = random.randint(-rows, -1)
                rs['speeds'][c] = random.uniform(0.3, 1.5)
                head = int(rs['heads'][c])
            trail_len = int(rows * density)
            for r in range(rows):
                dist = head - r
                if 0 <= dist < trail_len:
                    brightness = 1.0 - dist / trail_len
                    char_idx = min(n_chars - 1, int(brightness * (n_chars - 1)))
                    if random.random() < 0.1:
                        char_idx = random.randint(0, n_chars - 1)
                    grid[r][c] = chars[char_idx]

    elif mode == "static":
        for r in range(rows):
            for c in range(cols):
                v = (math.sin(r * 0.3 + t * 2) * math.sin(c * 0.4 + t * 1.5)
                     + math.sin((r + c) * 0.2 + t * 3)) / 2.0
                v = (v + 1) / 2
                char_idx = int(v * (n_chars - 1))
                grid[r][c] = chars[max(0, min(n_chars - 1, char_idx))]

    elif mode == "morph":
        for r in range(rows):
            for c in range(cols):
                v = (math.sin(r * 0.15 + t * 1.5) * math.cos(c * 0.2 + t * 2.0)
                     + math.sin(math.sqrt(r * r + c * c) * 0.1 + t * 2.5)) / 2.0
                v = (v + 1) / 2
                char_idx = int(v * (n_chars - 1))
                grid[r][c] = chars[max(0, min(n_chars - 1, char_idx))]

    # Render grid to image using cached tiles
    img = Image.new("RGB", (width, height), (0, 0, 0))

    if color == "rainbow":
        # Rainbow: render per-column with hue-shifted tiles
        for r in range(rows):
            for c in range(cols):
                ch = grid[r][c]
                if ch == ' ':
                    continue
                hue = (c / cols + t * 0.1) % 1.0
                rc, gc, bc = colorsys.hsv_to_rgb(hue, 0.9, 0.9)
                tile = Image.new("RGB", (char_size, char_size), (0, 0, 0))
                d = ImageDraw.Draw(tile)
                try:
                    font = ImageFont.truetype(
                        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                        max(6, char_size - 2))
                except Exception:
                    font = ImageFont.load_default()
                d.text((1, 0), ch, fill=(int(rc * 255), int(gc * 255), int(bc * 255)),
                       font=font)
                img.paste(tile, (c * char_size, r * char_size))
    else:
        # Paste pre-rendered tiles at grid positions
        for r in range(rows):
            for c in range(cols):
                ch = grid[r][c]
                if ch == ' ':
                    continue
                img.paste(tiles[ch], (c * char_size, r * char_size))

    return img

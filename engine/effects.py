"""Visual effects and transitions for YTP-style video generation."""

import math
import random

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw


# ── Core Effects ────────────────────────────────────────────────────────────

def effect_deep_fry(img):
    """Oversaturate, sharpen, add noise."""
    img = ImageEnhance.Color(img).enhance(random.uniform(3, 8))
    img = ImageEnhance.Contrast(img).enhance(random.uniform(2, 5))
    img = ImageEnhance.Sharpness(img).enhance(random.uniform(3, 10))
    arr = np.array(img)
    noise = np.random.randint(-30, 30, arr.shape, dtype=np.int16)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def effect_channel_shift(img):
    """Shift RGB channels apart for glitch look."""
    arr = np.array(img)
    shift_x = random.randint(5, 25)
    shift_y = random.randint(-10, 10)
    result = np.zeros_like(arr)
    result[:, :, 0] = np.roll(arr[:, :, 0], shift_x, axis=1)
    result[:, :, 1] = arr[:, :, 1]
    result[:, :, 2] = np.roll(arr[:, :, 2], -shift_x, axis=1)
    if shift_y:
        result[:, :, 0] = np.roll(result[:, :, 0], shift_y, axis=0)
    return Image.fromarray(result)


def effect_datamosh(img):
    """Simulate datamoshing by corrupting random rectangular regions."""
    arr = np.array(img)
    h, w = arr.shape[:2]
    for _ in range(random.randint(3, 12)):
        bh = random.randint(10, min(150, h - 1))
        bw = random.randint(50, min(400, w - 1))
        by = random.randint(0, h - bh)
        bx = random.randint(0, w - bw)
        shift = random.randint(-100, 100)
        src_x = max(0, min(w - bw, bx + shift))
        arr[by:by+bh, bx:bx+bw] = arr[by:by+bh, src_x:src_x+bw]
    return Image.fromarray(arr)


def effect_scanlines(img):
    """Add VHS-style scanlines."""
    arr = np.array(img)
    arr[::3, :] = arr[::3, :] // 2
    return Image.fromarray(arr)


def effect_invert_glitch(img):
    """Randomly invert a horizontal band."""
    arr = np.array(img)
    h = arr.shape[0]
    y_start = random.randint(0, h // 2)
    y_end = min(h, y_start + random.randint(50, 300))
    arr[y_start:y_end] = 255 - arr[y_start:y_end]
    return Image.fromarray(arr)


def effect_zoom_and_rotate(img, t):
    """Ken Burns on acid."""
    w, h = img.size
    angle = math.sin(t * 3) * 15
    scale = 1.0 + 0.3 * abs(math.sin(t * 2))
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    new_size = (int(w * scale), int(h * scale))
    img = img.resize(new_size, Image.LANCZOS)
    left = (img.width - w) // 2
    top = (img.height - h) // 2
    return img.crop((left, top, left + w, top + h))


def effect_mirror_stretch(img):
    """Mirror half the image for that classic YTP look."""
    arr = np.array(img)
    w = arr.shape[1]
    half = w // 2
    if random.random() > 0.5:
        arr[:, half:] = arr[:, half:0:-1][:, :half]
    else:
        arr[:, :half] = arr[:, -1:half-1:-1][:, :half]
    return Image.fromarray(arr)


def effect_pixel_sort(img):
    """Sort pixels in rows by brightness for glitch art."""
    arr = np.array(img)
    h = arr.shape[0]
    brightness = np.mean(arr, axis=2)
    num_rows = random.randint(20, 100)
    rows = random.sample(range(h), min(num_rows, h))
    for row in rows:
        threshold = random.randint(50, 200)
        mask = brightness[row] > threshold
        indices = np.where(mask)[0]
        if len(indices) > 1:
            sorted_indices = indices[np.argsort(brightness[row, indices])]
            arr[row, indices] = arr[row, sorted_indices]
    return Image.fromarray(arr)


# ── New Effects ─────────────────────────────────────────────────────────────

def effect_vhs_tracking(img):
    """VHS tracking error — horizontal bands shift left/right with noise bars."""
    arr = np.array(img)
    h, w = arr.shape[:2]
    # Pick 2-5 bands to distort
    n_bands = random.randint(2, 5)
    for _ in range(n_bands):
        band_y = random.randint(0, h - 30)
        band_h = random.randint(5, 30)
        shift = random.randint(-80, 80)
        y_end = min(h, band_y + band_h)
        arr[band_y:y_end] = np.roll(arr[band_y:y_end], shift, axis=1)
        # Add noise bar at the edge
        noise_h = random.randint(1, 4)
        ny = min(h, y_end)
        ny_end = min(h, ny + noise_h)
        arr[ny:ny_end] = np.random.randint(0, 256, arr[ny:ny_end].shape, dtype=np.uint8)
    return Image.fromarray(arr)


def effect_chromatic_aberration(img, intensity=1.0):
    """Radial chromatic aberration — channels scale differently from center."""
    arr = np.array(img).astype(np.float32)
    h, w = arr.shape[:2]
    cy, cx = h / 2, w / 2

    result = np.zeros_like(arr)
    for ch, scale in enumerate([1.0 + 0.005 * intensity, 1.0, 1.0 - 0.005 * intensity]):
        yy, xx = np.mgrid[0:h, 0:w]
        src_y = ((yy - cy) / scale + cy).astype(np.int32)
        src_x = ((xx - cx) / scale + cx).astype(np.int32)
        src_y = np.clip(src_y, 0, h - 1)
        src_x = np.clip(src_x, 0, w - 1)
        result[:, :, ch] = arr[src_y, src_x, ch]

    return Image.fromarray(result.astype(np.uint8))


def effect_posterize(img, levels=4):
    """Reduce color depth for a posterized/retro look."""
    arr = np.array(img)
    factor = 256 // levels
    arr = (arr // factor) * factor
    return Image.fromarray(arr)


def effect_wave_distort(img, t=0, amplitude=15, frequency=0.02):
    """Sinusoidal wave distortion — rows shift by a sine wave."""
    arr = np.array(img)
    h, w = arr.shape[:2]
    result = np.zeros_like(arr)
    for y in range(h):
        shift = int(amplitude * math.sin(2 * math.pi * frequency * y + t * 5))
        result[y] = np.roll(arr[y], shift, axis=0)
    return Image.fromarray(result)


def effect_glitch_blocks(img, n_blocks=8):
    """Random rectangular blocks get displaced, recolored, or duplicated."""
    arr = np.array(img)
    h, w = arr.shape[:2]
    for _ in range(n_blocks):
        bh = random.randint(10, h // 4)
        bw = random.randint(20, w // 3)
        by = random.randint(0, h - bh)
        bx = random.randint(0, w - bw)
        block = arr[by:by+bh, bx:bx+bw].copy()

        op = random.choice(["displace", "recolor", "duplicate", "invert"])
        if op == "displace":
            dy = random.randint(0, h - bh)
            dx = random.randint(0, w - bw)
            arr[dy:dy+bh, dx:dx+bw] = block
        elif op == "recolor":
            ch = random.randint(0, 2)
            arr[by:by+bh, bx:bx+bw, ch] = 255 - block[:, :, ch]
        elif op == "duplicate":
            for rep in range(random.randint(2, 4)):
                dy = min(h - bh, by + bh * rep)
                arr[dy:dy+bh, bx:bx+bw] = block
        elif op == "invert":
            arr[by:by+bh, bx:bx+bw] = 255 - block

    return Image.fromarray(arr)


def effect_bit_crush(img, bits=3):
    """Reduce bit depth per channel for a crunchy digital look."""
    arr = np.array(img)
    shift = 8 - bits
    arr = (arr >> shift) << shift
    return Image.fromarray(arr)


def effect_feedback_loop(img, t=0, decay=0.7, offset=(10, 10)):
    """Simulate video feedback — blend offset copies on top of each other."""
    arr = np.array(img).astype(np.float32)
    h, w = arr.shape[:2]
    result = arr.copy()
    for i in range(3):
        dx = offset[0] * (i + 1)
        dy = offset[1] * (i + 1)
        shifted = np.roll(np.roll(arr, dx, axis=1), dy, axis=0)
        alpha = decay ** (i + 1)
        result = result * (1 - alpha * 0.5) + shifted * alpha * 0.5
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


def effect_color_halftone(img, dot_size=6):
    """Simulate CMYK halftone dots."""
    arr = np.array(img)
    h, w = arr.shape[:2]
    result = np.full_like(arr, 255)
    for y in range(0, h, dot_size):
        for x in range(0, w, dot_size):
            block = arr[y:y+dot_size, x:x+dot_size]
            if block.size == 0:
                continue
            avg = block.mean(axis=(0, 1)).astype(np.uint8)
            result[y:y+dot_size, x:x+dot_size] = avg
    return Image.fromarray(result)


def effect_thermal(img):
    """Thermal camera / heat map look."""
    arr = np.array(img).astype(np.float32)
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    norm = gray / 255.0
    result = np.zeros_like(arr)
    # Cold (blue) -> warm (red/yellow) colormap
    result[:, :, 0] = np.clip(norm * 3 * 255, 0, 255)        # R rises fast
    result[:, :, 1] = np.clip((norm - 0.33) * 3 * 255, 0, 255)  # G mid
    result[:, :, 2] = np.clip((0.66 - norm) * 3 * 255, 0, 255)  # B falls
    return Image.fromarray(result.astype(np.uint8))


# ── Transitions ─────────────────────────────────────────────────────────────

def transition_dissolve(img_a, img_b, t):
    """Cross-dissolve between two images. t: 0=all A, 1=all B."""
    return Image.blend(img_a, img_b, min(1.0, max(0.0, t)))


def transition_wipe_horizontal(img_a, img_b, t):
    """Horizontal wipe from left to right."""
    w = img_a.size[0]
    split = int(t * w)
    result = np.array(img_a)
    b_arr = np.array(img_b)
    result[:, :split] = b_arr[:, :split]
    return Image.fromarray(result)


def transition_wipe_vertical(img_a, img_b, t):
    """Vertical wipe from top to bottom."""
    h = img_a.size[1]
    split = int(t * h)
    result = np.array(img_a)
    b_arr = np.array(img_b)
    result[:split, :] = b_arr[:split, :]
    return Image.fromarray(result)


def transition_glitch_cut(img_a, img_b, t):
    """Glitchy transition — random blocks swap between images."""
    arr_a = np.array(img_a)
    arr_b = np.array(img_b)
    h, w = arr_a.shape[:2]
    result = arr_a.copy()
    n_blocks = int(t * 20) + 1
    for _ in range(n_blocks):
        bh = random.randint(20, h // 3)
        bw = random.randint(40, w // 2)
        by = random.randint(0, h - bh)
        bx = random.randint(0, w - bw)
        if random.random() < t:
            result[by:by+bh, bx:bx+bw] = arr_b[by:by+bh, bx:bx+bw]
    return Image.fromarray(result)


def transition_pixel_scatter(img_a, img_b, t):
    """Pixels randomly switch from A to B."""
    arr_a = np.array(img_a)
    arr_b = np.array(img_b)
    mask = np.random.random(arr_a.shape[:2]) < t
    result = arr_a.copy()
    result[mask] = arr_b[mask]
    return Image.fromarray(result)


def transition_zoom_through(img_a, img_b, t):
    """Zoom into A until it dissolves into B."""
    if t < 0.5:
        scale = 1.0 + t * 2
        w, h = img_a.size
        new_size = (int(w * scale), int(h * scale))
        zoomed = img_a.resize(new_size, Image.LANCZOS)
        left = (zoomed.width - w) // 2
        top = (zoomed.height - h) // 2
        return zoomed.crop((left, top, left + w, top + h))
    else:
        return Image.blend(img_a, img_b, (t - 0.5) * 2)

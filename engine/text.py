"""Text overlay styles for YTP video frames."""

import random
from PIL import Image, ImageDraw, ImageFont

# Font paths (Linux/DejaVu)
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def _load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_text_overlay(img, text, style="normal"):
    """Draw text with various YTP styles onto an image."""
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font_size = random.randint(28, 72) if style == "normal" else random.randint(48, 120)
    font = _load_font(FONT_SANS_BOLD, font_size)

    if style == "glitch":
        for _ in range(5):
            x = random.randint(20, w // 3)
            y = random.randint(20, h - 100)
            color = random.choice([
                (255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (255, 0, 255),
            ])
            draw.text((x, y), text, fill=color, font=font)

    elif style == "bottom_text":
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (w - tw) // 2
        y = h - th - 40
        for dx, dy in [(-3,-3),(3,-3),(-3,3),(3,3),(-3,0),(3,0),(0,-3),(0,3)]:
            draw.text((x+dx, y+dy), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

    elif style == "scattered":
        words = text.split()
        for word in words:
            x = random.randint(0, max(1, w - 200))
            y = random.randint(0, max(1, h - 80))
            angle = random.randint(-45, 45)
            color = (random.randint(150, 255), random.randint(0, 255), random.randint(0, 255))
            tmp = Image.new("RGBA", (500, 150), (0, 0, 0, 0))
            tmp_draw = ImageDraw.Draw(tmp)
            tmp_draw.text((10, 10), word, fill=color, font=font)
            tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
            img.paste(tmp, (x, y), tmp)

    elif style == "typewriter":
        font = _load_font(FONT_MONO, 32)
        y = h // 2 - 50
        draw.rectangle([(0, y - 20), (w, y + 80)], fill=(0, 0, 0))
        draw.text((40, y), f"> {text}", fill=(0, 255, 0), font=font)
        bbox = draw.textbbox((40, y), f"> {text}", font=font)
        draw.text((bbox[2] + 5, y), "\u2588", fill=(0, 255, 0), font=font)

    else:  # "normal"
        x = random.randint(50, max(51, w // 2))
        y = random.randint(50, max(51, h - 150))
        draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

    return img

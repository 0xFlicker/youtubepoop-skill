"""External asset acquisition — GIPHY and DALL-E."""

import random
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont


def fetch_giphy_gifs(searches, assets_dir, api_key, progress, step_key="giphy"):
    """Fetch GIFs from GIPHY. Skips already-downloaded files."""
    assets_dir = Path(assets_dir)

    if progress.is_done(step_key):
        print(f"  [cached] GIPHY assets")
        return sorted(assets_dir.glob("giphy_*.gif"))

    for i, query in enumerate(searches):
        for j in range(2):
            path = assets_dir / f"giphy_{i}_{j}.gif"
            if path.exists():
                continue
            print(f"  Fetching GIPHY: '{query}' [{j+1}/2]...")
            try:
                r = requests.get("https://api.giphy.com/v1/gifs/search", params={
                    "api_key": api_key, "q": query, "limit": 3, "rating": "pg-13",
                })
                data = r.json().get("data", [])
                if j < len(data):
                    url = data[j]["images"]["fixed_width"]["url"]
                    img_data = requests.get(url).content
                    path.write_bytes(img_data)
            except Exception as e:
                print(f"    Warning: {e}")

    progress.mark_done(step_key)
    return sorted(assets_dir.glob("giphy_*.gif"))


def generate_dalle_images(prompts, assets_dir, api_key, progress, step_key="dalle"):
    """Generate images with DALL-E. Skips existing images."""
    from openai import OpenAI
    assets_dir = Path(assets_dir)

    if progress.is_done(step_key):
        print(f"  [cached] DALL-E images")
        return sorted(assets_dir.glob("dalle_*.png"))

    client = OpenAI(api_key=api_key)

    for i, prompt in enumerate(prompts):
        path = assets_dir / f"dalle_{i}.png"
        if path.exists():
            print(f"  [cached] DALL-E image {i+1}/{len(prompts)}")
            continue

        print(f"  Generating DALL-E image {i+1}/{len(prompts)}...")
        try:
            response = client.images.generate(
                model="dall-e-3", prompt=prompt,
                size="1024x1024", quality="standard", n=1,
            )
            img_data = requests.get(response.data[0].url).content
            path.write_bytes(img_data)
        except Exception as e:
            print(f"    Warning: {e}")
            img = Image.new("RGB", (1024, 1024),
                            (random.randint(0, 50), 0, random.randint(100, 200)))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            except Exception:
                font = ImageFont.load_default()
            draw.text((100, 450), "[ HALLUCINATION\n  NOT FOUND ]",
                       fill=(255, 0, 100), font=font)
            img.save(path)

    progress.mark_done(step_key)
    return sorted(assets_dir.glob("dalle_*.png"))

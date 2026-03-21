"""External asset acquisition — GIPHY and DALL-E."""

import random
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont


def fetch_giphy_gifs(searches, assets_dir, api_key, progress, step_key="giphy"):
    """Fetch GIFs from GIPHY. Skips already-downloaded files.

    De-duplicates across queries by tracking GIPHY IDs — if a result was
    already downloaded for a previous search, the next unique result from
    the same query is used instead.
    """
    assets_dir = Path(assets_dir)

    if progress.is_done(step_key):
        print(f"  [cached] GIPHY assets")
        return sorted(assets_dir.glob("giphy_*.gif"))

    seen_ids = set()

    for i, query in enumerate(searches):
        for j in range(2):
            path = assets_dir / f"giphy_{i}_{j}.gif"
            if path.exists():
                continue
            print(f"  Fetching GIPHY: '{query}' [{j+1}/2]...")
            try:
                r = requests.get("https://api.giphy.com/v1/gifs/search", params={
                    "api_key": api_key, "q": query, "limit": 10, "rating": "pg-13",
                })
                data = r.json().get("data", [])
                # Pick the first result whose ID we haven't seen
                picked = None
                for item in data:
                    if item["id"] not in seen_ids:
                        picked = item
                        seen_ids.add(item["id"])
                        break
                if picked:
                    url = picked["images"]["fixed_width"]["url"]
                    img_data = requests.get(url).content
                    path.write_bytes(img_data)
                else:
                    print(f"    Warning: no unique results for '{query}'")
            except Exception as e:
                print(f"    Warning: {e}")

    progress.mark_done(step_key)
    return sorted(assets_dir.glob("giphy_*.gif"))


def generate_dalle_images(prompts, assets_dir, api_key, progress, step_key="dalle"):
    """Generate images with Grok Imagine (xAI). Skips existing images."""
    import base64
    assets_dir = Path(assets_dir)

    if progress.is_done(step_key):
        print(f"  [cached] Grok Imagine images")
        return sorted(assets_dir.glob("dalle_*.png"))

    for i, prompt in enumerate(prompts):
        path = assets_dir / f"dalle_{i}.png"
        if path.exists():
            print(f"  [cached] Grok Imagine image {i+1}/{len(prompts)}")
            continue

        print(f"  Generating Grok Imagine image {i+1}/{len(prompts)}...")
        try:
            r = requests.post(
                "https://api.x.ai/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "grok-imagine-image",
                    "prompt": prompt,
                    "n": 1,
                    "aspect_ratio": "1:1",
                    "response_format": "b64_json",
                },
            )
            r.raise_for_status()
            b64_data = r.json()["data"][0]["b64_json"]
            path.write_bytes(base64.b64decode(b64_data))
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

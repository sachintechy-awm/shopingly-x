"""
Generates placeholder product and category images for ShopinglyX using Pillow.

This has ALREADY been run once to produce the images shipped in
store/static/store/images/. You only need to re-run it if you add or change
products in store/product_data.py and want fresh matching images:

    python generate_placeholder_images.py

Requires: pip install Pillow
"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

from store.product_data import CATEGORIES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_DIR = os.path.join(BASE_DIR, "store", "static", "store", "images", "products")
CATEGORIES_DIR = os.path.join(BASE_DIR, "store", "static", "store", "images", "categories")

os.makedirs(PRODUCTS_DIR, exist_ok=True)
os.makedirs(CATEGORIES_DIR, exist_ok=True)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def gradient_background(size, color_start, color_end):
    """Vertical gradient background image."""
    w, h = size
    base = Image.new("RGB", (w, h), color_start)
    top = hex_to_rgb(color_start) if isinstance(color_start, str) else color_start
    bottom = hex_to_rgb(color_end) if isinstance(color_end, str) else color_end
    draw = ImageDraw.Draw(base)
    for y in range(h):
        ratio = y / h
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return base


def get_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_decorative_circles(draw, w, h, color):
    lighter = tuple(min(255, c + 35) for c in color)
    draw.ellipse([w - 160, -80, w + 80, 160], fill=lighter)
    draw.ellipse([-100, h - 140, 140, h + 100], fill=lighter)


def make_product_image(name, color_start, color_end, out_path, size=(600, 600)):
    img = gradient_background(size, color_start, color_end)
    draw = ImageDraw.Draw(img)
    draw_decorative_circles(draw, size[0], size[1], hex_to_rgb(color_start))

    # semi-transparent card in the middle for text contrast
    card_margin = 40
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle(
        [card_margin, size[1] // 2 - 90, size[0] - card_margin, size[1] // 2 + 90],
        radius=24, fill=(255, 255, 255, 40)
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    font = get_font(34)
    wrapped = textwrap.fill(name, width=20)
    lines = wrapped.split("\n")
    line_height = 42
    total_height = line_height * len(lines)
    y = size[1] // 2 - total_height // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (size[0] - text_w) // 2
        draw.text((x, y), line, font=font, fill="white")
        y += line_height

    img.save(out_path, quality=85)


def make_category_image(name, color_start, color_end, out_path, size=(700, 420)):
    img = gradient_background(size, color_start, color_end)
    draw = ImageDraw.Draw(img)
    draw_decorative_circles(draw, size[0], size[1], hex_to_rgb(color_start))

    font = get_font(46)
    bbox = draw.textbbox((0, 0), name, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size[0] - text_w) // 2
    y = (size[1] - text_h) // 2
    draw.text((x, y), name, font=font, fill="white")
    img.save(out_path, quality=85)


def main():
    product_id = 1
    for category in CATEGORIES:
        cat_out = os.path.join(CATEGORIES_DIR, f"{category['slug']}.jpg")
        make_category_image(category["name"], category["color"], category["color_end"], cat_out)
        print(f"Created category image: {cat_out}")

        for product in category["products"]:
            name = product[0]
            out_path = os.path.join(PRODUCTS_DIR, f"product_{product_id}.jpg")
            make_product_image(name, category["color"], category["color_end"], out_path)
            print(f"Created product image {product_id}: {out_path}")
            product_id += 1

    print(f"\nDone. Generated {product_id - 1} product images and {len(CATEGORIES)} category images.")


if __name__ == "__main__":
    main()

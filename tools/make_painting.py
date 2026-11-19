"""Turn a photo into a Terraria painting texture in pixel-art style.

Usually you don't run this directly: build_paintings.py runs it for every
photo in assets/. To try one photo by hand:

    python tools/make_painting.py assets/peron.jpg JuanPeron --focus 0.5,0.28,0.55

Writes, into Content/Paintings/:
    JuanPeron.png       the tile texture (16x16 tiles with 2px gaps)
    JuanPeronItem.png   the inventory icon
and a big preview into tools/previews/JuanPeron_preview.png to check the look.

Needs Pillow:  pip install Pillow
"""

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

# --- Terraria's rules -------------------------------------------------------
TILE = 16        # a tile is 16x16 pixels
GAP = 2          # textures leave a 2px gap between tiles
FAT = 2          # Terraria art uses 2x2 "fat pixels"
FAT_PER_TILE = TILE // FAT   # 8 fat pixels per tile

FRAME_COLOR = (43, 26, 16)   # thin dark-wood frame, 1 fat pixel wide
DEFAULT_SIZE = (3, 4)
DEFAULT_COLORS = 24

ROOT = Path(__file__).resolve().parent.parent   # the mod's folder
OUT = ROOT / "Content" / "Paintings"
PREVIEWS = ROOT / "tools" / "previews"


def parse_size(text):
    """'3x4' -> (3, 4)"""
    match = re.fullmatch(r"\s*(\d)x(\d)\s*", text)
    if not match:
        raise ValueError(f"size must look like 3x4, got {text!r}")
    return int(match[1]), int(match[2])


def parse_focus(text):
    """'0.47,0.32,0.55' -> (0.47, 0.32, 0.55): face center x, center y, crop height."""
    parts = [float(p) for p in text.split(",")]
    if len(parts) != 3 or not all(0 < p <= 1 for p in parts):
        raise ValueError(f"focus must be three numbers between 0 and 1, got {text!r}")
    return tuple(parts)


def crop_to_focus(photo, focus, aspect):
    """Cut out the part of the photo around the face, in the painting's shape.

    focus = (center x, center y, height), each a fraction of the photo.
    Without focus, use the biggest crop of that shape, a bit above center.
    """
    if focus is None:
        return ImageOps.fit(photo, (1000, round(1000 / aspect)), centering=(0.5, 0.3))
    W, H = photo.size
    cx, cy, hf = focus
    h = min(hf * H, H, W / aspect)
    w = h * aspect
    x0 = min(max(cx * W - w / 2, 0), W - w)   # keep the box inside the photo
    y0 = min(max(cy * H - h / 2, 0), H - h)
    return photo.crop((round(x0), round(y0), round(x0 + w), round(y0 + h)))


def pixelate(img, width, height, colors, enhance=True):
    """Shrink to width x height fat pixels with a small palette."""
    # Terraria colors are vivid: boost saturation and contrast a little
    # (skipped for pixel art, which was already boosted)
    if enhance:
        img = ImageEnhance.Color(img).enhance(1.25)
        img = ImageEnhance.Contrast(img).enhance(1.1)

    # Shrink in two steps and sharpen in between, at 4x the final size, so
    # the sharpening works on features the size of a final pixel: eyes,
    # brows, mustaches survive instead of being averaged away
    img = img.resize((width * 4, height * 4), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=2))
    img = img.resize((width, height), Image.LANCZOS)

    # Small palette, no dithering (dither=0: no speckled dots).
    # kmeans=3 refines the palette a few times to fit the picture better.
    img = img.quantize(colors=colors, dither=0, kmeans=3)
    return img.convert("RGB")


def framed(img, width, height, colors, enhance=True):
    """Picture of width x height fat pixels with a 1-fat-pixel frame."""
    art = Image.new("RGB", (width, height))
    art.paste(pixelate(img, width - 2, height - 2, colors, enhance), (1, 1))
    ImageDraw.Draw(art).rectangle([0, 0, width - 1, height - 1], outline=FRAME_COLOR)
    return art


def slice_into_tiles(picture, tiles_w, tiles_h):
    """Cut the picture into 16x16 tiles and space them out with 2px gaps."""
    stride = TILE + GAP
    sheet = Image.new("RGBA", (tiles_w * stride - GAP, tiles_h * stride - GAP))
    for ty in range(tiles_h):
        for tx in range(tiles_w):
            box = (tx * TILE, ty * TILE, (tx + 1) * TILE, (ty + 1) * TILE)
            sheet.paste(picture.crop(box), (tx * stride, ty * stride))
    return sheet


def load_pixel_art(path, tiles_w, tiles_h):
    """Read finished pixel art (e.g. a preview) back at fat-pixel resolution.

    The image must have the painting's shape, at any whole-number scale,
    with every fat pixel a solid square (like the previews this script makes).
    """
    img = Image.open(path).convert("RGB")
    w, h = tiles_w * FAT_PER_TILE, tiles_h * FAT_PER_TILE
    if img.width % w or img.height % h or img.width // w != img.height // h:
        raise ValueError(f"{path.name} is {img.width}x{img.height}; pixel art for a "
                         f"{tiles_w}x{tiles_h} painting must be {w}x{h} times a whole number")
    return img.resize((w, h), Image.NEAREST)


def make_painting(photo_path, name, size=DEFAULT_SIZE, focus=None, colors=DEFAULT_COLORS,
                  pixel_art=False):
    """Convert one photo (or use finished pixel art as-is). Returns the paths it wrote."""
    tiles_w, tiles_h = size
    if pixel_art:
        art = load_pixel_art(Path(photo_path), tiles_w, tiles_h)
        face = art.crop((1, 1, art.width - 1, art.height - 1))  # inside the frame, for the icon
    else:
        photo = ImageOps.exif_transpose(Image.open(photo_path)).convert("RGB")
        face = crop_to_focus(photo, focus, tiles_w / tiles_h)
        art = framed(face, tiles_w * FAT_PER_TILE, tiles_h * FAT_PER_TILE, colors)

    # The painting at fat-pixel resolution, doubled to real pixels
    picture = art.resize((art.width * FAT, art.height * FAT), Image.NEAREST)

    # The inventory icon: same painting, at most 16 fat pixels big
    scale = 16 / max(art.size)
    icon = framed(face, round(art.width * scale), round(art.height * scale), colors,
                  enhance=not pixel_art)
    icon = icon.resize((icon.width * FAT, icon.height * FAT), Image.NEAREST)

    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    tile_png, item_png = OUT / f"{name}.png", OUT / f"{name}Item.png"
    slice_into_tiles(picture, tiles_w, tiles_h).save(tile_png)
    icon.save(item_png)
    preview = PREVIEWS / f"{name}_preview.png"
    picture.resize((picture.width * 4, picture.height * 4), Image.NEAREST).save(preview)
    return tile_png, item_png, preview


def check_name(name):
    """The name becomes a C# class name: letters/digits, starting with a letter."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name):
        raise ValueError(f"name must be one word of plain letters/digits (e.g. JuanPeron), got {name!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("photo", type=Path, help="the photo to convert")
    parser.add_argument("name", help="painting name, one word, e.g. JuanPeron")
    parser.add_argument("--size", default="3x4", help="width x height in tiles (default 3x4)")
    parser.add_argument("--focus", help="face center x,y and crop height as fractions, e.g. 0.5,0.3,0.55")
    parser.add_argument("--colors", type=int, default=DEFAULT_COLORS, help="palette size (default 24)")
    args = parser.parse_args()
    try:
        check_name(args.name)
        size = parse_size(args.size)
        focus = parse_focus(args.focus) if args.focus else None
    except ValueError as err:
        parser.error(str(err))
    for path in make_painting(args.photo, args.name, size, focus, args.colors):
        print(path)


if __name__ == "__main__":
    main()

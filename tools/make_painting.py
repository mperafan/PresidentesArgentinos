"""Turn a photo into a Terraria painting texture in pixel-art style.

Usage:
    python tools/make_painting.py photo.jpg Peron
    python tools/make_painting.py photo.jpg Peron --size 2x3 --colors 20

Writes, into Content/Paintings/:
    Peron.png       the tile texture (16x16 tiles with 2px gaps)
    PeronItem.png   the inventory icon
and a big preview into tools/previews/Peron_preview.png to check the look.

Needs Pillow:  pip install Pillow
"""

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

# --- Terraria's rules -------------------------------------------------------
TILE = 16        # a tile is 16x16 pixels
GAP = 2          # textures leave a 2px gap between tiles
FAT = 2          # Terraria art uses 2x2 "fat pixels"
FAT_PER_TILE = TILE // FAT   # 8 fat pixels per tile

# --- Frame colors (dark wood, like vanilla paintings) -----------------------
OUTLINE = (43, 26, 16)
WOOD = (122, 78, 40)
LIGHT = (168, 112, 58)    # top/left edge: catches the light
SHADOW = (82, 50, 26)     # bottom/right edge: in shadow
FRAME = 2                 # frame thickness in fat pixels

ROOT = Path(__file__).resolve().parent.parent   # the mod's folder


def parse_size(text):
    """'3x3' -> (3, 3)"""
    match = re.fullmatch(r"(\d)x(\d)", text)
    if not match:
        raise argparse.ArgumentTypeError("size must look like 3x3 or 2x3")
    return int(match[1]), int(match[2])


def pixelate(photo, width, height, colors):
    """Shrink the photo to width x height fat pixels with a small palette."""
    # Crop to the right shape. centering=(0.5, 0.3) keeps more of the top,
    # where faces usually are in a portrait.
    img = ImageOps.fit(photo, (width * 8, height * 8), centering=(0.5, 0.3))

    # Terraria colors are vivid: boost saturation and contrast a little
    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Contrast(img).enhance(1.15)

    # Shrink with a smooth filter so each fat pixel is the average of its area
    img = img.resize((width, height), Image.LANCZOS)

    # Reduce to a small palette, without dithering (dither=0: no speckled dots)
    img = img.quantize(colors=colors, dither=0)
    return img.convert("RGB")


def draw_frame(art):
    """Draw a wooden frame with light and shadow around the art (in place)."""
    d = ImageDraw.Draw(art)
    w, h = art.size
    d.rectangle([0, 0, w - 1, h - 1], outline=OUTLINE)            # outer line
    d.rectangle([1, 1, w - 2, h - 2], outline=WOOD)               # wood ring
    d.line([1, 1, w - 2, 1], fill=LIGHT)                          # top
    d.line([1, 1, 1, h - 2], fill=LIGHT)                          # left
    d.line([1, h - 2, w - 2, h - 2], fill=SHADOW)                 # bottom
    d.line([w - 2, 1, w - 2, h - 2], fill=SHADOW)                 # right


def make_art(photo, tiles_w, tiles_h, colors):
    """The whole painting at fat-pixel resolution (1 pixel = 1 fat pixel)."""
    w, h = tiles_w * FAT_PER_TILE, tiles_h * FAT_PER_TILE
    art = Image.new("RGB", (w, h))
    inner = pixelate(photo, w - 2 * FRAME, h - 2 * FRAME, colors)
    art.paste(inner, (FRAME, FRAME))
    draw_frame(art)
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


def make_icon(photo, tiles_w, tiles_h, colors):
    """A small inventory icon: the same painting, at most 16 fat pixels big."""
    scale = 16 / max(tiles_w, tiles_h) / FAT_PER_TILE
    w = round(tiles_w * FAT_PER_TILE * scale)
    h = round(tiles_h * FAT_PER_TILE * scale)
    icon = Image.new("RGB", (w, h))
    icon.paste(pixelate(photo, w - 2, h - 2, colors), (1, 1))
    ImageDraw.Draw(icon).rectangle([0, 0, w - 1, h - 1], outline=WOOD)
    return icon.resize((w * FAT, h * FAT), Image.NEAREST)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("photo", type=Path, help="the photo to convert")
    parser.add_argument("name", help="painting name, one word, e.g. Peron")
    parser.add_argument("--size", type=parse_size, default=(3, 3),
                        help="width x height in tiles (default 3x3)")
    parser.add_argument("--colors", type=int, default=16,
                        help="palette size (default 16)")
    args = parser.parse_args()

    # The name becomes a C# class name, so: letters/digits, starting with a letter
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", args.name):
        parser.error("name must be one word of plain letters/digits, e.g. Peron")

    tiles_w, tiles_h = args.size
    photo = ImageOps.exif_transpose(Image.open(args.photo)).convert("RGB")

    art = make_art(photo, tiles_w, tiles_h, args.colors)
    picture = art.resize((art.width * FAT, art.height * FAT),
                         Image.NEAREST)   # fat pixels -> real pixels

    out = ROOT / "Content" / "Paintings"
    previews = ROOT / "tools" / "previews"
    out.mkdir(parents=True, exist_ok=True)
    previews.mkdir(parents=True, exist_ok=True)

    sheet = slice_into_tiles(picture, tiles_w, tiles_h)
    sheet.save(out / f"{args.name}.png")
    make_icon(photo, tiles_w, tiles_h, args.colors).save(out / f"{args.name}Item.png")
    picture.resize((picture.width * 4, picture.height * 4),
                   Image.NEAREST).save(previews / f"{args.name}_preview.png")

    print(f"{args.name}: {tiles_w}x{tiles_h} tiles, texture {sheet.width}x{sheet.height} px")
    print(f"  {out / (args.name + '.png')}")
    print(f"  {out / (args.name + 'Item.png')}")
    print(f"  preview: {previews / (args.name + '_preview.png')}")


if __name__ == "__main__":
    main()

# Presidentes Argentinos

A tModLoader (Terraria) mod that adds pixel-art portraits of Argentine presidents
as paintings you hang on walls. Each painting has its own recipe at a **Sawmill**.

| Painting | Recipe |
|---|---|
| Alberto Fernández | 10 Wood + 1 Amethyst |
| Cristina Fernández de Kirchner | 10 Wood + 1 Topaz |
| Javier Milei | 10 Wood + 1 Sapphire |
| Mauricio Macri | 10 Wood + 1 Emerald |
| Juan Domingo Perón | 10 Wood + 1 Ruby |
| Julio Argentino Roca | 10 Wood + 1 Diamond |
| Domingo Faustino Sarmiento | 10 Wood + 1 Amber |

("Wood" is any kind of wood.)

## Try it in the game

1. Install **tModLoader** (free on Steam) and the **.NET 8 SDK**.
2. Clone this repo into tModLoader's mod sources folder:
   ```
   cd "%USERPROFILE%\Documents\My Games\Terraria\tModLoader\ModSources"
   git clone https://github.com/mperafan/PresidentesArgentinos.git
   ```
3. In tModLoader: **Workshop → Develop Mods → Build + Reload** next to Presidentes Argentinos.
4. In a world: build a **Sawmill**, then craft a painting and hang it on a background wall.

## Adding a painting

1. Put a photo in `assets/`.
2. Add a line for it to `assets/paintings.txt` (name, face crop, size, recipe; the file explains each column).
   Without a line, it still works with defaults.
3. Run the converter (needs Python and `pip install Pillow`):
   ```
   python tools/build_paintings.py
   ```
   Check the result in `tools/previews/`. Adjust the focus numbers and run again if the face isn't centered.
4. **Build + Reload** in tModLoader.

## How it works

- `tools/make_painting.py` turns one photo into Terraria pixel art: crops to the face,
  shrinks to 2x2 "fat pixels", sharpens, reduces to 24 colors, adds a frame, and cuts
  it into 16x16 tiles with 2px gaps.
- `tools/build_paintings.py` runs that for every photo and generates
  `Content/PaintingList.cs` and the item names in `Localization/`.
- `Content/PaintingTile.cs` and `Content/PaintingItem.cs` are one generic painting;
  `PresidentesArgentinos.cs` creates one of each per entry in the list.

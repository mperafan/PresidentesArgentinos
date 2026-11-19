using System.Linq;
using Microsoft.Xna.Framework;
using Terraria;
using Terraria.DataStructures;
using Terraria.ID;
using Terraria.Localization;
using Terraria.ModLoader;
using Terraria.ObjectData;

namespace PresidentesArgentinos.Content
{
	// The painting hanging on a wall. Set up like Terraria's own paintings.
	[Autoload(false)] // created in PresidentesArgentinos.Load, once per painting
	public class PaintingTile : ModTile
	{
		private readonly PaintingInfo info;

		public PaintingTile(PaintingInfo info) {
			this.info = info;
		}

		// Each instance needs its own name and texture
		public override string Name => info.Name + "Tile";
		public override string Texture => $"PresidentesArgentinos/Content/Paintings/{info.Name}";

		public override void SetStaticDefaults() {
			Main.tileFrameImportant[Type] = true;      // a multi-tile object, not a block
			Main.tileLavaDeath[Type] = true;           // burns in lava, like wood
			TileID.Sets.FramesOnKillWall[Type] = true; // falls if its wall is removed

			// Start from the 3x3 wall-hanging template and resize it
			TileObjectData.newTile.CopyFrom(TileObjectData.Style3x3Wall);
			TileObjectData.newTile.Width = info.Width;
			TileObjectData.newTile.Height = info.Height;
			TileObjectData.newTile.CoordinateHeights = Enumerable.Repeat(16, info.Height).ToArray();
			TileObjectData.newTile.Origin = new Point16((info.Width - 1) / 2, (info.Height - 1) / 2);
			TileObjectData.addTile(Type);

			DustType = DustID.WoodFurniture;
			AddMapEntry(new Color(120, 85, 60), Language.GetText("MapObject.Painting"));
		}
	}
}

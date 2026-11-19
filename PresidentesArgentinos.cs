using PresidentesArgentinos.Content;
using Terraria.ModLoader;

namespace PresidentesArgentinos
{
	public class PresidentesArgentinos : Mod
	{
		// One tile + one item for each painting in the generated PaintingList.
		// They're added by hand (not autoloaded) because they're all the same
		// classes, just with different data.
		public override void Load() {
			foreach (PaintingInfo info in PaintingList.All) {
				AddContent(new PaintingTile(info));
				AddContent(new PaintingItem(info));
			}
		}
	}
}

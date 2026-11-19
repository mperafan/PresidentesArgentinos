using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace PresidentesArgentinos.Content
{
	// The painting in your inventory. Using it places the PaintingTile.
	[Autoload(false)] // created in PresidentesArgentinos.Load, once per painting
	public class PaintingItem : ModItem
	{
		private readonly PaintingInfo info;

		public PaintingItem(PaintingInfo info) {
			this.info = info;
		}

		public override string Name => info.Name;
		public override string Texture => $"PresidentesArgentinos/Content/Paintings/{info.Name}Item";

		// Copies of this item keep their info (tModLoader copies items a lot)
		protected override bool CloneNewInstances => true;

		public override void SetDefaults() {
			Item.DefaultToPlaceableTile(Mod.Find<ModTile>(info.Name + "Tile").Type);
			Item.width = 24;
			Item.height = 32;
			Item.value = Item.buyPrice(silver: 50);
			Item.rare = ItemRarityID.Blue;
		}

		public override void AddRecipes() {
			Recipe recipe = CreateRecipe();
			foreach ((string item, int count) in info.Recipe) {
				if (item == "Wood") {
					recipe.AddRecipeGroup(RecipeGroupID.Wood, count); // any wood
				}
				else if (ItemID.Search.TryGetId(item, out int id)) {
					recipe.AddIngredient(id, count);
				}
				else {
					Mod.Logger.Error($"Painting {info.Name}: unknown item '{item}' in recipe");
				}
			}
			recipe.AddTile(TileID.Sawmill);
			recipe.Register();
		}
	}
}

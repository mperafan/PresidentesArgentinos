using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace PinkBunnyMod.Items
{
	// A starter sword. The texture is the PNG with the same name in this folder.
	public class PinkBunnySword : ModItem
	{
		public override void SetDefaults() {
			Item.damage = 20;
			Item.DamageType = DamageClass.Melee;
			Item.width = 40;
			Item.height = 40;
			Item.useTime = 20;
			Item.useAnimation = 20;
			Item.useStyle = ItemUseStyleID.Swing;
			Item.knockBack = 5;
			Item.value = Item.buyPrice(silver: 50);
			Item.rare = ItemRarityID.Pink;
			Item.UseSound = SoundID.Item1;
			Item.autoReuse = true;
		}

		// Crafted from 10 dirt blocks at a workbench, so it's easy to test
		public override void AddRecipes() {
			Recipe recipe = CreateRecipe();
			recipe.AddIngredient(ItemID.DirtBlock, 10);
			recipe.AddTile(TileID.WorkBenches);
			recipe.Register();
		}
	}
}

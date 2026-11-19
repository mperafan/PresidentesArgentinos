namespace PresidentesArgentinos.Content
{
	// Everything that makes one painting different from another.
	// Recipe: Terraria item names ("Wood" = any wood) and amounts.
	public record PaintingInfo(string Name, int Width, int Height, (string Item, int Count)[] Recipe);
}

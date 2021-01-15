from biome import Biome

biome_lists = []
biome_rarity = []

rocky_dungeon = Biome(
    name="Rocky Dungeon",
    biome_id="rocky_dungeon",
    biome_desc="Desc of rocky dungeon biome (TEST)",
    rarity=1,
    map_width=80,
    map_height=80,
)
biome_lists.append(rocky_dungeon)
biome_rarity.append(rocky_dungeon.rarity)

desert_dungeon = Biome(
    name="Desert Dungeon",
    biome_id="desert_dungeon",
    biome_desc="desert_dungeon (TEST)",
    rarity=1,
    map_width=80,
    map_height=80,
)
biome_lists.append(desert_dungeon)
biome_rarity.append(desert_dungeon.rarity)
from biome import Biome, tileset
import tile_factories
import color

biome_dict = {}
biome_rarity = []

rocky_dungeon = Biome(
    name="돌무더기",
    biome_id="rocky_dungeon",
    biome_desc="Desc of rocky dungeon biome (TEST)",
    rarity=99,
    biome_color=color.b_rocky_dungeon,
    map_width=80,
    map_height=80,
)
biome_dict[rocky_dungeon.biome_id] = rocky_dungeon
biome_rarity.append(rocky_dungeon.rarity)

desert_dungeon = Biome(
    name="사막",
    biome_id="desert_dungeon",
    biome_desc="desert_dungeon (TEST)",
    rarity=1,
    biome_color=color.b_desert_dungeon,
    map_width=80,
    map_height=80,
    tileset=tileset({
        "t_wall":tile_factories.sandstone_wall,
        "t_floor":tile_factories.sand_floor(),
        "t_dense_grass":tile_factories.dense_grass_desert,
        "t_sparse_grass":tile_factories.sparse_grass_desert,
    }),
    terrain = {"trap_field":5,},#TODO
)
biome_dict[desert_dungeon.biome_id] = desert_dungeon
biome_rarity.append(desert_dungeon.rarity)

ancient_ruins = Biome(
    name="고대 유적",
    biome_id="ancient_ruins",
    biome_desc="ancient_ruins (TEST)",
    rarity=0,
    biome_color=color.b_ancient_ruin,
    max_rooms=1,
    map_width=80,
    map_height=80,
    respawn_ratio=0,
    max_monsters_per_room=0,
    max_items_per_room=0,
    tileset=tileset({
        "t_wall":tile_factories.quartz_wall,
        "t_floor":tile_factories.quartz_floor,
    }),
    terrain = {"dungeon_chamber":1},
)
biome_dict[ancient_ruins.biome_id] = ancient_ruins
biome_rarity.append(ancient_ruins.rarity)
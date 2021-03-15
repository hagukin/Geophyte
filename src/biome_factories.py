from biome import Biome, tileset
import tile_types

biome_dict = {}
biome_rarity = []

rocky_dungeon = Biome(
    name="Rocky Dungeon",
    biome_id="rocky_dungeon",
    biome_desc="Desc of rocky dungeon biome (TEST)",
    rarity=1,
    map_width=80,
    map_height=80,
)
biome_dict[rocky_dungeon.biome_id] = rocky_dungeon
biome_rarity.append(rocky_dungeon.rarity)

desert_dungeon = Biome(
    name="Desert Dungeon",
    biome_id="desert_dungeon",
    biome_desc="desert_dungeon (TEST)",
    rarity=1,
    map_width=80,
    map_height=80,
    tileset=tileset({
        "t_wall":tile_types.wall_desert,
        "t_floor":tile_types.floor_desert,
        "t_dense_grass":tile_types.dense_grass_desert,
        "t_sparse_grass":tile_types.sparse_grass_desert,
    }),
    terrain = {"trap_field":5,},#TODO
)
biome_dict[desert_dungeon.biome_id] = desert_dungeon
biome_rarity.append(desert_dungeon.rarity)

ancient_ruins = Biome(
    name="Ancient Ruins",
    biome_id="ancient_ruins",
    biome_desc="ancient_ruins (TEST)",
    rarity=0,
    max_rooms=1,
    map_width=80,
    map_height=80,
    respawn_ratio=0,
    max_monsters_per_room=0,
    max_items_per_room=0,
    tileset=tileset({
        "t_wall":tile_types.wall_ancient_ruins,
        "t_floor":tile_types.floor_ancient_ruins,
    }),
    terrain = {"dungeon_chamber":1},
)
biome_dict[ancient_ruins.biome_id] = ancient_ruins
biome_rarity.append(ancient_ruins.rarity)
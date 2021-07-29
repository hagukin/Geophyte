from biome import Biome, tileset
import tiles
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
        "t_wall":tiles.wall_desert,
        "t_floor":tiles.floor_desert,
        "t_dense_grass":tiles.dense_grass_desert,
        "t_sparse_grass":tiles.sparse_grass_desert,
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
    generate_descending_stair=False,
    tileset=tileset({
        "t_wall":tiles.wall_ancient_ruins,
        "t_floor":tiles.floor_ancient_ruins,
    }),
    terrain = {"chamber_of_kugah":1},
)
biome_dict[ancient_ruins.biome_id] = ancient_ruins
biome_rarity.append(ancient_ruins.rarity)
from biome import Biome, get_tileset
import terrain_factories
import tiles
import copy
import color

biome_dict = {}
biome_rarity = []

rocky_dungeon = Biome(
    name="돌무더기",
    biome_bgm_id="bgm_mystical_beginning",
    biome_id="rocky_dungeon",
    biome_desc="Desc of rocky dungeon biome (TEST)",
    rarity=100,
    biome_color=color.b_rocky_dungeon,
    map_width=67,
    map_height=41,
)
biome_dict[rocky_dungeon.biome_id] = rocky_dungeon
biome_rarity.append(rocky_dungeon.rarity)

def rocky_dungeon_small(max_rooms: int, room_x_spacing: int):
    tmp = copy.deepcopy(rocky_dungeon)
    tmp.max_rooms = max_rooms
    tmp._room_x_spacing = room_x_spacing
    return tmp

crystal_cavern = Biome(
    name="석영 동굴",
    biome_bgm_id="bgm_mystical_beginning",
    biome_id="crystal_cavern",
    biome_desc="Desc of crystal cavern biome (TEST)",
    rarity=30,
    biome_color=color.b_crystal_cavern,
    map_width=67,
    map_height=41,
    tileset=get_tileset({
        "t_wall":tiles.wall_crystal,
        "t_floor":tiles.floor_crystal,
        "t_shallow_water":tiles.shallow_water_crystal,
        "t_deep_water":tiles.deep_water_crystal,
    }),
    remove_all_terrain_of_type=("gen_grass", "gen_plants"),
)
biome_dict[crystal_cavern.biome_id] = crystal_cavern
biome_rarity.append(crystal_cavern.rarity)

forest = Biome(
    name="숲",
    biome_id="forest",
    biome_desc="Desc of forest biome (TEST)",
    rarity=1,
    biome_color=color.b_forest,
    tileset=get_tileset({
        "t_wall":tiles.wall_forest,
        "t_floor":tiles.floor_forest,
        "t_dense_grass":tiles.dense_grass_forest,
        "t_sparse_grass":tiles.sparse_grass_forest,
    }),
    remove_all_terrain_of_type=("spawn_door",), # Remove all terrains that has spawn_door = True.
    #NOTE: You can still add back terrains that spawns door such as shops by adding them in 'additional_terrain' argument.
    additional_terrain=({
        terrain_factories.swamp : 50,
        terrain_factories.ocean : 3,
        terrain_factories.grass_field_spawn_no_door : 80,
        terrain_factories.large_grass_field_spawn_no_door : 80,
        terrain_factories.general_shop : 1,
        terrain_factories.weapon_shop : 1,
        terrain_factories.potion_shop : 1,
        terrain_factories.scroll_shop : 1,
        terrain_factories.guarded_treasure : 1,
        terrain_factories.forest_chamber_spawn_no_door : 130,
    }),
    map_width=80,
    map_height=60,
)
biome_dict[forest.biome_id] = forest
biome_rarity.append(forest.rarity)

#
# orc_town = Biome(
#     name="오크 타운",
#     biome_id="orc_town",
#     biome_desc="Desc of orc_town biome (TEST)",
#     rarity=0,
#     biome_color=color.b_orc_town,
#     tileset=get_tileset({
#         "t_wall":tiles.wall_forest,
#         "t_floor":tiles.floor_forest,
#         "t_dense_grass":tiles.dense_grass_forest,
#         "t_sparse_grass":tiles.sparse_grass_forest,
#     }),
#     remove_all_terrain_of_type=("spawn_door",), # Remove all terrains that has spawn_door = True.
#     #NOTE: You can still add back terrains that spawns door such as shops by adding them in 'additional_terrain' argument.
#     additional_terrain=({
#         terrain_factories.swamp : 50,
#         terrain_factories.ocean : 3,
#         terrain_factories.grass_field_spawn_no_door : 80,
#         terrain_factories.large_grass_field_spawn_no_door : 80,
#         terrain_factories.general_shop : 1,
#         terrain_factories.weapon_shop : 1,
#         terrain_factories.potion_shop : 1,
#         terrain_factories.scroll_shop : 1,
#         terrain_factories.guarded_treasure : 1,
#     }),
#     map_width=80,
#     map_height=60,
# )
# biome_dict[forest.biome_id] = forest
# biome_rarity.append(forest.rarity)


desert_dungeon = Biome(
    name="사막",
    biome_id="desert_dungeon",
    biome_desc="desert_dungeon (TEST)",
    rarity=1,
    biome_color=color.b_desert_dungeon,
    map_width=67,
    map_height=41,
    tileset=get_tileset({
        "t_wall":tiles.wall_desert,
        "t_floor":tiles.floor_desert,
        "t_dense_grass":tiles.dense_grass_desert,
        "t_sparse_grass":tiles.sparse_grass_desert,
    }),
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
    tileset=get_tileset({
        "t_wall":tiles.wall_ancient_ruins,
        "t_floor":tiles.floor_ancient_ruins,
    }),
    terrain = {terrain_factories.chamber_of_kugah:1},
)
biome_dict[ancient_ruins.biome_id] = ancient_ruins
biome_rarity.append(ancient_ruins.rarity)
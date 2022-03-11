from biome import Biome, get_tileset
import terrain_factories
import tiles
import copy
import color
from language import interpret as i

biome_dict = {}
biome_rarity = []

rocky_dungeon = Biome(
    name=i("돌무더기", f"rocky dungeon"),
    biome_bgm_id="bgm_mystical_beginning",
    biome_id="rocky_dungeon",
    biome_desc=i("바위, 함정, 그리고 괴물. 던전이 당신을 반긴다.",
                 "Rocks, traps, and monsters. The dungeon welcomes you."),
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
    name=i("석영 동굴", f"crystal cavern"),
    biome_bgm_id="bgm_mystic_train",
    biome_id="crystal_cavern",
    biome_desc=i("끓어오르는 대지의 열기는 아름다운 석영들을 만들어낸다. 그러나 그 아름다움의 뒷편엔 죽음이 도사리고 있음을 명심해야 한다.",
                 "The heat coming from the core forms a beautiful crystals. But be aware of the death lurking behind the beauty."),
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
    name=i("숲", "forest"),
    biome_bgm_id="bgm_pianomotive",
    biome_id="forest",
    biome_desc=i("숲은 고요하고도 생명이 넘치는 곳이다.",
                 "A forest is a silent place, but is full of life."),
    room_spacing=15,
    rarity=1,
    biome_color=color.b_forest,
    tileset=get_tileset({
        "t_wall":tiles.wall_forest,
        "t_floor":tiles.floor_forest,
        "t_dense_grass":tiles.dense_grass_forest,
        "t_sparse_grass":tiles.sparse_grass_forest,
    }),
    additional_terrain=({
        terrain_factories.oak_tree_forest : 140,
    }),
    banned_entities=("closed_door",), # Ban doors
    map_width=80,
    map_height=60,
)
biome_dict[forest.biome_id] = forest
biome_rarity.append(forest.rarity)


desert_dungeon = Biome(
    name=i("사막", "desert dungeon"),
    biome_bgm_id="bgm_virtual_relaxation",
    biome_id="desert_dungeon",
    biome_desc=i(""),
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
    additional_terrain=({
        terrain_factories.cactus_field : 80,
        terrain_factories.oak_tree_forest : 0,
        terrain_factories.grass_field : 2,
    }),
)
biome_dict[desert_dungeon.biome_id] = desert_dungeon
biome_rarity.append(desert_dungeon.rarity)


orc_elf_warzone = Biome(
    name=i("전쟁터", "warzone"),
    biome_id="orc_elf_warzone",
    biome_desc=i(""),
    rarity=0,
    biome_color=color.b_warzone,
    room_spacing=20,
    map_width=67,
    map_height=41,
    respawn_ratio=0,
    tileset=get_tileset({
        "t_wall":tiles.wall_forest,
        "t_floor":tiles.floor_forest,
        "t_dense_grass":tiles.dense_grass_forest,
        "t_sparse_grass":tiles.sparse_grass_forest,
    }),
    terrain = {terrain_factories.battlefield:1},
)
biome_dict[orc_elf_warzone.biome_id] = orc_elf_warzone
biome_rarity.append(orc_elf_warzone.rarity)


ancient_ruins = Biome(
    name=i("고대 유적", "ancient ruins"),
    biome_id="ancient_ruins",
    biome_desc=i(""),
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
from terrain import Terrain
from unique_terrains.shop import ShopTerrain
from unique_terrains.chamber_of_kugah import ChamberOfKugahTerrain
import semiactor_factories

terrain_dict = {}
terrain_rarity = []

# Dungeon chamber (Standard)
dungeon_chamber = Terrain(
    name="던전 챔버",
    terrain_id="dungeon_chamber",
    terrain_desc="Desc of dungeon chamber terrain (TEST)",
    rarity=5,
    spawn_item=True,
    spawn_monster=True,
    gen_grass=None,
)
terrain_dict[dungeon_chamber.terrain_id] = dungeon_chamber
terrain_rarity.append(dungeon_chamber.rarity)


# Grass Field
grass_field = Terrain(
    name="평야",
    terrain_id="grass_field",
    terrain_desc="Desc of grass_field terrain (TEST)",
    rarity=6,
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(1,8), "scale_range":(1,4), "density":0.6},
)
terrain_dict[grass_field.terrain_id] = grass_field
terrain_rarity.append(grass_field.rarity)


# Trap Field
trap_field = Terrain(
    name="함정 필드",
    terrain_id="trap_field",
    terrain_desc="Desc of trap_field terrain (TEST)",
    rarity=5,
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(1,6), "scale_range":(1,4), "density":0.3},
    gen_traps={
        "checklist":{
            semiactor_factories.spike_trap:5,
            semiactor_factories.explosion_trap:5,
            semiactor_factories.flame_trap:5,
            semiactor_factories.acid_spray_trap:5,
            semiactor_factories.icicle_trap:5,
            semiactor_factories.poison_spike_trap:5,
            semiactor_factories.sonic_boom_trap:5,
        },
        "max_traps_per_room":5,
        "spawn_chance":0.05,
        "forced_traps_gen_number":4
    },
)
terrain_dict[trap_field.terrain_id] = trap_field
terrain_rarity.append(trap_field.rarity)


# Chest Room
chest_room = Terrain(
    name="창고",
    terrain_id="chest_room",
    terrain_desc="chest room desc",
    rarity=2,
    spawn_item=False,
    spawn_monster=True,
    gen_chests={"checklist":{"large_wooden_chest" : 10}, "chest_num_range":(1,8), "initial_items":None},
)
terrain_dict[chest_room.terrain_id] = chest_room
terrain_rarity.append(chest_room.rarity)


# Large Lake
large_lake = Terrain(
    name="큰 호수",
    terrain_id="large_lake",
    terrain_desc="Desc of large_lake terrain (TEST)",
    rarity=4,
    min_width=12,
    min_height=12,
    max_width=16,
    max_height=16,
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(4,8), "scale_range":(2,6), "density":0.7},
    gen_water={"core_num_range":(1,1), "scale_range":(7,11), "density":0.9, "no_border":False},
)
terrain_dict[large_lake.terrain_id] = large_lake
terrain_rarity.append(large_lake.rarity)

# Large pit
large_pit = Terrain(
    name="큰 구덩이",
    terrain_id="large_pit",
    terrain_desc="Desc of large_pit terrain (TEST)",
    rarity=2,
    min_width=12,
    min_height=12,
    max_width=16,
    max_height=16,
    spawn_item=True,
    spawn_monster=True,
    gen_pits={"core_num_range":(1,1), "scale_range":(7,11), "density":0.9, "no_border":False},
)
terrain_dict[large_pit.terrain_id] = large_pit
terrain_rarity.append(large_pit.rarity)


# Giant Hole
giant_hole = Terrain(
    name="큰 구멍",
    terrain_id="giant_hole",
    terrain_desc="Desc of giant_hole terrain (TEST)",
    rarity=2,
    spawn_item=False,
    spawn_monster=False,
    gen_holes={"core_num_range":(1,8), "scale_range":(1,4), "density":0.6},
)
terrain_dict[giant_hole.terrain_id] = giant_hole
terrain_rarity.append(giant_hole.rarity)


# Ocean
ocean = Terrain(
    name="바다",
    terrain_id="Ocean",
    terrain_desc="Desc of ocean terrain (TEST)",
    rarity=2,
    spawn_item=True,
    spawn_monster=True,
    gen_water={"core_num_range":(3,5), "scale_range":(4,8), "density":0.9, "no_border":True},
)
terrain_dict[ocean.terrain_id] = ocean
terrain_rarity.append(ocean.rarity)


# Swamp
swamp = Terrain(
    name="늪지대",
    terrain_id="swamp",
    terrain_desc="Desc of swamp terrain (TEST)",
    rarity=2,
    min_width=15,
    min_height=15,
    max_width=20,
    max_height=20,
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(4,8), "scale_range":(2,4), "density":0.7},
    gen_water={"core_num_range":(10,20), "scale_range":(2,4), "density":0.6, "no_border":False},
)
terrain_dict[swamp.terrain_id] = swamp
terrain_rarity.append(swamp.rarity)


# General shop
from custom_terrgen import ShopTerrGen
import item_factories
general_shop = ShopTerrain(
    name="잡동사니 상점",
    terrain_id="general_shop",
    terrain_desc="general shop desc",
    rarity=1,
    min_width=6,
    max_width=10,
    min_height=6,
    max_height=10,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=None,
)
terrain_dict[general_shop.terrain_id] = general_shop
terrain_rarity.append(general_shop.rarity)


# Potion shop
from custom_terrgen import ShopTerrGen
import item_factories
potion_shop = ShopTerrain(
    name="포션 상점",
    terrain_id="potion_shop",
    terrain_desc="potion shop desc",
    rarity=99, #FIXME
    min_width=6,
    max_width=10,
    min_height=6,
    max_height=10,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=
    {
        item_factories.potion_of_healing : item_factories.potion_of_healing.rarity,
        item_factories.potion_of_flame : item_factories.potion_of_flame.rarity,
        item_factories.potion_of_levitation : item_factories.potion_of_levitation.rarity,
        item_factories.potion_of_liquified_ants : item_factories.potion_of_liquified_ants.rarity,
        item_factories.potion_of_monster_detection : item_factories.potion_of_monster_detection.rarity,
        item_factories.potion_of_poison : item_factories.potion_of_poison.rarity,
        item_factories.potion_of_paralysis : item_factories.potion_of_paralysis.rarity,
        item_factories.potion_of_acid : item_factories.potion_of_acid.rarity,
        item_factories.potion_of_frost : item_factories.potion_of_frost.rarity,
    },
)
terrain_dict[potion_shop.terrain_id] = potion_shop
terrain_rarity.append(potion_shop.rarity)


# Chamber Of Kugah
from custom_terrgen import ChamberOfKugahTerrGen
chamber_of_kugah = ChamberOfKugahTerrain(
    name="쿠가의 성소",
    terrain_id="chamber_of_kugah",
    terrain_desc="chamber of kugah desc",
    rarity=0,
    min_width=30,
    max_width=30,
    min_height=30,
    max_height=30,
    custom_gen=ChamberOfKugahTerrGen.generate_chamber_of_kugah,
)
terrain_dict[chamber_of_kugah.terrain_id] = chamber_of_kugah
terrain_rarity.append(chamber_of_kugah.rarity)
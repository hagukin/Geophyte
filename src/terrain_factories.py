from terrain import Terrain
from unique_terrains.shop import ShopTerrain
from unique_terrains.chamber_of_kugah import ChamberOfKugahTerrain
from unique_terrains.guarded_treasure import GuardedTreasureTerrain
import semiactor_factories
from order import InventoryOrder

terrain_dict = {}

# Dungeon chamber (Standard)
dungeon_chamber = Terrain(
    name="던전 챔버",
    terrain_id="dungeon_chamber",
    terrain_desc="Desc of dungeon chamber terrain (TEST)",
    rarity=40,
    spawn_item=True,
    spawn_monster=True,
    gen_grass=None,
)
terrain_dict[dungeon_chamber] = dungeon_chamber.rarity


# Forest chamber
forest_chamber = Terrain(
    name="숲",
    terrain_id="forest_chamber",
    terrain_desc="Desc of forest_chamber terrain (TEST)",
    rarity=5,
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(1,6), "scale_range":(1,4), "density":0.3},
    gen_plants={
        "checklist":{
            semiactor_factories.oak_tree:5,
        },
        "max_plants_per_room":99,
        "spawn_chance":0.2,
        "forced_plants_gen_number":0
    },
)
terrain_dict[forest_chamber] = forest_chamber.rarity


# Forest chamber spawn no door
forest_chamber_spawn_no_door = Terrain(
    name="숲",
    terrain_id="forest_chamber_spawn_no_door",
    terrain_desc="Desc of forest_chamber_spawn_no_door terrain (TEST)",
    rarity=0, # Manual
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(1,6), "scale_range":(1,4), "density":0.3},
    gen_plants={
        "checklist":{
            semiactor_factories.oak_tree:5,
        },
        "max_plants_per_room":99,
        "spawn_chance":0.2,
        "forced_plants_gen_number":0
    },
    spawn_door=False,
)
terrain_dict[forest_chamber_spawn_no_door] = forest_chamber_spawn_no_door.rarity


# Landmine chamber
landmine_chamber = Terrain(
    name="지뢰밭",
    terrain_id="landmine_chamber",
    terrain_desc="Desc of dungeon chamber terrain (TEST)",
    rarity=10,
    spawn_item=True,
    spawn_monster=False,
    gen_grass=None,
    gen_traps={
        "checklist":{
            semiactor_factories.explosion_trap:5,
        },
        "max_traps_per_room":100,
        "spawn_chance":0.5,
        "forced_traps_gen_number":0
    },
    gen_chests={"checklist":{"large_wooden_chest" : 10}, "chest_num_range":(1,1), "initial_items":None},
)
terrain_dict[landmine_chamber] = landmine_chamber.rarity


# Grass Field
grass_field = Terrain(
    name="평야",
    terrain_id="grass_field",
    terrain_desc="Desc of grass_field terrain (TEST)",
    rarity=60,
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(1,8), "scale_range":(1,4), "density":0.6},
)
terrain_dict[grass_field] = grass_field.rarity


# Grass Field Spawn No Door
grass_field_spawn_no_door = Terrain(
    name="평야",
    terrain_id="grass_field_spawn_no_door",
    terrain_desc="Desc of grass_field_spawn_no_door terrain (TEST)",
    rarity=0, # Must add terrain manually to generate
    spawn_item=True,
    spawn_monster=True,
    has_door=True, # HAS DOOR CONVEXES
    spawn_door=False,
    gen_grass={"core_num_range":(1,8), "scale_range":(1,4), "density":0.6},
)
terrain_dict[grass_field_spawn_no_door] = grass_field_spawn_no_door.rarity


# Large Grass Field Spawn No Door
large_grass_field_spawn_no_door = Terrain(
    name="평야",
    terrain_id="large_grass_field_spawn_no_door",
    terrain_desc="Desc of large_grass_field_spawn_no_door terrain (TEST)",
    rarity=0, # Must add terrain manually to generate
    spawn_item=True,
    spawn_monster=True,
    has_door=True, # HAS DOOR CONVEXES
    spawn_door=False,
    min_width=9,
    max_width=14,
    gen_grass={"core_num_range":(1,8), "scale_range":(1,9), "density":0.6},
)
terrain_dict[large_grass_field_spawn_no_door] = large_grass_field_spawn_no_door.rarity


# Trap Field
trap_field = Terrain(
    name="함정 필드",
    terrain_id="trap_field",
    terrain_desc="Desc of trap_field terrain (TEST)",
    rarity=50,
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
terrain_dict[trap_field] = trap_field.rarity


# Chest Room
chest_room = Terrain(
    name="창고",
    terrain_id="chest_room",
    terrain_desc="chest room desc",
    rarity=1,
    spawn_item=False,
    spawn_monster=True,
    gen_chests={"checklist":{"large_wooden_chest" : 10}, "chest_num_range":(1,3), "initial_items":None},
)
terrain_dict[chest_room] = chest_room.rarity

# Large pit
large_pit = Terrain(
    name="큰 구덩이",
    terrain_id="large_pit",
    terrain_desc="Desc of large_pit terrain (TEST)",
    rarity=1,
    min_width=12,
    min_height=12,
    max_width=16,
    max_height=16,
    spawn_item=True,
    spawn_monster=True,
    shape={
        "blob":1,
    },
    gen_pits={"core_num_range":(1,8), "scale_range":(1,4), "density":0.9, "no_border":True},
)
terrain_dict[large_pit] = large_pit.rarity


# Giant Hole
giant_hole = Terrain(
    name="큰 구멍",
    terrain_id="giant_hole",
    terrain_desc="Desc of giant_hole terrain (TEST)",
    rarity=3,
    spawn_item=False,
    spawn_monster=False,
    gen_holes={"core_num_range":(1,8), "scale_range":(1,4), "density":0.6, "no_border":True},
)
terrain_dict[giant_hole] = giant_hole.rarity


# Ocean
ocean = Terrain(
    name="바다",
    terrain_id="Ocean",
    terrain_desc="Desc of ocean terrain (TEST)",
    rarity=2,
    spawn_item=True,
    spawn_monster=True,
    spawn_door=False,
    gen_water={"core_num_range":(3,6), "scale_range":(4,8), "density":0.9, "no_border":True},
)
terrain_dict[ocean] = ocean.rarity


# Swamp
swamp = Terrain(
    name="늪지대",
    terrain_id="swamp",
    terrain_desc="Desc of swamp terrain (TEST)",
    rarity=15,
    spawn_item=True,
    spawn_monster=True,
    spawn_door=False,
    gen_grass={"core_num_range":(4,8), "scale_range":(2,4), "density":0.7},
    gen_water={"core_num_range":(10,20), "scale_range":(2,4), "density":0.6, "no_border":True},
)
terrain_dict[swamp] = swamp.rarity


# General shop
from custom_terrgen import ShopTerrGen
import item_factories
general_shop = ShopTerrain(
    name="잡동사니 상점",
    terrain_id="general_shop",
    terrain_desc="general shop desc",
    rarity=1,
    min_width=6,
    max_width=8,
    min_height=6,
    max_height=8,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=None,
    sell_items_type_limit=None,
    shape=None
)
terrain_dict[general_shop] = general_shop.rarity


# Potion shop
from custom_terrgen import ShopTerrGen
import item_factories
potion_shop = ShopTerrain(
    name="포션 상점",
    terrain_id="potion_shop",
    terrain_desc="potion shop desc",
    rarity=1,
    min_width=6,
    max_width=8,
    min_height=6,
    max_height=8,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=None,
    sell_items_type_limit=(InventoryOrder.POTION, ),
    shape=None,
)
terrain_dict[potion_shop] = potion_shop.rarity


# Weapon shop
from custom_terrgen import ShopTerrGen
import item_factories
weapon_shop = ShopTerrain(
    name="무기 상점",
    terrain_id="weapon_shop",
    terrain_desc="weapon shop desc",
    rarity=1,
    min_width=6,
    max_width=8,
    min_height=6,
    max_height=8,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=None,
    sell_items_type_limit=(InventoryOrder.MELEE_WEAPON, InventoryOrder.THROWING_WEAPON,),
    shape=None,
)
terrain_dict[weapon_shop] = weapon_shop.rarity


# Scroll shop
from custom_terrgen import ShopTerrGen
import item_factories
scroll_shop = ShopTerrain(
    name="주문서 상점",
    terrain_id="scroll_shop",
    terrain_desc="scroll shop desc",
    rarity=1,
    min_width=6,
    max_width=8,
    min_height=6,
    max_height=8,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=None,
    sell_items_type_limit=(InventoryOrder.SCROLL,),
    shape=None,
)
terrain_dict[scroll_shop] = scroll_shop.rarity


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
    shape={
        "circular":4,
    },
)
terrain_dict[chamber_of_kugah] = chamber_of_kugah.rarity


# Chamber Of Kugah
from custom_terrgen import GuardedTreasureTerrGen
guarded_treasure = GuardedTreasureTerrain(
    name="보호받는 보물",
    terrain_id="guarded_treasure",
    terrain_desc="guarded treasure desc",
    rarity=1,
    spawn_item=False,
    spawn_monster=False,
    custom_gen=GuardedTreasureTerrGen.generate_guarded_treasure,
    gen_chests=None, # Disable procedural chest spawning
    gen_treasure_chests={"checklist":{"golden_chest" : 10},
                "chest_num_range":(1,1),
                "initial_items": None},
)
terrain_dict[guarded_treasure] = guarded_treasure.rarity
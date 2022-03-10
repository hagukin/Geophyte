from terrain import Terrain
from unique_terrains.shop import ShopTerrain
from unique_terrains.chamber_of_kugah import ChamberOfKugahTerrain
from unique_terrains.guarded_treasure import GuardedTreasureTerrain
import semiactor_factories
import item_factories
import actor_factories
from order import InventoryOrder
from language import interpret as i

terrain_dict = {}

# Dungeon chamber (Standard)
dungeon_chamber = Terrain(
    name=i("던전 챔버", "dungeon chamber"),
    terrain_id="dungeon_chamber",
    terrain_desc="",
    rarity=100,
    spawn_item=True,
    spawn_monster=True,
    gen_grass=None,
)
terrain_dict[dungeon_chamber] = dungeon_chamber.rarity


# battlefield
battlefield = Terrain(
    name=i("전장", "battlefield"),
    terrain_id="battlefield",
    terrain_desc="",
    rarity=0,
    spawn_item=True,
    spawn_monster=True,
    monsters_cnt={70:1},# Fill with monsters
    spawn_door=False,
    has_door=False,
    max_width=50,
    min_width=45,
    max_height=35,
    min_height=30,
    shape={"rectangular":1},
    monster_to_spawn={
        actor_factories.orc_warrior:5,
        actor_factories.orc_blacksmith:1,
        actor_factories.orc_shaman:1,
        actor_factories.orc_lord:1,
        actor_factories.elf_fighter:5,
        actor_factories.elf_assasin:1,
        actor_factories.elf_herbalist:1,
    },
    gen_grass={"core_num_range":(8,20), "scale_range":(1,4), "density":0.6},
)
terrain_dict[battlefield] = battlefield.rarity


# Monater lair
monster_lair = Terrain(
    name=i("괴물 둥지", "monster lair"),
    terrain_id="monster_lair",
    terrain_desc="",
    rarity=2,
    spawn_item=True,
    spawn_monster=True,
    make_monster_sleep=False,
    monsters_cnt={64:1},# Fill with monsters
    adjust_monster_difficulty=-3, # easier enemies
    door_num_range=(1,),
    door_num_weight=(1,),
    max_width=8,
    max_height=8,
    protected=True,
    can_have_stair=False,
    door_types={
      semiactor_factories.locked_door:1
    },
    shape={
        "rectangular":1,
        "circular": 1,
    },
)
terrain_dict[monster_lair] = monster_lair.rarity


# Forest chamber
forest_chamber = Terrain(
    name=i("숲", "forest"),
    terrain_id="forest_chamber",
    terrain_desc="",
    rarity=70,
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


# explosion chamber
explosion_chamber = Terrain(
    name=i("폭발 챔버", "explosion chamber"),
    terrain_id="flame_chamber",
    terrain_desc="",
    rarity=30,
    spawn_item=True,
    spawn_monster=False,
    gen_grass={"core_num_range":(4,8), "scale_range":(1,4), "density":0.9},
    gen_traps={
        "checklist":{
            semiactor_factories.explosion_trap:5,
        },
        "max_traps_per_room":5,
        "spawn_chance":0.1,
        "forced_traps_gen_number":1
    },
)
terrain_dict[explosion_chamber] = explosion_chamber.rarity


# Grass Field
grass_field = Terrain(
    name=i("평야", "grassfield"),
    terrain_id="grass_field",
    terrain_desc="",
    rarity=120,
    spawn_item=True,
    spawn_monster=True,
    gen_grass={"core_num_range":(1,8), "scale_range":(1,4), "density":0.6},
)
terrain_dict[grass_field] = grass_field.rarity


# Trap Field
trap_field = Terrain(
    name=i("함정 필드", "trap field"),
    terrain_id="trap_field",
    terrain_desc="",
    rarity=50,
    spawn_item=True,
    spawn_monster=True,
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


# Trap Field with grass
trap_field_with_grass = Terrain(
    name=i("함정 필드", "trap field"),
    terrain_id="trap_field_with_grass",
    terrain_desc="",
    rarity=25,
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
    name=i("창고", "storage"),
    terrain_id="chest_room",
    terrain_desc="",
    rarity=5,
    spawn_item=False,
    spawn_monster=False,
    gen_chests={"checklist":{"large_wooden_chest" : 10}, "chest_num_range":(1,3), "initial_items":None},
    has_door=True,
    spawn_door=True,
    door_num_range = (1,),
    door_num_weight = (1,),
    protected=True,
    can_have_stair=False,
    door_types={
      semiactor_factories.chained_locked_door:1
    },
)
terrain_dict[chest_room] = chest_room.rarity


# Large pit
large_pit = Terrain(
    name=i("큰 구덩이", "large pit"),
    terrain_id="large_pit",
    terrain_desc="",
    rarity=3,
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
    name=i("큰 구멍", "giant hole"),
    terrain_id="giant_hole",
    terrain_desc="",
    rarity=7,
    spawn_item=False,
    spawn_monster=False,
    gen_holes={"core_num_range":(1,8), "scale_range":(1,4), "density":0.6, "no_border":True},
)
terrain_dict[giant_hole] = giant_hole.rarity


# Ocean
ocean = Terrain(
    name=i("바다", "ocean"),
    terrain_id="ocean",
    terrain_desc="",
    rarity=2,
    spawn_item=True,
    spawn_monster=True,
    spawn_door=False,
    gen_water={"core_num_range":(3,6), "scale_range":(4,5), "density":0.9, "no_border":True},
    monsters_cnt={0:1, 1:1, 2:2, 3:1},
    underwater_mon_ratio=1,
)
terrain_dict[ocean] = ocean.rarity


# Lake
lake = Terrain(
    name=i("호수", "lake"),
    terrain_id="lake",
    terrain_desc="",
    rarity=6,
    spawn_item=True,
    spawn_monster=True,
    spawn_door=False,
    gen_water={"core_num_range":(1,4), "scale_range":(4,5), "density":0.9, "no_border":True},
)
terrain_dict[lake] = lake.rarity


# Piranha lake
piranha_lake = Terrain(
    name=i("피라냐 호수", "piranha lake"),
    terrain_id="piranha_lake",
    terrain_desc="",
    rarity=3,
    spawn_item=True,
    spawn_monster=True,
    spawn_door=False,
    gen_water={"core_num_range":(1,4), "scale_range":(4,5), "density":0.9, "no_border":False},
    monster_to_spawn_underwater={actor_factories.piranha:1},
    monsters_cnt={3:3, 4:3},
    underwater_mon_ratio=1, # underwater monsters only (is not guarenteed)
)
terrain_dict[piranha_lake] = piranha_lake.rarity


# Swamp
swamp = Terrain(
    name=i("늪지대", "swamp"),
    terrain_id="swamp",
    terrain_desc="",
    rarity=30,
    spawn_item=True,
    spawn_monster=True,
    spawn_door=False,
    gen_grass={"core_num_range":(4,8), "scale_range":(2,4), "density":0.7},
    gen_water={"core_num_range":(10,20), "scale_range":(2,4), "density":0.6, "no_border":True},
)
terrain_dict[swamp] = swamp.rarity


# General shop
from custom_terrgen import ShopTerrGen
general_shop = ShopTerrain(
    name=i("잡동사니 상점", "general shop"),
    terrain_id="general_shop",
    terrain_desc="",
    rarity=3,
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
potion_shop = ShopTerrain(
    name=i("포션 상점", "potion shop"),
    terrain_id="potion_shop",
    terrain_desc="",
    rarity=2,
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
weapon_shop = ShopTerrain(
    name=i("무기 상점", "weapon shop"),
    terrain_id="weapon_shop",
    terrain_desc="",
    rarity=1,
    min_width=6,
    max_width=8,
    min_height=6,
    max_height=8,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=None,
    sell_items_type_limit=(InventoryOrder.MELEE_WEAPON, ),
    shape=None,
)
terrain_dict[weapon_shop] = weapon_shop.rarity


# Armor shop
from custom_terrgen import ShopTerrGen
armor_shop = ShopTerrain(
    name=i("갑옷 상점", "armor shop"),
    terrain_id="armor_shop",
    terrain_desc="",
    rarity=1,
    min_width=6,
    max_width=8,
    min_height=6,
    max_height=8,
    custom_gen=ShopTerrGen.generate_shop,
    sell_items=None,
    sell_items_type_limit=(InventoryOrder.ARMOR, ),
    shape=None,
)
terrain_dict[armor_shop] = armor_shop.rarity


# Scroll shop
from custom_terrgen import ShopTerrGen
scroll_shop = ShopTerrain(
    name=i("주문서 상점", "scroll shop"),
    terrain_id="scroll_shop",
    terrain_desc="",
    rarity=2,
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
    name=i("쿠가의 성소", "chamber of Kugah"),
    terrain_id="chamber_of_kugah",
    terrain_desc="",
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
    name=i("보호받는 보물", "guarded treasure"),
    terrain_id="guarded_treasure",
    terrain_desc="",
    rarity=2,
    spawn_item=False,
    spawn_monster=False,
    custom_gen=GuardedTreasureTerrGen.generate_guarded_treasure,
    gen_chests=None, # Disable procedural chest spawning
    gen_treasure_chests={"checklist":{"golden_chest" : 10},
                "chest_num_range":(1,1),
                "initial_items": None},
)
terrain_dict[guarded_treasure] = guarded_treasure.rarity
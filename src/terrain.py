import random
from typing import Dict, Optional

import game
import semiactor_factories

class Terrain:
    """
    Terrain component for the rooms.
    """
    @property
    def engine(self):
        return game.Game.engine

    def __init__(
        self,
        name: str = "<Unnamed>",
        terrain_id: str = "<Undefined id>",
        terrain_desc: str = "",
        rarity: int = 1,
        min_width: int = 6, # min 6
        max_width: int = 11,
        min_height: int = 6, # min 6
        max_height: int = 10,
        shape: dict = None,
        spawn_item: bool = True,
        items_cnt: Dict = None,
        item_to_spawn: Dict = None,
        monsters_cnt: Dict = None,
        spawn_monster: bool = True,
        spawn_monster_of_difficulty: Optional[int] = None, # Can overwrite biome.monster_difficulty
        adjust_monster_difficulty: int = 0, # Adjust toughness. Can have negative value
        monster_to_spawn: Dict = None,
        make_monster_sleep: bool=False,
        has_wall: bool = True, #TODO: need to add feature
        protected: bool = False,
        has_door: bool = True,
        spawn_door: bool = True, # Different from has door
        can_have_stair: bool = True,
        door_num_range = (1,2,3,4),
        door_num_weight = (3,7,2,1),
        door_types: Dict=None,
        gen_grass = None,
        gen_holes = None,
        gen_water = None,
        gen_pits = None,
        gen_traps = None,
        gen_plants = None,
        gen_chests = None,
        custom_gen = None,
    ):
        """
        Args:
            shape:
                Dictionary.
                Keys contain different types of room shape that can be generated in this type of terrain.
                Values contain the chance of the room shape getting chosen. (weight)
            door_num_range:
                possible number of doors per room. This value should sync up with door_num_weight.
            door_num_weight:
                chance of having certain number of doors
            has_door:
                Whether door convex exists.
            spawn_door:
                Whether to spawn door semiactor or not.
                If False, but has door, the terrain will spawn nothing onto the door location.
            protected:
                whether the room that own's this terrain component has a wall that can be destroyed during procgen from other terrains' generation process
                e.g. if set to true, ocean generation will not overlap with with this room's outer&inner area.
            gen_grass:
                {
                    "core_num_range":Tuple(int,int), 
                    "scale_range":Tuple(int,int), 
                    "density":int
                }
            gen_holes:
                same as gen_grass.
            gen_water:
                {
                    "core_num_range":Tuple(int,int), 
                    "scale_range":Tuple(int,int), 
                    "density":int, 
                    "no_border":bool
                }
                no_border:
                    Boolean value that indicates whether the water can spread across different rooms or not
            gen_pits:
                Same as gen_water.
            gen_traps:
                {
                    "checklist":dict{semiactor : weight},
                    "max_traps_per_room":int, 
                    "spawn_chance":float, 
                    "forced_traps_gen_number":int = 0
                }
                checklist:
                    a dictionary data that stores different types of traps that can be generated in this terrain.
                    Key = Semiactor's id, Value = chance of getting spawned(weight)
                max_traps_per_room:
                    maximum amount of traps that can be generated in this terrain
                spawn_chance:
                    chance of generating a trap for a single tile.
                forced_traps_gen_number:
                    Number of traps that are guarenteed to be generated.
                    If the room has not enough valid tiles to randomize traps, it will randomize the maximum amount.
                    NOTE: This value is effected by max_traps_per_room
            gen_plants:
                NOTE: Based off of gen_traps
                {
                    "checklist":dict{semiactor : weight},
                    "max_plants_per_room":int,
                    "spawn_chance":float,
                    "forced_plants_gen_number":int = 0
                }
                checklist:
                    a dictionary data that stores different types of plants that can be generated in this terrain.
                    Key = Semiactor's id, Value = chance of getting spawned(weight)
                max_plants_per_room:
                    maximum amount of plants that can be generated in this terrain
                spawn_chance:
                    chance of generating a plant for a single tile.
                forced_plants_gen_number:
                    Number of plants that are guarenteed to be generated.
                    If the room has not enough valid tiles to randomize plants, it will randomize the maximum amount.
                    NOTE: This value is effected by max_plants_per_room
            gen_chests:
                {
                    "checklist":dict{chest_id : spawn_chance}, 
                    "chest_num_range":Tuple(int, int), 
                    "initial_items":[(Item, Chance of having this Item when generated, (min item num, max item num))]
                }
                initial_items:
                    A list that contains information about what kind of items will be generated in the chests that are spawned in this terrain.
                    If the value is set to None, the chest will use default values.
            custom_gen:
                Function. The function will randomize an unique terrains that is specified to this room.
                FUnction is called during procgen.generate_terrain().
                Can be set to None.
            monster_to_spawn:
                Dictionary. Key - monster, value - weight
                if set to None, terrain will use default values (from actor_factories) instead.
                weight is set to None if you are using the original rarity value.
                e.g. {actor_factories.orc_warrior : 3, actor_factories.orc_shaman : 1}

                NOTE: the specification only affects the procgen process.
                meaning that when monsters are getting respawned, this value cannot interfere with the type of monsters that are being respawned.
            item_to_spawn:
                same as monster_to_spawn parameter
        """

        self.name = name
        self.terrain_id = terrain_id
        self.terrain_desc = terrain_desc

        self.rarity = rarity

        # Key: amount
        # Value: weight
        self.items_cnt = {0:15, 1:8, 2:4, 3:1}
        self.monsters_cnt = {0:4, 1:9, 2:5, 3:2}
        if items_cnt:
            self.items_cnt = items_cnt
        if monsters_cnt:
            self.monsters_cnt = monsters_cnt
        self.make_monster_sleep = make_monster_sleep

        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

        if shape == None:
            self.shape = {
            "rectangular":2,
            "circular":4,
            "blob":5,
            }
        else:
            self.shape = shape

        self.spawn_item = spawn_item
        self.item_to_spawn = item_to_spawn
        self.spawn_monster = spawn_monster
        self.monster_to_spawn = monster_to_spawn
        self.spawn_monster_of_difficulty = spawn_monster_of_difficulty
        self.adjust_monster_difficulty = adjust_monster_difficulty

        self.has_wall = has_wall
        self.protected = protected
        self.has_door = has_door
        self.spawn_door = spawn_door
        self.can_have_stair = can_have_stair
        self.door_num_range = door_num_range
        self.door_num_weight = door_num_weight
        self.door_types = {semiactor_factories.closed_door:1}
        if door_types:
            self.door_types = door_types

        self.gen_grass = gen_grass
        self.gen_holes = gen_holes
        self.gen_water = gen_water
        self.gen_pits = gen_pits
        self.gen_traps = gen_traps
        self.gen_plants = gen_plants
        self.gen_chests = gen_chests
        self.custom_gen = custom_gen
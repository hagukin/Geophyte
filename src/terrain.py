import random

class Terrain:
    """
    Terrain component for the rooms.
    """

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
        item_spawn_chance: float = 0.5,
        min_items_per_room: int = 0,
        max_items_per_room: int = 4,
        spawn_monster: bool = True,
        monster_spawn_chance: float = 0.5,
        min_monsters_per_room: int = 0,
        max_monsters_per_room: int = 4,
        has_wall: bool = True, #TODO: need to add feature
        protected: bool = False,
        has_door: bool = True,
        can_have_stair: bool = True,
        door_num_range = (1,2,3,4),
        door_num_weight = (3,7,2,1),
        gen_grass = None,
        gen_holes = None,
        gen_water = None,
        gen_pits = None,
        gen_traps = None,
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
                    If the room has not enough valid tiles to generate traps, it will generate the maximum amount.
                    NOTE: This value is effected by max_traps_per_room
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
                Function. The function will generate an unique terrains that is specified to this room.
                FUnction is called during procgen.generate_terrain().
                Can be set to None.
        """

        self.name = name
        self.terrain_id = terrain_id
        self.terrain_desc = terrain_desc

        self.rarity = rarity

        self.item_spawn_chance = item_spawn_chance
        self.monster_spawn_chance = monster_spawn_chance

        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room
        self.min_monsters_per_room = min_monsters_per_room
        self.min_items_per_room = min_items_per_room

        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

        if shape == None:
            self.shape = {
            "rectangular":2,
            "circular":4,
            "perpendicular":4,
        }
        else:
            self.shape = shape

        self.spawn_item = spawn_item
        self.spawn_monster = spawn_monster

        self.has_wall = has_wall
        self.protected = protected
        self.has_door = has_door
        self.can_have_stair = can_have_stair
        self.door_num_range = door_num_range
        self.door_num_weight = door_num_weight

        self.gen_grass = gen_grass
        self.gen_holes = gen_holes
        self.gen_water = gen_water
        self.gen_pits = gen_pits
        self.gen_traps = gen_traps
        self.gen_chests = gen_chests
        self.custom_gen = custom_gen
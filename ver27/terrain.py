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
        max_width: int = 16,
        min_height: int = 6, # min 6
        max_height: int = 16,
        shape: dict = {
            "rectangular":2,
            "circular":4,
            "perpendicular":4,
        },
        spawn_item: bool = True,
        spawn_monster: bool = True,
        has_wall: bool = True, #TODO: need to add feature
        has_door: bool = True,
        door_num_range = (1,2,3,4),
        door_num_weight = (3,7,2,1),
        gen_grass = None,
        gen_water = None,
        gen_traps = None,
        gen_chests = None,
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
            gen_grass:
                {
                    "core_num_range":Tuple(int,int), 
                    "scale_range":Tuple(int,int), 
                    "density":int
                }
            gen_water:
                {
                    "core_num_range":Tuple(int,int), 
                    "scale_range":Tuple(int,int), 
                    "density":int, 
                    "no_border":bool
                }
                no_border:
                    Boolean value that indicates whether the water can spread across different rooms or not
            gen_traps:
                {
                    "checklist":dict{id : name}, 
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
        """

        self.name = name,
        self.terrain_id = terrain_id,
        self.terrain_desc = terrain_desc,

        self.rarity = rarity

        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

        self.shape = shape

        self.spawn_item = spawn_item
        self.spawn_monster = spawn_monster

        self.has_wall = has_wall
        self.has_door = has_door
        self.door_num_range = door_num_range
        self.door_num_weight = door_num_weight

        self.gen_grass = gen_grass
        self.gen_water = gen_water
        self.gen_traps = gen_traps
        self.gen_chests = gen_chests
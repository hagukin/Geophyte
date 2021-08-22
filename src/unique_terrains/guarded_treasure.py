from terrain import Terrain
from typing import TYPE_CHECKING
from entity import Actor
from actor_factories import giant

if TYPE_CHECKING:
    from room_factories import Room
    from chest_factories import ChestSemiActor

class GuardedTreasureTerrain(Terrain):
    """
    Shop terrain component.
    """
    def __init__(
        self,
        name: str = "Guarded Treasure",
        terrain_id: str = "guarded_treasure",
        terrain_desc: str = "",
        rarity: int = 1,
        min_width: int = 11, # min 6
        max_width: int = 11,
        min_height: int = 11, # min 6
        max_height: int = 11,
        shape: dict = None,
        spawn_item: bool = False,
        spawn_monster: bool = False,
        has_wall: bool = True, #TODO: need to add feature
        protected: bool = True,
        has_door: bool = True,
        can_have_stair: bool = False,
        door_num_range = (1,2,),
        door_num_weight = (1,1 ),
        gen_grass = None,
        gen_holes=None,
        gen_water = None,
        gen_pits = None,
        gen_traps = None,
        gen_chests = None, # NOTE: Set this to None.
        gen_treasure_chests = None, # Modify this value.
        custom_gen = None, # Must have one
        guardian_type: Actor = giant, # If none, choose dynamically.
    ):
        super().__init__(
            name=name,
            terrain_id=terrain_id,
            terrain_desc=terrain_desc,
            rarity=rarity,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            shape=shape,
            spawn_item=spawn_item,
            spawn_monster=spawn_monster,
            has_wall=has_wall,
            protected=protected,
            has_door=has_door,
            can_have_stair=can_have_stair,
            door_num_range=door_num_range,
            door_num_weight=door_num_weight,
            gen_grass=gen_grass,
            gen_holes=gen_holes,
            gen_water=gen_water,
            gen_pits=gen_pits,
            gen_traps=gen_traps,
            gen_chests=gen_chests,
            custom_gen=custom_gen,
        )
        """
        Args:
            gen_treasure_chests:
                NOTE: Same format as gen_chests
                {
                    "checklist":dict{chest_id : spawn_chance}, 
                    "chest_num_range":Tuple(int, int), 
                    "initial_items":[(Item, Chance of having this Item when generated, (min item num, max item num))]
                }
                initial_items:
                    A list that contains information about what kind of items will be generated in the chests that are spawned in this terrain.
                    If the value is set to None, the chest will use default values.
            contain_items:
                {
                    item object : chance of spawning(weight)
                }
        """
        if shape == None:
            self.shape = {
            "circular":1 #Shops can be in any shape, but rectangular is most stable
            }
        else:
            self.shape = shape

        self.gen_treasure_chests = gen_treasure_chests

        self.guardian_type = guardian_type# Actor

        self.guardians = [] # List





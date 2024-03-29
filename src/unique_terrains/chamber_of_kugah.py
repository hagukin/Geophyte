from terrain import Terrain
from typing import TYPE_CHECKING
from rooms import Room
from game_map import GameMap
from entity import Actor
from actor_factories import shopkeeper


class ChamberOfKugahTerrain(Terrain):
    """
    Shop terrain component.
    """
    def __init__(
        self,
        name: str = "chamber of Kugah",
        terrain_id: str = "chamber_of_kugah",
        terrain_desc: str = "",
        rarity: int = 0,
        min_width: int = 30, # min 6
        max_width: int = 30,
        min_height: int = 30, # min 6
        max_height: int = 30,
        shape: dict = None,
        spawn_item: bool = False,
        spawn_monster: bool = False,
        has_wall: bool = True, #TODO: need to add feature
        protected: bool = True,
        has_door: bool = False,
        can_have_stair: bool = True,
        door_num_range = (0,),
        door_num_weight = (1,),
        gen_grass = None,
        gen_holes=None,
        gen_water = None,
        gen_pits = None,
        gen_traps = None,
        gen_chests = None,
        custom_gen = None, # Must have one
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
        if shape == None:
            self.shape = {
            "circular":99, #Shops can be in any shape, but rectangular is most stable
        }
        else:
            self.shape = shape


class ChamberOfKugahTerrGen:
    @staticmethod
    def generate_amulet_of_kugah(gamemap: GameMap, room: Room) -> None:
        from item_factories import amulet_of_kugah
        coors = room.center
        tmp = amulet_of_kugah.spawn(gamemap, coors[0], coors[1])

    @staticmethod
    def generate_chamber_of_kugah(gamemap: GameMap, room: Room) -> None:
        """
        Custom function for generating chamber of kugah.
        """
        ChamberOfKugahTerrGen.generate_amulet_of_kugah(gamemap, room)





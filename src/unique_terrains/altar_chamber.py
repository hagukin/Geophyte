from terrain import Terrain
from typing import TYPE_CHECKING
from rooms import Room
from game_map import GameMap
from entity import Actor
from actor_factories import shopkeeper


class AltarChamberTerrain(Terrain):
    """
    Altar terrain component.
    """
    def __init__(
        self,
        name: str = "altar chamber",
        terrain_id: str = "altar_chamber",
        terrain_desc: str = "",
        rarity: int = 0,
        min_width: int = 6, # min 6
        max_width: int = 8,
        min_height: int = 6, # min 6
        max_height: int = 8,
        shape: dict = None,
        spawn_item: bool = False,
        spawn_monster: bool = False,
        has_wall: bool = True,
        protected: bool = True,
        has_door: bool = True,
        can_have_stair: bool = True,
        door_num_range=(1, 2, 3, 4),
        door_num_weight=(3, 7, 2, 1),
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
            "circular":1,
        }
        else:
            self.shape = shape


class AltarChamberTerrGen:
    @staticmethod
    def generate_altar(gamemap: GameMap, room: Room) -> None:
        # FIXME TODO ADD ALTAR
        from semiactor_factories import altar
        coors = room.center
        tmp = altar.spawn(gamemap, coors[0], coors[1])

    @staticmethod
    def generate_altar_chamber(gamemap: GameMap, room: Room) -> None:
        """
        Custom function for generating chamber of kugah.
        """
        AltarChamberTerrGen.generate_altar(gamemap, room)



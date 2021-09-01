import copy
from typing import Tuple, List, Optional, TYPE_CHECKING
import tiles
import color

def get_tileset(
    adjustments: dict=None,
):
    """
    Args:
        adjustments:
            dictionary. key - tile id, value - tile
            if any adjustments value is given, this function will modify the default tilesets as given.
    """
    tileset = {
        "t_wall":tiles.wall,
        "t_border":tiles.vintronium,
        "t_floor":tiles.floor,
        "t_dense_grass":tiles.dense_grass,
        "t_sparse_grass":tiles.sparse_grass,
        "t_ascending_stair":tiles.ascending_stair,
        "t_descending_stair":tiles.descending_stair,
        "t_burnt_floor":tiles.burnt_floor,
        "t_deep_pit":tiles.deep_pit,
        "t_shallow_pit":tiles.shallow_pit,
        "t_hole":tiles.hole,
        "t_deep_water":tiles.deep_water,
        "t_shallow_water":tiles.shallow_water,
        "t_ice":tiles.ice,
        "t_DEBUG":tiles.DEBUG,
    }

    if adjustments:
        for tile in adjustments.items():
            tileset[tile[0]] = tile[1]

    return tileset


class Biome:
    """
    Biome component for the gamemap.
    """
    def __init__(
        self,
        name: str = "<Unnamed>",
        biome_id: str = "<Undefined id>",
        biome_desc: str = "",
        rarity: int = 1,
        biome_color: Tuple = color.black,
        max_rooms: int = 100,
        map_width: int = 67, # min 67
        map_height: int = 41, # min 41
        respawn_ratio: float = 0.5,
        respawn_time: float = 50,
        generate_descending_stair: bool = True,
        tileset=None,
        terrain: dict = None,
        additional_terrain: dict = None,
        remove_all_terrain_of_type: Optional[Tuple[str]] = None,

        # TODO Add biome-differentiated monster generating system feature
    ):
        """
        Args:
            biome_color:
                A color representation of this biome.
                Can be used in many different visual aspects.
                NOTE: It is highly recommended to use low contrast, dark tone colors since it is mainly used for background coloring.
            biome_desc:
                Recommended not to write more than 5 lines.
                Each lines should contain less than 110 characters. (Including blanks)
            respawn_ratio:
                This parameter is connected to the maximum number of monsters that can be spawned by the gamemap's monster regeneration.
                The value itself means the maximum ratio of the monster number compared to the original monster number when the gamemap was first generated.
                ex. respawn_ratio = 0.5, starting monster number = 100
                > If more than 50 monster die or leaves the game map, monster regeneration begins.
                > Which means, unless more than 50 monsters die, the gamemap will not regenerate any monster.
            respawn_time:
                Time that takes for a single loop of monster regeneration. (In-game turn)
            generate_descending_stair:
                Whether to randomize descending stair or not.
                e.g. you can set this to False when generating last level (maximum depth)
            tileset:
                tileset of this biome.
                The arguments must be passed by using the "tileset() function" above.
            terrain:
                Possible terrains for this gamemap/biome.
                key - terrain id (string)
                value - weight (integer)
            additional_terrain:
                If you want to modify specific terrain's rarity, or add specific terrain to the biome, use this value.
                You can modify self.terrain directly is there's a lot of changes to be made from default terrain list.
            remove_all_terrain_of_type:
                iterate through tileset, and remove all tileset that satisfies the given condition.
                e.g.
                remove_all_terrain_of_type = ("has_door", "gen_traps")
                -> Will set rarity of terrains that has door OR generate traps to 0
        """
        if tileset is None:
            tileset = get_tileset()
        self.tileset = tileset
        self.name = name
        self.biome_id = biome_id
        self.biome_desc = biome_desc
        self.rarity = rarity
        self.biome_color = biome_color
        self.max_rooms = max_rooms
        self.map_width = map_width
        self.map_height = map_height
        self.respawn_ratio = respawn_ratio
        self.respawn_time = respawn_time
        self.generate_descending_stair = generate_descending_stair
        if terrain is None:
            import terrain_factories
            terrain = terrain_factories.terrain_dict
        self.terrain = copy.deepcopy(terrain)

        if remove_all_terrain_of_type:
            for string in remove_all_terrain_of_type:
                if string == "spawn_door":
                    for k in self.terrain.keys():
                        if k.spawn_door:
                            self.terrain[k] = 0
                #TODO Add other conditions

        if additional_terrain: # Handled after removal
            for k, v in additional_terrain.items():
                key = self.find_terrain_of_id(k.terrain_id)
                if self.terrain[key]:
                    print(f"DEBUG::Replacing {key.terrain_id} of rarity {self.terrain[key]} to rarity {v}. - biome: {self.biome_id}")
                self.terrain[key] = v # Could overwrite existing value

    def find_terrain_of_id(self, terrain_id: str):
        """Search self.terrain and return the Terrain obj with given id."""
        for terr in self.terrain:
            if terr.terrain_id == terrain_id:
                return terr
        raise Exception(f"ERROR::Could not find terrain {terrain_id} from biome.terrain")
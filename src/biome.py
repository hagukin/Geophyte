from typing import Tuple
import tiles
import color

def tileset(
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
        max_rooms: int = 3000,
        map_width: int = 70, # min 70
        map_height: int = 45, # min 45
        respawn_ratio: float = 0.4,
        respawn_time: float = 50,
        max_monsters_per_room: int = 4,
        max_items_per_room: int = 4,
        tileset: dict = tileset(),
        terrain: dict = None,
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
            tileset:
                tileset of this biome.
                The arguments must be passed by using the "tileset() function" above.
            terrain:
                Possible terrains for this gamemap/biome.
                key - terrain id (string)
                value - weight (integer)
        """
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
        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room
        self.tileset = tileset
        self.terrain = terrain
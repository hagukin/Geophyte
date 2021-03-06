import tile_types

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
        "t_wall":tile_types.wall,
        "t_border":tile_types.vintronium,
        "t_floor":tile_types.floor,
        "t_dense_grass":tile_types.dense_grass,
        "t_sparse_grass":tile_types.sparse_grass,
        "t_ascending_stair":tile_types.ascending_stair,
        "t_descending_stair":tile_types.descending_stair,
        "t_burnt_floor":tile_types.burnt_floor,
        "t_deep_pit":tile_types.deep_pit,
        "t_shallow_pit":tile_types.shallow_pit,
        "t_deep_water":tile_types.deep_water,
        "t_shallow_water":tile_types.shallow_water,
        "t_DEBUG":tile_types.DEBUG,
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
        self.max_rooms = max_rooms
        self.map_width = map_width
        self.map_height = map_height
        self.respawn_ratio = respawn_ratio
        self.respawn_time = respawn_time
        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room
        self.tileset = tileset
        self.terrain = terrain
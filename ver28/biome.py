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
        terrain: dict = {        },
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
            terrain:
                Possible terrains for this gamemap/biome.
                TODO feature currently under development.
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
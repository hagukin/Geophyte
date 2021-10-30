import copy
from typing import Tuple, List, Optional, TYPE_CHECKING, Dict
import tiles
import color
import actor_factories

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
        biome_bgm_id: str = "",
        biome_bgs_id: str = "",
        rarity: int = 1,
        room_spacing: int = 1,
        biome_color: Tuple = color.black,
        max_rooms: int = 100,
        map_width: int = 67, # min 67
        map_height: int = 41, # min 41
        monster_difficulty: Dict=None,
        respawn_ratio: float = 0.8,
        respawn_time: float = 50,
        generate_descending_stair: bool = True,
        tileset=None,
        terrain: dict = None,
        additional_terrain: dict = None,
        remove_all_terrain_of_type: Optional[Tuple[str, ...]] = None,
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
            room_spacing:
                minimum X axis distance between each room.
                should always have value over 0. (default 1)
                higher the value gets, the biome gets less compact.
                NOTE: Use room_x_spacing or room_y_spacing instead.
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
            monster_difficulty:
                Dictionary. Key - difficulty, value - weight
                If not None, every monster generated in this biome will be clamped into given difficulty range.
                e.g. {5: 3, 6: 1}

                NOTE: If terrain in the biome has specifed monster generation dictionary(monster_to_spawn),
                    it will ignore this limit range.
                NOTE: This value DO AFFECT respawning monsters.
                NOTE: If you set this value to something weird, for example{999: 1}, the game has potential danger of stucking in infinite loop which is extremely bad.
                We do check if every key is valid beforehand, still it is highly recommended to follow the following rules:
                    1) dictionary should have more than 1 item.
                    2) you should check each keys in the dictionary is valid.
        """
        if tileset is None:
            tileset = get_tileset()
        self.tileset = tileset
        self.name = name
        self.biome_id = biome_id
        self.biome_desc = biome_desc
        self.biome_bgm_id = biome_bgm_id
        self.biome_bgs_id = biome_bgs_id
        self.rarity = rarity
        self._room_x_spacing = room_spacing
        if self._room_x_spacing < 1:
            print(f"WARNING::Biome {name} has room_spacing less than 1.")
            self._room_x_spacing = 1
        if self._room_x_spacing > map_width / 2: # Too sparse
            print(f"WARNING::Biome {name} has room_spacing value as {self._room_x_spacing}. Are you sure this is the right value?")
        self._room_y_spacing = max(1, int(self._room_x_spacing * map_height / map_width))
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
                elif string == "gen_grass":
                    for k in self.terrain.keys():
                        if k.gen_grass:
                            self.terrain[k] = 0
                elif string == "gen_plants":
                    for k in self.terrain.keys():
                        if k.gen_grass:
                            self.terrain[k] = 0
                #TODO Add other conditions

        if additional_terrain: # Handled after removal
            for k, v in additional_terrain.items():
                key = self.find_terrain_of_id(k.terrain_id)
                if self.terrain[key]:
                    print(f"DEBUG::Replacing {key.terrain_id} of rarity {self.terrain[key]} to rarity {v}. - biome: {self.biome_id}")
                self.terrain[key] = v # Could overwrite existing value

        self.monster_difficulty = monster_difficulty
        if self.monster_difficulty:
            self.adjust_biome_monster_difficulty()

    @property
    def room_x_spacing(self) -> int:
        return self._room_x_spacing

    @property
    def room_y_spacing(self) -> int:
        return self._room_y_spacing

    def adjust_biome_monster_difficulty(self) -> None:
        """Search for any potential error which could be caused from wrong monster difficulty key value.
        e.g. if mosnter difficulty is {1 : 5, 9999: 3}, 9999 is removed since there are no mosnters that has difficulty 9999.
        likewise, is monster difficulty is {28: 1}, and 28 is a valid difficulty but there is no monster that has difficulty 28, it is removed as well."""
        remove_key = []
        for key in self.monster_difficulty.keys():
            if key not in actor_factories.ActorDB.monster_difficulty.keys():
                print(f"ERROR::Biome {self.biome_id} has monster_difficulty specified and key {key} is invalid. Key is removed.")
                remove_key.append(key)
                continue
            elif not actor_factories.ActorDB.monster_difficulty[key]:
                print(f"ERROR::Biome {self.biome_id} has monster_difficulty specified and key {key} is valid, but there are no monsters that belong to {key} key difficulty. Key is removed.")
                remove_key.append(key)
                continue
        for remove in remove_key:
            self.monster_difficulty.pop(remove)

    def find_terrain_of_id(self, terrain_id: str):
        """Search self.terrain and return the Terrain obj with given id."""
        for terr in self.terrain:
            if terr.terrain_id == terrain_id:
                return terr
        raise Exception(f"ERROR::Could not find terrain {terrain_id} from biome.terrain")
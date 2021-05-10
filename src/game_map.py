from __future__ import annotations
import numpy as np  # type: ignore
import random
import tile_factories

from typing import Iterable, Iterator, Optional, Tuple, List, TYPE_CHECKING
from entity import Actor, Item, SemiActor
from order import TilemapOrder

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from biome import Biome
    from tile import Tile


class GameMap:
    def __init__(
        self, depth: int, engine: Engine, biome: Biome, entities: Iterable[Entity] = (),
    ):
        """
        Vars:
            tiles:
                Tile objects mapped to x,y coordinates.
            sprites:
                Current sprite objects mapped to x,y coordinates.
            NOTE: Tiles stores the gamemap data, and sprites stores the graphical information.
        """
        self.depth = depth
        self.engine = engine
        self.biome = biome
        self.width, self.height = biome.map_width, biome.map_height

        self.entities = list(entities)

        self.tileset = biome.tileset # initialized at procgen

        self.tiles = np.full((biome.map_width, biome.map_height), fill_value=tile_factories.debug_tile(), order="F")
        self.sprites = np.full((biome.map_width, biome.map_height), fill_value=tile_factories.shroud().skin.light(), order="F")

        self.tilemap = np.full((biome.map_width, biome.map_height), fill_value=TilemapOrder.VOID.value, order="F")
        self.tunnelmap = np.full((biome.map_width, biome.map_height), fill_value=True, order="F")# Set to True=tunnel can be built on that location
        self.protectmap = np.full((biome.map_width, biome.map_height), fill_value=False, order="F")# Set to True=terrain cannot overwrite(generate onto) that location
        self.ascend_loc = None # Location of ascending stair that goes to the upper floor.
        self.descend_loc = None

        self.starting_monster_num = 0 # The number of monsters that are spawned when the gamemap is generated. This value is initialized at procgen.spawn_monster().
        self.respawn_ratio = biome.respawn_ratio # go to biome.py for detailed description
        self.respawn_time = biome.respawn_time
        self.respawn_turn_left = 0

        self.visible = np.full(
            (biome.map_width, biome.map_height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (biome.map_width, biome.map_height), fill_value=False, order="F"
        )  # Tiles the player has seen before

    @property
    def gamemap(self) -> GameMap:
        return self

    def __deepcopy__(self, memo):
        return self ##TODO TEST Disabled deepcopy

    def fill_tiles_with(self, tile_function, randomize: bool):
        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[0])):
                self.tiles[x,y] = tile_function(randomize)

    def is_type(self, entity: Entity, types: Tuple[str]) -> bool:
        for t in types:
            if t == "actor" and isinstance(entity, Actor) and not entity.is_dead:
                return True
            elif t == "item" and isinstance(entity, Item):
                return True
            elif t == "semiactor" and isinstance(entity, SemiActor):
                return True
        return False
    
    def typed_entities(self, types: List[str]) -> Iterator[Entity]:
        """Iterate over this maps entities of given types."""
        yield from (
            entity
            for entity in self.entities
            if self.is_type(entity, types)
        )

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and not entity.is_dead
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in reversed(self.entities) if isinstance(entity, Item))

    @property
    def semiactors(self) -> Iterator[SemiActor]:
        """Iterate over this maps active semiactors, and return in list."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, SemiActor) and entity.is_active
        )

    def get_all_blocking_entities_at_location(self, location_x, location_y) -> Iterator[Entity]:
        yield from (entity for entity in reversed(self.entities) if (entity.blocks_movement and entity.x == location_x and entity.y == location_y))

    def get_any_entity_at_location(
        self, location_x: int, location_y: int, exception=None,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (entity.x == location_x and entity.y == location_y and entity != exception):
                return entity

        return None

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def get_all_actors_at_location(self, x: int, y: int) -> Optional[List]:
        tmp = []
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                tmp.append(actor)
        if len(tmp):
            return tmp
        return None

    def get_all_items_at_location(self, x: int, y: int) -> Optional[List[Item]]:
        tmp = []
        for item in self.items:
            if item.x == x and item.y == y:
                tmp.append(item)
        if len(tmp):
            return tmp
        return None

    def get_item_at_location(self, x: int, y: int) -> Optional[Item]:
        for item in self.items:
            if item.x == x and item.y == y:
                return item

        return None

    def get_semiactor_at_location(self, x: int, y: int) -> Optional[SemiActor]:
        for semiactor in self.semiactors:
            if semiactor.x == x and semiactor.y == y:
                return semiactor

        return None

    def get_semiactor_with_bumpaction_at_location(self, x: int, y: int) -> Optional[SemiActor]:
        for semiactor in self.semiactors:
            if semiactor.x == x and semiactor.y == y and semiactor.bump_action:
                return semiactor
        
        return None

    def get_all_semiactors_at_location(self, x: int, y: int) -> Optional[List[SemiActor]]:
        tmp = []
        for semiactor in self.semiactors:
            if semiactor.x == x and semiactor.y == y:
                tmp.append(semiactor)
        if len(tmp):
            return tmp
        return None

    def check_if_id_at_location(self, entity_id: str, x: int, y: int) -> bool:
        for entity in self.entities:
            if (entity.x == x and entity.y == y and entity.entity_id == entity_id):
                return True
        return False

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def remove_dup_entities(self) -> None:
        self.entities = list(set(self.entities))
    
    def sort_entities(self) -> None:

        self.remove_dup_entities()

        for i in range(len(self.entities)):
            self.entities[i].entity_order = len(self.entities) - i

        self.entities = sorted(
            self.entities, key=lambda x: (x.render_order.value, -x.entity_order)
        )

    def respawn_monsters(self) -> None:
        """
        Respawn monsters for this gamemap.
        This method is called once per turn, only if the player is on this gamemap.
        """
        if self.respawn_turn_left == self.respawn_time:
            # Reset time left
            self.respawn_turn_left = 0

            # Check if there is enough monsters in this gamemap or not
            actor_num = 0
            for entity in self.entities:
                if isinstance(entity, Actor) and not entity.is_dead:
                    actor_num += 1

            if actor_num > int(self.starting_monster_num * self.respawn_ratio):
                return None

            # If player can see every single parts of the map, a monster will not be generated.
            if False in self.visible:
                try_count = 1

                # To prevent looping infinitly, this method will stop searching for place to spawn monster after 10 tries.
                while try_count < 10:
                    random_x = random.randint(3, self.width - 3)
                    random_y = random.randint(3, self.height - 3)

                    # A tile should not be visible currently, should be walkable, and there should be no entities on it.
                    if self.visible[random_x, random_y]:
                        try_count += 1
                        continue
                    elif not self.tiles["walkable"][random_x, random_y]:
                        try_count += 1
                        continue
                    elif any(entity.x == random_x and entity.y == random_y for entity in self.entities):
                        try_count += 1
                        continue
                    else:
                        # TODO: change tpyes of monster spawned depending on the biome type
                        # TODO: the monster difficulty should rise as time goes on to prevent farming. This can be done by adjusting the toughness parameter.
                        import procgen
                        difficulty_chosen = procgen.choose_monster_difficulty(depth=self.depth, toughness=1)
                        procgen.spawn_monsters_by_difficulty(x=random_x, y=random_y, difficulty=difficulty_chosen, dungeon=self, spawn_awake=True, is_first_generation=False)
                        
                        break
        # Add turn
        self.respawn_turn_left += 1

    def get_names_at_location(self, tile_x: int, tile_y: int, display_id: bool = False) -> str:
        """
        Display entity's name that are at the mouse cursor location. (Only when the location is visible)
        """
        if not self.engine.camera.abs_in_bounds(tile_x, tile_y) or not self.visible[tile_x, tile_y]:
            return ""

        names = []

        for entity in reversed(self.entities):
            if entity.x == tile_x and entity.y == tile_y:
                if display_id:
                    names.append(f"{id(entity)}:{entity.name}")
                    continue

                if isinstance(entity, Item):
                    # If entity is a item, display stack_count as well
                    if entity.stack_count > 1:
                        names.append(f"{entity.name} x{entity.stack_count}")
                    else:
                        names.append(entity.name)
                elif isinstance(entity, Actor):
                    if entity.ai:
                        if entity.ai.owner == self.engine.player:
                            names.append(f"펫 {entity.name}")
                        else:
                            names.append(entity.name)
                    else:
                        names.append(entity.name)
                else:
                    names.append(entity.name)

        names = ", ".join(names)
        names = names[0:self.engine.config["render_on_mouse_entity_letter_width"]]

        return names.capitalize()

    def get_tile_name_at_location(self, tile_x: int, tile_y: int) -> str:
        """
        Display tile's name that are at the mouse cursor location. (Only when the location is explored)
        """
        if not self.engine.camera.abs_in_bounds(tile_x, tile_y) or not self.explored[tile_x, tile_y]:
            return ""

        return self.tiles[tile_x, tile_y].tile_name.capitalize()
from __future__ import annotations

import numpy as np  # type: ignore
import random
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from entity import Actor, Item, SemiActor
from order import TilemapOrder

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from biome import Biome


class GameMap:
    def __init__(
        self, depth: int, engine: Engine, biome: Biome, entities: Iterable[Entity] = (),
    ):
        self.depth = depth
        self.engine = engine
        self.biome = biome
        self.width, self.height = biome.map_width, biome.map_height
        self.entities = list(entities)

        self.tileset = biome.tileset # initialized at procgen

        self.tiles = np.full((biome.map_width, biome.map_height), fill_value=tile_types.DEBUG(), order="F")
        self.tilemap = np.full((biome.map_width, biome.map_height), fill_value=TilemapOrder.VOID.value, order="F")
        self.tunnelmap = np.full((biome.map_width, biome.map_height), fill_value=True, order="F")# Set to True=tunnel can be built on that location
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
    def semiactors(self) -> Iterator[Actor]:
        """Iterate over this maps active semiactors, and return in list."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, SemiActor) and entity.is_active
        )

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


    def get_item_at_location(self, x: int, y: int) -> Optional[Item]:
        for item in self.items:
            if item.x == x and item.y == y:
                return item

        return None

    def get_semiactor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for semiactor in self.semiactors:
            if semiactor.x == x and semiactor.y == y:
                return semiactor

        return None

    def get_semiactor_with_bumpaction_at_location(self, x: int, y: int) -> Optional[Actor]:
        for semiactor in self.semiactors:
            if semiactor.x == x and semiactor.y == y and semiactor.bump_action:
                return semiactor
        
        return None

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

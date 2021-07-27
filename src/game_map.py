from __future__ import annotations

import numpy as np  # type: ignore
import random

from numpy.lib.arraysetops import isin
import tiles

from typing import Iterable, Iterator, Optional, Tuple, List, TYPE_CHECKING
from entity import Actor, Item, SemiActor
from order import TilemapOrder
from game import Game

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from biome import Biome


class GameMap:
    def __init__(
        self, depth: int, biome: Biome, entities: Iterable[Entity] = (),
    ):
        self.depth = depth
        self.biome = biome
        self.width, self.height = biome.map_width, biome.map_height
        self.entities = list()

        self.tileset = biome.tileset # initialized at procgen

        self.tiles = np.full((biome.map_width, biome.map_height), fill_value=tiles.DEBUG(), order="F")
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

    @property
    def engine(self) -> Engine:
        return Game.engine

    def is_type(self, entity: Entity, types: Tuple(str)) -> bool:
        for t in types:
            if t == "actor" and isinstance(entity, Actor) and not entity.is_dead:
                return True
            elif t == "item" and isinstance(entity, Item):
                return True
            elif t == "semiactor" and isinstance(entity, SemiActor):
                return True
        return False
    
    def typed_entities(self, types: List(str)) -> Iterator[Entity]:
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
    def semiactors(self) -> Iterator[Actor]:
        """Iterate over this maps active semiactors, and return in list."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, SemiActor) and entity.is_active
        )

    def remove_entity(self, entity: Entity) -> None:
        """Removes all connection with the given entity.
        Its recommended to use this method instead of doing gamemap.entities.remove(something)"""
        try:
            self.entities.remove(entity)
        except ValueError:
            raise Exception(f"ERROR::{entity.entity_id} is not in gamemap.entities.")

    def check_tile_monster_spawnable(self, x:int, y:int, must_not_be_in_sight: bool=False):
        if must_not_be_in_sight and self.visible[x, y]:
            return False
        if any(entity.x == x and entity.y == y for entity in self.entities) or not self.tiles["walkable"][x, y]:
            return False
        else:
            return True

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

    def get_all_actors_at_location(self, x: int, y: int) -> Optional[Actor]:
        tmp = []
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                tmp.append(actor)
        if len(tmp):
            return tmp
        return None

    def get_all_items_at_location(self, x: int, y: int) -> Optional[Item]:
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

    def get_all_semiactors_at_location(self, x: int, y: int) -> Optional[SemiActor]:
        tmp = []
        for semiactor in self.semiactors:
            if semiactor.x == x and semiactor.y == y:
                tmp.append(semiactor)
        if len(tmp):
            return tmp
        return None

    def get_random_tile(
            self,
            should_no_entity: bool = False,
            should_walkable: bool = False,
            should_safe_to_walk: bool = False,
            should_transparent: bool = False,
            should_not_walkable: bool = False,
            should_not_safe_to_walk: bool = False,
            should_not_transparent: bool = False,
            threshold: Optional[int] = 5000,
            return_random_location_if_not_found: bool = False,
    ) -> Tuple[int,int]:
        """
        Args:
            threshold:
                Max try count.
                If None, try indefinitely.
        """
        t = -1
        while (threshold == None) or (threshold != None and t < threshold):
            t += 1
            x = random.randint(1, self.width - 1)
            y = random.randint(1, self.height - 1)

            if should_no_entity and self.get_any_entity_at_location(x,y) != None:
                continue
            if should_walkable and not self.tiles[x,y]["walkable"]:
                continue
            if should_safe_to_walk and not self.tiles[x,y]["safe_to_walk"]:
                continue
            if should_transparent and not self.tiles[x,y]["transparent"]:
                continue
            if should_not_walkable and self.tiles[x,y]["walkable"]:
                continue
            if should_not_safe_to_walk and self.tiles[x,y]["safe_to_walk"]:
                continue
            if should_not_transparent and self.tiles[x,y]["transparent"]:
                continue
            return (x,y)

        if return_random_location_if_not_found:
            x = random.randint(1, self.width - 1)
            y = random.randint(1, self.height - 1)
            print("ERROR::CAN'T FIND APPROPRIATE TILE. RETURNING RANDOM TILE INSTEAD.")
            return (x,y)
        else:
            print("ERROR::CAN'T FIND APPROPRIATE TILE. RETURNING (0,0) INSTEAD.")
            return (0,0)

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

    def update_enemy_fov(self, is_initialization: bool=False) -> None:
        """
        Recomputes the vision of actors on this gamemap (besides player)
        This function is called every turn, but the actual update might not be called every turn due to perf. issues.
        """
        for actor in set(self.actors):
            # initialize actors vision
            if is_initialization:
                if actor.ai:
                    actor.ai.init_vision()

            ## The game will not update every actor's vision/additional vision every turn due to performance issues
            # actor.ai.update_vision()
            # if actor.actor_state.has_telepathy\
            #     or actor.actor_state.is_detecting_obj[2]:
            #     self.update_additional_vision(actor=actor)

    def adjustments_before_new_map(self, update_player_fov: bool=False):
        self.sort_entities()
        if update_player_fov:
            self.engine.update_fov()
            self.engine.update_entity_in_sight(is_initialization=True)
        self.update_enemy_fov(is_initialization=True)

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
                    if not self.check_tile_monster_spawnable(random_x, random_y, must_not_be_in_sight=True):
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

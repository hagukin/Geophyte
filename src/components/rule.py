from __future__ import annotations

import numpy as np  # type: ignore
import tcod
import random
import semiactor_factories

from components.base_component import BaseComponent
from typing import List, Tuple
    

class BaseRule(BaseComponent):
    def __init__(self):
        self.parent = None

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """
        Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.parent.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.parent.gamemap.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.parent.x, self.parent.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class FireRule(BaseRule):
    def __init__(self, base_damage: int=3, add_damage: int=1, fire_duration: int=6):
        super().__init__()
        self.base_damage = base_damage
        self.add_damage = add_damage
        self.fire_duration = fire_duration


    def perform(self) -> None:
        # Decrease liftime
        if self.parent.lifetime > 0:
            self.parent.lifetime -= 1

        # Delete old entities
        if self.parent.lifetime == 0:
            self.engine.game_map.tiles[self.parent.x, self.parent.y] = self.engine.game_map.tileset["t_burnt_floor"]()
            self.parent.remove_self()
            return None

        # Set Random Graphics
        color = random.randint(1, 4)
        if color == 1:
            self.parent._fg = (255, 255, 255)
            self.parent._bg = (254, 212, 1)
        elif color == 2:
            self.parent._fg = (235, 66, 1)
            self.parent._bg = (254, 139, 0)
        elif color == 3:
            self.parent._fg = (255, 179, 54)
            self.parent._bg = (251, 122, 14)
        elif color == 4:
            self.parent._fg = (254, 212, 1)
            self.parent._bg = (239, 239, 231)

        # Collision with entities
        # NOTE: Actual calculations are handled in entity.collided_with_fire()
        for entity in self.engine.game_map.entities:
            if entity.x == self.parent.x and entity.y == self.parent.y:
                entity.collided_with_fire(self.parent)

        # Remove entity if floor is not flammable
        if self.engine.game_map.tiles[self.parent.x, self.parent.y]["flammable"] == False:
            self.parent.remove_self()
            return None

        # Spread fire
        spread_dir = ((1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,-1), (-1,1), (1,-1))

        for direction in spread_dir:
            if self.engine.game_map.tiles[self.parent.x + direction[0], self.parent.y + direction[1]]["flammable"]:
                # Check if there is any other fire semiactor on the tile
                flag = False
                semiactors = self.engine.game_map.get_all_semiactors_at_location(self.parent.x + direction[0], self.parent.y + direction[1])
                if semiactors:
                    for semiactor in semiactors:
                        if semiactor.entity_id == "fire":
                            flag = True
                if flag:
                    continue

                # chance of catching fire depends on "flammable"
                if random.random() <= self.engine.game_map.tiles[self.parent.x + direction[0], self.parent.y + direction[1]]["flammable"]:
                    semiactor_factories.fire.spawn(self.engine.game_map, self.parent.x + direction[0], self.parent.y + direction[1], 6)



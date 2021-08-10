from game_map import GameMap
from terrain import Terrain
from typing import Tuple, List
from game_map import GameMap
from order import TilemapOrder
from entity import Actor
import numpy as np

class Room:
    def __init__(self, x: int, y: int, width: int, height: int, parent: GameMap, terrain: Terrain):
        """
        Vars:
            protectmap:
                Similar to gamemap's protect map, except it only shows the protected area of this particular room.
                (Only this room's area is marked as 1 if its protected.)
        """
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
        self.width = width
        self.height = height
        self.parent = parent # gamemap
        self.room_protectmap = np.full((parent.biome.map_width, parent.biome.map_height), fill_value=False, order="F")
        self.terrain = terrain
        self.doors = [] # door locations (not convex)
        
    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array indexes."""
        raise NotImplementedError()

    @property
    def outer(self) -> Tuple[slice, slice]:
        """Return the outer(walls) + inner area of this room as a 2D array index."""
        raise NotImplementedError()

    @property
    def inner_tiles(self): # Returns List of Tuples
        """Return the list of all coordinates of this room's inner tiles."""
        tile_coordinates = []
        for inner_slice in self.inner:
            x1 = inner_slice[0].start
            x2 = inner_slice[0].stop
            y1 = inner_slice[1].start
            y2 = inner_slice[1].stop
            for x in range(x1, x2):
                for y in range(y1, y2):
                    tile_coordinates.append((x, y))
        
        return tile_coordinates

    @property
    def outer_tiles(self): #TODO TEST
        """Return the list of all coordinates of this room's wall + inner tiles."""
        tile_coordinates = []
        for outer_slice in self.outer:
            x1 = outer_slice[0].start
            x2 = outer_slice[0].stop
            y1 = outer_slice[1].start
            y2 = outer_slice[1].stop
            for x in range(x1, x2):
                for y in range(y1, y2):
                    tile_coordinates.append((x, y))
        
        return tile_coordinates

    @property
    def wall_tiles(self): #TODO NOT TESTED
        """Return the list of all coordinates of this room's wall tiles."""
        return list(set(self.outer_tiles) - set(self.inner_tiles))

    def intersects(self, other) -> bool: # other = other room
        """Return True if this room overlaps with another room of any type."""
        for tile_slice in self.outer:
            # Check for tiles that should not collide with other rooms
            if TilemapOrder.ROOM_INNER.value in self.parent.tilemap[tile_slice]\
                or TilemapOrder.TUNNEL.value in self.parent.tilemap[tile_slice]\
                or 1 in self.parent.protectmap[tile_slice]: #NOTE: Warning - It's only checking the room area, not the door convex area. Which means that door convexes can still collided with protected area!
                return True
            # NOTE: The following lines of code prevents protected room being generated onto door/door convex location.
            # Preventing door being generated onto protected room is handled during door_generation in procgen.py.
            if self.terrain.protected:
                # Check if there is any door / door convex on this room's location.
                if TilemapOrder.DOOR.value in self.parent.tilemap[tile_slice]\
                    or TilemapOrder.DOOR_CONVEX.value in self.parent.tilemap[tile_slice]:
                    return True

        return False

    def get_door_dir(self, x: int, y: int) -> str:
        """returns direction of the given location of the door convex."""
        if x == self.x2:
            return 'r'
        elif x == self.x1:
            return 'l'
        elif y == self.y1:
            return 'u'
        elif y == self.y2:
            return 'd'
        else:
            raise Exception("FATAL ERROR::Cannot find the door anywhere on the edge of the room.")
    
    def check_if_in_room(self, x:int, y: int) -> bool:
        """Check if the given coordinates is in this room's inner area."""
        for cor in self.inner_tiles:
            if cor[0] == x and cor[1] == y:
                return True
        return False

    def door_up(self) -> Tuple[slice, slice]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        raise NotImplementedError()

    def door_left(self) -> Tuple[slice, slice]:
        """Randomly randomize door convex location next to the left wall, and return the location as a 2D array index."""
        raise NotImplementedError()

    def door_right(self) -> Tuple[slice, slice]:
        """Randomly randomize door convex location next to the right wall, and return the location as a 2D array index."""
        raise NotImplementedError()

    def door_down(self) -> Tuple[slice, slice]:
        """Randomly randomize door convex location next to the lower wall, and return the location as a 2D array index."""
        raise NotImplementedError()

    def get_actors_in_room(self) -> List[Actor]:
        """
        Returns a list of actors that are currently in the room.
        Standing on the door is considered outside of the room.

        TODO FIXME Function not tested yet
        """
        actors_in_room = []
        for inner_slice in self.inner:
            x1 = inner_slice[0].start
            x2 = inner_slice[0].stop
            y1 = inner_slice[1].start
            y2 = inner_slice[1].stop
            for actor in self.parent.actors:
                if x1 <= actor.x < x2 and y1 <= actor.y < y2:
                    actors_in_room.append(actor)
        
        return actors_in_room



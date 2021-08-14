import random
import copy
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
            width:
                including outer walls
        """
        self.x1 = x
        self.y1 = y
        self.width = width
        self.height = height
        self.parent = parent # gamemap
        self.terrain = terrain
        self.doors_rel = {} # Contains ("dir": (x,y))
        self.door_convexes_rel = {}  # Contains ("dir": (x,y))
        self.init_doors_rel()

    @property
    def single_door(self) -> Tuple[int,int]:
        """Return the only door location this room has. Used in shops, etc."""
        tmp = list(self.doors.values())
        if len(tmp) != 1:
            print("WARNING::Room has more or less than 1 door but called room.single_door property.")
        return list(self.doors.values())[0]

    @property
    def doors(self):
        """Returns absolute coordinates"""
        tmp = copy.copy(self.doors_rel)
        for k, coor in tmp.items():
            tmp[k] = (coor[0]+self.x1, coor[1]+self.y1)
        return tmp

    @property
    def door_convexes(self):
        """Returns absolute coordinates"""
        tmp = copy.copy(self.door_convexes_rel)
        for k, coor in tmp.items():
            tmp[k] = (coor[0] + self.x1, coor[1] + self.y1)
        return tmp

    def door_ups_rel(self) -> List[Tuple[int, int]]:
        raise NotImplementedError()

    def door_lefts_rel(self) -> List[Tuple[int, int]]:
        raise NotImplementedError()

    def door_rights_rel(self) -> List[Tuple[int, int]]:
        raise NotImplementedError()

    def door_downs_rel(self) -> List[Tuple[int, int]]:
        raise NotImplementedError()

    def init_doors_rel(self) -> None:
        # set door position (Not actually generating)
        # choose the direction of the door
        tempdir = ["u", "d", "l", "r"]
        random.shuffle(tempdir)
        door_num = random.choices(self.terrain.door_num_range, self.terrain.door_num_weight, k=1)[0]
        door_directions = []
        for i in range(door_num):
            door_directions.append(tempdir[i % 4])  # udlr 1234

        for direction in door_directions:
            if direction == 'u':
                dx = 0
                dy = -1
                door_x, door_y = random.choice(self.door_ups_rel())
            elif direction == 'd':
                dx = 0
                dy = 1
                door_x, door_y = random.choice(self.door_downs_rel())
            elif direction == 'l':
                dx = -1
                dy = 0
                door_x, door_y = random.choice(self.door_lefts_rel())
            elif direction == 'r':
                dx = 1
                dy = 0
                door_x, door_y = random.choice(self.door_rights_rel())
            else:
                print(f"FATAL ERROR::Invalid door direction - {direction}. Using Upper direction instead.")
                dx = 0
                dy = -1
                door_x, door_y = random.choice(self.door_ups_rel())

            self.door_convexes_rel[direction] = (door_x + dx, door_y + dy)
            self.doors_rel[direction] = (door_x, door_y)

    @property
    def x2(self):
        return self.x1 + self.width - 1

    @property
    def y2(self):
        return self.y1 + self.height - 1

    def move(self, x: int=0, y: int=0):
        self.x1 = x
        self.y1 = y
        
    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> List[Tuple[slice, slice]]:
        """Return the inner area of this room as a 2D array indexes."""
        raise NotImplementedError()

    @property
    def outer(self) -> List[Tuple[slice, slice]]:
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
        """Return True if this room overlaps with another room of any type
        OR if the room is out of map bound."""

        # Collided with map border
        if self.x2 > self.parent.tiles.shape[0] - 4 or self.y2 > self.parent.tiles.shape[1] - 4\
            or self.x1 < 4 or self.y1 < 4:
            return True

        for tile_slice in self.outer:
            # Check for tiles that should not collide with other rooms
            if TilemapOrder.ROOM_INNER.value in self.parent.tilemap[tile_slice]\
                or TilemapOrder.TUNNEL.value in self.parent.tilemap[tile_slice] \
                or TilemapOrder.DOOR_CONVEX.value in self.parent.tilemap[tile_slice]\
                or 1 in self.parent.protectmap[tile_slice]: #NOTE: Warning - It's only checking the room area, not the door convex area. Which means that door convexes can still collided with protected area!
                return True
            # NOTE: The following lines of code prevents protected room being generated onto door/door convex location.
            # Preventing door being generated onto protected room is handled during door_generation in procgen.py.
            if self.terrain.protected:
                # Check if there is any door / door convex on this room's location.
                if TilemapOrder.DOOR.value in self.parent.tilemap[tile_slice]\
                    or TilemapOrder.DOOR_CONVEX.value in self.parent.tilemap[tile_slice]:
                    return True
        for door_loc in self.doors.values():
            if (self.parent.protectmap[door_loc] == 1 and not self.check_if_in_room(*door_loc))\
                or self.parent.tilemap[door_loc] == TilemapOrder.DOOR.value\
                or self.parent.tilemap[door_loc] == TilemapOrder.DOOR_CONVEX.value\
                or self.parent.tilemap[door_loc] == TilemapOrder.MAP_BORDER.value:
                return True
            for dx, dy in ((1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                if self.parent.tilemap[door_loc[0]+dx, door_loc[1]+dy] == TilemapOrder.DOOR.value:
                    print("LOG::Prevented adjacent door generation")
                    return True
        for door_con_loc in self.door_convexes.values():
            if (self.parent.protectmap[door_con_loc] == 1 and not self.check_if_in_room(*door_con_loc)) \
                or self.parent.tilemap[door_con_loc] == TilemapOrder.ROOM_WALL.value\
                or self.parent.tilemap[door_con_loc] == TilemapOrder.DOOR.value \
                or self.parent.tilemap[door_con_loc] == TilemapOrder.MAP_BORDER.value:
                return True
        return False
    
    def check_if_in_room(self, x:int, y: int) -> bool:
        """Check if the given coordinates is in this room's inner area."""
        for inner_slice in self.inner:
            if x <= inner_slice[0].stop and x >= inner_slice[0].start and y <= inner_slice[1].stop and y >= inner_slice[1].start:
                return True
        return False

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



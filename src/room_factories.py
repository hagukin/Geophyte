import random

from game_map import GameMap
from terrain import Terrain
from typing import Tuple
from game_map import GameMap
from order import TilemapOrder


class Room:
    def __init__(self, x: int, y: int, width: int, height: int, parent: GameMap, terrain: Terrain):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
        self.width = width
        self.height = height
        self.parent = parent
        self.tilemap = parent.tilemap
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
            if TilemapOrder.ROOM_INNER.value in self.tilemap[tile_slice] or TilemapOrder.TUNNEL.value in self.tilemap[tile_slice]:
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
            raise Exception() #Wrong coordinates


class RectangularRoom(Room):
    """
    Example.
    height = 6, width = 7

    ##+++##
    #.....#
    +.....+
    +.....+
    #.....#
    ##+++##

    + : possible door generation location 
    """
    def __init__(self, x: int, y: int, width: int, height: int, parent: GameMap, terrain: Terrain):
        super().__init__(x, y, width, height, parent, terrain)

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return [(slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2))]

    @property
    def outer(self) -> Tuple[slice, slice]:
        """Return the outer(walls) + inner area of this room as a 2D array index."""
        return [(slice(self.x1, self.x2 + 1), slice(self.y1, self.y2 + 1))]

    def door_up(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the upper wall, and return the location as a 2D array index."""
        door_up_list = []
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        door_up_list.append((slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1)))
        return door_up_list

    def door_left(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the left wall, and return the location as a 2D array index."""
        door_left_list = []
        y_start = self.y2 - self.height + 3
        y_end = self.y1 + self.height - 3
        randloc = random.randint(y_start, y_end)
        door_left_list.append((slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1)))
        return door_left_list

    def door_right(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the right wall, and return the location as a 2D array index."""
        door_right_list = []
        y_start = self.y2 - self.height + 3
        y_end = self.y1 + self.height - 3
        randloc = random.randint(y_start, y_end)
        door_right_list.append((slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1)))
        return door_right_list

    def door_down(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the lower wall, and return the location as a 2D array index."""
        door_down_list = []
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        door_down_list.append((slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2)))
        return door_down_list


class CircularRoom(Room): # Not using ellipse generation algorithm due to performance issues
    """
    Example.
    height = 6, width = 7

     #+++#
    ##...##
    +.....+
    +.....+
    ##...##
     #+++#

    + : possible door generation location 
    """

    def __init__(self, x: int, y: int, width: int, height: int, parent: GameMap, terrain: Terrain):
        super().__init__(x, y, width, height, parent, terrain)

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        inner_list = []
        inner_list.append((slice(self.x1 + 2, self.x2 - 1), slice(self.y1 + 1, self.y1 + 2))) # indicates the top row of the room
        inner_list.append((slice(self.x1 + 2, self.x2 - 1), slice(self.y2 - 1, self.y2))) # indicates the bottom row of the room
        for i in range(self.height - 3):
            inner_list.append((slice(self.x1 + 1, self.x2), slice(self.y1 + 2 + i, self.y1 + 3 + i)))
        return inner_list

    @property
    def outer(self) -> Tuple[slice, slice]:
        """Return the outer(walls) + inner area of this room as a 2D array index."""
        outer_list = []
        outer_list.append((slice(self.x1 + 1, self.x2), slice(self.y1, self.y1 + 1))) # indicates the top row of the room
        outer_list.append((slice(self.x1 + 1, self.x2), slice(self.y2, self.y2 + 1))) # indicates the bottom row of the room
        for i in range(self.height - 1):
            outer_list.append((slice(self.x1, self.x2 + 1), slice(self.y1 + 1 + i, self.y1 + 2 + i)))
        return outer_list

    def door_up(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the upper wall, and return the location as a 2D array index."""
        door_up_list = []
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        door_up_list.append((slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1)))
        return door_up_list

    def door_left(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the left wall, and return the location as a 2D array index."""
        door_left_list = []
        y_start = self.y2 - self.height + 3
        y_end = self.y1 + self.height - 3
        randloc = random.randint(y_start, y_end)
        door_left_list.append((slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1)))
        return door_left_list

    def door_right(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the right wall, and return the location as a 2D array index."""
        door_right_list = []
        y_start = self.y2 - self.height + 3
        y_end = self.y1 + self.height - 3
        randloc = random.randint(y_start, y_end)
        door_right_list.append((slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1)))
        return door_right_list

    def door_down(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the lower wall, and return the location as a 2D array index."""
        door_down_list = []
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        door_down_list.append((slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2)))
        return door_down_list


class PerpendicularRoom(Room):
    """
    Example.
    height = 6 width = 6 rotation = 1

    ##++##
    #....+
    +....+
    +..###
    #..#
    #++#

    ##++##
    #....+
    +....+
    +..@@@
    #..@@@
    #++@@@

    @ : square area
    + : possible door generation location 

    square area width = int(width / 2)
    square area height = int(height / 2)

    NOTE
    Rotation 1
    ##
    #

    Rotation 2
    ##
     #
    
    Rotation 3
     #
    ##

    Rotation 4
    #
    ##
    """

    def __init__(self, x: int, y: int, width: int, height: int, parent: GameMap, terrain: Terrain):
        super().__init__(x, y, width, height, parent, terrain)
        self.rotation = random.randint(1,4)


    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        inner_list = []
        if self.rotation == 1:
            inner_list.append((slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2 - int(self.height / 2)))) # indicates the top row of the room
            inner_list.append((slice(self.x1 + 1, self.x2 - int(self.width / 2)), slice(self.y2 - int(self.height / 2), self.y2))) # indicates the bottom row of the room
        elif self.rotation == 2:
            inner_list.append((slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2 - int(self.height / 2)))) # indicates the top row of the room
            inner_list.append((slice(self.x1 + int(self.width / 2), self.x2), slice(self.y2 - int(self.height / 2), self.y2))) # indicates the bottom row of the room
        elif self.rotation == 3:
            inner_list.append((slice(self.x1 + 1, self.x2), slice(self.y2 - int(self.height / 2), self.y2))) # 윗칸
            inner_list.append((slice(self.x1 + int(self.width / 2), self.x2), slice(self.y1 + 1, self.y2 - int(self.height / 2)))) # 아랫칸
        elif self.rotation == 4:
            inner_list.append((slice(self.x1 + 1, self.x2), slice(self.y2 - int(self.height / 2), self.y2))) # 윗칸
            inner_list.append((slice(self.x1 + 1, self.x2 - int(self.width / 2)), slice(self.y1 + 1, self.y2 - int(self.height / 2)))) # 아랫칸
        return inner_list

    @property
    def outer(self) -> Tuple[slice, slice]:
        """Return the outer(walls) + inner area of this room as a 2D array index."""
        outer_list = []
        if self.rotation == 1:
            outer_list.append((slice(self.x1, self.x2 + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1))) # indicates the top row of the room
            outer_list.append((slice(self.x1, self.x2 - int(self.width / 2) + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1))) # indicates the bottom row of the room
        elif self.rotation == 2:
            outer_list.append((slice(self.x1, self.x2 + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1))) # indicates the top row of the room
            outer_list.append((slice(self.x1 + int(self.width / 2) - 1, self.x2 + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1))) # indicates the bottom row of the room   
        elif self.rotation == 3:
            outer_list.append((slice(self.x1, self.x2 + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1))) # indicates the top row of the room
            outer_list.append((slice(self.x1 + int(self.width / 2) - 1, self.x2 + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1))) # indicates the bottom row of the room
        elif self.rotation == 4:
            outer_list.append((slice(self.x1, self.x2 + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1))) # indicates the top row of the room
            outer_list.append((slice(self.x1, self.x2 - int(self.width / 2) + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1))) # indicates the bottom row of the room
        return outer_list

    def door_up(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the upper wall, and return the location as a 2D array index."""
        door_up_list = []
        if self.rotation == 1 or self.rotation == 2:
            randloc = random.randint(self.x1 + 2, self.x2 - 2)
            door_up_list.append((slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1)))
        elif self.rotation == 3:
            randloc = random.randint(self.x1 + int(self.width / 2), self.x2 - 1)
            door_up_list.append((slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1)))
        elif self.rotation == 4:
            randloc = random.randint(self.x1 + 1, self.x2 - int(self.width / 2) - 1)
            door_up_list.append((slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1)))
        return door_up_list

    def door_left(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the left wall, and return the location as a 2D array index."""
        door_left_list = []
        if self.rotation == 1 or self.rotation == 4:
            y_start = self.y1 + 3
            y_end = self.y1 + self.height - 3
            randloc = random.randint(y_start, y_end)
            door_left_list.append((slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1)))
        elif self.rotation == 2:
            y_start = self.y1 + 1
            y_end = self.y1 + int(self.height / 2) - 1
            randloc = random.randint(y_start, y_end)
            door_left_list.append((slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1)))
        elif self.rotation == 3:
            y_start = self.y1 + int(self.height / 2)
            y_end = self.y2 - 1
            randloc = random.randint(y_start, y_end)
            door_left_list.append((slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1)))
        return door_left_list

    def door_right(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the right wall, and return the location as a 2D array index."""
        door_right_list = []
        if self.rotation == 1:
            y_start = self.y1 + 2
            y_end = self.y1 + int(self.height / 2) - 1
            randloc = random.randint(y_start, y_end)
            door_right_list.append((slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1)))
        elif self.rotation == 2 or self.rotation == 3:
            y_start = self.y1 + 3
            y_end = self.y1 + self.height - 3
            randloc = random.randint(y_start, y_end)
            door_right_list.append((slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1)))
        elif self.rotation == 4:
            y_start = self.y1 + int(self.height / 2)
            y_end = self.y2 - 1
            randloc = random.randint(y_start, y_end)
            door_right_list.append((slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1)))
        return door_right_list

    def door_down(self) -> Tuple[slice, slice]:
        """Randomly generate door convex location next to the lower wall, and return the location as a 2D array index."""
        door_down_list = []
        if self.rotation == 1:
            randloc = random.randint(self.x1 + 2, self.x2 - int(self.width / 2) - 1)
            door_down_list.append((slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2)))
        elif self.rotation == 2:
            randloc = random.randint(self.x1 + int(self.width / 2), self.x2 - 1)
            door_down_list.append((slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2)))
        elif self.rotation == 3 or self.rotation == 4:
            door_down_list = []
            randloc = random.randint(self.x1 + 2, self.x2 - 2)
            door_down_list.append((slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2)))
        return door_down_list
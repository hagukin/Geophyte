import random

import numpy as np

from game_map import GameMap
from terrain import Terrain
from typing import Tuple, List
from game_map import GameMap
from room import Room

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
    def inner(self) -> List[Tuple[slice, slice]]:
        """Return the inner area of this room as a 2D array index."""
        return [(slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2))]

    @property
    def outer(self) -> List[Tuple[slice, slice]]:
        """Return the outer(walls) + inner area of this room as a 2D array index."""
        return [(slice(self.x1, self.x2 + 1), slice(self.y1, self.y2 + 1))]

    def door_up(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        return [(slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1))]

    def door_left(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the left wall, and return the location as a 2D array index."""
        randloc = random.randint(self.y2 - self.height + 3, self.y1 + self.height - 3)
        return [(slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1))]

    def door_right(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the right wall, and return the location as a 2D array index."""
        randloc = random.randint(self.y2 - self.height + 3, self.y1 + self.height - 3)
        return [(slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1))]

    def door_down(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the lower wall, and return the location as a 2D array index."""
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        return [(slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2))]


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
    def inner(self) -> List[Tuple[slice, slice]]:
        """Return the inner area of this room as a 2D array index."""
        inner_list = [
            (slice(self.x1 + 2, self.x2 - 1), slice(self.y1 + 1, self.y1 + 2)), # indicates the top row of the room
            (slice(self.x1 + 2, self.x2 - 1), slice(self.y2 - 1, self.y2)) # indicates the bottom row of the room
        ]
        for i in range(self.height - 3):
            inner_list.append((slice(self.x1 + 1, self.x2), slice(self.y1 + 2 + i, self.y1 + 3 + i)))
        return inner_list

    @property
    def outer(self) -> List[Tuple[slice, slice]]:
        """Return the outer(walls) + inner area of this room as a 2D array index."""
        outer_list = [
            (slice(self.x1 + 1, self.x2), slice(self.y1, self.y1 + 1)), # indicates the top row of the room
            (slice(self.x1 + 1, self.x2), slice(self.y2, self.y2 + 1)) # indicates the bottom row of the room
        ]
        for i in range(self.height - 1):
            outer_list.append((slice(self.x1, self.x2 + 1), slice(self.y1 + 1 + i, self.y1 + 2 + i)))
        return outer_list

    def door_up(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        return [(slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1))]

    def door_left(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the left wall, and return the location as a 2D array index."""
        randloc = random.randint(self.y2 - self.height + 3, self.y1 + self.height - 3)
        return [(slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1))]

    def door_right(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the right wall, and return the location as a 2D array index."""
        randloc = random.randint(self.y2 - self.height + 3, self.y1 + self.height - 3)
        return [(slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1))]

    def door_down(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the lower wall, and return the location as a 2D array index."""
        randloc = random.randint(self.x1 + 2, self.x2 - 2)
        return [(slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2))]


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
    def inner(self) -> List[Tuple[slice, slice]]:
        """Return the inner area of this room as a 2D array index."""
        if self.rotation == 1:
            inner_list = [
                (slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2 - int(self.height / 2))), # indicates the top row of the room
                (slice(self.x1 + 1, self.x2 - int(self.width / 2)), slice(self.y2 - int(self.height / 2), self.y2)) # indicates the bottom row of the room
            ]
        elif self.rotation == 2:
            inner_list = [
                (slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2 - int(self.height / 2))),# indicates the top row of the room
                (slice(self.x1 + int(self.width / 2), self.x2), slice(self.y2 - int(self.height / 2), self.y2)) # indicates the bottom row of the room
            ]
        elif self.rotation == 3:
            inner_list = [
                (slice(self.x1 + 1, self.x2), slice(self.y2 - int(self.height / 2), self.y2)), # Up
                (slice(self.x1 + int(self.width / 2), self.x2), slice(self.y1 + 1, self.y2 - int(self.height / 2)))# Down
            ]
        elif self.rotation == 4:
            inner_list = [
                (slice(self.x1 + 1, self.x2), slice(self.y2 - int(self.height / 2), self.y2)), # Up
                (slice(self.x1 + 1, self.x2 - int(self.width / 2)), slice(self.y1 + 1, self.y2 - int(self.height / 2))) # Down
            ]
        else:
            print("FATAL ERROR::Can't get room.inner")
            return []
        return inner_list

    @property
    def outer(self) -> List[Tuple[slice, slice]]:
        """Return the outer(walls) + inner area of this room as a 2D array index."""
        if self.rotation == 1:
            outer_list = [
                (slice(self.x1, self.x2 + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1)), # indicates the top row of the room
                (slice(self.x1, self.x2 - int(self.width / 2) + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1)) # indicates the bottom row of the room
            ]
        elif self.rotation == 2:
            outer_list = [
                (slice(self.x1, self.x2 + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1)), # indicates the top row of the room
                (slice(self.x1 + int(self.width / 2) - 1, self.x2 + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1)) # indicates the bottom row of the room
            ]
        elif self.rotation == 3:
            outer_list = [
                (slice(self.x1, self.x2 + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1)), # indicates the top row of the room
                (slice(self.x1 + int(self.width / 2) - 1, self.x2 + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1)) # indicates the bottom row of the room
            ]
        elif self.rotation == 4:
            outer_list = [
                (slice(self.x1, self.x2 + 1), slice(self.y2 - int(self.height / 2) - 1, self.y2 + 1)), # indicates the top row of the room
                (slice(self.x1, self.x2 - int(self.width / 2) + 1), slice(self.y1, self.y2 - int(self.height / 2) + 1)) # indicates the bottom row of the room
            ]
        else:
            return []
        return outer_list

    def door_up(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        if self.rotation == 1 or self.rotation == 2:
            randloc = random.randint(self.x1 + 2, self.x2 - 2)
            door_up_list = [(slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1))]
        elif self.rotation == 3:
            randloc = random.randint(self.x1 + int(self.width / 2), self.x2 - 1)
            door_up_list = [(slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1))]
        elif self.rotation == 4:
            randloc = random.randint(self.x1 + 1, self.x2 - int(self.width / 2) - 1)
            door_up_list = [(slice(randloc, randloc + 1), slice(self.y1 - 1, self.y1))]
        else:
            return []
        return door_up_list

    def door_left(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the left wall, and return the location as a 2D array index."""
        if self.rotation == 1 or self.rotation == 4:
            randloc = random.randint(self.y1 + 3, self.y1 + self.height - 3)
            door_left_list = [(slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1))]
        elif self.rotation == 2:
            randloc = random.randint(self.y1 + 1, self.y1 + int(self.height / 2) - 1)
            door_left_list = [(slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1))]
        elif self.rotation == 3:
            randloc = random.randint(self.y1 + int(self.height / 2), self.y2 - 1)
            door_left_list = [(slice(self.x1 - 1, self.x1), slice(randloc, randloc + 1))]
        else:
            return []
        return door_left_list

    def door_right(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the right wall, and return the location as a 2D array index."""
        if self.rotation == 1:
            randloc = random.randint(self.y1 + 2, self.y1 + int(self.height / 2) - 1)
            door_right_list = [(slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1))]
        elif self.rotation == 2 or self.rotation == 3:
            randloc = random.randint(self.y1 + 3, self.y1 + self.height - 3)
            door_right_list = [(slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1))]
        elif self.rotation == 4:
            randloc = random.randint(self.y1 + int(self.height / 2), self.y2 - 1)
            door_right_list = [(slice(self.x2 + 1, self.x2 + 2), slice(randloc, randloc + 1))]
        else:
            return []
        return door_right_list

    def door_down(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the lower wall, and return the location as a 2D array index."""
        if self.rotation == 1:
            randloc = random.randint(self.x1 + 2, self.x2 - int(self.width / 2) - 1)
            door_down_list = [(slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2))]
        elif self.rotation == 2:
            randloc = random.randint(self.x1 + int(self.width / 2), self.x2 - 1)
            door_down_list = [(slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2))]
        elif self.rotation == 3 or self.rotation == 4:
            randloc = random.randint(self.x1 + 2, self.x2 - 2)
            door_down_list = [(slice(randloc, randloc + 1), slice(self.y2 + 1, self.y2 + 2))]
        else:
            return []
        return door_down_list


class BlobRoom(Room):
    def __init__(self, x: int, y: int, parent: GameMap, terrain: Terrain, min_mass: int=25, max_mass: int=100, density: float=0.5, max_fill_gap_size: int = 1000000):
        from blob import generate_blob_of_mass
        self.blob = generate_blob_of_mass(min_chunk_mass=min_mass, max_chunk_mass=max_mass, density=density)
        self.blob.gooify(max_fill_gap_size) # NOTE: blob.grid indicates only the inner area of the room.
        width = self.blob.width + 2 # for outer walls
        height = self.blob.height + 2
        super().__init__(x, y, width, height, parent, terrain)

    @staticmethod
    def grid_to_slice(grid: np.ndarray, search_for: int=True) -> List[Tuple[slice, slice]]:
        lst = []
        width, height = grid.shape
        for x in range(len(grid)):
            y1, y2 = None, None
            for y in range(len(grid[0])):
                if grid[x][y] == search_for:
                    if y1 is None:
                        y1 = y
                    else:
                        y2 = y
                    if y == height-1:
                        if y2 is None:
                            y2 = y
                        lst.append((slice(x, x + 1), slice(y1, y2 + 1)))
                        y1, y2 = None, None
                else:
                    if y2 is None:
                        y2 = y1
                    if y1 is not None:
                        lst.append((slice(x, x + 1), slice(y1, y2 + 1)))
                        y1, y2 = None, None
        return lst





## DEBUG SESSION
# from blob import generate_blob_of_mass
# print("==============BEGIN=========================")
# k = generate_blob_of_mass(100, 100, 0.5)
# k.print()
# print("=======================================")
# k.gooify(max_fill_gap_size=0)
# k.print()
# t = BlobRoom.grid_to_slice(k.grid)
#
# map2 = np.full((50, 50), fill_value=False, order="F")
#
# for inner_slice in t:
#     map2[inner_slice] = True
# print("____________SLICE__________")
# for x in map2:
#     for y in x:
#         if y == True:
#             print('#', end="")
#         else:
#             print('.', end="")
#     print()
import random

import numpy as np

from util import surround_grid_value_with
from game_map import GameMap
from terrain import Terrain
from typing import Tuple, List
from game_map import GameMap
from room import Room
from collections import deque

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
    def __init__(self,
                 x: int,
                 y: int,
                 width: int,
                 height: int,
                 parent: GameMap,
                 terrain: Terrain,
                 area_min_density: float,
                 area_max_density: float,
                 rotate_chance: float = 0.5,
                 max_fill_gap_size: int = 99):
        """
        Vars:
            is_valid:
                used to check if the room can fit in gamemap location.
                if False, procgen will dump this room.s
        """
        from blob import generate_blob_of_size
        self.grid = np.full((width, height), fill_value=0, order="F")
        tmp = generate_blob_of_size(width-2, height-2, area_min_density=area_min_density, area_max_density=area_max_density, int_grid=True, max_fill_gap_size=3) #ignore walls
        tmp = tmp.grid
        self.grid[1:1+tmp.shape[0], 1:1+tmp.shape[1]] = tmp
        surround_grid_value_with(self.grid, search_for=1, surround_with=2) # 2 - outer wall

        if random.random() <= rotate_chance:
            self.width = height
            self.height = width
            self.grid = np.rot90(self.grid,k=random.randint(1,4))
        super().__init__(x, y, width, height, parent, terrain)

    @staticmethod
    def grid_to_slice(grid: np.ndarray, grid_dx: int=0, grid_dy: int=0, search_for: int=1) -> List[Tuple[slice, slice]]:
        """
        Convert the given 2d grid into a list of tuple that contains two slices.

        Args:
            grid: search_for:
                2d array that indicates the grid.
                Can contain any value you want, but you should specify what value to search from using 'search_for' parameter.
                e.g.
                grid =
                000000
                022220
                221122
                211112
                221122
                022220
                000000
                if you want to convert the '2' parts (the inner area) only, you should pass in 2 to search_for parameter.
            grid_dx:
            grid_dy:
                used to move the given slice objects for certain amount.
                if both of them are set to 0,
                the slice objects will start from (0,0).

                NOTE: When creating a slice for Room objects, you should pass in its x1, y1 value here
                so that the slice objects can contain not the relative coordinates, but the absolute coordinates(gamemap grid coordinates).
            """
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
                        lst.append((slice(x + grid_dx, x + grid_dx + 1), slice(y1 + grid_dy, y2 + grid_dy + 1)))
                        y1, y2 = None, None
                else:
                    if y2 is None:
                        y2 = y1
                    if y1 is not None:
                        lst.append((slice(x + grid_dx, x + grid_dx + 1), slice(y1 + grid_dy, y2 + grid_dy + 1)))
                        y1, y2 = None, None
        return lst

    @staticmethod
    def grid_get_door_loc(grid: np.ndarray, door_dir: str="u", grid_dx: int = 0, grid_dy: int = 0, search_for: int = False) -> List[Tuple[slice, slice]]: ###FIXME TODO UP DOOR
        """
        Get the valid door location for the given grid and return as slice object.
        Args:
            door_dir:
                the direction of the door relative to center.
                "u" "d" "l" "r"
        """
        lst = []
        width, height = grid.shape

        if door_dir == "u":
            for x in range(len(grid)):
                if grid[x][0] == search_for:
                    lst.append((slice(x + grid_dx, x + grid_dx + 1), slice(0 + grid_dy, 0 + grid_dy + 1)))
                    return lst
        return lst

    @property
    def inner(self) -> List[Tuple[slice, slice]]:
        """Return the inner area of this room as a 2D array index."""
        return BlobRoom.grid_to_slice(self.grid, grid_dx=self.x1, grid_dy=self.y1, search_for=1)

    @property
    def outer(self) -> List[Tuple[slice, slice]]:
        """Return the inner area of this room as a 2D array index."""
        return BlobRoom.grid_to_slice(self.grid, grid_dx=self.x1, grid_dy=self.y1, search_for=2)

    def door_up(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        cands = deque()
        blob_wall_width = self.grid.shape[0]
        blob_wall_height = self.grid.shape[1]
        found = False
        for y in range(0, blob_wall_height):
            for x in range(0, blob_wall_width):
                if self.grid[x,y] == 2:
                    found = True
                    cands.append((x,y))
            if found:
                cands.pop()
                cands.popleft()
                break
        if not found or len(cands) == 0:
            print("FATAL ERROR::BlobRoom DoorGen error")
        randloc = random.choice(cands)
        return [(slice(self.x1 + randloc[0], self.x1 + randloc[0] + 1),
                 slice(self.y1 + randloc[1] - 1, self.y1  + randloc[1]))]

    def door_down(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        cands = deque()
        blob_wall_width = self.grid.shape[0]
        blob_wall_height = self.grid.shape[1] - 1
        found = False
        for y in range(blob_wall_height, 0, -1):
            for x in range(0, blob_wall_width):
                if self.grid[x, y] == 2:
                    found = True
                    cands.append((x, y))
            if found:
                cands.pop()
                cands.popleft()
                break
        if not found or len(cands) == 0:
            print("FATAL ERROR::BlobRoom DoorGen error")
        randloc = random.choice(cands)
        return [(slice(self.x1 + randloc[0], self.x1 + randloc[0] + 1),
                 slice(self.y1 + randloc[1] + 1, self.y1 + randloc[1] + 2))]

    def door_left(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        cands = deque()
        blob_wall_width = self.grid.shape[0]
        blob_wall_height = self.grid.shape[1]
        found = False
        for x in range(0, blob_wall_width):
            for y in range(0, blob_wall_height):
                if self.grid[x, y] == 2:
                    found = True
                    cands.append((x, y))
            if found:
                cands.pop()
                cands.popleft()
                break
        if not found or len(cands) == 0:
            print("FATAL ERROR::BlobRoom DoorGen error")
        randloc = random.choice(cands)
        return [(slice(self.x1 + randloc[0] - 1, self.x1 + randloc[0]),
                 slice(self.y1 + randloc[1], self.y1 + randloc[1] + 1))]

    def door_right(self) -> List[Tuple[slice, slice]]:
        """Randomly randomize door convex location next to the upper wall, and return the location as a 2D array index."""
        cands = deque()
        blob_wall_width = self.grid.shape[0] - 1
        blob_wall_height = self.grid.shape[1]
        found = False
        for x in range(blob_wall_width, 0, -1):
            for y in range(0, blob_wall_height):
                if self.grid[x, y] == 2:
                    found = True
                    cands.append((x, y))
            if found:
                cands.pop()
                cands.popleft()
                break
        if not found or len(cands) == 0:
            print("FATAL ERROR::BlobRoom DoorGen error")
        randloc = random.choice(cands)
        return [(slice(self.x1 + randloc[0] + 1, self.x1 + randloc[0] + 2),
                 slice(self.y1 + randloc[1], self.y1 + randloc[1] + 1))]

#
#
##DEBUG SESSION
# from terrain import Terrain
# from biome import Biome
# print("____________BLOB____________")
# import time
# tc = time.time()
# r = BlobRoom(x=3, y=3, width=16, height=16, parent=GameMap(0, Biome()), terrain=Terrain(), max_fill_gap_size=3, area_min_density=0.2, area_max_density=0.6)
# # for i in r.grid:
# #     for k in i:
# #         if k == 2:
# #             print("#", end="")
# #         elif k == 1:
# #             print("^", end="")
# #         else:
# #             print(".", end="")
# #     print()
#
# t = BlobRoom.grid_to_slice(r.grid, grid_dx=5, grid_dy=5, search_for=1)
# t2 = BlobRoom.grid_to_slice(r.grid, grid_dx=5, grid_dy=5, search_for=2)
# map = np.full((50, 50), fill_value=0, order="F")
#
# for sliceobj in t:
#     map[sliceobj] = 1
# for sliceobj in t2:
#     map[sliceobj] = 2
# print("____________SLICE__________")
# # for x in map:
# #     for y in x:
# #         if y == 1:
# #             print('^', end="")
# #         elif y == 2:
# #             print('#', end="")
# #         else:
# #             print('.', end="")
# #     print()
#
# print(time.time() - tc)
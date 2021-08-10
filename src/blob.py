from collections import deque
from typing import List, Optional, Tuple
import numpy as np
import tcod
import random

class Blob:
    def __init__(self, grid_width, grid_height, noise_density, int_grid: bool=False):
        """
        Args:
            int_grid:
                whether this Blob object's grid uses boolean or integer for its value.
                When generating a blobRoom, you should use integer since there are 3 types of informations you can store.
                => void, outer, inner
        Vars:
            grid_width, grid_height:
                e.g.
                .###..
                #####.
                #.....
                ###...
                ......

                -> grid_width 6, grid_height 5
                -> blob_width 5, blob_height 4
        """
        self.grid_width = grid_width # The width of a grid, not the blob itself. NOTE: must be higher than target blob_weight
        self.grid_height = grid_height
        self.blob_width = None # Initialized after blob is generated.
        self.blob_height = None # Initialized after blob is generated.
        self.noise_density = noise_density
        if int_grid:
            self.grid = np.full((grid_width, grid_height), fill_value=0, order="F")
        else:
            self.grid = np.full((grid_width, grid_height), fill_value=False, order="F")
        self.blob = None
        self.tried = []

    def noise(self):
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if random.random() <= self.noise_density:
                    self.grid[x, y] = 1

    def get_start_cell(self) -> Optional[Tuple[int, int]]:
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if self.grid[x][y]:
                    return (x, y)
        return None

    def remove_non_chunks(self):
        q = deque()
        for x, y in self.tried:
            visited = np.full((self.grid_width, self.grid_height), fill_value=False, order="F")
            q.append((x, y))
            while q:
                curr = q.popleft()
                if curr == None:
                    break
                for dxdy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    nx = curr[0] + dxdy[0]
                    ny = curr[1] + dxdy[1]
                    if nx >= 0 and nx < self.grid_width \
                            and ny >= 0 and ny < self.grid_height:
                        if not visited[nx][ny] and self.grid[nx][ny]:
                            visited[nx][ny] = True
                            self.grid[nx][ny] = False
                            q.append((nx, ny))

    def blobify(self, min_chunk_mass, max_chunk_mass) -> bool:
        """Make current noise map into one big blob so that every node is connected.
        NOTE: 'Connected' means either one of the 4 sides of the node is connected to other living node.
        NOTE: There can be several different blobs in self.grid after running blobify(). So you must run remove_non_chunks() afterwards.
        Return:
            boolean, whether the algorithm found a chunk of a given size or not."""
        self.tried.clear()
        visited = np.full((self.grid_width, self.grid_height), fill_value=False, order="F")
        chunk_size = 1

        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if not self.grid[x][y]:
                    continue

                q = deque()
                q.append((x, y))
                while q:
                    curr = q.popleft()
                    if curr == None:
                        break
                    for dxdy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                        nx = curr[0] + dxdy[0]
                        ny = curr[1] + dxdy[1]
                        if nx >= 0 and nx < self.grid_width \
                                and ny >= 0 and ny < self.grid_height:
                            if not visited[nx][ny] and self.grid[nx][ny]:
                                visited[nx][ny] = True
                                q.append((nx, ny))
                                chunk_size += 1
                                if chunk_size >= max_chunk_mass:
                                    self.grid = visited
                                    return True
                if chunk_size > min_chunk_mass:
                    self.grid = visited
                    return True
                else:
                    self.tried.append((x, y))
                    chunk_size = 1
        return False

    def crop(self, force_width: int = None, force_height: int = None):
        """Make self.grid into a new minimal sized rectangular grid.
        e.g.
        ..#
        ..#
        ... (3x3)

        to

        #
        # (1x2)
        """
        min_x, max_x, min_y, max_y = self.grid_width, 0, self.grid_height, 0

        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if self.grid[x][y] == 1:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)

        if force_width:
            if max_x > min_x + force_width:
                print(f"WARNING::max_x {max_x} is larger than min_x + force_width{min_x + force_width}. blob is partially lost.")
            max_x = min_x + force_width
        if force_height:
            if max_y > min_y + force_height:
                print(f"WARNING::max_y {max_y} is larger than min_y + force_height{min_y + force_height}. blob is partially lost.")
            max_y = min_y + force_height

        self.blob = self.grid[min_x:max_x+1, min_y:max_y+1]
        self.blob_width, self.blob_height = self.blob.shape

    def gooify(self, max_fill_gap_size: int = 999):
        """Make blob more denser by filling the gaps.
        Args:
            max_fill_gap_size:
                the number of maximum False node that are filled with True.
                if set to 999(or high enough number), this function will fill every visible gaps.

        e.g.
        .#...#.
        ####.#.
        ..####.
        ###.#..


        max_connect_dist = 999
        .#####.
        ######
        ..####
        #####.

        max_connect_dist = 2
        .#...#.
        ######.
        ######.
        #####..
        """
        min_y, max_y = self.grid_height, 0

        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if self.grid[x][y] == True:
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    gap_size = max_y - min_y - 1
                    if gap_size <= max_fill_gap_size and gap_size > 0:
                        for y in range(min_y+1, min_y+gap_size+1):
                            self.grid[x][y] = True
                    min_y += 1+gap_size
                    max_y = 0
            min_y, max_y = self.grid_height, 0


def generate_blob_of_mass(
        min_chunk_mass: int,
        max_chunk_mass: int,
        grid_magnifier: Optional[float] = None,
        noise_density: float=0.5,
        int_grid=True
) -> Blob:
    """
    Args:
        grid_magnifier:
            Higher the number is, the longer the function takes.
            But the chance of failure reduces.
            if set to Optional, function automatically assigns a value.
        noise_density:
            The initial noice map's density.
            has almost no effect to the results.
    """
    if grid_magnifier is None:
        C = 1 + 3/np.log10(max_chunk_mass)
    else:
        C = grid_magnifier
    edge_len = int(np.sqrt(max_chunk_mass) * (1 / noise_density) * C)
    grid = Blob(edge_len, edge_len, noise_density, int_grid)
    grid.noise()
    while not grid.blobify(min_chunk_mass, max_chunk_mass):
        grid.noise()
    grid.remove_non_chunks()
    grid.crop()
    return grid



def generate_blob_of_size_fast(
        width: int,
        height: int,
        area_min_density: float,
        area_max_density: float,
        noise_density: float=0.5,
        int_grid=True
) -> Blob:
    """
    A faster version of generating blob.
    Instead the shape might look a little 'blocky'

    Args:
        area_min_density: area_max_density:
            float 0 ~ 1.
            Different from noise_density.
            Indicates the density of the room.
            if set to 1,
    """
    grid = Blob(width, height, noise_density, int_grid)
    grid.noise()
    while not grid.blobify(width*height*area_min_density, width*height*area_max_density):
        grid.noise()
    grid.remove_non_chunks()
    grid.crop(width, height)
    return grid


def generate_blob_of_size_slow(
        width: int,
        height: int,
        area_min_density: float,
        area_max_density: float,
        grid_magnifier: Optional[float] = None,
        noise_density: float=0.5,
        int_grid=True
) -> Blob:
    """
    A slower version of generating blob.
    Shapes are a bit more natural.
    Args:
        grid_magnifier:
            Higher the number is, the longer the function takes.
            But the chance of failure reduces.
            if set to Optional, function automatically assigns a value.
        area_min_density: area_max_density:
            float 0 ~ 1.
            Different from noise_density.
            Indicates the density of the room.
            if set to 1,
    """
    if grid_magnifier is None:
        C = 1 + 3/np.log10(width*height)
    else:
        C = grid_magnifier
    grid = Blob(int(width*C), int(height*C), noise_density, int_grid)
    grid.noise()
    while not grid.blobify(width*height*area_min_density, width*height*area_max_density):
        grid.noise()
    grid.remove_non_chunks()
    grid.crop(width, height)
    return grid



def debug(grid: np.ndarray):
    for i in grid:
        for k in i:
            if k:
                print("#", end="")
            else:
                print(".", end="")
        print(end="\n")


import time
t = time.time()
for _ in range(1):
    print("==============BEGIN=========================")
    z = generate_blob_of_size_slow(width=10, height=10, area_min_density=0.3, area_max_density=0.5)
    z.gooify(5)
    debug(z.blob)
    print("^Slow")
    y = generate_blob_of_size_fast(width=10, height=10, area_min_density=0.3, area_max_density=0.5)
    y.gooify(5)
    debug(y.blob)
    print("^Fast")
    x = generate_blob_of_mass(min_chunk_mass=100, max_chunk_mass=100, noise_density=0.5)
    x.gooify(5)
    debug(x.blob)
    print("^Mass")
    print("=======================================")
print(time.time() - t)
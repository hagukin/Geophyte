from collections import deque
from typing import List, Optional, Tuple
import numpy as np
import random

class Blob:
    def __init__(self, width, height, noise_density):
        self.width = width
        self.height = height
        self.noise_density = noise_density
        self.grid = np.full((width, height), fill_value=False, order="F")
        self.tried = []

    def CA(self):
        """
        Cellular Automata.
        1. 살아있는 세포 주변에 다른 살아있는 세포의 갯수가 두 개 미만이면 사망
        2. 살아있는 세포 주변에 다른 살아있는 세포의 갯수가 두 개 혹은 세 개이면 그대로 생존
        3. 살아있는 세포 주변에 다른 살아있는 세포의 갯수가 세 개를 넘을 경우 사망
        4. 죽은 세포 주변에 정확히 세 개의 살아있는 세포가 있을 경우 부활

        If your goal is to get a new random shaped grid, you can use noise() instead.
        """
        temp_grid = np.full(
            (self.width, self.height), fill_value=True, order="F"
        )

        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                cell_count = 0
                for x_add, y_add in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    try:
                        if self.grid[x + x_add, y + y_add] == True:
                            cell_count += 1
                    except:
                        continue

                if self.grid[x][y]:
                    if cell_count == 3:
                        continue
                    else:
                        temp_grid[x][y] = False
                else:
                    if cell_count == 3:
                        temp_grid[x][y] = True

        self.grid = temp_grid

    def noise(self):
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if random.random() <= self.noise_density:
                    self.grid[x, y] = True

    def get_start_cell(self) -> Optional[Tuple[int, int]]:
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if self.grid[x][y]:
                    return (x, y)
        return None

    def remove_non_chunks(self):
        q = deque()
        for x, y in self.tried:
            visited = np.full((self.width, self.height), fill_value=False, order="F")
            q.append((x, y))
            while q:
                curr = q.popleft()
                if curr == None:
                    break
                for dxdy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    nx = curr[0] + dxdy[0]
                    ny = curr[1] + dxdy[1]
                    if nx >= 0 and nx < self.width \
                            and ny >= 0 and ny < self.height:
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
        visited = np.full((self.width, self.height), fill_value=False, order="F")
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
                        if nx >= 0 and nx < self.width \
                                and ny >= 0 and ny < self.height:
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
        min_x, max_x, min_y, max_y = self.width, 0, self.height, 0

        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if self.grid[x][y] == True:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)

        if force_width:
            max_x = min_x + force_width
            if max_x > self.width:
                max_x = self.width
                print("WARNING::max_x is larger than grid width. is reduced down to grid width")
        if force_height:
            max_y = min_y + force_height
            if max_y > self.height:
                max_y = self.height
                print("WARNING::max_y is larger than grid height. is reduced down to grid height.")

        self.grid = self.grid[min_x:max_x, min_y:max_y]
        self.width, self.height = self.grid.shape

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
        min_y, max_y = self.height, 0

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
            min_y, max_y = self.height, 0

    def print(self):
        for i in self.grid:
            for k in i:
                if k:
                    print("#", end="")
                else:
                    print(".", end="")
            print(end="\n")


def generate_blob_of_mass(min_chunk_mass: int, max_chunk_mass: int, max_fill_gap_size: int, acc_const: Optional[float] = None, noise_density: float=0.5) -> Blob:
    """
    Args:
        acc_const:
            Higher the number is, the longer the function takes.
            But the chance of failure reduces.
            if set to Optional, function automatically assigns a value.
        noise_density:
            The initial noice map's density.
            has almost no effect to the results.
    """
    if acc_const is None:
        C = 1 + 3/np.log10(max_chunk_mass)
    else:
        C = acc_const
    edge_len = int(np.sqrt(max_chunk_mass) * (1 / noise_density) * C)
    grid = Blob(edge_len, edge_len, noise_density)
    grid.noise()
    grid.gooify(max_fill_gap_size=max_fill_gap_size)
    while not grid.blobify(min_chunk_mass, max_chunk_mass):
        grid.noise()
        grid.gooify(max_fill_gap_size=max_fill_gap_size)
    grid.remove_non_chunks()
    grid.crop()
    return grid


def generate_blob_of_size_fast(width: int, height: int, area_min_density: float, area_max_density: float, max_fill_gap_size: int, noise_density: float=0.5) -> Blob:
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
    grid = Blob(width, height, noise_density)
    grid.noise()
    grid.gooify(max_fill_gap_size=max_fill_gap_size)
    while not grid.blobify(width*height*area_min_density, width*height*area_max_density):
        grid.noise()
        grid.gooify(max_fill_gap_size=max_fill_gap_size)
    grid.remove_non_chunks()
    grid.crop(width, height)
    return grid


def generate_blob_of_size_slow(width: int, height: int, area_min_density: float, area_max_density: float, max_fill_gap_size: int, acc_const: Optional[float] = None, noise_density: float=0.5) -> Blob:
    """
    A slower version of generating blob.
    Shapes are a bit more natural.

    Args:
        acc_const:
            Higher the number is, the longer the function takes.
            But the chance of failure reduces.
            if set to Optional, function automatically assigns a value.
        area_min_density: area_max_density:
            float 0 ~ 1.
            Different from noise_density.
            Indicates the density of the room.
            if set to 1,
    """
    if acc_const is None:
        C = 1 + 3/np.log10(width*height)
    else:
        C = acc_const
    grid = Blob(int(width*C), int(height*C), noise_density)
    grid.noise()
    grid.CA()
    grid.gooify(max_fill_gap_size=max_fill_gap_size)
    while not grid.blobify(width*height*area_min_density, width*height*area_max_density):
        grid.CA()
        grid.gooify(max_fill_gap_size=max_fill_gap_size)
    grid.remove_non_chunks()
    grid.crop(width, height)
    grid.blobify(0, 1000000)
    return grid


import time
t = time.time()
for _ in range(5):
    print("==============BEGIN=========================")
    x = generate_blob_of_size_slow(width=10, height=10, area_min_density=0.3, area_max_density=1, max_fill_gap_size=0, noise_density=0.2)
    x.print()
    print("^Slow")
    y = generate_blob_of_size_fast(width=10, height=10, area_min_density=0.3, area_max_density=1, max_fill_gap_size=0, noise_density=0.2)
    y.print()
    print("^Fast")
    print("=======================================")
print(time.time() - t)
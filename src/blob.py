from collections import deque
from typing import List, Optional, Tuple
import numpy as np
import random

class Blob:
    def __init__(self, width, height, density):
        self.width = width
        self.height = height
        self.density = density
        self.grid = np.full((width, height), fill_value=True, order="F")
        self.tried = []

    def generate(self):
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if random.random() <= self.density:
                    self.grid[x, y] = False

    def CA(self):
        """
        Cellular Automata.
        1. 살아있는 세포 주변에 다른 살아있는 세포의 갯수가 두 개 미만이면 사망
        2. 살아있는 세포 주변에 다른 살아있는 세포의 갯수가 두 개 혹은 세 개이면 그대로 생존
        3. 살아있는 세포 주변에 다른 살아있는 세포의 갯수가 세 개를 넘을 경우 사망
        4. 죽은 세포 주변에 정확히 세 개의 살아있는 세포가 있을 경우 부활
        """
        temp_grid = np.full(
            (self.width, self.height), fill_value=True, order="F"
        )

        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                cell_count = 0
                for x_add in range(3):
                    for y_add in range(3):
                        try:
                            if self.grid[x - 1 + x_add, y - 1 + y_add] == True:
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
            max_x = min_x + force_width,
            if max_x >= self.width:
                max_x = self.width - 1
                print("WARNING::max_x is larger than grid width. is reduced down to grid width")
        if force_height:
            max_y = min_y + force_height
            if max_y >= self.height:
                max_y = self.height - 1
                print("WARNING::max_y is larger than grid height. is reduced down to grid height.")

        self.grid = self.grid[min_x:max_x + 1, min_y:max_y + 1]
        self.width, self.height = self.grid.shape

    def gooify(self, max_connect_dist: int = 3):
        """Make blob more denser by filling the gaps.
        Args:
            max_connect_dist:
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
                    # for y in range(min_y, max_y):
                    #     self.grid[x][y] = True

                    if max_y - min_y < max_connect_dist + 2:
                        for y in range(min_y, max_y):
                            self.grid[x][y] = True
                        min_y = max_y
                        max_y = 0
            min_y, max_y = self.height, 0

    def print(self):
        for i in self.grid:
            for k in i:
                if k:
                    print("#", end="")
                else:
                    print(" ", end="")
            print(end="\n")


def generate_blob_of_mass(min_chunk_mass: int, max_chunk_mass: int, density: float, acc_const: int = 4) -> Blob:
    edge_len = int(np.sqrt(max_chunk_mass) * (1 / density) * acc_const)
    grid = Blob(edge_len, edge_len, density)
    grid.generate()
    while not grid.blobify(min_chunk_mass, max_chunk_mass):
        grid.CA()
    grid.remove_non_chunks()
    grid.crop()
    return grid

# for _ in range(1):
#     print("==============BEGIN=========================")
#     x = generate_blob_of_mass(49, 50, 0.5)
#     x.print()
#     print("=======================================")
#     x.gooify()
#     x.print()

import numpy as np
import random

# input : width, height, density
# output : 2darray
# NOTE This file is currently unused, and is not efficient.

class CA:
    def __init__(self, width, height, density, death_limit=4, birth_limit=3):
        self.width = width
        self.height = height
        self.density = density
        self.grid = np.full(
            (width, height), fill_value=True, order="F"
        )
        self.death_limit = death_limit
        self.birth_limit = birth_limit
    
    def generate(self):
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                if random.random() <= self.density:
                    self.grid[x, y] = False
    
    def refresh(self):
        """
        Dead cells = False
        Living cells = True
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

                # 인접한 살아있는 세포 숫자 계산
                cell_count = 0
                for x_add in range(3):
                    for y_add in range(3):
                        try:
                            if self.grid[x-1+x_add, y-1+y_add] == True:
                                cell_count += 1
                        except:
                            continue

                if self.grid[x][y]:
                    if cell_count < self.death_limit:
                        temp_grid[x][y] = True
                    else:
                        temp_grid[x][y] = False
                else:
                    if cell_count < self.birth_limit:
                        temp_grid[x][y] = True

        self.grid = temp_grid
                
    def print(self):
        for i in self.grid:
            for k in i:
                if k:
                    print("#", end="")
                else:
                    print(" ", end="")
            print(end="\n")

# TEST CODE
# grid = CA(40, 40, 0.5, 4, 3)
# grid.generate()
# for i in range(10):
#     grid.refresh()
# grid.print()

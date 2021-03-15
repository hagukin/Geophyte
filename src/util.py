from __future__ import annotations

import math
import numpy as np

def draw_circle(radius: int, fat_circles: bool = False):
    grid = np.zeros((radius*2 + 1, radius*2 + 1))
    for y in range(len(grid) + 1):
        for x in range(len(grid[0]) + 1):
            if pow(y - radius, 2) + pow(x - radius, 2) <= pow(radius, 2):
                grid[y,x] = 1
            elif fat_circles and pow(y - radius, 2) + pow(x - radius, 2) <= pow(radius, 2) * 1.4:
                grid[y,x] = 1
    return grid

def get_distance(x1, y1, x2, y2) -> float:
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


from __future__ import annotations
from typing import List
from tcod.map import compute_fov

import copy

def calc_explosion(engine, center_x: int, center_y: int, radius: int, fat_circles: bool = False, penetrate_wall: bool = True, only_in_sight: bool = False) -> List[Tuple(int,int)]:
    """
    returns list of coordinates that the circle includes.
    coordinates are given as an absolute value.
    """
    grid = [[(i - radius, j - radius) for i in range(radius*2 + 1)] for j in range(radius*2 + 1)]
    res = []
    mask = copy.copy(engine.game_map.tiles["walkable"][:])
    expl_range = compute_fov(
        mask,
        (center_x, center_y),
        radius=radius,
    )

    for horizontal in grid:
        for xy in horizontal:
            map_x = min(max(xy[0] + center_x, 0), engine.game_map.width - 1)
            map_y = min(max(xy[1] + center_y, 0), engine.game_map.height - 1)

            if not penetrate_wall and not expl_range[map_x, map_y]:
                continue
            if only_in_sight and not engine.game_map.visible[map_x, map_y]:
                continue

            if pow(xy[0], 2) + pow(xy[1], 2) <= pow(radius, 2):
                res.append((map_x, map_y))
            elif fat_circles and pow(xy[0], 2) + pow(xy[1], 2) <= pow(radius, 2) * 1.4:
                res.append((map_x, map_y))
    return res
from __future__ import annotations

import random
from typing import Tuple, Optional, List, Any
from tcod.map import compute_fov
from tcod import Console, console_get_width
from entity import Actor, Entity
from game import Game

import math
import numpy as np
import copy


def restart_game() -> None:
    """
    sys.executable: python executeable
    os.path.abspath(__file__): python file
    *sys.argv: remaining argument
    NOTE: Under construction
    """
    pass

def draw_circle(radius: int, fat_circles: bool = False):
    grid = np.zeros((radius*2 + 1, radius*2 + 1))
    for y in range(len(grid) + 1):
        for x in range(len(grid[0]) + 1):
            if pow(y - radius, 2) + pow(x - radius, 2) <= pow(radius, 2):
                grid[y,x] = 1
            elif fat_circles and pow(y - radius, 2) + pow(x - radius, 2) <= pow(radius, 2) * 1.4:
                grid[y,x] = 1
    return grid


def calc_circle(engine, center_x: int, center_y: int, radius: int, fat_circles: bool = False):
    """
    returns list of coordinates that the circle includes.
    coordinates are given as an absolute value.
    """
    grid = [[(i - radius, j - radius) for i in range(radius*2 + 1)] for j in range(radius*2 + 1)]
    res = []
    for horizontal in grid:
        for xy in horizontal:
            map_x = min(max(xy[0] + center_x, 0), engine.game_map.width - 1)
            map_y = min(max(xy[1] + center_y, 0), engine.game_map.height - 1)

            if pow(xy[0], 2) + pow(xy[1], 2) <= pow(radius, 2):
                res.append((map_x, map_y))
            elif fat_circles and pow(xy[0], 2) + pow(xy[1], 2) <= pow(radius, 2) * 1.4:
                res.append((map_x, map_y))
    return res


def calc_explosion(engine, center_x: int, center_y: int, radius: int, fat_circles: bool = False, penetrate_wall: bool = True, only_in_sight: bool = False) -> List[Tuple[int,int]]:
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


def get_distance(x1, y1, x2, y2) -> float:
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def grayscale(rgb: Tuple[int,int,int]) -> float:
    return (rgb[0] + rgb[1] + rgb[2]) / 3


def blueshift(rgb: Tuple[int,int,int]) -> Tuple[int,int,int]: #WARN: FUNCTION NOT TESTED
    gs = grayscale(rgb)
    red = 0 #temporary
    green = round(rgb[0] * 0.8) #Around 0~210. the lower the number, the closer the color gets to cyan
    green -= int(green / (gs * 765))
    blue = 255
    blue -= int(blue / (gs * 765))

    return (max(0,min(255,red)), max(0,min(255,green)), max(0,min(255,blue)))


def draw_thick_frame(
        console: Console,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        char_type: int = 0,
        fg: Optional[Tuple[int, int, int]] = None,
        bg: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        if char_type == 0:
            frame = (' ',' ',' ',' ',' ',' ',' ',' ',' ',' ')
        elif char_type == 1:
            frame = (' ','#','#','#','#','#','#','#','#','#')
        elif char_type == 2:
            frame = (' ','┗','━','┛','┃',' ','┃','┏','━','┓')
        elif char_type == 3:
            frame = (' ','╚','═','╝','║',' ','║','╔','═','╗')

        for ypos in range(y, y+height):
            if ypos == y:
                console.print(x, ypos, frame[7], fg, bg)
                for xpos in range(x+1, x+width):
                    console.print(xpos, ypos, frame[2], fg, bg)
                console.print(x+width-1, ypos, frame[9], fg, bg)
            elif ypos == y+height-1:
                console.print(x, ypos, frame[1], fg, bg)
                for xpos in range(x+1, x+width):
                    console.print(xpos, ypos, frame[2], fg, bg)
                console.print(x+width-1, ypos, frame[3], fg, bg)
            else:
                console.print(x, ypos, frame[4], fg, bg)
                console.print(x+width-1, ypos, frame[6], fg, bg)

        console.print(x + int(width/2 - len(title)/2), y, string=title, fg=fg, bg=bg)


def center_print(console, string: str, y: int, fg: Tuple[int,int,int] = None, bg: Tuple[int,int,int] = None) -> int:
    """
    Input: string
    Output: x coordinates for the string to be written on the center of the screen.
    """
    console.print(x=int(console_get_width(console) / 2) - int(len(string) / 2), y=y, string=string, fg=fg, bg=bg)


def draw_horizontal_line(
    console: Console,
    y: int, # top line
    thickness: int = 0, # = height
    title: str = "",
    fg: Optional[Tuple[int, int, int]] = None,
    bg: Optional[Tuple[int, int, int]] = None,
) -> None:
    for j in range(thickness):
        for i in range(console.width):
            console.print(x=i, y=y+j, string=" ", fg=fg, bg=bg)

    if title:
        center_print(console, title, y=int(thickness / 2) + y, fg=fg, bg=bg)


def multiline(
        string: str,
        width: int,
        newline_cnt: int=1
) -> Tuple[str, int]:
    x = 0
    line_cnt = 1
    tmp = ""
    while x < len(string):
        tmp += string[x:width + x]
        x += width
        if x < len(string):
            for i in range(newline_cnt):
                tmp += "\n" # prevent adding newline to the last sentence
                line_cnt += 1
    return tmp, line_cnt


def equip_region_name_to_str(region_name) -> str:
    translated = None
    if Game.language == "KR":
        if region_name == "main hand":
            translated = "메인 핸드"
        elif region_name == "off hand":
            translated = "오프 핸드"
        elif region_name == "head":
            translated = "머리"
        elif region_name == "face":
            translated = "얼굴"
        elif region_name == "torso":
            translated = "상반신"
        elif region_name == "fist":
            translated = "손"
        elif region_name == "belt":
            translated = "허리춤"
        elif region_name == "leg":
            translated = "다리"
        elif region_name == "feet":
            translated = "발"
        elif region_name == "cloak":
            translated = "망토"
        elif region_name == "amulet":
            translated = "아뮬렛"
        elif region_name == "left ring":
            translated = "왼손 반지"
        elif region_name == "right ring":
            translated = "오른손 반지"
        return translated
    return region_name


def spawn_monster_of_appr_diff_8way(gamemap, center_x: int, center_y: int, spawn_cnt: int=8, spawn_on_center: bool=False, randomize: bool=True) -> List[Actor]:
    """
    Args:
        spawn_cnt:
            the MAXIMUM number of entity spawned.
            It is very likely that the actual spawn count is smaller.
        randomize:
            randomize spawn direction.
    """
    spawned_list = []

    if spawn_on_center:
        if gamemap.check_tile_monster_spawnable(center_x, center_y):
            tmp = gamemap.spawn_monster_of_appr_diff_to_gamemap(center_x, center_y)
            if tmp:
                spawned_list.append(tmp)

    curr_spawn_cnt = 0
    xs = [1, 0, -1]
    ys = [1, 0, -1]
    if randomize:
        random.shuffle(xs)
        random.shuffle(ys) # randomize spawn place

    for dx in xs:
        for dy in ys:
            if dx == 0 and dy == 0:
                continue
            if curr_spawn_cnt >= spawn_cnt:
                return spawned_list
            if gamemap.check_tile_monster_spawnable(center_x+dx, center_y+dy):
                tmp = gamemap.spawn_monster_of_appr_diff_to_gamemap(center_x+dx, center_y+dy)
                if tmp:
                    spawned_list.append(tmp)
                    curr_spawn_cnt += 1

    return spawned_list


def spawn_entity_8way(entity, gamemap, center_x: int, center_y: int, spawn_cnt: int=8, spawn_on_center: bool=False, randomize: bool=True) -> List[Entity]:
    """
    The function will try to spawn the given entity near the center_x, y.

    Args:
        spawn_cnt:
            the MAXIMUM number of entity spawned.
            It is very likely that the actual spawn count is smaller.
        randomize:
            randomize spawn direction.
    """
    def spawn(_entity, _gamemap, _x: int, _y: int) -> Entity:
        if isinstance(_entity, Actor):
            if gamemap.check_tile_monster_spawnable(_x, _y):
                return _entity.spawn(_gamemap, _x, _y, is_active=True)
        else:
            return _entity.spawn(_gamemap, _x, _y)

    spawned_list = []

    if spawn_on_center:
        tmp = spawn(entity, gamemap, center_x, center_y)
        if tmp:
            spawned_list.append(tmp)

    curr_spawn_cnt = 0
    xs = [1, 0, -1]
    ys = [1, 0, -1]
    if randomize:
        random.shuffle(xs)
        random.shuffle(ys) # randomize spawn place

    for dx in xs:
        for dy in ys:
            if dx == 0 and dy == 0:
                continue
            if curr_spawn_cnt >= spawn_cnt:
                return spawned_list
            tmp = spawn(entity, gamemap, center_x+dx, center_y+dy)
            if tmp:
                spawned_list.append(tmp)
                curr_spawn_cnt += 1

    return spawned_list


def surround_grid_value_with(grid: np.ndarray, search_for: Any, surround_with: Any, surround_8way: bool = True) -> None:
    """Search the given value from the grid, and surround it with 'surround_with' object.
    NOTE: This function will overwrite ANY value with 'surround_with' in the list besides 'search_for'. """
    if surround_8way:
        dxdy = ((0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1))
    else:
        dxdy = ((0, 1), (1, 0), (0, -1), (-1, 0))

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == search_for:
                for dx, dy in dxdy:
                    nx = i + dx
                    ny = j + dy
                    if nx >= 0 and nx < len(grid) and ny >= 0 and ny < len(grid[0]) and grid[nx][ny] != search_for:
                        grid[nx][ny] = surround_with

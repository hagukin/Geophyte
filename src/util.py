from __future__ import annotations
from typing import Tuple, Optional
from tcod import Console

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

def grayscale(rgb: Tuple(int,int,int)) -> int:
    return (rgb[0] + rgb[1] + rgb[2]) / 3

def blueshift(rgb: Tuple(int,int,int)) -> Tuple(int,int,int): #WARN: FUNCTION NOT TESTED
    gs = grayscale(rgb) 
    red = 0 #temporary
    green = rgb[0] * 0.8 #Around 0~210. the lower the number, the closer the color gets to cyan
    green -= int(green / (gs * 765))
    blue = 255
    blue -= int(blue / (gs * 765))

    return (red, green, blue)

def draw_thick_frame(
        console: Console,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        fg: Optional[Tuple[int, int, int]] = None,
        bg: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        frame = ('','#','#','#','#','#','#','#','#','#',)
        #frame = (' ','╚','═','╝','║',' ','║','╔','═','╗')

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

        
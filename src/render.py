from __future__ import annotations
import random

import pygame.mouse

from main import main

from typing import Optional, Tuple, TYPE_CHECKING
from util import draw_thick_frame
from entity import Actor, Item

import tcod
import color

if TYPE_CHECKING:
    from game_map import GameMap
    from tcod import Console
    from tcod.context import Context
    from engine import Engine
    
def descend_background(console: Console, context: Context, main_color: Tuple, diversity: int = 10) -> None:
    """
    Clear entire console and display graphics that are going to be shown during descending(dungeon generating) process.

    Args:
        diversity:
            value used for shifting rgb value slightly.
            Lower number = smoother screen
    """
    console.clear(bg=color.black)
    for y in range(console.height):
        for x in range(console.width):
            console.print(
                x=x,
                y=y,
                string=" ",
                bg=( 
                    max(0, min(255, main_color[0] + random.randint(-diversity, diversity))),
                    max(0, min(255, main_color[1] + random.randint(-diversity, diversity))),
                    max(0, min(255, main_color[2] + random.randint(-diversity, diversity)))
                )
            )
    context.present(console, keep_aspect=True)







def insert_string(origin: str, insert: str, insert_loc: int) -> str:
    return origin[:insert_loc] + insert + origin[insert_loc:]


def render_message_window(
    console: Console, 
    engine: Engine, 
    text: str,
    fixed_width: bool = False,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    title: Optional[str] = "",
    frame_fg: Optional[Tuple[int, int, int]] = (218, 196, 0),
    frame_bg: Optional[Tuple[int, int, int]] = (0, 0, 0),
    text_fg: Optional[Tuple[int, int, int]] = (255, 255, 255),
) -> None:
    """
    Text should be given as a single line.
    The function will automatically divide it into multiple lines if necessary.
    Args:
        x, y:
            top-left position of the window.
            if set to None(default), the function will assign a position between (5,5) ~ (width/2, 5).
        width, height:
            if set to None(default), the function will assign a size between 5 ~ screen_width - 14.
    """
    # values
    screen_width, screen_height = engine.config["screen_width"], engine.config["screen_height"]
    msg = text
    msg_length = len(text)

    # constants
    DEFAULT_X_PADDING = 4
    DEFAULT_Y_PADDING = 4 # Fixed
    MAX_FRAME_WIDTH = screen_width - (DEFAULT_X_PADDING * 2)
    DEFAULT_FRAME_WIDTH = MAX_FRAME_WIDTH
    MAX_FRAME_HEIGHT = screen_height - (DEFAULT_Y_PADDING * 2)

    if fixed_width:
        msg_width = DEFAULT_FRAME_WIDTH - 2
        msg_height = min(int(msg_length / msg_width) + 1, MAX_FRAME_HEIGHT - 2)
        
        # Set frame width, height, x, y
        width, height = msg_width + 2, msg_height + 2
        if not x and not y:
            x, y = DEFAULT_X_PADDING, DEFAULT_Y_PADDING
        msg_x, msg_y = x+1, y+1

        # divide string into multiple parts
        loc = msg_width
        for i in range(0, msg_height):
            msg = insert_string(msg, "\n", loc * (i+1) + i) # adding i because the string gradually gets longer becuase "\n" is being added.
    else:
        if msg_length > MAX_FRAME_WIDTH - 2:
            msg_width = MAX_FRAME_WIDTH - 2
            msg_height = min(int(msg_length / msg_width) + 1, MAX_FRAME_HEIGHT - 2)

            # Set frame width, height, x, y
            if not width and not height:
                width, height = msg_width + 2, msg_height + 2
            if not x and not y:
                x, y = DEFAULT_X_PADDING, DEFAULT_Y_PADDING
            msg_x, msg_y = x+1, y+1

            # divide string into multiple parts
            loc = msg_width
            for i in range(0, msg_height):
                msg = insert_string(msg, "\n", loc * (i+1) + i) # adding i because the string gradually gets longer becuase "\n" is being added.
        else:
            msg_width = max(msg_length, len(title) + 2)
            msg_height = 1

            # Set frame width, height, x, y
            if not width and not height:
                width, height = msg_width + 2, msg_height + 2
            if not x and not y:
                x = int((screen_width - msg_width + 2) / 2)
                y = DEFAULT_Y_PADDING
            msg_x, msg_y = x+1, y+1

    # draw frame
    #draw_thick_frame(console, x, y, width, height, title=title, fg=frame_fg, bg=frame_bg)
    console.draw_frame(x, y, width, height, title=title, clear=True, fg=frame_fg, bg=frame_bg)

    # print msg
    engine.print_str(msg_x, msg_y, msg, fg=text_fg)

def render_img(
    console, 
    img,
    dest_x:int = 0, 
    dest_y:int = 0, 
    img_x: int = 0, 
    img_y: int = 0,
    img_width: int = -1,
    img_height: int = -1,
    ):
    """
    Args:
        https://python-tcod.readthedocs.io/en/latest/tcod/image.html?highlight=blit_2x#tcod.image.Image.blit_2x

        console (Console):
            Blit destination Console.
        dest_x (int):
            Console tile X position starting from the left at 0.
        dest_y (int):
            Console tile Y position starting from the top at 0.
        img_x (int):
            Left corner pixel of the Image to blit
        img_y (int):
            Top corner pixel of the Image to blit
        img_width (int):
            Width of the Image to blit. Use -1 for the full Image width.
        img_height (int):
            Height of the Image to blit. Use -1 for the full Image height.
    """
    # tcod.image_blit(image=img, console=console, x=dest_x, y=dest_y, bkgnd_flag=1, scalex=0.7, scaley=0.7, angle=0)
    tcod.image_blit_2x(image=img, console=console, dx=dest_x, dy=dest_y, sx=img_x, sy=img_y, w=img_width, h=img_height)
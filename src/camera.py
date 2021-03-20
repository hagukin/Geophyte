from engine import Engine
from typing import List

import tile_types
import numpy as np
import visual
import color
from collections import deque

class Camera:
    """
    A camera object for rendering game maps.

    absolute coordinates:
        location on the gamemap
    relative coordinates:
        location on the screen(console)
    """
    def __init__(self,
        engine: Engine,
        width: int=40, 
        height: int=30,
        xpos: int=0,
        ypos: int=0,
        display_x: int=0,
        display_y: int=0,
        show_all: bool=False
        ):
        """
        Args:
            xpos, ypos:
                position of the camera on in-game gamemap.
                Camera's location is its top leftmost corner.
            display_x:
                position of the camera on game screen / console.
        """
        self.engine = engine
        self.width = width
        self.half_width = int(width / 2)
        self.height = height
        self.half_height = int(height / 2)
        self.xpos = xpos # position on gamemap
        self.ypos = ypos
        self.display_x = display_x
        self.display_y = display_y
        self.show_all = show_all # TODO : Add feature and make it work properly with magic mapping
        self.visuals =  deque() # List of visual objects that are going to be rendered this turn.
        self.prev_gameturn = self.engine.game_turn # Keeps track of game turn to determine whether the camera should decrease the lifetime of the visual objects or not.

    @property
    def biggest_x(self):
        """returns biggest absolute x coordinate."""
        self.adjust()
        return self.xpos + self.width

    @property
    def biggest_y(self):
        """returns biggest absolute y coordinate."""
        self.adjust()
        return self.ypos + self.height

    def in_bounds(self, abs_x: int, abs_y: int) -> bool:
        coor = self.get_relative_coordinate(abs_x=abs_x, abs_y=abs_y)
        if self.display_x <= coor[0] <= self.width + self.display_x - 1 and self.display_y <= coor[1] <= self.height + self.display_y - 1:
            return True
        else:
            return False

    def adjust(self) -> None:
        """adjust camera position."""
        self.xpos = self.engine.player.x - self.half_width
        self.ypos = self.engine.player.y - self.half_height
        self.xpos = min(max(0, self.xpos), self.engine.game_map.width - self.width)
        self.ypos = min(max(0, self.ypos), self.engine.game_map.height - self.height)

    def render(self, console, draw_frame=False) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.tiles_rgb[self.display_x : self.width + self.display_x , self.display_y : self.height + self.display_y] = np.select(
            condlist=[self.engine.game_map.visible, self.engine.game_map.explored],
            choicelist=[self.engine.game_map.tiles["light"], self.engine.game_map.tiles["dark"]],
            default=tile_types.SHROUD,
        )[self.xpos : self.xpos+self.width, self.ypos : self.ypos+self.height]

        # Render entities
        for entity in self.engine.game_map.entities:
            if self.xpos <= entity.x < self.xpos + self.width and self.ypos <= entity.y < self.ypos + self.height:
                if self.engine.game_map.visible[entity.x, entity.y]:
                    console.print(
                        x=entity.x - self.xpos + self.display_x, 
                        y=entity.y - self.ypos + self.display_y, 
                        string=entity.char, 
                        fg=entity.fg, 
                        bg=entity.bg,
                    )

        # Render visual objects
        tmp_len = len(self.visuals)
        for _ in range(tmp_len):
            curr = self.visuals.pop()

            if self.xpos <= curr.x < self.xpos + self.width and self.ypos <= curr.y < self.ypos + self.height:
                console.print(
                    x=curr.x - self.xpos + self.display_x,
                    y=curr.y - self.ypos + self.display_y,
                    string=curr.char, 
                    fg=curr.fg, 
                    bg=curr.bg,
                )
            
            if (self.engine.game_turn > self.prev_gameturn):
                curr.lifetime -= 1
            if curr.lifetime > 0:
                self.visuals.append(curr)
        self.prev_gameturn = self.engine.game_turn

        # Draw frame around the camera
        if draw_frame:
            console.draw_frame(x=self.display_x-1, y=self.display_y-1, width=self.width+2, height=self.height+2, clear=False, fg=color.white)

    def get_relative_coordinate(self, *, abs_x: int=None, abs_y: int=None) -> int:
        """
        Changes absolute coordinates into relative coordinates.
        Input : x coordinates on the map
        Output : x coordinates on camera
        """
        if abs_x != None and abs_y != None:
            relative_x = abs_x - self.xpos + self.display_x
            relative_y = abs_y - self.ypos + self.display_y
            return relative_x, relative_y
        elif abs_x != None:
            relative_x = abs_x - self.xpos + self.display_x
            return relative_x
        else:
            relative_y = abs_y - self.ypos + self.display_y
            return relative_y

    def get_absolute_coordinate(self, *, relative_x: int=None, relative_y: int=None) -> int:
        """
        Changes relative coordinates into absolute coordinates.
        Input : x coordinates on camera
        Output : x coordinates on the map
        """
        if relative_x != None and relative_y != None:
            abs_x = relative_x + self.xpos - self.display_x
            abs_y = relative_y + self.ypos - self.display_y
            return abs_x, abs_y
        elif relative_x != None:
            abs_x = relative_x + self.xpos - self.display_x
            return abs_x
        else:
            abs_y = relative_y + self.ypos - self.display_y
            return abs_y

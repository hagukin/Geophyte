from typing import List, Optional, Tuple

import tiles
import numpy as np
import visual
import copy
import color
from collections import deque
from game import Game

class Camera:
    """
    A camera object for rendering game maps.

    absolute coordinates:
        location on the gamemap
    relative coordinates:
        location on the screen(console)
    """
    def __init__(self,
        engine,
        width: int=40, 
        height: int=30,
        xpos: int=0,
        ypos: int=0,
        display_x: int=0,
        display_y: int=0,
        ):
        """
        Args:
            xpos, ypos:
                position of the camera on in-game gamemap.
                Camera's location is its top leftmost corner.
            display_x:
                position of the camera on game screen / console.
            dx, dy:
                cam x position = xpos + dx
        """
        self.width = width
        self.half_width = int(width / 2)
        self.height = height
        self.half_height = int(height / 2)
        self.xpos = xpos # position on gamemap
        self.ypos = ypos
        self.dx = 0
        self.dy = 0
        self.display_x = display_x
        self.display_y = display_y
        self.visuals =  deque() # List of visual objects that are going to be rendered this turn.
        self.prev_visuals = deque()
        self.prev_gameturn = 1 # Keeps track of game turn to determine whether the camera should decrease the lifetime of the visual objects or not.

    @property
    def engine(self):
        return Game.engine

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

    def move(self, dx: int=0, dy: int=0) -> bool:
        """Move the camera position."""
        failed = False
        if 0 <= self.xpos + dx <= self.engine.game_map.width - self.width:
            self.dx = self.dx + dx
        else:
            failed = True
        if 0 <= self.ypos + dy <= self.engine.game_map.height - self.height:
            self.dy = self.dy + dy
        else:
            failed = True
        return not failed

    def clear_visuals(self) -> None:
        self.visuals.clear()
        self.prev_visuals.clear()

    def reset_dxdy(self, adjust:bool=True) -> None:
        self.dx = 0
        self.dy = 0
        if adjust:
            self.adjust()

    def in_bounds(self, abs_x: int, abs_y: int) -> bool:
        coor = self.abs_to_rel(abs_x=abs_x, abs_y=abs_y)
        if self.display_x <= coor[0] <= self.width + self.display_x - 1 and self.display_y <= coor[1] <= self.height + self.display_y - 1:
            return True
        else:
            return False

    def adjust(self) -> None:
        """adjust camera position."""
        self.xpos = self.engine.player.x - self.half_width
        self.ypos = self.engine.player.y - self.half_height
        self.xpos = min(max(0, self.xpos), self.engine.game_map.width - self.width) + self.dx
        self.ypos = min(max(0, self.ypos), self.engine.game_map.height - self.height) + self.dy

    def render_visuals(self, console) -> None:
        """
        Render visual objects.

        NOTE: Visual objects can be rendered multiple times between one game turn and next game turn,
        since multiple gameloops can exist between them.
        """
        if self.engine.game_turn > self.prev_gameturn:
            self.prev_visuals.clear()
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
                self.prev_visuals.append(curr)
                curr.lifetime -= 1
                if curr.lifetime > 0:
                    self.visuals.append(curr)
            
            self.prev_gameturn = self.engine.game_turn
        elif self.engine.game_turn == self.prev_gameturn:
            for curr in self.prev_visuals:
                if self.xpos <= curr.x < self.xpos + self.width and self.ypos <= curr.y < self.ypos + self.height:
                    console.print(
                        x=curr.x - self.xpos + self.display_x,
                        y=curr.y - self.ypos + self.display_y,
                        string=curr.char, 
                        fg=curr.fg, 
                        bg=curr.bg,
                    )

    def render_entities(self, console) -> None:
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

    def render_tiles(self, console) -> None:
        console.tiles_rgb[self.display_x : self.width + self.display_x , self.display_y : self.height + self.display_y] = np.select(
            condlist=[self.engine.game_map.visible, self.engine.game_map.explored],
            choicelist=[self.engine.game_map.tiles["light"], self.engine.game_map.tiles["dark"]],
            default=tiles.SHROUD,
        )[self.xpos : self.xpos+self.width, self.ypos : self.ypos+self.height]

    def render(self, console, draw_frame=False) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        # update enetities, sort them
        self.engine.game_map.sort_entities()
        self.engine.update_entity_in_sight()

        # Render tiles
        self.render_tiles(console)

        # Render entities
        self.render_entities(console)
        
        # Render visual objects
        self.render_visuals(console)

        # Draw frame around the camera
        if draw_frame:
            import util
            util.draw_thick_frame(console, x=self.display_x-1, y=self.display_y-1, width=self.width+2, height=self.height+2, fg=color.camera_frame_fg, bg=color.camera_frame_bg)
            console.draw_frame(x=self.display_x-1, y=self.display_y-1, width=self.width+2, height=self.height+2, clear=False, fg=color.camera_frame_fg, bg=color.camera_frame_bg)

    def abs_to_rel(self, abs_x: int, abs_y: int) -> Tuple[int,int]:
        """
        Changes absolute coordinates into relative coordinates.
        Input : x coordinates on the map
        Output : x coordinates on camera
        """
        rel_x = abs_x - self.xpos + self.display_x
        rel_y = abs_y - self.ypos + self.display_y
        return rel_x, rel_y

    def rel_to_abs(self, rel_x: int, rel_y: int) -> Tuple[int,int]:
        """
        Changes relative coordinates into absolute coordinates.
        Input : x coordinates on camera
        Output : x coordinates on the map
        """
        abs_x = rel_x + self.xpos - self.display_x
        abs_y = rel_y + self.ypos - self.display_y
        return abs_x, abs_y

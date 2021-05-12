from engine import Engine
from typing import List, Any, Tuple

import copy
import pygame.surface
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
        width: int=1280,
        height: int=720,
        xpos: int=0,
        ypos: int=0,
        display_x: int=0,
        display_y: int=0,
        zoom_ratio: float = 1,
        show_all: bool=False
        ):
        """
        Args:
            width, height:
                the tile width / height of this camera.
                e.g. 40 x 30
            xpos, ypos:
                position of the camera on in-game gamemap.
                Camera's location is its top leftmost corner.
            display_x:
                position of the camera on game screen / console.
        Vars:
            global_tick:
                tick value for all sprites that are being rendered.
                Sprites that are being rendered will use global_tick as there tick value by calling sprite.set_tick(global_tick).
                NOTE: To change indivisual sprites' tick, use sprite.update(tick) instead.
        """
        self.engine = engine
        self.width = width
        self.height = height
        self.xpos = xpos # grid position on gamemap
        self.ypos = ypos
        self.display_x = display_x # pixel position on display
        self.display_y = display_y

        self.zoom_ratio = zoom_ratio
        self.zoom_index = 1 # x1
        self.zoom_ratios = (0.5,1,1.75,2,3.5)
        self.origin_tile_size = self.engine.config["origin_tile_size"]
        self.tile_size = int(self.origin_tile_size * self.zoom_ratio)
        self.show_all = show_all # TODO : Add feature and make it work properly with magic mapping
        self.global_tick = 0.0

    def __deepcopy__(self, memo):
        return self #TODO DISABLED DEEPCOPY

    @property
    def gamemap(self):
        return self.engine.game_map

    @property
    def tile_width(self):
        return int(self.width / self.tile_size)

    @property
    def half_tile_width(self):
        return int(self.tile_width / 2)

    @property
    def tile_height(self):
        return int(self.height / self.tile_size)

    @property
    def half_tile_height(self):
        return int(self.tile_height / 2)

    def change_zoom_to(self, zoom_ratio: float) -> None:
        """Resize every in-game sprites relative to given zoom_ratio."""
        self.zoom_ratio = zoom_ratio
        self.tile_size = int(self.origin_tile_size * self.zoom_ratio)

    def zoom_in(self):
        self.zoom_index = min(self.zoom_index + 1, len(self.zoom_ratios) - 1)
        self.zoom_ratio = self.zoom_ratios[self.zoom_index]
        self.change_zoom_to(self.zoom_ratio)

    def zoom_out(self):
        self.zoom_index = max(self.zoom_index - 1, 0)
        self.zoom_ratio = self.zoom_ratios[self.zoom_index]
        self.change_zoom_to(self.zoom_ratio)

    def rel_cor(self, abs_x: int, abs_y: int) -> Tuple[int,int]:
        """
        Changes absolute coordinates into relative coordinates.
        Input : x coordinates on the map
        Output : x coordinates on camera
        """
        return abs_x - self.xpos, abs_y - self.ypos

    def abs_cor(self, relative_x: int, relative_y: int) -> Tuple[int,int]:
        """
        Changes relative coordinates into absolute coordinates.
        Input : x coordinates on camera
        Output : x coordinates on the map
        """
        return relative_x + self.xpos, relative_y + self.ypos

    def rel_display_cor(self, relative_x: int, relative_y: int) -> Tuple[int,int]:
        """
        Changes relative coordinates into display coordinates.
        Input : x coordinates on camera
        Output : x coordinates on the screen(surface)
        """
        return relative_x * self.tile_size + self.display_x, relative_y * self.tile_size + self.display_y

    def abs_display_cor(self, abs_x: int, abs_y: int) -> Tuple[int,int]:
        """
        Changes relative coordinates into display coordinates.
        Input : x coordinates on the map
        Output : x coordinates on the screen(surface)
        """
        return (abs_x - self.xpos) * self.tile_size + self.display_x, (abs_y - self.ypos) * self.tile_size + self.display_y

    def diplay_abs_cor(self, display_x: int, display_y: int) -> Tuple[int,int]:
        """
        Input: display xy coordinates
        Output: gamemap xy coordinates
        """
        return int((display_x - self.display_x) / self.tile_size) + self.xpos, int((display_y - self.display_y) / self.tile_size) + self.ypos

    def abs_in_bounds(self, abs_x: int, abs_y: int) -> bool: #TODO FIXME
        """
        Check if given x, y map coordinates is in camera's rectangular area's coordinates.
        """
        if self.xpos <= abs_x < self.tile_width + self.xpos and self.ypos <= abs_y < self.tile_height + self.ypos:
            return True
        else:
            return False

    def adjust(self) -> None:
        """adjust camera position."""
        self.xpos = self.engine.player.x - self.half_tile_width
        self.ypos = self.engine.player.y - self.half_tile_height
        self.xpos = min(max(0, self.xpos), self.engine.game_map.width - self.tile_width)
        self.ypos = min(max(0, self.ypos), self.engine.game_map.height - self.tile_height)

    def update_tick(self, speed:float):
        self.global_tick += speed
        if self.global_tick > 1:
            self.global_tick -= 1

    def update_entities(self, speed: float) -> None:
        for entity in self.engine.game_map.entities:
            if self.gamemap.visible[entity.x, entity.y]:
                entity.skin.curr_sprite.update(speed)

    def update_tiles(self, speed: float) -> None:
        """
        Update tile informations.
        Change current tile sprite information if necessary.
        """
        self.update_tick(speed)
        for x in range(self.xpos, self.xpos+self.tile_width):
            for y in range(self.ypos, self.ypos+self.tile_height):
                if self.gamemap.visible[x,y]:
                    if self.gamemap.sprites[x,y].sprite_id == self.gamemap.tiles[x,y].skin.light().sprite_id:
                        self.gamemap.sprites[x,y].set_tick(self.global_tick)
                    else:
                        self.gamemap.sprites[x,y] = self.gamemap.tiles[x,y].skin.light()
                        self.gamemap.sprites[x, y].set_tick(self.global_tick)
                elif self.gamemap.explored[x, y]:
                    if self.gamemap.sprites[x, y].sprite_id == self.gamemap.tiles[x,y].skin.dark().sprite_id:
                        self.gamemap.sprites[x,y].set_tick(self.global_tick)
                    else:
                        self.gamemap.sprites[x,y] = self.gamemap.tiles[x,y].skin.dark()
                        self.gamemap.sprites[x, y].set_tick(self.global_tick)

    def render_entities(self, screen) -> None:
        """
        Renders all entities in visible area.
        """
        for entity in self.engine.game_map.entities:
            if self.engine.game_map.visible[entity.x, entity.y]:
                if self.abs_in_bounds(entity.x, entity.y):
                    screen.blit(pygame.transform.scale(entity.skin.curr_sprite.curr_img, (self.tile_size, self.tile_size)),
                                self.abs_display_cor(entity.x, entity.y))

    def render_tiles(self, screen) -> None:
        for x in range(self.xpos, self.xpos + self.tile_width):
            for y in range(self.ypos, self.ypos + self.tile_height):
                screen.blit(pygame.transform.scale(self.gamemap.sprites[x,y].curr_img, (self.tile_size, self.tile_size)),
                            self.abs_display_cor(x, y))

    def update_frame(self, tile_speed: float, entity_speed: float):
        """
        Updates every graphical information in camera's visible area.
        """
        self.update_tiles(tile_speed)
        self.update_entities(entity_speed)

    def render(self, screen, draw_frame:bool=False) -> None:
        """
        Renders everything within the displaying area..
        """
        self.render_tiles(screen)
        self.render_entities(screen)

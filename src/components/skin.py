from __future__ import annotations

import copy
import random

from sprite import GameSprite
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity

class Skin():
    """An object that can contain one or more sprites depending on its purpose.
    Either entities or tiles can have this as a component."""
    def __init__(self, sprites_set: Optional[List[Dict]] = None):
        """
        Vars:
            sprites:
                Dictionary.
                key - string, value - Sprites

                NOTE:
                    < Mandatory types of sprites for each object types >
                    Actors:
                        default
                    Semiactors:
                        default
                    Items:
                        default
                    Tiles:
                        light
                        dark
        """
        self.parent: Optional[Entity] = None
        self.curr_index = 0
        if sprites_set:
            self.sprites_set: List[Dict] = sprites_set
        else:
            self.sprites_set = list()
            self.sprites_set.append(dict())

    @property
    def curr_sprite_set(self):
        return self.sprites_set[self.curr_index]

    def randomize(self) -> Skin:
        """Create a new instance of this variable and randomize it."""
        self.curr_index = random.randint(0,len(self.sprites_set)-1)
        return self

    def add_sprites(self, sprites: Dict):
        """Function will overwrite any preexisting items."""
        self.sprites_set.append(sprites)


class TileSkin(Skin):
    """Skin component for entities."""
    def __init__(self,
                 sprites_set: Optional[List[Dict]] = None,
                 is_dynamic: bool=False,
                 bitmap_true_when_not_walkable: bool = False,
                 bitmap_true_when_walkable: bool = False,
                 bitmap_true_when_not_water: bool = False,
                 bitmap_true_when_water: bool = False,
                 ):
        """
        NOTE:
            if the tile uses dynamic feature, tile_id should follow the following form.
            light/dark + bitmap number
            e.g. l

        Args:
            is_dynamic:
                whether this tile uses different sprites depending on the walls location or not.
        Vars:
            bitmap:
                handles nearby blocking tiles information. NOTE: udlr 0000
                NOTE: Warning) Bitmap will stay True for ALL BLOCKING TILES including walls, etc.
                NOTE: For most situations, self.bitmap value should remain constant after initialization.
                This is to prevent tile graphics from constantly changing after the initial procgen.
            bitmap_true_when_not_walkable:
                if True, the tile will set its bitmap value to 1 when there is non-walkable tile nearby.

            e.g. A Floor tile will have
            bitmap_true_when_not_walkable = True
            bitmap_true_when_walkable = False
            bitmap_true_when_not_water = False
            bitmap_true_when_water = True
        """
        super().__init__(sprites_set)
        self.parent = None
        self.is_dynamic = is_dynamic
        if is_dynamic:
            self._bitmap: str = "0000" # No walls nearby
            self.bitmap_true_when_not_walkable = bitmap_true_when_not_walkable
            self.bitmap_true_when_walkable = bitmap_true_when_walkable
            self.bitmap_true_when_not_water = bitmap_true_when_not_water
            self.bitmap_true_when_water = bitmap_true_when_water


    @property
    def bitmap(self) -> str:
        return self._bitmap

    def change_bitmap(self, value: str) -> None:
        """NOTE: Generally you shouldn't change the bitmap of a tile."""
        self._bitmap = value

    def check_bitmap_condition(self, gamemap, x, y) -> bool:
        """If the given coordinates satisfy this TileSkin's bitmap toggle condition, return True.
        e.g. stone_floor.check_if_bitmap_true() will return True if the given x, y is not walkable."""
        if self.bitmap_true_when_not_walkable and not gamemap.tiles[x,y].walkable:
            return True
        if self.bitmap_true_when_walkable and gamemap.tiles[x,y].walkable:
            return True
        if self.bitmap_true_when_not_water \
                and gamemap.tiles[x,y].tile_id != "deep_water"\
                and gamemap.tiles[x,y].tile_id != "shallow_water":
            return True
        if self.bitmap_true_when_water \
                and (gamemap.tiles[x,y].tile_id == "deep_water"\
                or gamemap.tiles[x,y].tile_id == "shallow_water"):
            return True

        return False

    def light(self) -> GameSprite:
        if self.is_dynamic:
            return self.curr_sprite_set["light"+self.bitmap]
        return self.curr_sprite_set["light"]

    def dark(self) -> GameSprite:
        if self.is_dynamic:
            return self.curr_sprite_set["dark"+self.bitmap]
        return self.curr_sprite_set["dark"]


class EntitySkin(Skin):
    """Skin component for entities."""

    def __init__(self, sprites_set: Optional[List[Dict]] = None, curr_sprite_state: str="default"):
        """
        Vars:
            current_sprite_state:
                string. indicates the current state this skin component is on.
        """
        super().__init__(sprites_set)
        self.curr_sprite_state: str = curr_sprite_state

    @property
    def default_sprite(self):
        return self.curr_sprite_set["default"]

    @property
    def curr_sprite(self):
        return self.curr_sprite_set[self.curr_sprite_state]


class VisualSkin(Skin):
    """Skin component for visual objects."""

    def __init__(self, sprites_set: Optional[List[Dict]] = None, curr_sprite_state: str="default"):
        """
        Vars:
            current_sprite_state:
                string. indicates the current state this skin component is on.
        """
        super().__init__(sprites_set)
        self.curr_sprite_state: str = curr_sprite_state

    @property
    def curr_sprite(self):
        return self.curr_sprite_set[self.curr_sprite_state]
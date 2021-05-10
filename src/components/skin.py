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
    def __init__(self, sprites_set: Optional[List[Dict]] = None):
        super().__init__(sprites_set)
        self.parent = None

    def light(self) -> GameSprite:
        return self.curr_sprite_set["light"]

    def dark(self) -> GameSprite:
        return self.curr_sprite_set["dark"]


class EntitySkin(Skin):
    """Skin component for entities."""

    def __init__(self, sprites_set: Optional[List[Dict]] = None):
        """
        Vars:
            current_sprite_state:
                string. indicates the current state this skin component is on.
        """
        super().__init__(sprites_set)
        self.curr_sprite_state: str = "default"

    @property
    def curr_sprite(self):
        return self.curr_sprite_set[self.curr_sprite_state]
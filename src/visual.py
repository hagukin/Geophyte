from __future__ import annotations
from typing import Optional, Tuple
from components.skin import Skin

import skin_factories

class Visual():
    def __init__(
        self, 
        x: int, #NOTE: X,Y ARE ABSOLUTE COORDINATES
        y: int,
        char: str,
        skin: Skin = skin_factories.skin_debug_tile(False),
        fg: Optional[Tuple[int,int,int]] = None,
        bg: Optional[Tuple[int,int,int]] = None,
        lifetime: int=1
        ):
        """
        Args:
            lifetime(int) :
                game turn left until this visual objects deletes itself.
                NOTE: The measurement isn't a gameloop, its a game turn. (player's action point spent)
        """
        self.x = x
        self.y = y
        self.char = char
        self.skin = skin
        self.fg = fg
        self.bg = bg
        self.lifetime = lifetime
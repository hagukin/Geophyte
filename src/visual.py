from __future__ import annotations
from typing import Optional, Tuple

class Visual():
    def __init__(
        self, 
        x: int, 
        y: int, 
        char: str, 
        fg: Optional[Tuple(int,int,int)] = None, 
        bg: Optional[Tuple(int,int,int)] = None, 
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
        self.fg = fg
        self.bg = bg
        self.lifetime = lifetime
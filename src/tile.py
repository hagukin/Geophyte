from __future__ import annotations
from typing import Optional, List
from components.skin import TileSkin


class Tile():
    def __init__(self,
                 skin: TileSkin,
                 walkable: bool,
                 safe_to_walk: bool,
                 flammable: float,
                 phaseable: bool,
                 transparent: int,
                 tile_name: str,
                 tile_id: str
                 ):
        self.skin = skin
        self.walkable = walkable
        self.safe_to_walk = safe_to_walk
        self.flammable = flammable
        self.phaseable = phaseable
        self.transparent = transparent
        self.tile_name = tile_name
        self.tile_id = tile_id


    def randomize(self) -> Tile:
        """Randomize self, and return self."""
        self.skin = self.skin.randomize()
        return self
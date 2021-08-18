from __future__ import annotations
from typing import TYPE_CHECKING
from game import Game

if TYPE_CHECKING:
    from engine import Engine
    from game_map import GameMap


class BaseComponent:
    def __init__(self, parent=None):
        self.parent = parent

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        return Game.engine
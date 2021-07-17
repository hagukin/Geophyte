from __future__ import annotations
from typing import TYPE_CHECKING
from game_map import GameMap
from game import Game

if TYPE_CHECKING:
    from engine import Engine


class BaseComponent:
    def __init__(self, parent=None):
        self.parent = parent

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        if self.parent.gamemap == None:
            print(f"WARNING::{self.parent.entity_id} tried to access engine object from its component '{self}' without having a gamemap.")
        return Game.engine
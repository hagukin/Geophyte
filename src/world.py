from __future__ import annotations
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, List
from engine import Engine
from game import Game

import shelve
import os
import copy

class World():
    def __init__(
        self,
        seed,
        max_depth:int=999 #TODO: Unused value
    ):
        """
        Represents the game world.
        Mainly handles memory management.

        Vars:
            saved_world:
                List with integers inside. Contains a List of depths of generated levels that are available for the game to use whenever it wants.
        """
        self.__seed = seed
        self.max_depth = max_depth
        self.mem_world = {}
        self.manual_deallocating_gamemap = [] # List of depths of gamemaps that are ignored from the optimization process.
        # NOTE: You must deallocate these manually.
        self.saved_maps = set() # # List of depths of gamemaps that are generated.
        self.mem_capacity = 1 # maximum number of (1 + mem_capacity*2) gamemaps will be on the memory. MIN: 2 
        #TODO DEBUG
        # NOTE: Change this number depending on the RAM size
    @property
    def engine(self):
        return Game.engine

    @property
    def seed(self):
        return copy.deepcopy(self.__seed) # Prevent passing a reference

    def check_has_map(self, depth: int) -> bool:
        if depth in self.saved_maps:
            return True
        return False

    def save_map(self, gamemap, depth:int) -> None:
        with shelve.open(os.getcwd()+f"\\saves\\worlds\\{self.engine.player.entity_id}") as save_file:
            # prevent pickle lib error(cannot serialize c objects)
            save_file["depth"+str(depth)] = gamemap
            save_file.close()

    def load_map(self, depth: int):
        if not self.check_has_map(depth=depth):
            raise Exception(f"ERROR::world.load_map() - Cannot find {depth} depth map.")

        if self.check_if_map_on_mem(depth):
            print(f"WARNING::Depth {depth} already exists on the memory. Will ignore the loading request.")
            return self.mem_world[depth]
        # Check if file exists
        if not os.path.isfile(os.getcwd()+f"\\saves\\worlds\\{self.engine.player.entity_id}.dat"):
            raise FileNotFoundError

        with shelve.open(os.getcwd()+f"\\saves\\worlds\\{self.engine.player.entity_id}") as save_file:
            gamemap = save_file["depth"+str(depth)]
            self.mem_world[depth] = gamemap
            save_file.close()
        return self.mem_world[depth]

    def optimize(self) -> None:
        """
        Delete unused gamemaps(or gamemaps that are very likely going to be unused for a while).
        """
        for depth in self.saved_maps:
            if (depth >= self.engine.depth - self.mem_capacity and depth <= self.engine.depth + self.mem_capacity) or depth in self.manual_deallocating_gamemap:
                if not self.check_if_map_on_mem(depth):
                    self.mem_world[depth] = self.get_map(depth)
            else:
                self.mem_world[depth] = None

            # DEBUG
            # for x, y in self.mem_world.items():
            #     print(x, y)
            # print(f"engine.depth:{self.engine.depth}")

    def check_if_map_on_mem(self, depth: int) -> bool:
        if depth not in list(self.mem_world.keys()) or self.mem_world[depth] is None:
            return False
        return True

    def get_map(self, depth:int):
        """
        Use get() instead of directly accessing mem_world[].
        NOTE: load_map() loads the map from the data file, while get_map() get the map no matter its on memory or not.
        Outside of this class boundary, using get_map is preferred.
        """
        if self.check_if_map_on_mem(depth):
            return self.mem_world[depth]
        elif depth in self.saved_maps:
            return self.load_map(depth)
        else:
            return None
    
    def set_map(self, gamemap, depth: int) -> None:
        self.mem_world[depth] = gamemap
        self.saved_maps.add(depth)
        return self.save_map(gamemap, depth)
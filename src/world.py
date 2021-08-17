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
            mem_capacity:
                maximum number of (1 + mem_capacity*2) gamemaps will be on the memory.
                MINIMUM VALUE = 1
        """
        self.__seed = seed
        self.max_depth = max_depth
        self.mem_world = {}

        self.depths_that_are_permanently_on_memory = [] # List of depths of gamemaps that are ignored from the optimization process, meaning they stay on the memory until the game closes.
        # Use with caution. You must deallocate these manually.

        self.saved_maps = set() # # List of depths of gamemaps that are generated.
        self.mem_capacity = 1 # MINIMUM VALUE = 1
        #TODO DEBUG
        # NOTE: Change this number depending on the RAM size
    @property
    def engine(self):
        return Game.engine

    @property
    def seed(self):
        return copy.deepcopy(self.__seed) # Prevent passing a reference

    def check_if_should_exist_in_memory(self, depth: int) -> bool:
        if (depth >= self.engine.depth - self.mem_capacity and depth <= self.engine.depth + self.mem_capacity) or depth in self.depths_that_are_permanently_on_memory:
            return True
        return False

    def check_if_map_has_been_generated(self, depth: int) -> bool:
        if depth in self.saved_maps:
            return True
        return False

    def save_map_to_memory(self, gamemap, depth: int) -> None:
        """Save map to the memory. Map is yet to be saved as a solid data(serialized form)."""
        self.mem_world[depth] = gamemap
        self.saved_maps.add(depth)
        return None

    def save_map_to_serialized_data(self, gamemap, depth:int) -> None:
        with shelve.open(os.getcwd()+f"\\storage\\data\\game") as save_file:
            # prevent pickle lib error(cannot serialize c objects)
            if gamemap == None:
                print("D")
            save_file["cache_depth_"+str(depth)] = gamemap
            save_file.close()

    def load_map_from_memory(self, depth: int):
        return self.mem_world[depth]

    def load_map_from_seriallized_data(self, depth: int):
        """Load a map from serialized data, not memory"""
        # Check if file exists
        if not os.path.isfile(os.getcwd()+f"\\storage\\data\\game.dat"):
            raise FileNotFoundError

        with shelve.open(os.getcwd()+f"\\storage\\data\\game") as save_file:
            gamemap = save_file["cache_depth_"+str(depth)]
        return gamemap

    def optimize(self) -> None:
        """
        Delete unused gamemaps from memory, and load gamemaps from serialized data if they are in mem_capacity range.
        """
        for depth in self.saved_maps:
            if self.check_if_should_exist_in_memory(depth):
                if not self.check_if_map_on_mem(depth):
                    self.mem_world[depth] = self.load_map_from_seriallized_data(depth)
            else:
                self.mem_world[depth] = None

    def check_if_map_on_mem(self, depth: int) -> bool:
        if depth not in list(self.mem_world.keys()) or self.mem_world[depth] is None:
            return False
        return True

    def save_world(self) -> None:
        """Save & Serialize ENTIRE existing gamemaps. For performance issue its recommended to use save_mem() or save_map_to_serialized_data() selectively."""
        for depth in self.saved_maps:
            self.save_map_to_serialized_data(self.get_map(depth), depth)

    def save_mem(self):
        """Update saved maps"""
        for depth in self.mem_world.keys():
            if self.check_if_map_on_mem(depth):
                self.save_map_to_serialized_data(self.load_map_from_memory(depth), depth)

    def get_map(self, depth:int):
        """
        Return:
            Retrieve map information from EITHER memory or data.
            Will ALWAYS prioritze memory data.

        NOTE: load_map_from_seriallized_data() loads the map from the data file, while get_map() get the map no matter its on memory or not.
        Outside of this class boundary, using get_map is preferred.
        """
        if self.check_if_map_on_mem(depth): # Prioritize memory.
            return self.load_map_from_memory(depth)
        elif depth in self.saved_maps:
            return self.load_map_from_seriallized_data(depth)
        else:
            print("FATAL ERROR:: {depth} depth missing")
            for k, v in self.mem_world.items():
                print(f"in-memory: {k, v}")
            return None

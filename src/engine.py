from __future__ import annotations

import tcod

from camera import Camera
from typing import TYPE_CHECKING, List, Optional, Tuple, Set, Deque, Dict
from util import draw_thick_frame
from tcod.path import SimpleGraph, Pathfinder
from tcod.console import Console
from tcod.map import compute_fov
from item_manager import ItemManager

import numpy as np
import random
import exceptions
import copy
import traceback
import color

from sound import SoundManager
from collections import deque
from actions import BumpAction, DescendAction, AscendAction, PickupAction
from procgen import generate_dungeon
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render import (
    render_character_name,
    render_gameinfo,
    render_health_bar,
    render_mana_bar,
    render_names_at_mouse_location,
    render_character_status,
    render_character_state,
    render_message_window,
)
from entity import Actor, Entity, Item, SemiActor

if TYPE_CHECKING:
    from game_map import GameMap
    from input_handlers import EventHandler
    from world import World


class Engine:
    def __init__(self, player: Actor):
        """
        Vars:
            player_path:
                Uses deque data structure to save player's path when the player uses mouse driven movements.
            player_dir:
                Uses tuple to save player's action direction(dx,dy) when the player uses mouse driven actions.
            actors_in_sight, items_in_sight:
                Set of actors/items that are currently in player's visible area.
            prev_actors_in_sight, prev_items_in_sight:
                Set of actors/items that was in player's visible area one turn ago.
            context:
                The actual window screen that shows the game.
            game_map:
                Current gamemap that player is in.
            world:
                Represents the entire game world.
        """
        self.event_handler: EventHandler = MainGameEventHandler()
        self.message_log = MessageLog(engine=self)
        self.player = player
        self.player_path:Deque = deque([])
        self.player_dir = None
        self.actors_in_sight: Set[Actor] = set()
        self.items_in_sight: Set[Item] = set()
        self.prev_actors_in_sight: Set[Actor] = set()
        self.prev_items_in_sight: Set[Item] = set()
        self.game_turn: int = 0
        self._mouse_pos: Tuple[int,int] = (0,0)
        self.depth: int = 0 # NOTE: engine.depth != gamemap.depth. Latter is a constant.
        self.toughness: int = 0
        self.easteregg: int = 0
        self._monster_activation_distance = 10 # distance
        self.sound_manager: SoundManager = None # Initialized in main
        self.config: Dict = None # Set from initialization
        self.console: tcod.Console = None # Set from main
        self.context: tcod.context.Context = None # Set from main
        self.camera: Camera = None # Set from initialization
        self.world: World = None # Set from initialization
        self.game_map: GameMap = None # Set from initialization
        self.item_manager: ItemManager = None # Set from initialization -> engine.initialize_item_manager()

    def set_mouse_pos(self, x, y):
        self._mouse_pos = x, y

    @property
    def mouse_location(self) -> Tuple[int,int]:
        if self._mouse_pos:
            return self._mouse_pos
        else:
            return 0,0

    @property
    def monster_activation_distance(self) -> int:
        return self._monster_activation_distance

    def clamp_mouse_on_map_rel(self, rel_x: int, rel_y: int) -> Tuple[int, int]:
        """Clamp the given x, y coordinates within the game map boundaries."""
        nx = max(self.camera.display_x, min(rel_x, self.camera.display_x + self.camera.width - 1))
        ny = max(self.camera.display_y, min(rel_y, self.camera.display_x + self.camera.height - 1))
        return nx, ny

    def clamp_mouse_on_map_abs(self, abs_x: int, abs_y: int) -> Tuple[int, int]:
        """Clamp the given x, y coordinates within the game map boundaries."""
        nx = max(self.camera.xpos, min(abs_x, self.camera.biggest_x - 1))
        ny = max(self.camera.ypos, min(abs_y, self.camera.biggest_y - 1))
        return nx, ny

    def initialize_item_manager(self):
        if self.item_manager == None:
            self.item_manager = ItemManager()
            self.item_manager.initialize_data()

        return None

    def refresh_gamemap_entities(self) -> None:
        """Refresh every entities' gamemap information to current gamemap.
        Function's main purpose is to prevent entity having the wrong gamemap information."""
        for e in self.game_map.entities:
            if e.gamemap != self.game_map:
                e.gamemap = self.game_map
                print(f"ERROR::{e.entity_id} has the wrong gamemap.")

    def check_entity_in_sight_of_actor(self, actor: Actor, entity: Entity) -> bool:
        if actor == self.player:
            return (self.game_map.visible[entity.x, entity.y])
        else:
            if actor.ai:
                return (actor.ai.vision[entity.x, entity.y])
        print("ERROR::Actor has no ai - engine.check_entity_in_sight_of_actor")
        return False

    def change_entity_depth(self, entity: Entity, depth: int, xpos: int, ypos: int, debug: bool=False) -> None:
        """This function does not prevent entity from falling onto a wall.
        This means entity can get stuck after falling(going down a level), 
        so you should calculate the appropriate xpos, ypos in advance and pass it to this function.
        """
        if debug:
            with open("memory_debug.txt", "a") as f:
                f.write(f"current depth: {self.depth} current gamemap: {len(self.game_map.entities)} current player pos: {self.player.x, self.player.y} \n")
                f.write(f"new depth: {depth} new gamemap: {len(self.world.get_map(depth).entities)} new player pos: {xpos, ypos} \n")
                f.write("_______________________________________________________ \n")

        if not self.world.check_if_map_on_mem(depth):
            # neither player nor other entities cannot move outside of memory capacity.
            # TODO: Might have to fix this part to make feature like multiple depth teleportation
            print(f"FATAL ERROR::SOMETHING WENT WRONG, CANNOT FIND MAP FROM MEMORY. ENTITY SHOULD NOT BE ABLE TO REACH DEPTH {depth}, which is higher than (current engine depth + world.mem_capacity). (={self.depth+self.world.mem_capacity}). FUNCTION CANCELLED.")
            return None # do nothing

        if entity == self.player: # Map can be only generated when player moves.
            # Delete all de/ascending actors set to prevent dead actor descending.
            # e.g. ant and player is both at depth 1
            # player went down to depth 2, and ant tries to follow player 1 (gamemap depth 2 now has ant as descending actors)
            # player immediately ascends back, ant is still at depth 1(since it never actually descended. its only in the descend list). player kills ant.
            # player descneds back to depth 2. since there is ant saved in descending actors of gamemap depth 2, ant(which is dead) will descend.
            self.game_map.descending_actors.clear()
            self.game_map.ascending_actors.clear()

            # world[depth] should've been already generated from previous map generations.
            if not self.world.check_if_map_has_been_generated(depth):
                raise Exception(f"FATAL ERROR::SOMETHING WENT WRONG. PLAYER IS JUMPING TO DEPTH {self.depth} TO NONGENERATED DEPTH {depth}. CONSIDER INCREASING WORLD.MEM_CAPACITY. - world[depth] should've been already generated from previous map generations.")
            self.game_map = self.world.get_map(depth)
            self.depth = depth
            self.refresh_gamemap_entities()
            self.camera.clear_visuals()

            for tmp_depth in range(depth-self.world.mem_capacity, depth+self.world.mem_capacity+1): #USING (depth-self.world.mem_capacity, depth+self.world.mem_capacity+1) in order to make negative depth level generations.
                if not self.world.check_if_map_has_been_generated(tmp_depth)\
                    and self.world.check_if_should_exist_in_memory(depth):
                        # MOST OF THE TIME THERE IS GOING TO BE ONLY 1 NEW GAMEMAP THATS BEING GENERATED.
                        print(f"DEBUG::GENERATING DEPTH {tmp_depth}")
                        new_map = self.generate_new_dungeon(depth=tmp_depth, console=self.console, context=self.context,display_process=True)
                        new_map.adjustments_before_new_map() # Adjust things (AI's vision, etc. player's vision is initialized AFTER player has been placed.)
                        self.world.save_map_to_memory(new_map, tmp_depth)
                if not self.world.check_if_map_on_mem(tmp_depth):
                    self.world.save_map_to_memory(self.world.load_map_from_serialized_data(tmp_depth), tmp_depth)
        else:
            if not self.world.check_if_map_has_been_generated(depth): # When entity moves to an ungenerated map, it causes FATAL ERROR as seen below.
                print("FATAL ERROR::NON-PLAYER ENTITY TRIED TO MOVE TO A NONGENERATED DEPTH. FUNCTION CANCELLED.")
                return None # do nothing

        # place physically and remove entity from its old gamemap.
        # NOTE: It is CRUCIAL to remove entity BEFORE serializing the gamemap, otherwise it will have duplicate entity.
        if entity.gamemap:
            entity.gamemap.remove_entity(entity)
        entity.place(xpos, ypos, self.world.get_map(depth=depth))

        # Update fov since player is now placed on new gamemap.
        if entity == self.player:
            if self.sound_manager:
                self.sound_manager.play_bgm_for_biome(self.game_map.biome)
                self.sound_manager.play_bgs_for_biome(self.game_map.biome)
            self.update_fov()

        """
        IMPORTANT: ALL CHANGES MADE TO GAMEMAPS THAT ARE OUTSIDE OF CURRENT self.depth +- self.world.mam_capaicty ARE NOT SAVED.
        TO SAVE ALL AND EVERY SINGLE CHANGES MADE TO THE ENTIRE GAMEMAPS, USE SELF.WORLD.SAVE_WORLD() INSTEAD. (But its a heavy function)
        ALSO world.save_mem() and world.optimize() should be called at last.
        """
        self.world.save_mem()  # Save all updated memories as data
        self.world.optimize()  # Optimize memory (delete and load)


    def handle_world(self, turn_pass: bool) -> None:
        """
        Handles things that happens regardless of player's will.
        This function will run after every in-game events.
        However most of its parts will not function unless the game world's time has passed.

        Args:
            turn_pass:
                This indicates whether the time has passed after player's input.
                If this is False, world's time will not pass as well.
                NOTE To stop a game world time except for the player, you should set turn_pass to False.
        """
        if turn_pass:
            self.player.spend_action_point()
            self.time_pass()
            self.handle_enemy_turns()
            self.handle_semiactor_turns()
            self.handle_actor_states()
            self.handle_item_states()
            self.handle_semiactor_states()
            self.handle_gamemap_states()
            self.update_fov()
            self.game_map.actors_change_depth_gradually()
            self.game_map.update_enemy_fov()

    def time_pass(self) -> None:
        while self.player.action_point < 60:
            for entity in set(self.game_map.actors) - {self.player}:
                entity.gain_action_point()
            for entity in set(self.game_map.semiactors):
                entity.gain_action_point()
            self.player.gain_action_point()
        self.game_turn += 1
        
    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai and not entity.actor_state.is_dead:
                while entity.action_point >= 60:
                    try:
                        entity.ai.perform()
                    except exceptions.Impossible:
                        pass  # Ignore impossible action exceptions from AI.
                    entity.spend_action_point()

    def handle_item_states(self) -> None:
        """
        Handle things about items that should be updated every turn.
        e.g. Rotting foods, burning items
        """
        for item in set(self.game_map.items):
            if item.item_state.is_burning:
                item.item_state.burn()
            if item.edible:
                item.edible.time_pass()
        for entity in set(self.game_map.actors):# NOTE: If this cause too much performance issues, change the code so that the game only checks player's inventory.
            for item in entity.inventory.items:
                if item.item_state.is_burning:
                    item.item_state.burn(owner=entity)# NOTE: The fireproof checking of the inventory happens during the ignition of the fire. (at rule.py)
                if item.edible:
                    item.edible.time_pass()

    def handle_semiactor_states(self) -> None:
        """
        Handle things about items that should be updated every turn.
        e.g. Rotting foods, burning items
        """
        for semiactor in set(self.game_map.semiactors):
            if semiactor.semiactor_info.is_burning:
                semiactor.semiactor_info.burn()

    def handle_actor_states(self) -> None:
        """
        Handle things about actors that should be updated every turn.
        e.g. burning monsters

        When something should be handled immediately, this isn't the place to do it.
        e.g. electrical shock
        """
        for actor in set(self.game_map.actors):
            # Bug prevention
            if actor.is_dead:
                print("WARNING::THE ACTOR IS DEAD BUT HANDLE_ACTOR_STATES() IS STILL RUNNING.")
                continue

            ### Unique status effects ###
            # Burning
            if actor.actor_state.is_burning != [0,0,0,0]:
                actor.actor_state.actor_burn()
            # Paralyzed
            if actor.actor_state.is_paralyzing != [0,0]:
                actor.actor_state.actor_paralyzing()
            # Sleeping
            if actor.actor_state.is_sleeping != [0,0]:
                actor.actor_state.actor_sleeping()
            # Confusion
            if actor.actor_state.is_confused != [0,0]:
                actor.actor_state.actor_confused()
            # Completly frozen
            if actor.actor_state.is_frozen != [0,0,0]:
                actor.actor_state.actor_frozen()
            # Freezing
            if actor.actor_state.is_freezing != [0,0,0,0,0]:
                actor.actor_state.actor_freeze()
            # Bleeding
            if actor.actor_state.is_bleeding != [0,0,0]:
                actor.actor_state.actor_bleed()
            # Melting from acid
            if actor.actor_state.is_melting != [0,0,0,0]:
                actor.actor_state.actor_melting()
            # Levitating
            if actor.actor_state.is_levitating != [0,0]:
                actor.actor_state.actor_levitating()
            # Poisoned
            if actor.actor_state.is_poisoned != [0,0,0,0]:
                actor.actor_state.actor_poisoned()
            # Submerging handled in environmental_effects
            # Drowning
            if actor.actor_state.is_drowning != [0,0]:
                actor.actor_state.actor_drowning()
            # Detecting far objects
            if actor.actor_state.is_detecting_obj[2]: #List is not empty
                actor.actor_state.actor_detecting()
                # Actual detection happens during update_fov()

            ### Regular status effects ###
            # Health point recovering
            if actor.actor_state.heal_wounds:
                actor.actor_state.actor_heal_wounds()
            if actor.actor_state.regain_mana:
                actor.actor_state.actor_regain_mana()

            # Hunger
            if actor.actor_state.hunger >= 0:
                actor.actor_state.actor_gets_hungry()

    def handle_semiactor_turns(self) -> None:
        """
        Handle semiactors' actions.
        NOTE: Semiactor's lifetime is handled in rule.perform(). 
        This includes deleting semiactors after there lifetime, and decreasing the lifetime every turn.
        """
        current_entities = self.game_map.entities
        current_semiactors = []

        for entity in current_entities:
            if isinstance(entity, SemiActor) and entity.is_active:
                current_semiactors.append(entity)

        for entity in set(current_semiactors):
            if entity.rule:
                if entity.do_action:
                    while entity.action_point >= 60:
                        try:
                            entity.rule.perform()
                        except exceptions.Impossible:
                            print(f"DEBUG::HANDLE_SEMIACTOR_TURNS() - IMPOSSIBLE ACTION WAS TRIED FROM THE SEMIACTOR{entity.name}")
                            pass
                        entity.spend_action_point()

            # If the semiactor has walkable component, set its previous_entity to None 
            # so that it can be triggered again when it is stepped on by the same entity.
            if entity.walkable:
                # Check if the entity has previous_entity variables. (Some trap semiactors might not have this variable when it's unnecessary.)
                try:
                    if entity.walkable.previous_entity:
                        entity.walkable.previous_entity = None
                except AttributeError:
                    pass
                
    def handle_gamemap_states(self) -> None:
        """
        Handles changes that occurs on gamemap.
        This functions should run once every player's turn.
        e.g. monster regeneration
        """
        self.game_map.respawn_monsters()


    def generate_new_dungeon(self, console, context, depth=1, display_process=True) -> GameMap:
        """Generate new dungeon and return as gamemap object"""
        return generate_dungeon(
            console,
            context,
            depth,
            display_process
        )


    def update_entity_in_sight(self, is_initialization=False) -> None:
        """
        Update informations about entities that are currently in player's sight.

        Args:
            is_initialization:
                When this function is called the first time right before the main game loop begins, this parameter is set to True.
        """
        # Copy the old data to prev_ variables (shallow copy)
        self.prev_actors_in_sight = copy.copy(self.actors_in_sight)
        self.prev_items_in_sight = copy.copy(self.items_in_sight)

        self.actors_in_sight.clear()
        self.items_in_sight.clear()

        # Get new data
        for entity in self.game_map.entities:
            if self.camera.in_bounds(entity.x, entity.y) and self.game_map.visible[entity.x, entity.y]:
                if isinstance(entity, Actor):
                    self.actors_in_sight.add(entity)
                elif isinstance(entity, Item):
                    self.items_in_sight.add(entity)
        
        # If the function is called for the first time, copy data and set prev_ variables again since it was set to nothing before.
        if is_initialization:
            self.prev_actors_in_sight = copy.copy(self.actors_in_sight)
            self.prev_items_in_sight = copy.copy(self.items_in_sight)

    def apply_telepathy(self, actor: Actor, target: Actor, visible: np.ndarray) -> None:
        """
        Check if the actor can see(using telepathy) certain target.
        If it can, make the tile visible.
        """
        from util import get_distance
        # Make actor type entities visible
        if actor == self.player:
            from visual import Visual

            # telepathy distance is affected by actor's intelligence. Max 8
            if not visible[target.x, target.y] and get_distance(actor.x, actor.y, target.x, target.y) < max(actor.status.changed_status["intelligence"] * 0.6, 15):
                # different colors depending on the ai's hostility
                tele_color = color.white
                if target.ai:
                    if target.ai.owner == actor:
                        tele_color = color.green
                    elif target.ai.check_if_enemy(actor):
                        tele_color = color.red
                
                self.camera.visuals.append(Visual(target.x, target.y, char='?', fg=tele_color, bg=None, lifetime=1))
        else:
            # AI can see
            if hasattr(actor, "ai"):
                if get_distance(actor.x, actor.y, target.x, target.y) < max(actor.status.changed_status["intelligence"] * 0.6, 15):
                    visible[target.x, target.y] = True

    def detect_entities(self, actor: Actor, visible: np.ndarray, explored: Optional[np.ndarray]=None) -> None:
        # Make certain types of entities visible
        for entity in self.game_map.typed_entities(actor.actor_state.is_detecting_obj[2]):
            visible[entity.x, entity.y] = True

        # If the actor has explored vision, update it too
        if isinstance(explored, np.ndarray):
            explored |= visible

    def update_fov(self) -> None:
        """
        Recompute the visible area based on the players point of view.
        + apply telepathy
        """
        temp_vision = copy.copy(self.game_map.tiles["transparent"])

        for entity in self.game_map.entities:
            if entity.blocks_sight:
                temp_vision[entity.x, entity.y] = False

        self.game_map.visible[:] = compute_fov(
            temp_vision,
            (self.player.x, self.player.y),
            radius=self.player.status.changed_status["eyesight"],
        )

        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

        # Update additional vision effects
        self.update_additional_vision(actor=self.player)

    def update_additional_vision(self, actor: Actor) -> None:
        if actor == self.player:
            explored = self.game_map.explored
            visible = self.game_map.visible
        elif actor.ai:
            explored = None
            visible = actor.ai.vision
        else:
            print("ACTOR_STATE - ACTOR_DETECTING : THE ACTOR HAS NO AI / VISION")
            return
        
        # Entity detection
        if actor.actor_state.is_detecting_obj[2]:
            if isinstance(explored, np.ndarray):
                self.detect_entities(self.player, visible=visible, explored=explored)
            else:
                self.detect_entities(self.player, visible=visible)
        
        # Telepathy
        if actor.actor_state.has_telepathy:
            for target in set(self.game_map.actors):
                self.apply_telepathy(actor, target, visible=visible)

    

    def set_player_path(self, dest_x: int, dest_y: int, ignore_unexplored: bool=True, ignore_dangerous_tiles: bool=True, ignore_blocking_entities: bool=True, ignore_semiactors: bool=True) -> None:
        """
        This function sets the player's path when mouse movement is used.

        ### FLOW
        # Set the cost of certain tiles to 1(True) if the tile satisfies the following conditions.
        # explored == True, walkable == True, safe_to_walk == True
        ###
        """
        # Copy the walkable array. (All walkable tiles are set to 1)
        cost = np.array(self.game_map.tiles["walkable"], dtype=np.int8)

        # 1. Set unexplored tiles' cost to 0
        # TODO : using the numpy mask might increase the performance here.
        if ignore_unexplored:
            not_explored_coordinates = zip(*np.where(self.game_map.explored[:,:] == False))

            for cor in not_explored_coordinates:
                # Even if the position clicked if currently unexplored, the game will randomize path and allow player to move to that tile
                # UNLESS the path contains other unexplored tiles.
                # This is due to convenience, and other touch/click driven moving roguelikes like pixel dungeon uses similar mechanics.
                # TODO: This mechanics can be improved. 
                if cor[0] == dest_x and cor[1] == dest_y:
                    continue
                cost[cor] = 0
        
        # 2. Set safe_to_walk=False tiles' cost to 0
        if ignore_dangerous_tiles:
            dangerous_coordinates = zip(*np.where(self.game_map.tiles["safe_to_walk"][:,:] == False))

            for cor in dangerous_coordinates:
                # If the player is already on a dangerous tile, ignore same types of tile and exclude them from "dangerous coordinates".
                # The reaseon for this is convenience.
                # For example, when the player is in the middle of ocean, the player is most likely to be standing on the deep water tile.(which is considered "dangerous tile")
                # When player click somewhere else to get out of the ocean, the game will not randomize any path because the player is surrounded by dangerous tiles(deep water).
                # However by excluding all deep water tiles from "dangerous tile" temporarily, the player can now get out of the ocean by clicking somewhere else.
                if self.game_map.tiles[cor]["tile_id"] == self.game_map.tiles[self.player.x, self.player.y]["tile_id"]:
                    continue

                cost[cor] = 0

        # 3. Check for entities
        for parent in self.game_map.entities:
            if ignore_blocking_entities:
                # If there is any entity(that blocks) on the tile, try to exclude that tile from path generation if possible.
                # NOTE: However, we ignore the entity that is at the destination of the mouse click.
                if parent.blocks_movement and cost[parent.x, parent.y]:
                    if parent.x != dest_x or parent.y != dest_y:
                        cost[parent.x, parent.y] += 100
            
            if ignore_semiactors:
                # Exclude tiles that has a dangerous semiactor on it.
                if isinstance(parent, SemiActor):
                    if (parent.x != dest_x or parent.y != dest_y) and not parent.safe_to_move:
                        cost[parent.x, parent.y] = 0

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = SimpleGraph(cost=cost, cardinal=2, diagonal=3, greed=1)
        pathfinder = Pathfinder(graph)

        # Set start position
        pathfinder.add_root((self.player.x, self.player.y))  

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Save player paths
        for index in path:
            self.player_path.appendleft((index[0], index[1]))

    def do_player_queue_actions(self) -> bool:
        """
        The game will automatically do an action for the player based on the player_path, player_dir information.
        """
        ### A. If player path exist (=if the player clicked a tile that is at least 2 tiles away)
        if self.player_path:

            # Check if there is any new actor spotted in sight
            if not self.config["ignore_enemy_spotted_during_mouse_movement"] and self.prev_actors_in_sight != self.actors_in_sight:
                # If so, stop the movement.
                # TODO: Add a feature to stop ONLY if the actor is hostile to player?
                self.player_path.clear()
                return False

            dest_xy = self.player_path[-1]
            dx = dest_xy[0] - self.player.x
            dy = dest_xy[1] - self.player.y

            # Check for semiactors
            collided_semiactor = self.game_map.get_semiactor_at_location(dest_xy[0], dest_xy[1])
            if collided_semiactor:
                if collided_semiactor.entity_id == "opened_door":
                    BumpAction(self.player, dx, dy).perform()
                    self.player_path.pop() # Don't clear the path since you can just move onto opened doors
                    return True
                else:
                    BumpAction(self.player, dx, dy).perform()
                    self.player_path.clear()
                    return True
            if self.game_map.get_actor_at_location(dest_xy[0], dest_xy[1]):
                # If the monster is in the way, the game automatically attacks it.
                # After the attack the game will delete the player's path.
                BumpAction(self.player, dx, dy).perform()
                self.player_path.clear()
                return True
            else:
                try:
                    BumpAction(self.player, dx, dy).perform()
                    self.player_path.pop()
                    return True
                except Exception as e:
                    # If something unexpectedly blocks the way, perform BumpAction and delete all paths.
                    # NOTE: This part of the code is written to prevent unexpected circumstances crashing the game.
                    # So be aware that issues can be ignored here.
                    print(f"DEBUG::{e}")
                    self.player_path.clear()
                    return False

        ### B. If the player clicked one of nearby tiles (including the tile player is at)
        elif self.player_dir:

            # B-1. Clicked the tile that player is currently at
            if self.player_dir == (0,0):

                item_on_ground = self.game_map.get_item_at_location(self.player.x, self.player.y)
                if item_on_ground:
                    try:
                        PickupAction(entity=self.player).perform()
                        self.player_dir = None
                        return True
                    except exceptions.Impossible as exc:
                        self.message_log.add_message(exc.args[0], color.impossible)
                        self.player_dir = None
                        return False
                    except:
                        traceback.print_exc()
                        self.message_log.add_message(traceback.format_exc(), color.error)
                        self.player_dir = None
                        return False
                # Check for descending stairs
                if self.game_map.tiles[self.player.x, self.player.y]["tile_id"] == "descending_stair":
                    try:
                        DescendAction(entity=self.player).perform()
                        self.player_dir = None
                        return True
                    except exceptions.Impossible as exc:
                        self.message_log.add_message(exc.args[0], color.impossible)
                        self.player_dir = None
                        return False
                    except:
                        traceback.print_exc()
                        self.message_log.add_message(traceback.format_exc(), color.error)
                        self.player_dir = None
                        return False
                # Check for ascending stairs
                elif self.game_map.tiles[self.player.x, self.player.y]["tile_id"] == "ascending_stair":
                    try:
                        AscendAction(entity=self.player).perform()
                        self.player_dir = None
                        return True
                    except exceptions.Impossible as exc:
                        self.message_log.add_message(exc.args[0], color.impossible)
                        self.player_dir = None
                        return False
                    except:
                        traceback.print_exc()
                        self.message_log.add_message(traceback.format_exc(), color.error)
                        self.player_dir = None
                        return False
                
            # B-2. Clicked one of the nearby tile
            else:
                try:
                    BumpAction(self.player, self.player_dir[0], self.player_dir[1]).perform()
                    self.player_dir = None
                    return True
                except exceptions.Impossible as exc:
                    self.message_log.add_message(exc.args[0], color.impossible)
                    self.player_dir = None
                    return False
                except:
                    traceback.print_exc()
                    self.message_log.add_message(traceback.format_exc(), color.error)
                    self.player_dir = None
                    return False

        return True # Turn passes after every actions like normal

    def refresh_screen(self) -> None:
        """Refresh current console and apply it to current context."""
        self.render(self.console)
        self.context.present(self.console)

    def render_visible_entities(self, console: Console, gui_x: int, gui_y: int, height: int, draw_frame: bool=False) -> None:
        x = gui_x
        num = gui_y

        for actor in self.actors_in_sight:
            if num - gui_y >= height - 3: # Out of border
                console.print(x=x, y=num, string="...", fg=color.gray)
                break
            console.print(x=x, y=num, string=actor.char, fg=actor.fg)
            if actor.ai:
                if actor.ai.check_if_enemy(self.player):
                    console.print(x=x+2, y=num, string=actor.name, fg=color.light_red)
                else:
                    if actor.ai.owner == self.player:
                        console.print(x=x + 2, y=num, string=actor.name, fg=color.light_green)
                    else:
                        console.print(x=x + 2, y=num, string=actor.name, fg=color.light_gray)
            else:
                console.print(x=x + 2, y=num, string=actor.name, fg=color.light_gray)

            num += 1

        for item in self.items_in_sight:
            if num - gui_y >= height - 3: # Out of border
                console.print(x=x, y=num, string="...", fg=color.gray)
                break
            console.print(x=x, y=num, string=item.char, fg=item.fg)
            console.print(x=x+2, y=num, string=item.name, fg=color.light_gray)
            num += 1
        
        # draw frame
        if draw_frame:
            draw_thick_frame(console, x=gui_x-1, y=gui_y-1, width=28, height=height, title="시야 내 정보", fg=color.gui_frame_fg, bg=color.gui_frame_bg)
            #console.draw_frame(x=gui_x-1, y=gui_y-1, width=28, height=height, title="시야 내 정보", clear=False, fg=color.gui_frame_fg, bg=color.gui_frame_bg)

    def render_rightside(self, console: Console, gui_x: int, gui_y: int) -> None:
        """
        Handles the GUI about players status.
        This includes player status, and player's status effects.
        Args:
            gui_x, gui_y:
                top-left side of the graphical user interfaces.
                NOTE: This is NOT the coordinate of the GUi frame. This is the coordinate of the inner area.
        """

        render_character_status(
            console=console, 
            x=gui_x, 
            y=gui_y, 
            width=self.config["rside_width"], 
            height=self.config["status_height"], 
            character=self.player, 
            draw_frame=True
            )

        render_character_state(
            console=console,
            engine=self, 
            x=gui_x, 
            y=gui_y + self.config["status_height"] - 2, 
            height=self.config["state_height"], 
            character=self.player, 
            draw_frame=True
            )

        self.render_visible_entities(
            console, 
            gui_x, 
            gui_y + self.config["status_height"] + self.config["state_height"], 
            height=self.config["sight_info_height"], 
            draw_frame=True
            )

    def draw_window(
            self,
            console: Console,
            text: str,
            fixed_width: bool = False,
            x: Optional[int] = None,
            y: Optional[int] = None,
            width: Optional[int] = None,
            height: Optional[int] = None,
            title: Optional[str] = "",
            frame_fg: Optional[Tuple[int, int, int]] = (218, 196, 0),
            frame_bg: Optional[Tuple[int, int, int]] = (0, 0, 0),
            text_fg: Optional[Tuple[int, int, int]] = (255, 255, 255),
        ):
            render_message_window(
                console=console, 
                engine=self, 
                text=text, 
                fixed_width=fixed_width,
                x=x,
                y=y,
                width=width,
                height=height,
                title=title,
                frame_fg=frame_fg,
                frame_bg=frame_bg,
                text_fg=text_fg,
            )

    def render_gui(self, console: Console) -> None:
        """
        Handles rendering all the graphical user interfaces.
        """
        # Some values are hard-coded.
        self.message_log.render(console=console, x=1, y=self.config["camera_height"]+2, width=self.config["camera_width"], height=self.config["msg_log_height"], draw_frame=True)
        render_gameinfo(console=console, x=1, y=self.config["camera_height"] + self.config["msg_log_height"] + 3, depth=self.depth, game_turn=self.game_turn)
        self.render_rightside(console=console, gui_x=self.config["camera_width"] + 2, gui_y=1)
    
    def render(self, console: Console) -> None:
        """
        Handles rendering everything from the game.
        """
        self.camera.adjust()
        self.camera.render(console, draw_frame=True)
        self.render_gui(console=console)

        render_names_at_mouse_location(console=console, x=1, y=0, engine=self)

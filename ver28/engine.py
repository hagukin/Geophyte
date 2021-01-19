from __future__ import annotations
from typing import TYPE_CHECKING, List
from tcod.path import SimpleGraph, Pathfinder
from tcod.console import Console
from tcod.map import compute_fov
from item_manager import ItemManager

import numpy as np
import exceptions
import copy
import traceback
import color

from collections import deque
from actions import BumpAction, DescendAction, AscendAction, PickupAction
from procgen import generate_dungeon
from procgen import choose_biome
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import (
    render_character_name,
    render_gameinfo,
    render_health_bar,
    render_mana_bar,
    render_names_at_mouse_location,
    render_character_status,
    render_character_state,
)
from entity import Actor, Item, SemiActor

if TYPE_CHECKING:
    from game_map import GameMap
    from input_handlers import EventHandler


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
                Collection of entire gamemaps created.
        """
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog(engine=self)
        self.mouse_location = (0, 0)
        self.mouse_dir = (1, 1)
        self.player = player
        self.player_path = deque([])
        self.player_dir = None
        self.actors_in_sight = set()
        self.items_in_sight = set()
        self.prev_actors_in_sight = set()
        self.prev_items_in_sight = set()
        self.game_turn = 0
        self.config = None # Set from initialization
        self.console = None
        self.context = None
        self.camera = None
        self.world = {}
        self.game_map: GameMap = None
        self.depth: int = 0
        self.item_manager: ItemManager = None

    @property
    def mouse_relative_location(self):
        x, y = self.camera.get_relative_coordinate(abs_x=self.mouse_location[0], abs_y=self.mouse_location[1])
        return x, y

    def initialize_item_manager(self):
        if self.item_manager == None:
            self.item_manager = ItemManager()
            self.item_manager.initialize_data()

        return None

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
            self.handle_gamemap_states()
            self.update_fov()
            self.update_enemy_fov()
            self.update_entity_in_sight()

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
                print("ERROR :: THE ACTOR IS DEAD BUT HANDLE_ACTOR_STATES() IS STILL RUNNING.")

            ### Unique status effects ###
            # Burning
            if actor.actor_state.is_burning != [0,0,0,0]:
                actor.actor_state.actor_burn()
            # Paralyzed
            if actor.actor_state.is_paralyzing != [0,0]:
                actor.actor_state.actor_paralyzing()
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
            # Poisoned
            if actor.actor_state.is_poisoned != [0,0,0,0]:
                actor.actor_state.actor_poisoned()
            # Water related status effects NOTE: Drowning status effect is handled seperately
            if actor.actor_state.is_submerged:
                actor.actor_state.actor_submerged()
                if not actor.actor_state.is_underwater and actor.actor_state.was_submerged:
                    # actor moved from deep water to shallow water
                    actor.status.reset_bonuses(["bonus_dexterity", "bonus_agility"])
            elif actor.actor_state.was_submerged:
                # actor is completely out of water
                actor.status.reset_bonuses(["bonus_dexterity", "bonus_agility"])
            # Drowning
            if actor.actor_state.is_drowning != [0,0]:
                actor.actor_state.actor_drowning()

            ### Regular status effects ###
            # Health point recovering
            if actor.actor_state.heal_wounds:
                actor.actor_state.actor_heal_wounds()
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

    def generate_new_dungeon(self, depth=1) -> GameMap:
        """Generate new dungeon and return as gamemap object"""
        # Set temporary context, console values to prevent cffi error
        temp_console, temp_context = self.console, self.context
        self.console, self.context = None, None

        # Select biome
        biome = choose_biome()

        # Generate dungeon
        new_dungeon = generate_dungeon(
            biome=biome,
            engine=self,
            depth=depth,
        )

        # Get console, context info back.
        self.console, self.context = temp_console, temp_context
        return new_dungeon

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

        # Get new data
        for entity in self.game_map.entities:
            if self.game_map.visible[entity.x, entity.y]:
                if isinstance(entity, Actor):
                    self.actors_in_sight.add(entity)
                elif isinstance(entity, Item):
                    self.items_in_sight.add(entity)
        
        # If the function is called for the first time, copy data and set prev_ variables again since it was set to nothing before.
        if is_initialization:
            self.prev_actors_in_sight = copy.copy(self.actors_in_sight)
            self.prev_items_in_sight = copy.copy(self.items_in_sight)

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
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

    def update_enemy_fov(self, is_initialization: bool=False) -> None:
        """
        Recomputes the vision of actors besides player.
        This function is called every turn, but the actual update might not be called every turn due to perf. issues.
        """
        for actor in set(self.game_map.actors):
            # initialize actors vision
            if is_initialization:
                if actor.ai:
                    actor.ai.vision = np.full((self.game_map.width, self.game_map.height), fill_value=False, order="F")
                    actor.ai.update_vision()

            ## The game will not update every actor's vision every turn due to performance issues
            # actor.ai.update_vision()

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
                # Even if the position clicked if currently unexplored, the game will generate path and allow player to move to that tile 
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
                # When player click somewhere else to get out of the ocean, the game will not generate any path because the player is surrounded by dangerous tiles(deep water).
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

    def do_player_queue_actions(self) -> None:
        """
        The game will automatically do an action for the player based on the player_path, player_dir information.
        """
        ### A. If player path exist (=if the player clicked a tile that is at least 2 tiles away)
        if self.player_path:

            # Check if there is any new actor spotted in sight
            if self.prev_actors_in_sight != self.actors_in_sight:
                # If so, stop the movement.
                # TODO: Add an option to not stop?
                # TODO: Add a feature to stop ONLY if the actor is hostile to player?
                self.update_entity_in_sight()# update actors only when it's necessary
                self.player_path = deque([])
                return False

            dest_xy = self.player_path[-1]
            dx = dest_xy[0] - self.player.x
            dy = dest_xy[1] - self.player.y

            # Check for semiactors
            collided_semiactor = self.game_map.get_semiactor_at_location(dest_xy[0], dest_xy[1])
            if collided_semiactor:
                if collided_semiactor.entity_id == "closed_door":
                    # We do not pop from the path, because the player has to first open the door and then move to the tile.
                    BumpAction(self.player, dx, dy).perform()
                    return True
            if self.game_map.get_actor_at_location(dest_xy[0], dest_xy[1]):
                # If the monster is in the way, the game automatically attacks it.
                # After the attack the game will delete the player's path.
                BumpAction(self.player, dx, dy).perform()
                self.player_path = deque([])
                return True
            else:
                # If something unexpectedly blocks the way, perform BumpAction and delete all paths.
                #NOTE: This part of the code is meant to prevent unexpected circumstances crashing the game.
                # So be aware that issues can be ignored here.
                try:
                    BumpAction(self.player, dx, dy).perform()
                    self.player_path.pop()
                    return True
                except Exception as e:
                    print(f"DEBUG::{e}")
                    self.player_path = deque([])
                    return False

        ### B. If the player clicked one of nearby tiles (including the tile player is at)
        elif self.player_dir:

            # B-1. Clicked the tile that player is currently at
            if self.player_dir == (0,0):
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
                # If there is no stair, check for items.
                # TODO: What if the item is dropped on the stair tile?
                else:
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

    def render_playerinfo(self, console: Console, gui_x: int, gui_y: int, draw_frame: bool=False) -> None:
        """
        Handles the GUI about players status.
        """
        render_character_name(console=console, x=gui_x, y=gui_y, character=self.player)

        render_health_bar(
            console=console,
            x=gui_x,
            y=gui_y+2,
            current_value=self.player.status.hp,
            maximum_value=self.player.status.max_hp,
            total_width=26,
        )

        render_mana_bar(
            console=console,
            x=gui_x,
            y=gui_y+3,
            current_value=self.player.status.mp,
            maximum_value=self.player.status.max_mp,
            total_width=26,
        )

        render_character_status(console=console, x=gui_x, y=gui_y + 5, character=self.player)

        render_character_state(console=console, x=gui_x, y=gui_y + 14, character=self.player)

        if draw_frame:
            # If the border goes across the game screen it will not be displayed.
            # TODO: Most of the values are hard-coded.

            # border for status gui
            console.draw_frame(x=gui_x-1, y=gui_y-1, width=28, height=15, title="Player Status", clear=False, fg=(255,255,255), bg=(0,0,0))
            # border for state gui
            console.draw_frame(x=gui_x-1, y=gui_y+14, width=28, height=8, title="Status Effect", clear=False, fg=(255,255,255), bg=(0,0,0))
            
    def render_gui(self, console: Console) -> None:
        """
        Handles rendering all the graphical user interfaces.
        """
        # TODO: Most of the values are hard-coded.

        self.message_log.render(console=console, x=1, y=48, width=70, height=9, draw_frame=True)
        render_gameinfo(console=console, x=1, y=58, depth=self.depth, game_turn=self.game_turn)
        self.render_playerinfo(console=console, gui_x=73, gui_y=1, draw_frame=True)

    def render(self, console: Console) -> None:
        """
        Handles rendering everything from the game.
        """
        self.camera.adjust()
        self.camera.render(console, draw_frame=True)
        self.render_gui(console=console)

        render_names_at_mouse_location(console=console, x=3, y=46, engine=self)

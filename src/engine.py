from __future__ import annotations
from camera import Camera
from typing import TYPE_CHECKING, List, Optional, Tuple, Set
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
        self.mouse_location = (0, 0)
        self.mouse_dir = (1, 1)
        self.player = player
        self.player_path = deque([])
        self.player_dir = None
        self.actors_in_sight: Set[Actor] = set()
        self.items_in_sight: Set[Item] = set()
        self.prev_actors_in_sight: Set[Actor] = set()
        self.prev_items_in_sight: Set[Item] = set()
        self.game_turn = 0
        self.config = None # Set from initialization
        self.console = None
        self.context = None
        self.camera: Camera = None
        self.world = None
        self.game_map: GameMap = None
        self.depth: int = 0
        self.item_manager: ItemManager = None

    @property
    def mouse_relative_location(self):
        x, y = self.camera.abs_to_rel(abs_x=self.mouse_location[0], abs_y=self.mouse_location[1])
        return x, y

    def clamp_mouse_on_map(self, x: int, y: int) -> Tuple[int, int]:
        """Clamp the given x, y coordinates within the game map boundaries."""
        nx = max(self.camera.xpos, min(x, self.camera.biggest_x - 1))
        ny = max(self.camera.ypos, min(y, self.camera.biggest_y - 1))
        return nx, ny

    def initialize_item_manager(self):
        if self.item_manager == None:
            self.item_manager = ItemManager()
            self.item_manager.initialize_data()

        return None

    def change_gamemap_depth(self, depth: int) -> None:
        """Change the current floor as given depth. Generate new gamemap if there are no gamemap of the given depth.
        NOTE: Calling this method solely is not recommended. Try using DescendAction.perform()"""
        goal_depth = depth
        if not self.world.check_has_map(goal_depth):
            raise Exception("ERROR::engine.change_gamemap_depth() - gamemap not generated")

        if not self.world.check_has_map(goal_depth+1): # Check if gamemap below the goal depth already exists. (Pre-generating a level for falling down to next level and stuffs)
            self.world.set_map(self.generate_new_dungeon(depth=goal_depth+1, console=self.console, context=self.context), goal_depth+1)
        
        self.game_map = self.world.get_map(goal_depth)
        self.depth = goal_depth

        # Optimize memory
        self.world.optimize()

        # Adjust things (AI's vision is initialized here)
        self.game_map.adjustments_before_new_map(update_player_fov=False)##TEST TODO

    def change_entity_depth(self, entity: Entity, depth: int, xpos: int, ypos: int) -> None:
        """This function does not prevent entity from falling onto a wall.
        This means entity can get stuck after falling(going down a level), 
        so you should calculate the appropriate xpos, ypos in advance and pass it to this function.
        """
        if not self.world.check_has_map(depth): # If there is no level below current level, generate new level.
            print("WARNING::Something went wrong, Pre-generated level missing!")
            self.world.set_map(self.generate_new_dungeon(depth=depth, console=self.console, context=self.context, display_process=False), depth)

        if entity == self.player:
            self.change_gamemap_depth(depth)

        if entity.gamemap:
            entity.gamemap.entities.remove(entity)# Remove entity from previous gamemap if it has one

        new_gamemap = self.world.get_map(depth)
        new_gamemap.entities.append(entity)
        new_gamemap.sort_entities()
        entity.place(xpos, ypos, new_gamemap)
        entity.gamemap = new_gamemap

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
            self.game_map.update_enemy_fov()
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

    def add_special_effect_to_target(self, target: Actor, effects, effects_var, caused_by: Optional[Actor]=None) -> None:
        """
        This method takes two lists, applies the status effects to the given actor.

        It is usually done by calling apply_xxxing methods,
        but on some cases, if the special effects should be handled immediatly,
        a function can be directly called from this method. (e.g. electric shock)

        NOTE: This function is mainly used for melee attack special effects.

        Args:
            effects: A list that contains tuples. The tuples contains one string and one float.
                The string indicates which status effects should be applied when the attack is successfully delivered.
                The float indicates the possiblity of such effects to be applied, and it has range of 0 to 1.

                They are usually passed in from the AI component's __init__().
            
            effects_var: A list that contains the parameters for the status effects of this function call.
                The effect_var parameter MUST sync up with the effects parameter, and they should have the EXACT SAME ORDER.
                If the effect doesn't need any parameter, an empty list is passed.

                They are usually passed in from the AI component's __init__().
            caused_by:
                Actor who caused this special effect.

        Examples:
            the melee attack have 30% chance of giving burning effects and 50% chance of giving bleeding effects.
            effects = [("bleed_target", 0.3), ("burn_target", 0.5)]

            the burning effect and the bleeding effect's parameter are passed as well.
            effects_var = [[10,5,4,4], [20,4,4,4]]

            call engine.add_special_effect_to_target() from MeleeAction.perform()
        """
        # Check if this melee attack has any special effects
        if effects:

            # Check if the effects param and effects var param are synced.
            if len(effects) != len(effects_var):
                raise Exception("ERROR::engine.add_special_effects - Something went wrong. effects != effects_var")

            # Apply status effects
            for n in range(len(effects)):

                # Calcultate the odds
                if random.random() <= effects[n][1]:
                    pass
                else:
                    continue # This effect will not be applied, move to next effect.

                # Negative status effects
                if effects[n][0] == "burn_target":
                    target.actor_state.apply_burning(effects_var[n])
                elif effects[n][0] == "poison_target":
                    target.actor_state.apply_poisoning(effects_var[n])
                elif effects[n][0] == "freeze_target":
                    target.actor_state.apply_freezing(effects_var[n])
                elif effects[n][0] == "electrocute_target":
                    target.actor_state.apply_electrocution(effects_var[n])
                    target.actor_state.actor_electrocuted(source_actor=caused_by)
                elif effects[n][0] == "bleed_target":
                    target.actor_state.apply_bleeding(effects_var[n])
                elif effects[n][0] == "paralyze_target":
                    target.actor_state.apply_paralyzation(effects_var[n])
                elif effects[n][0] == "slow_target":
                    target.actor_state.apply_slowness(effects_var[n])
                elif effects[n][0] == "sleep_target":
                    target.actor_state.apply_sleeping(effects_var[n])
                elif effects[n][0] == "melt_target":
                    target.actor_state.apply_melting(effects_var[n])
                elif effects[n][0] == "sick_target":
                    target.actor_state.apply_sickness(effects_var[n])
                elif effects[n][0] == "anger_target":
                    target.actor_state.apply_anger(effects_var[n])
                elif effects[n][0] == "confuse_target":
                    target.actor_state.apply_confusion(effects_var[n])
                elif effects[n][0] == "hallucinate_target":
                    target.actor_state.apply_hallucination(effects_var[n])
                
                # Other status effects
                elif effects[n][0] == "fast_target":
                    target.actor_state.apply_haste(effects_var[n])
                elif effects[n][0] == "invisible_target":
                    target.actor_state.apply_invisibility(effects_var[n])
                elif effects[n][0] == "phase_target":
                    target.actor_state.apply_phasing(effects_var[n])
                elif effects[n][0] == "levitate_target":
                    target.actor_state.apply_levitation(effects_var[n])

    def generate_new_dungeon(self, console, context, depth=1, display_process=True) -> GameMap:
        """Generate new dungeon and return as gamemap object"""
        # Generate regular dungeon
        new_dungeon = generate_dungeon(
            console=console,
            context=context,
            depth=depth,
            display_process=display_process
        )
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

        self.actors_in_sight.clear()
        self.items_in_sight.clear()

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
                self.update_entity_in_sight()# update actors only when it's necessary
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
            console.print(x=x+2, y=num, string=actor.name, fg=color.light_gray)
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

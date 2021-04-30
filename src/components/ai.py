from __future__ import annotations

import random
import numpy as np
import copy
from numpy.core.shape_base import block
import tcod

from typing import List, Tuple, Optional
from actions import Action, BumpAction, MeleeAction, WaitAction, ThrowItem, EatItem, PickupAction
from components.base_component import BaseComponent
from entity import Actor, SemiActor, Entity, Item
    

class BaseAI(BaseComponent):
    """
    It is not recommeded to call any methods that are being called from .perform() outside of .perform() method.
    """
    def __init__(
            self,
            alignment: str, 
            do_melee_atk: bool,
            do_ranged_atk: bool,
            use_ability: bool,

            allied_type: set=set(),
            allied_id: set=set(),
            allied_with: set=set(),

            hostile_type: set=set(),
            hostile_id: set=set(),
            hostile_with: set=set(),

            attracted_eat_type: set=set(),
            attracted_eat_id: set=set(),
            attracted_eat_with: set=set(),
            
            attracted_own_type: set=set(),
            attracted_own_id: set=set(),
            attracted_own_with: set=set(),

            tameable: int = 1,
            owner: Actor = None,
        ):
        """
        Vars:
            tameable:
                Integer. 0 means the ai is always tameable, and the higher the number is, the harder it becomes to tame it.
                Negative values means that the ai cannot be tamed.
        """
        super().__init__()

        self.parent = None
        self.attacked_from = None
        self.target = None
        self.attraction = None # Either Item or SemiActor
        self.do_what_to_attraction = None # What action does this ai wants to perform to its attraction (e.g. Eating)
        self.path: List[Tuple[int, int]] = []
        self.active: bool = False # whether to wait or wander during its idle state
        self.in_player_sight: bool = False
        self.alignment = alignment

        # Vision
        self.vision = None # initialized in engine.update_enemy_fov() which is called from engine.handle_world()

        # bool, types of attack this ai can do
        self.do_melee_atk = do_melee_atk
        self.do_ranged_atk = do_ranged_atk
        self.use_ability = use_ability

        # Use engine.add_special_effects_to_actor() as a reference
        # These two values are initiated in ai_factories.py
        self.melee_effects = []
        self.melee_effects_var = []

        # Alliance
        self.allied_with = allied_with # actor that is alligned with
        self.allied_id = allied_id # monster type(monster_id) that are alligned with (e.g. fire_ant)
        self.allied_type = allied_type # species that are alligned with (e.g. char "a")

        # Enemy
        self.hostile_with = hostile_with # actor that is considered as an enemy
        self.hostile_id = hostile_id # monster type(monster_id) that is considered as an enemy
        self.hostile_type = hostile_type # species that is considered as an enemy

        # Attraction - Ai wants to eat these
        self.attracted_eat_type = attracted_eat_type # edible.edible_type (string)
        self.attracted_eat_id = attracted_eat_id
        self.attracted_eat_with = attracted_eat_with

        # Attraction - Ai wants to own(possess) these
        self.attracted_own_type = attracted_own_type # item.InventoryOrder (enum)
        self.attracted_own_id = attracted_own_id
        self.attracted_own_with = attracted_own_with

        # Owner
        self.tameable = tameable
        self.owner = owner
    
    def init_vision(self) -> None:
        """Initialize this ai's vision"""
        self.vision = np.full((self.engine.game_map.width, self.engine.game_map.height), fill_value=False, order="F")
        self.update_vision()

    def activate(self) -> None:
        """Activate this ai"""
        self.init_vision()
        self.active = True

    def check_active(self) -> None:
        # Set to active when this ai is in player's sight
        if self.gamemap.visible[self.parent.x, self.parent.y] and self.vision[self.engine.player.x, self.engine.player.y]:
            # prevent overwriting
            if self.in_player_sight:
                return None

            self.in_player_sight = True
            self.activate()
        else:
            if not self.in_player_sight:
                return None

            self.in_player_sight = False # NOTE: self.active remains True even after going out of player's sight
    
    def set_owner(self, owner: Actor) -> None:
        self.owner = owner
        if owner == self.engine.player:
            self.parent.actor_state.hunger = self.parent.actor_state.size * 25 * 12 # Set to "normal" hunger state.
            # From now on, this actor can starve to death.

    def try_tame(self, tamer: Actor, tame_power: int) -> bool:
        """
        Returns:
            boolean. returns True if tamer successfully tamed this ai. return False if failed.
        """
        if self.tameable > 0 and self.tameable >= tame_power:
            self.set_owner(tamer)
            return True
        else:
            return False

    def disable_targeting_ally(self) -> None:
        """
        Prevent ai to attack its owner or its ally.
        """
        if self.target and self.owner:
            if self.target == self.owner:
                self.target = None
            elif self.target.ai:
                if self.target.ai.owner == self.owner:
                    self.target = None

    def perform(self) -> None:
        """
        Check if this actor is in player's sight.
        Actor's self.active will to True after being seen once.
        """
        # active check
        self.check_active()

        # update vision if ai's in player's sight due to performance issue
        if self.active and self.gamemap.visible[self.parent.x, self.parent.y]:
            self.update_vision()

        # immobility check
        if self.parent.check_for_immobility():
            return WaitAction(self.parent).perform()
        
        # target check
        self.disable_targeting_ally()

        # return 
        if self.alignment == "hostile" or self.alignment == "neutral" or self.alignment == "allied" or self.owner:
            return self.perform_hostile()
        elif self.alignment == "peaceful":
            return self.perform_peaceful()
        
    def wander(self) -> Action:
        """
        Actor will wander around the dungeon randomly.

        NOTE: Currently the ai will not move(for one turn) if it fails to find a random walkable location.
        You can force ai to always move by adding a while loop, but this could cause some performance issues in certain situations.
        """
        random_x = random.randint(3, self.gamemap.width - 3)
        random_y = random.randint(3, self.gamemap.height - 3)

        if self.gamemap.tiles[random_x, random_y]["walkable"]:
            self.path = self.get_path_to(random_x, random_y)

    def idle_action(self) -> Action:
        """
        If the ai is not active, it will do nothing when its in idle state.
        If its active, it will wander around.
        Pets will follow its owner instead.
        """
        if self.owner:
            self.idle_action_pet()
        else:
            if self.active:
                if not self.path:
                    return self.wander()
            else:
                return WaitAction(self.parent).perform()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """
        Compute and return a path to the target position.
        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.parent.gamemap.tiles["walkable"], dtype=np.int8)

        for parent in self.parent.gamemap.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if parent.blocks_movement and cost[parent.x, parent.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[parent.x, parent.y] += 10

        ### Intelligent ai will try to avoid dangerous tiles/semiactors by removing them from path, or setting their cost high.
        # If the ai is currently flying it will ignore some of the dangers.
        if self.parent.status.changed_status["intelligence"] > 1:##TODO DEBUG

            # 1. If the AI is not flying, raise costs for safe_to_walk = False tiles.
            # NOTE: The reason for not entirely removing dangerous tiles from path is, to prevent ai "stuck" between dangerous tiles. (It can't generate path to get out if its surrounded)
            if not self.parent.actor_state.is_flying:
                dangerous_coordinates = zip(*np.where(self.gamemap.tiles["safe_to_walk"][:,:] == False))
                for cor in dangerous_coordinates:
                    # If the actor is already on dangerous tile, same types of tiles will be considered safe. 
                    # (Thus, the ai will be able to find its way out from the middle of giant pool of water.)
                    if self.gamemap.tiles[cor]["tile_id"] == self.gamemap.tiles[self.parent.x, self.parent.y]["tile_id"]:
                        continue

                    # If the tile is deep water, but the ai is able to swim, its considered safe.
                    if self.parent.actor_state.can_swim and self.gamemap.tiles[cor]["tile_id"] == "deep_water":
                        break
                    else:# TODO: Add logics besides just deep water. (e.g. actors with fire res 100% will ignore lava pools.)
                        cost[cor] += 50

            # 2. Tiles with dangerous semiactors to bump into, will also have high costs.
            for parent in self.gamemap.entities:
                if isinstance(parent, SemiActor):
                    if (parent.x != dest_x or parent.y != dest_y) and not parent.safe_to_move:
                        cost[parent.x, parent.y] += 50

        # Create a graph from the cost array and pass that graph to a new pathfinder
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root((self.parent.x, self.parent.y))  # Start position

        # Compute the path to the destination and remove the starting point
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]]
        return [(index[0], index[1]) for index in path]

    def move_path(self) -> None:
        if self.path:
            dest_x, dest_y = self.path[0]
            try:
                # Check if there is any actor blocking.
                # If there is one, check if that actor is this ai's potential target. If so, proceeds(BumpAction). If not, consider the path blocked.
                bump_actor = self.parent.gamemap.get_actor_at_location(dest_x, dest_y)
                if bump_actor:
                    if self.check_if_enemy(bump_actor):
                        BumpAction(self.parent, dest_x - self.parent.x, dest_y - self.parent.y,).perform()
                    else:
                        raise None
                else:
                    BumpAction(self.parent, dest_x - self.parent.x, dest_y - self.parent.y,).perform()

                # If it moved the coordinate is popped from the path.
                # If not, it remains.
                if self.parent.x == dest_x and self.parent.y == dest_y:
                    self.path.pop(0)
                return None
            except:
                if self.target: # if the AI was chasing the target
                    pass # keep chasing regardless of valid path existing it since new path will be generated next turn
                else: # if the AI was wandering
                    self.wander() # Select new destination to wander

    def get_melee_action(self, dx, dy):
        """
        Return the action this ai will perform when its melee attacking something.
        If the ai has any sort of special effects to its melee attack, its passed as a parameter.
        """
        return MeleeAction(self.parent, dx, dy, self.melee_effects, self.melee_effects_var).perform()

    def get_ranged_action(self, dx, dy, ammo):
        """
        Return the action this ai will perform when its range attacking(besides spellcasting) something.
        """
        return ThrowItem(entity=self.parent, item=ammo, target_xy=(dx, dy)).perform()

    def get_ability_action(self, x, y, target, ability):
        """
        Return the action this ai will perform when its using its ability.
        This includes magical attacks, using magic buffs, and many more.

        Deciding which ability that this ai is going to use is done in "check_if_use_ability_possible", not here.
        """
        return ability.activatable.get_action(caster=self.parent, x=x, y=y, target=target).perform()

    def check_is_ranged_atk_possible(self, attacker: Actor, target: Actor):
        """
        Check if this ai is currently able to range attack the given target, and return the result.
        The checking process differs from different types of actors, and it may include checking ammo left, mana left, maximum range of attacking, current status effects, etc.
        
        NOTE: AI with throwing attack feature should override this function in ai_factories.

        If the ai is able to range attack, this function will return the result as following form:
        (direction, ammo)
            direction:
                Tuple. Values indicates the direction, not the location. Directions are given as dx, dy from the attacker.
            ammo:
                Returns item_id, not the actual object.
        """
        raise NotImplementedError()

    def check_is_melee_atk_possible(self, attacker: Actor, target: Actor, cheby_dist: int):
        """
        Check if this ai is currently able to melee attack the given target, and return the result as boolean.

        NOTE: AI can overwrite this function if needed, but most of the time this function will keep its basic form.
        NOTE: Currently all melee attacks have range of 1 tile.
        """
        if cheby_dist <= 1:
            return True
        else:
            return False

    def check_is_use_ability_possible(self, attacker: Actor, target: Actor):
        """
        Check if this ai is currently able to use ability, and return the result.

        If the ai is able to range attack, this function will return the result as following form:
        (coordinate, target, ability_chosen)
            coordinate:
                Tuple. Indicates the position, not the direction. Set to None if the ability doesn't need any coordinates.
            target:
                Return None if there is no target.
            ability:
                Return the ability object(not the id!) that are being used.
        """
        raise NotImplementedError()

    def get_ranged_direction(self, attacker: Actor, target: Actor, valid_range: int=4):
        """
        If target is
        1. in possible attacking direction (8-ways linear direction)
        2. in valid range
        3. not blocked from any obstacle
        return the direction as tuple.
        If any of them is unsatisfied, return None. 

        e.g. @-actor T-target
        . . T
        . . .
        @ . .
        return (1,-1)
        """
        # get coordinate axis distances
        x_diff = target.x - attacker.x
        y_diff = target.y - attacker.y

        # Check if in range
        distance = int(attacker.distance(target.x, target.y))
        if distance > valid_range:
            return None

        # (0,0) is not considered as a valid direction
        if x_diff == 0 and y_diff == 0:
            return None

        # Check if the target is in possible attack direction (linear direction)
        direction = None

        if abs(x_diff) == abs(y_diff):#(1,1), (-1,-1), (1,-1), (-1,1)
            if x_diff > 0:
                if y_diff > 0:
                    direction = (1,1)
                else:
                    direction = (1,-1)
            else:
                if y_diff > 0:
                    direction = (-1,1)
                else:
                    direction = (-1,-1)
        elif x_diff == 0:# (0,1), (0,-1)
            if y_diff > 0:
                direction = (0,1)
            else:
                direction = (0,-1)
        elif y_diff == 0:# (1,0), (-1,0)
            if x_diff > 0:
                direction = (1,0)
            else:
                direction = (-1,0)
        else:
            return None

        # Check for obstacles
        for i in range(1, distance):
            blocking_actor = attacker.gamemap.get_actor_at_location(attacker.x + i * direction[0], attacker.y + i * direction[1])

            # Non-walkable tile is blocking
            if not attacker.gamemap.tiles["walkable"][attacker.x + i * direction[0], attacker.y + i * direction[1]]:
                return None
            # if actor is blocking, check if that actor is also considered as enemy.
            # (preventing friendly fire)
            # NOTE: The actor will not attack if there is any non-hostile actor between the actor and the target.
            elif blocking_actor:
                if self.check_if_enemy(blocking_actor):
                    continue
                else:
                    return None
            else:
                continue
        
        # return
        return direction

    def check_if_enemy(self, actor: Actor) -> bool:
        """
        Returns True if the given actor is considered as an enemy.
        This does not always mean the actor is currently set as a target.
        """
        # Actor will not target itself
        if actor == self.parent:
            return False
        elif actor == self.target:
            return True

        # If the actor has an owner
        if self.owner:
            # Actor will not target its owner but everyone else
            if actor == self.owner:
                return False
            
            # If actor serves same owner, return False
            if actor.ai:
                if actor.ai.owner == self.owner:
                    return False

            # If the owner has an ai, the pet will follow owner's targeting decision.
            if self.owner.ai:
                if self.owner.ai.check_if_enemy(actor):
                    return True
                else:
                    return True

            return True

        if self.alignment == "hostile":
            # Check hostile types, ids, and entities.
            if actor.char in self.hostile_type:
                return True
            elif actor.entity_id in self.hostile_id:
                return True
            elif actor in self.hostile_with:
                return True
            else:
                return False
        elif self.alignment == "neutral":
            return False
        elif self.alignment == "allied":
            # Check allied types, ids, and entities.
            if actor.char in self.allied_type:
                return False
            elif actor.entity_id in self.allied_id:
                return False
            elif actor in self.allied_with:
                return False
            else:
                return True
        elif self.alignment == "peaceful":
            return False

    def check_if_attracted(self, entity: Entity) -> bool:
        # Check hostile types, ids, and entities.
        if isinstance(entity, Item): #TODO: and if entity is hungry
            if entity.edible:
                if entity.edible.edible_type in self.attracted_eat_type:
                    self.do_what_to_attraction = "eat"
                    return True
                elif entity.entity_id in self.attracted_eat_id:
                    self.do_what_to_attraction = "eat"
                    return True
                elif entity in self.attracted_eat_with:
                    self.do_what_to_attraction = "eat"
                    return True
            elif not self.parent.inventory.check_if_full(): # Only wishes for more if it's inventory isnt full
                if entity.item_type in self.attracted_own_type:
                    self.do_what_to_attraction = "own"
                    return True
                elif entity.entity_id in self.attracted_own_id:
                    self.do_what_to_attraction = "own"
                    return True
                elif entity in self.attracted_own_with:
                    self.do_what_to_attraction = "own"
                    return True
                else:
                    return False
        return False

    def get_target(self) -> None:
        if self.owner:
            return self.get_target_pet()

        if self.alignment == "hostile":
            return self.get_target_hostile()
        elif self.alignment == "neutral":
            return self.get_target_neutral()
        elif self.alignment == "allied":
            return self.get_target_allied()
        elif self.alignment == "peaceful":
            return None

    def update_vision(self) -> None:
        """
        Updates this ai's vision.
        """
        temp_vision = copy.copy(self.parent.gamemap.tiles["transparent"])

        for entity in self.parent.gamemap.entities:
            if entity.blocks_sight:
                temp_vision[entity.x, entity.y] = False

        # Visible radius is proportionate to eyesight.
        self.vision[:] = tcod.map.compute_fov(
            temp_vision,
            (self.parent.x, self.parent.y),
            radius=self.parent.status.changed_status["eyesight"],
        )

    def set_attraction(self) -> None:
        """
        Set attraction only if the actor has no current target.
        """
        # The AI will start targeting only when its in player's sight due to performance issues.
        # NOTE: Ai's vision is already up to date if it is active and in player's sight
        if self.gamemap.visible[self.parent.x, self.parent.y]:
            for entity in self.gamemap.entities:
                if self.vision[entity.x, entity.y]:
                    if self.check_if_attracted(entity):
                        # Set to attraction if in sight
                        self.attraction = entity
                        break

    def get_target_hostile(self) -> Optional[Actor]:
        """
        Set target only if the actor fits this ai's condition of being hostile to.
        If there is this ai has no hostile types, species, or entities, it will act peacefully.
        Return: the target actor
        """
        # The AI will start targeting only when its in player's sight due to performance issues.
        # NOTE: Ai's vision is already up to date if it is active and in player's sight
        if self.gamemap.visible[self.parent.x, self.parent.y]:
            for actor in self.gamemap.actors:
                if self.check_if_enemy(actor):
                    # Set to target if in sight
                    if self.vision[actor.x, actor.y]:
                        return actor

    def get_target_neutral(self) -> None:
        """
        AI will not set any target unless its attacked.
        """
        return None

    def get_target_allied(self) -> Optional[Actor]:
        """
        Set target if the actor does not fit this ai's condition of being allied to.
        If there is this ai has no allied types, species, or entities, it will act hostile to everyone.
        """
        # The AI will start targeting only when its in player's sight due to performance issues.
        # NOTE: Ai's vision is already up to date if it is active and in player's sight
        if self.gamemap.visible[self.parent.x, self.parent.y]:
            for actor in self.gamemap.actors:
                if self.check_if_enemy(actor):
                    # Set to target if in sight
                    if self.vision[actor.x, actor.y]:
                        return actor
        
        # NOTE: Allied actor will fight back if attacked from its ally, but this is due to attacked_from auto-targeting, thus the alliacne is still valid.
        # TODO: maybe this should be changed so that the alliance breaks? or break alliance if attacked twice?

    def get_target_pet(self) -> None:
        """
        Act pretty much the same as get_target_allied, except that it will recalculate vision every turn if the pet is owned by the player.
        """
        # Only the player pets will set targets even when they are out of player's sight.
        get_target_this_turn = False

        if self.owner == self.engine.player:
            get_target_this_turn = True
        elif self.gamemap.visible[self.parent.x, self.parent.y] or self.gamemap.visible[self.owner.x, self.owner.y]: # if either owner or ai itself is visible, set target this turn
            get_target_this_turn = True

        if get_target_this_turn:
            for actor in self.gamemap.actors:
                if self.check_if_enemy(actor):
                    # Set to target if in sight
                    if self.vision[actor.x, actor.y]:
                        return actor

    def set_revenge_target(self) -> None:
        """
        If attacked, set the attacker as target.
        """
        # NOTE: attacked_from is initialized from status.take_damage()
        if self.attacked_from:
            if self.attacked_from != self.owner: #TODO: Make pet to fight back when they are attacked repetitively?
                self.target = self.attacked_from
                self.attacked_from = None

    def perform_hostile(self) -> None:
        # If attacked from other actors from that actor's turn, the ai will save that actor to self.attacked_from, and will set that actor as a target when this ai's turn arrives.
        # tl;dr Revenge when attacked.
        self.set_revenge_target()

        # If the target is alive find a path. Else choose new target.
        if self.target and not self.target.actor_state.is_dead:
            dx = self.target.x - self.parent.x
            dy = self.target.y - self.parent.y
            distance = max(abs(dx), abs(dy))  # Chebyshev distance.

            # forget attraction
            self.attraction = None

            # Check if target is still in sight
            # NOTE: vision already up to date since this function is(and shoud only be) called from perform()
            if self.vision[self.target.x, self.target.y]:
                target_in_sight = True
            else:
                # If target is out of sight currently, but the ai has special intrinsics available,
                # calculate ai's additional vision and check if the target is still out of sight.
                self.engine.update_additional_vision(self.parent)
                if self.vision[self.target.x, self.target.y]:
                    target_in_sight = True
                else:
                    target_in_sight = False

            if target_in_sight:
                # Check if the ai can use any abilities
                #TODO: Currently the ai will not use any abilities unless it has target set and the target is in sight.
                # But the ai should use abilities such as healing regardless of its target's location.
                if self.use_ability:
                    # temp = (location, target, ability object to use)
                    temp = self.check_is_use_ability_possible(attacker=self.parent, target=self.target)
                    if temp:
                        coordinate, target, selected_ability = temp
                        # If there is no coordinates given, set x,y to None
                        if coordinate:
                            x = coordinate[0]
                            y = coordinate[1]
                        else:
                            x = None
                            y = None

                        return self.get_ability_action(x=x, y=y, target=target, ability=selected_ability)

                # Check if the ai can melee attack
                if self.do_melee_atk:
                    if self.check_is_melee_atk_possible(attacker=self.parent, target=self.target, cheby_dist=distance):
                        return self.get_melee_action(dx=dx, dy=dy)

                # Check if the ai can range attack
                if self.do_ranged_atk:
                    temp = self.check_is_ranged_atk_possible(attacker=self.parent, target=self.target)
                    if temp:
                        attack_dir, ammo = temp
                        return self.get_ranged_action(dx=attack_dir[0], dy=attack_dir[1], ammo=ammo)
                    
                # if none of the above works, set new path and approach to target.
                self.path = self.get_path_to(self.target.x, self.target.y)
            else:
                self.target_out_of_sight()
        elif self.attraction:

            # Check if attraction is still in sight
            # NOTE: vision already up to date since this function is(and shoud only be) called from perform()
            if self.vision[self.attraction.x, self.attraction.y]:
                # If ai has an attraction, set new path
                if self.attraction.x == self.parent.x and self.attraction.y == self.parent.y:
                    if self.do_what_to_attraction == "eat":
                        # Eat it
                        EatItem(self.parent, self.attraction).perform()
                        self.attraction = None
                        self.do_what_to_attraction = None
                        self.path = None
                        return None
                    elif self.do_what_to_attraction == "own":
                        # Pick it up
                        PickupAction(self.parent).perform()
                        self.attraction = None
                        self.do_what_to_attraction = None
                        self.path = None
                        return None
                    else:
                        raise Exception() # AI is attracted to something but has no idea what to do with it
                else:
                    self.path = self.get_path_to(self.attraction.x, self.attraction.y)
            else:
                # attraction is out of sight, reset attraction
                self.attraction = None
        else:
            if self.target: # If target died, reset the path
                self.path = None
                self.target = None
            else:
                self.target = None

            # Reset the target, set attraction if there is no valid target nearby
            tmp_target = self.get_target()
            if tmp_target == None:
                self.set_attraction()
            else:
                self.target = tmp_target
        
        # If there is already a path, follow the path
        if self.path:
            self.move_path()
            return None
        else:
            # No target, no path -> idle_action()
            return self.idle_action()

    def perform_peaceful(self):
        if self.path:
            self.move_path()
        else:
            return self.idle_action()
    
    def idle_action_pet(self):
        """
        Pets will follow their owner when idling.
        """
        self.path = self.get_path_to(self.owner.x, self.owner.y) #TODO: Currently pet will follow whereever the owner is.
        self.path.pop() # Remove last coordinate from the path since the pet should move next to the owner, not on the owner.

    def target_out_of_sight(self) -> None:
        """
        Things to do when the ai has a target but target is out of sight.
        If target is still alive, but out of sight, ai will not automatically re-calculate the route since it doesn't know where the target is.
        NOTE: This function is called when the target is not only out of sight, but also undetected by any intrinsic abilities this ai has.
        """
        pass

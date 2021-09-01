from __future__ import annotations

import random
import numpy as np
import copy
from numpy.core.shape_base import block
import tcod
import actions

from typing import List, Tuple, Optional, Dict
from util import get_distance
from ability import Ability
from skill_ai import Skill_AI
from actions import Action, BumpAction, MeleeAction, WaitAction, ThrowItem, EatItem, PickupAction
from components.base_component import BaseComponent
from entity import Actor, SemiActor, Entity, Item
    

class BaseAI(BaseComponent):
    """
    It is not recommeded to call any methods that are being called from .perform() outside of .perform() method.
    """
    def __init__(
            self,
            alignment: Tuple,
            do_melee_atk: bool,
            do_ranged_atk: bool,
            use_ability: bool,

            allied_type:Tuple=None,
            allied_id:Tuple=None,
            allied_with:Tuple=None,

            hostile_type:Tuple=None,
            hostile_id:Tuple=None,
            hostile_with:Tuple=None,

            attracted_eat_type:Tuple=None,
            attracted_eat_id:Tuple=None,
            attracted_eat_with:Tuple=None,

            attracted_own_type:Tuple=None,
            attracted_own_id:Tuple=None,
            attracted_own_with:Tuple=None,
            owner: Actor = None,
        ):
        """
        Args:
            alignment:
                Tuple.
                (("hostile", "neutral", "allied", "peaceful"), (1,0,3,4))
        """
        super().__init__()
        self.attacked_from = None
        self.target = None
        self.attraction = None # Either Item or SemiActor
        self.do_what_to_attraction = None # What action does this ai wants to perform to its attraction (e.g. Eating)
        self.path: List[Tuple[int, int]] = []
        self.active: bool = False # whether to wait or wander during its idle state
        self.in_player_sight: bool = False

        self.alignment = None
        self.alignment_chance = alignment

        # Vision
        self.vision = None # initialized in engine.update_enemy_fov() which is called from engine.handle_world()

        # bool, types of attack this ai can do
        self.do_melee_atk = do_melee_atk
        self.do_ranged_atk = do_ranged_atk
        self.use_ability = use_ability

        # Alliance
        if allied_type is None:
            self.allied_type = set()
        else:
            self.allied_type = set(allied_type)  # species that are alligned with (e.g. char "a")
        if allied_id is None:
            self.allied_id = set()
        else:
            self.allied_id = set(allied_id)  # monster type(monster_id) that are alligned with (e.g. fire_ant)
        if allied_with is None:
            self.allied_with = set()
        else:
            self.allied_with = set(allied_with)  # actor that is alligned with

        # Enemy
        if hostile_type is None:
            self.hostile_type = set()
        else:
            self.hostile_type = set(hostile_type)  # species that is considered as an enemy
        if hostile_id is None:
            self.hostile_id = set()
        else:
            self.hostile_id = set(hostile_id)  # monster type(monster_id) that is considered as an enemy
        if hostile_with is None:
            self.hostile_with = set()
        else:
            self.hostile_with = set(hostile_with) # actor that is considered as an enemy

        # Attraction - Ai wants to eat these
        if attracted_eat_type is None:
            self.attracted_eat_type = set()
        else:
            self.attracted_eat_type = set(attracted_eat_type)  # edible.edible_type (string)
        if attracted_eat_id is None:
            self.attracted_eat_id = set()
        else:
            self.attracted_eat_id = set(attracted_eat_id)
        if attracted_eat_with is None:
            self.attracted_eat_with = set()
        else:
            self.attracted_eat_with = set(attracted_eat_with)

        # Attraction - Ai wants to own(possess) these
        if attracted_own_type is None:
            self.attracted_own_type = set()
        else:
            self.attracted_own_type = set(attracted_own_type)  # item.InventoryOrder (enum)
        if attracted_own_id is None:
            self.attracted_own_id = set()
        else:
            self.attracted_own_id = set(attracted_own_id)
        if attracted_own_with is None:
            self.attracted_own_with = set()
        else:
            self.attracted_own_with = set(attracted_own_with)

        self.owner = owner

    def initialize(self):
        self.init_alignment()
        self.init_vision()

    def init_alignment(self) -> None:
        self.alignment = random.choices(list(self.alignment_chance[0]), list(self.alignment_chance[1]), k=1)[0]
    
    def init_vision(self) -> None:
        """Initialize this ai's vision"""
        self.vision = np.full((self.parent.gamemap.width, self.parent.gamemap.height), fill_value=False, order="F")
        self.update_vision()

    def activate(self) -> None:
        """Activate this ai"""
        self.active = True

    def check_active(self) -> None:
        if self.active: # prevent overwriting
            return None

        # Set to active when this ai is in player's sight or player is in ai's sight
        if self.gamemap.visible[self.parent.x, self.parent.y] or self.vision[self.engine.player.x, self.engine.player.y]:
                self.activate()
                return None
        else:
            if get_distance(self.engine.player.x, self.engine.player.y, self.parent.x, self.parent.y) < self.engine.config["monster_activation_distance"]:
                self.activate()

            if not self.in_player_sight:
                return None
            self.in_player_sight = False # NOTE: self.active remains True even after going out of player's sight
    
    def set_owner(self, owner: Actor) -> None:
        self.owner = owner
        if owner == self.engine.player:
            self.parent.actor_state.hunger = self.parent.actor_state.size * 25 * 12 # Set to "normal" hunger state.
            # From now on, this actor can starve to death.

    def try_tame(self, tamer: Actor, tame_bonus: int) -> bool:
        """
        Returns:
            boolean. returns True if tamer successfully tamed this ai. return False if failed.
        """
        if self.parent.tameable > 0 and self.parent.tameable <= max(0, tamer.status.changed_status["charm"] - random.randint(0,10)) + tame_bonus:
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
        
    def wander(self) -> None:
        """
        Actor will wander around the dungeon randomly.

        NOTE: Currently the ai will not move(for one turn) if it fails to find a random walkable location.
        You can force ai to always move by adding a while loop, but this could cause some performance issues in certain situations.
        """
        random_x = random.randint(3, self.gamemap.width - 3)
        random_y = random.randint(3, self.gamemap.height - 3)

        if self.gamemap.tiles[random_x, random_y]["walkable"]:
            self.path = self.get_path_to(random_x, random_y)

    def perform_idle_action(self) -> None:
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
        intelligence = self.parent.status.changed_status["intelligence"]
        cost = np.array(self.parent.gamemap.tiles["walkable"], dtype=np.int8) # set to 1 (walkable)

        for e in self.parent.gamemap.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if e.blocks_movement and cost[e.x, e.y]:
                cost[e.x, e.y] += 10
            if intelligence > 3 and isinstance(e, SemiActor):
                if (e.x != dest_x or e.y != dest_y) and not e.safe_to_move:
                    cost[e.x, e.y] += intelligence * 5 # AIs with higher intelligence is more likely to dodge dangerous semiactors.

        if intelligence > 3:
            if not self.parent.is_on_air:
                dangerous_coordinates = zip(*np.where(self.gamemap.tiles["safe_to_walk"][:,:] == False))
                for cor in dangerous_coordinates:
                    if self.gamemap.tiles[cor]["tile_id"] == self.gamemap.tiles[self.parent.x, self.parent.y]["tile_id"]:
                        # If the actor is already on dangerous tile, same types of tiles will be considered safe.
                        # (Thus, the ai will be able to find its way out from the middle of giant pool of water.)
                        continue
                    if self.gamemap.check_tile_safe(self.parent, cor[0], cor[1], ignore_semiactor=True): # Semiactor is handled below.
                        break
                    cost[cor] += intelligence * 3  # AI with higher intelligence is more likely to dodge dangerous tiles.

        # Create a graph from the cost array and pass that graph to a new pathfinder
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root((self.parent.x, self.parent.y))  # Start position

        # Compute the path to the destination and remove the starting point
        path = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

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
                        if self.target:  # if the AI was chasing the target
                            pass  # keep chasing regardless of valid path existing it since new path will be generated next turn
                        else:  # if the AI was wandering
                            return self.wander()  # Select new destination to wander
                else:
                    BumpAction(self.parent, dest_x - self.parent.x, dest_y - self.parent.y,).perform()

                # If it moved the coordinate is popped from the path.
                # If not, it remains.
                if self.parent.x == dest_x and self.parent.y == dest_y:
                    self.path.pop(0)
                return None
            except:
                print("ERROR::SOMETHING WENT WRONG DURING AI.MOVE_PATH()")
                self.wander()
        else:
            print("ERROR::AI HAS NO PATH BUT CALLED MOVE_PATH()")
            self.wander()


    def perform_melee_action(self, dx, dy):
        """
        Return the action this ai will perform when its melee attacking something.
        If the ai has any sort of special effects to its melee attack, its passed as a parameter.
        """
        return MeleeAction(self.parent, dx, dy).perform()

    def perform_ranged_action(self, dx, dy, ammo):
        """
        Return the action this ai will perform when its range attacking(besides spellcasting) something.
        """
        return ThrowItem(entity=self.parent, item=ammo, target_xy=(dx, dy)).perform()

    def perform_ability_action(self, x, y, target, ability):
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

    def check_is_use_ability_possible(self, target: Actor) -> Optional[Optional[Tuple[int,int]], Actor, Ability]:
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

        TODO: Currnetly this function only supports skills/spells with target entity. (or at least the ai has a target in mind. e.g. lightning strike)
        """
        for s in self.parent.ability_inventory.abilities:
            ##########
            # SKILLS #
            ##########
            if s.ability_id == "sk_steal": # Check if has skill/spell
                ability_info = Skill_AI.skill_steal(actor=self.parent, target=target)
                if ability_info[0]: # Check if can use skill/spell right now
                    return ability_info[1], target, s

            ##########
            # SPELLS #
            ##########
            elif s.ability_id == "sp_lightning_bolt":
                ability_info = Skill_AI.spell_lightning_bolt(actor=self.parent, target=target)
                if ability_info[0]:
                    return ability_info[1], target, s
            elif s.ability_id == "sp_spectral_beam":
                ability_info = Skill_AI.spell_spectral_beam(actor=self.parent, target=target)
                if ability_info[0]:
                    return ability_info[1], target, s
            elif s.ability_id == "sp_soul_bolt":
                ability_info = Skill_AI.spell_soul_bolt(actor=self.parent, target=target)
                if ability_info[0]:
                    return ability_info[1], target, s
            elif s.ability_id == "sp_call_of_the_orc_lord":
                ability_info = Skill_AI.spell_call_of_the_orc_lord(actor=self.parent, target=target)
                if ability_info[0]:
                    return ability_info[1], target, s
        return None

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
                if entity.edible.edible_type in self.attracted_eat_type: # String
                    self.do_what_to_attraction = "eat"
                    return True
                elif entity.entity_id in self.attracted_eat_id:
                    self.do_what_to_attraction = "eat"
                    return True
                elif entity in self.attracted_eat_with:
                    self.do_what_to_attraction = "eat"
                    return True
            elif not self.parent.inventory.check_if_full(): # Only wishes for more if it's inventory isnt full
                if entity.item_type.value in [x.value for x in self.attracted_own_type]:
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

        # Check if target's gamemap is identical with ai's gamemap.
        # e.g. if player was being chased, goes down a level, and climbs back up
        # TODO: make some ai be able to follow target that has different gamemap (stair)
        if self.target:
            if self.target.gamemap != self.parent.gamemap:
                print(f"WARNING::Removing {self.parent.entity_id} ai's target. Target has different gamemap. ai depth: {self.parent.gamemap.depth}, target depth: {self.target.gamemap.depth}")
                self.target = None

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
                    temp = self.check_is_use_ability_possible(target=self.target)
                    if temp:
                        coordinate, target, selected_ability = temp
                        # If there is no coordinates given, set x,y to None
                        x, y = None, None
                        if coordinate != None:
                            x, y = coordinate[0], coordinate[1]


                        return self.perform_ability_action(x=x, y=y, target=target, ability=selected_ability)

                # Check if the ai can melee attack
                if self.do_melee_atk:
                    if self.check_is_melee_atk_possible(attacker=self.parent, target=self.target, cheby_dist=distance):
                        return self.perform_melee_action(dx=dx, dy=dy)

                # Check if the ai can range attack
                if self.do_ranged_atk:
                    temp = self.check_is_ranged_atk_possible(attacker=self.parent, target=self.target)
                    if temp:
                        attack_dir, ammo = temp
                        return self.perform_ranged_action(dx=attack_dir[0], dy=attack_dir[1], ammo=ammo)
                    
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
                        PickupAction(self.parent).pickup_single_item(item=self.attraction)
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
            # No target, no path -> perform_idle_action()
            return self.perform_idle_action()

    def perform_peaceful(self):
        if self.path:
            self.move_path()
        else:
            return self.perform_idle_action()
    
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

    def get_action_when_bumped_with(self, bumped_entity: Entity):
        """Returns an Action to perform when bumped with given entity.
        Is called from BumpAction.perform() """
        if bumped_entity.entity_id[-5:] == "chest":
            return actions.MovementAction(
                self.parent,
                dx=bumped_entity.x - self.parent.x,
                dy=bumped_entity.y - self.parent.y)
        elif bumped_entity.entity_id[-11:] == "locked_door":
            return actions.DoorUnlockAction(
                self.parent,
                dx=bumped_entity.x - self.parent.x,
                dy=bumped_entity.y - self.parent.y)
        else:
            return actions.WaitAction(self.parent)

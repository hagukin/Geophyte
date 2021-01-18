from __future__ import annotations

from typing import Optional, Tuple, List, TYPE_CHECKING

import copy
import math
import color
import exceptions
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item, SemiActor
    from ability import Ability

class Action:
    """
    A generic object to represent almost every type of actions.
    Both player and monster performs actions.
    """
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """
        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        """Pickup an item and add it to the actor's inventory, if there is a room for it."""

        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                # Remove the item from current gamemap
                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.add_item(item)

                if item.stack_count > 1:
                    self.engine.message_log.add_message(f"You picked up the {item.name} (x{item.stack_count})!")
                else:
                    self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return #prevents picking up everything at once. # TODO : Add feature to pickup everything at once

        raise exceptions.Impossible("There is nothing here to pick up.")


class DescendAction(Action):
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self, depth: int=None) -> None:
        """
        If the Player is the actor, and the game map is not yet generated, this method will generate a new gamemap object.
        """
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        if self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "descending_stair":
            ### Player Level Descending
            if self.entity == self.engine.player:
                if depth == None:
                    goal_depth = self.engine.depth + 1
                else: goal_depth = depth

                # Remove entity from previous gamemap
                self.engine.game_map.entities.remove(self.entity)
                
                if goal_depth in list(self.engine.world.keys()): # GameMap Already Exists.
                    self.engine.game_map = self.engine.world[goal_depth]
                    self.engine.depth = goal_depth
                else: # GameMap Does not Exists, Generate new dungeon.
                    self.engine.world[goal_depth] = self.engine.generate_new_dungeon(depth=goal_depth)
                    self.engine.game_map = self.engine.world[goal_depth]
                    self.engine.depth = goal_depth
            ### Monster Level Descending
            else: 
                pass # TODO

            # Add the entity to current gamemap
            self.engine.game_map.entities.append(self.entity)
            self.engine.game_map.sort_entities()
            self.entity.place(self.engine.game_map.ascend_loc[0], self.engine.game_map.ascend_loc[1], self.engine.world[self.engine.depth])

            # Set entity gamemap
            self.entity.gamemap = self.engine.game_map

        elif self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "ascending_stair":
            raise exceptions.Impossible("This stair only goes up.")
        else:
            raise exceptions.Impossible("There is no stair.")


class AscendAction(Action):
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self, depth: int=None) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        if self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "ascending_stair":
            ### Player Level Ascending
            if self.entity == self.engine.player:
                if depth == None:
                    goal_depth = self.engine.depth - 1
                else: goal_depth = depth

                # Remove entity from previous gamemap
                self.engine.game_map.entities.remove(self.entity)

                if goal_depth in list(self.engine.world.keys()):
                    self.engine.game_map = self.engine.world[goal_depth]
                    self.engine.depth = goal_depth
                else:
                    print("ERROR : LEVEL DOES NOT EXIST")
                    raise Exception # You cannot ascend to a level that does not exist.
            ### Monster Level Ascending
            else:
                pass
            
            # Add entity to current gamemap
            self.engine.game_map.entities.append(self.entity)
            self.engine.game_map.sort_entities()
            self.entity.place(self.engine.game_map.descend_loc[0], self.engine.game_map.descend_loc[1], self.engine.world[self.engine.depth])

            # Set entity gamemap
            self.entity.gamemap = self.engine.game_map
        elif self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "descending_stair":
            raise exceptions.Impossible("This stair only goes down.")
        else:
            raise exceptions.Impossible("There is no stair.")


class ItemAction(Action):
    """
    Handles actions that are directly related to items.
    """
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None, item_selected: Optional[Item] = None
        ):
        """
        Args:
            item_selected:
                While item parameter indicates what item called this action, item_selected parameter indicates
                what items was chosen by the action call.
                e.g. when you read scroll of enchantment to upgrade your longsword
                -> item = scroll of enchantment
                -> item_selected = longsword
        """
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy
        self.item_selected = item_selected

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        raise NotImplementedError


class ThrowItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.item.throwable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.entity.inventory.drop(self.item)


class SplitItem(Action):
    def __init__(self, entity: Actor, item: Item, split_amount: int):
        super().__init__(entity)
        self.item = item
        self.split_amount = split_amount

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.entity.inventory.split_item(item=self.item, split_amount=self.split_amount)


class ReadItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.item.readable.activate(self)


class QuaffItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.item.quaffable.activate(self)


class EatItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.item.edible.activate(self)


class EquipItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.entity.equipments.equip_equipment(self.item)


class UnequipItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.entity.equipments.remove_equipment(self.item.equipable.equip_region)


class AbilityAction(Action):
    def __init__(
        self, entity: Actor, ability: Ability, x = None, y = None, target = None,
    ):
        super().__init__(entity)
        self.ability = ability
        self.x = x
        self.y = y
        self.target = target

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        self.ability.activatable.activate(self)


class WaitAction(Action):
    """
    Skips the turn doing nothing.
    This action DO costs action points.
    """
    def perform(self) -> None:
        pass


class ActionWithDirection(Action):
    """
    Handles all types of action that has direction.
    """
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy

        # Choose a random direction when the actor is confused. NOTE: ignore direction 0,0
        if self.entity.actor_state.is_confused != [0,0]:
            self.dx, self.dy = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )
            
            # Message log
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You stagger!", color.white)

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    @property
    def target_semiactor(self) -> Optional[SemiActor]:
        """Return the semiactor at this actions destination."""
        return self.engine.game_map.get_semiactor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def __init__(self, entity: Actor, dx: int, dy: int, effects: List=None, effects_var: List=None):
        """
        Args:
            effects: A list that contains tuples. The tuples contains one string and one float.
                The string indicates which status effects should be applied when the attack is successfully delivered.
                The float indicates the possiblity of such effects to be applied, and it has range of 0 to 1.

                They are usually passed in from the AI component's __init__().
            
            effects_var: A list that contains the parameters for the status effects of this melee attack.
                The effect_var parameter MUST sync up with the effects parameter, and they should have the EXACT SAME ORDER.
                If the effect doesn't need any parameter, an empty list is passed.

                They are usually passed in from the AI component's __init__().

        Examples:
            the melee attack have 30% chance of giving burning effects and 50% chance of giving bleeding effects.
            effects = [("bleed_target", 0.3), ("burn_target", 0.5)]

            the burning effect and the bleeding effect's parameter are passed as well.
            effects_var = [[10,5,4,4], [20,4,4,4]]
        """
        super().__init__(entity, dx, dy)
        self.effects = effects
        self.effects_var = effects_var

    def melee_special_effect_to_target(self) -> None:
        """
        This method applies the status effects for this melee attack.

        It is usually done by modifying the actor_state components value, 
        but on some cases, if the special effects should be handled immediatly,
        a function can be directly called from this method. (e.g. electric shock)

        TODO : 공격자 자기 자신에게 가하는 특수효과를 처리하는 함수 제작?
        TODO : 특수효과는 맨손일때만 적용되게 만들기?
        """
        target = self.target_actor

        # Check if this melee attack has any special effects
        if self.effects:

            # Check if the effects param and effects var param are synced.
            if len(self.effects) != len(self.effects_var):
                raise Exception("Melee Special Effects - Something went wrong. effects != effects_var")

            # Apply status effects
            for n in range(len(self.effects)):

                # Calcultate the odds
                if random.random() <= self.effects[n][1]:
                    pass
                else:
                    continue # This effect will not be applied, move to next effect.

                # Negative status effects
                if self.effects[n][0] == "burn_target":
                    target.actor_state.is_burning = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "poison_target":
                    target.actor_state.is_poisoned = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "freeze_target":
                    target.actor_state.is_freezing = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "electrocute_target":
                    target.actor_state.is_electrocuting = copy.copy(self.effects_var[n])
                    target.actor_state.actor_electrocuted()
                elif self.effects[n][0] == "bleed_target":
                    target.actor_state.is_bleeding = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "paralyze_target":
                    target.actor_state.is_paralyzing = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "slow_target":
                    target.actor_state.is_acting_slower = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "sleep_target":
                    target.actor_state.is_sleeping = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "melt_target":
                    target.actor_state.is_melting = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "sick_target":
                    target.actor_state.is_sick = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "anger_target":
                    target.actor_state.is_angry = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "confuse_target":
                    target.actor_state.is_confused = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "hallucinate_target":
                    target.actor_state.is_hallucinating = copy.copy(self.effects_var[n])
                
                # Other status effects
                elif self.effects[n][0] == "fast_target":
                    target.actor_state.is_acting_faster = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "invisible_target":
                    target.actor_state.is_invisible = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "phase_target":
                    target.actor_state.is_phasing = copy.copy(self.effects_var[n])
                elif self.effects[n][0] == "fly_target":
                    target.actor_state.is_flying = copy.copy(self.effects_var[n])
                      
    def is_miss(self) -> bool:
        """Returns whether the attack was successful or not."""
        dexterity = self.entity.status.changed_status["dexterity"] # Attacker's dexterity
        agility = self.target_actor.status.changed_status["agility"] # Target's agility

        # Apply size bonus
        # Your chance of successfully attacking will increas when fighting a bigger opponents. Vice versa.
        size_bonus = 1 + (self.target_actor.actor_state.size - self.entity.actor_state.size) * 0.15
        miss_constant = 10 # NOTE miss_constant : When you are balancing the game, ONLY change this constant and not the function itself.

        if random.random() * (1.3**dexterity + 1) * size_bonus * miss_constant / agility < 1:
            return True
        else:
            return False

    def crit_calculation(self, base_multiplier=1.5, always_critical=False) -> float:
        crit_chance = random.randint(0, 3000)

        # If always_critical parameter is set to True
        if always_critical:
            critical_hit = True
            crit_multiplier = base_multiplier + random.random()
            return crit_multiplier

        # Regular circumstances
        if crit_chance < min(self.entity.status.changed_status["dexterity"] * 5 + self.entity.status.changed_status["strength"], 1000):
            critical_hit = True
            crit_multiplier = base_multiplier + random.random()
        else:
            crit_multiplier = 1

        return crit_multiplier

    def damage_calculation(self, crit_multiplier) -> int:
        target = self.target_actor
        damage = self.entity.status.changed_status["base_melee"] + random.randint(0, self.entity.status.changed_status["additional_melee"])
        strength = self.entity.status.changed_status["strength"]

        # Apply size bonus
        # 15% damage fall-off to bigger opponents. Vice versa
        size_bonus = 1 + (self.entity.actor_state.size - self.target_actor.actor_state.size) * 0.15
        damage *= size_bonus

        # Apply strength bonus
        strength_bonus =  1 + math.log10(strength + 1) # y = log2(x/5 + 1)
        damage *= strength_bonus

        # Physical damage fall-off
        damage = target.status.calculate_dmg_reduction(damage=damage, damage_type="physical", ignore_reduction=False, penetration_constant=strength)

        # Apply critical multiplier
        damage *= crit_multiplier

        # round the damage to integer
        damage = max(0, round(damage))

        return damage  

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        # Set target
        target = self.target_actor

        # If there is no target
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        # Attack missing calculation
        if self.is_miss():
            if self.entity is self.engine.player:
                self.engine.message_log.add_message(
                    f"You attack {target.name} but misses.", color.player_atk_missed
                )
            else:
                self.engine.message_log.add_message(
                    f"{self.entity.name.capitalize()} attacks {target.name} but misses.", color.enemy_atk_missed, target=self.entity,
                )
            return None

        # Calculate critical chance, multiplier
        critical_hit = False
        crit_multiplier = self.crit_calculation()
        if crit_multiplier > 1:
            critical_hit = True

        damage = self.damage_calculation(crit_multiplier=crit_multiplier)

        # Messege log
        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            if critical_hit:
                attack_color = color.player_crit
                # TODO : 사운드
            else:
                attack_color = color.player_atk
        else:
            if critical_hit:
                attack_color = color.enemy_crit
            else:
                attack_color = color.enemy_atk

        # If there is damage
        if damage > 0:
            if self.engine.game_map.visible[self.entity.x, self.entity.y] and self.engine.game_map.visible[target.x, target.y]:# 시야에 보이는 엔티티의 전투만 프린트함. (공격자, 피공격자 중 하나라도 시야 내에 있으면 로그를 표시함.)
                self.engine.message_log.add_message(
                    f"{attack_desc} for {damage} hit points.", attack_color
                )

                # Gain strength experience point
                # NOTE feature currently on progress
                # if self.entity.status.experience:
                #     self.entity.status.experience.gain_strength_exp(amount=100) ##DEBUG ##BETA

            # Apply damage
            target.status.take_damage(amount=damage, attacked_from=self.entity)
        else:
            if self.engine.game_map.visible[self.entity.x, self.entity.y] or self.engine.game_map.visible[target.x, target.y]:
                self.engine.message_log.add_message(
                    f"{attack_desc} but does no damage.", color.gray
                )
        
        # If the target is alive after calculating the pure melee damage hit, apply melee status effects.
        # Status effects are still applied if the damage is zero
        if not target.actor_state.is_dead:
            self.melee_special_effect_to_target()


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None
        
        # Set destination
        dest_x, dest_y = self.dest_xy

        ### Check map boundaries ###
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("The way is blocked.")

        # If the actor is stuck in pit
        if self.entity.actor_state.is_in_deep_pit:

            # There are no "crawl out failure" when the actor is moving between different depth of pits.
            if self.engine.game_map.tiles[dest_x, dest_y]["tile_id"] == "deep_pit" or self.engine.game_map.tiles[dest_x, dest_y]["tile_id"] == "shallow_pit":
                crawl_out_chance = 1
            else:
                # If the actor is big enough, it can crawl out freely
                if self.entity.actor_state.size >= 6:
                    crawl_out_chance = 1
                else:
                    crawl_out_chance = 0.005 * self.entity.status.changed_status["dexterity"] * (self.entity.actor_state.size ** 2) # crawl-out chance calculation

            if random.random() > crawl_out_chance:
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(f"You try to crawl out of the pit, but fail!", color.red, target=self.entity)
                else:
                    self.engine.message_log.add_message(f"{self.entity.name} try to crawl out of the pit, but fail.", color.gray, target=self.entity)
                return None # Turn passes

        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("The way is blocked.")
            
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("The way is blocked.")

        self.entity.move(self.dx, self.dy)


class DoorOpenAction(ActionWithDirection):
    def perform(self) -> None:
        import semiactor_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        # Get door coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        if not semiactor_on_dir:
            raise exceptions.Impossible("There is nothing to open.")
        elif semiactor_on_dir.entity_id == "closed_door":
            can_open_door = False
            can_try_break_door = False
            dexterity = self.entity.status.changed_status["dexterity"]
            strength = self.entity.status.changed_status["strength"]
            intelligence = self.entity.status.changed_status["intelligence"]

            # If the actor has arm, it can try to open the door regardless of its dexterity
            if self.entity.actor_state.has_left_arm or self.entity.actor_state.has_left_arm:
                can_open_door = True
            # If the actor has no arm, but has enough dexterity and intelligence, it still can try to open the door 
            # TODO : Adjust numbers
            elif dexterity >= 10 and intelligence >= 10:
                can_open_door = True
            # If the actor fits none of the conditions above, but has enough strength, it can still try to break the door open
            # TODO : Adjust numbers
            elif strength >= 17:
                can_open_door = False
                can_try_break_door = True

            # Player can always try to break open the door regardless of strength
            if self.entity == self.engine.player:
                can_try_break_door = True

            # Check if the actor can open the door
            if can_open_door:
                open_fail = random.randint(0, 18)
            
                if open_fail > dexterity: # check if the actor failed to open the door
                    self.engine.message_log.add_message(f"{self.entity.name} has failed to open the door!", color.invalid, target=self.entity)
                    return None

                self.engine.game_map.get_semiactor_at_location(dest_x, dest_y).remove_self()
                semiactor_factories.opened_door.spawn(self.engine.game_map, dest_x, dest_y, -1)
            # If the actor can't open the door but can try to break the door, actor tries it
            elif can_try_break_door:
                break_fail = random.randint(10, 20)

                if break_fail > strength:
                    self.engine.message_log.add_message(f"{self.entity.name} slams the door.", color.invalid, target=self.entity)
                    return None
                elif break_fail * 2 <= strength: # if the strength value is higher than the break_fail * 2, break open the door (Minimum str req. for breaking the door: 20)
                    self.engine.message_log.add_message(f"{self.entity.name} slams the door and destorys it!", color.invalid, target=self.entity)
                    self.engine.game_map.get_semiactor_at_location(dest_x, dest_y).remove_self()
                    # TODO: drop the wooden door pieces?
                else: # Bust open the door but not break it
                    self.engine.message_log.add_message(f"{self.entity.name} slams the door open!", color.invalid, target=self.entity)

                    self.engine.game_map.get_semiactor_at_location(dest_x, dest_y).remove_self()
                    semiactor_factories.opened_door.spawn(self.engine.game_map, dest_x, dest_y, -1)
            else:
                # If the actor has ai, but has no capabilities to open/break the door open, discard the current path and find a new path.
                if self.entity.ai:
                    self.entity.ai.path = None

            return None
        elif semiactor_on_dir.entity_id == "opened_door":
            raise exceptions.Impossible("It is already opened.")
        else:
            raise exceptions.Impossible("There is nothing to open.")


class DoorCloseAction(ActionWithDirection):
    def perform(self) -> None:
        import semiactor_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        # Set coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        if not semiactor_on_dir:
            raise exceptions.Impossible("There is nothing to close.")
        elif semiactor_on_dir.entity_id == "opened_door":
            can_close_door = False
            dexterity = self.entity.status.changed_status["dexterity"]
            intelligence = self.entity.status.changed_status["intelligence"]

            # If the actor has arm, it can try to close the door regardless of its dexterity
            if self.entity.actor_state.has_left_arm or self.entity.actor_state.has_left_arm:
                can_close_door = True
            # If the actor has no arm, but has enough dexterity and intelligence, it still can try to close the door 
            elif dexterity >= 10 and intelligence >= 10:
                can_close_door = True

            # If any entity (except for the door semiactor that the actor is trying to close) is on the same direction with the door, you can't close
            if self.engine.game_map.get_any_entity_at_location(dest_x, dest_y, exception=semiactor_on_dir):
                raise exceptions.Impossible("Something is blocking.")

            # Try to close the door
            close_fail = random.randint(0, 10) # if dex > 10, actor will not fail closing the door by chance
            if not can_close_door or close_fail > dexterity: # check if the actor has no capabilities, or if the actor failed closing it by chance
                self.engine.message_log.add_message(f"{self.entity.name} has failed to close the door!", color.invalid, target=self.entity)
                return None

            semiactor_on_dir.remove_self()
            semiactor_factories.closed_door.spawn(self.engine.game_map, dest_x, dest_y, -1)

            return None
        elif self.engine.game_map.get_semiactor_at_location(dest_x, dest_y).entity_id == "closed_door":
            raise exceptions.Impossible("It is already closed.")
        else:
            raise exceptions.Impossible("There is nothing to close.")


class ChestOpenAction(ActionWithDirection):
    def perform(self) -> None:
        import chest_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        # Set coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        if not semiactor_on_dir:
            raise exceptions.Impossible("There is nothing to loot.")
        elif isinstance(semiactor_on_dir, chest_factories.ChestSemiactor):# Check if the semiactor is chest type
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You opened the {semiactor_on_dir.name}.", color.invalid)
            else:
                self.engine.message_log.add_message(f"{self.entity.name} opened the {semiactor_on_dir.name}.", color.invalid, target=self.entity)

            # If the player is the actor, call input handler
            if self.entity == self.engine.player:
                from input_handlers import ChestEventHandler##DEBUG
                self.engine.event_handler = ChestEventHandler(self.engine, semiactor_on_dir.storage)
                return None
            # If the AI is the actor, TODO
            else:
                print("DEBUG::AI OPENED THE CHEST")
        else:
            raise exceptions.Impossible("There is nothing to loot.")


class PlaceSwapAction(Action):
    def __init__(self, entity: Actor, target: Entity):
        """
        NOTE: At least one of the entity should be an actor.
        """
        super().__init__(entity=entity)
        self.target = target

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        temp_x, temp_y = self.entity.x, self.entity.y
        self.entity.place(self.target.x, self.target.y)
        self.target.place(temp_x, temp_y)

        if self.entity == self.engine.player:
            self.engine.message_log.add_message(f"You swapped places with {self.target.name}.", color.white)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"You can't do anything!", color.red)
            return None

        # Check for actors. If there is one, return MeleeAction.
        # TODO Add force-attack system
        if self.target_actor:
            if self.entity == self.engine.player and self.target_actor.ai:
                if self.target_actor.ai.owner == self.engine.player or not self.target_actor.ai.check_if_enemy(self.engine.player):
                    return PlaceSwapAction(self.entity, self.target_actor).perform()
                else:
                    return MeleeAction(self.entity, self.dx, self.dy).perform()
            else:
                return MeleeAction(self.entity, self.dx, self.dy).perform()
        elif self.target_semiactor:
            if self.target_semiactor.bump_action:
                return self.target_semiactor.bump_action(self.entity, self.dx, self.dy).perform()
            else:
                return MovementAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

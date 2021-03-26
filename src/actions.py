from __future__ import annotations

from typing import Optional, Tuple, List, TYPE_CHECKING

import math
import color
import exceptions
import random
from korean import grammar as g

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
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if inventory.check_if_full():
                    raise exceptions.Impossible("인벤토리가 가득 찼습니다.")

                # Remove the item from current gamemap
                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.add_item(item)

                if item.stack_count > 1:
                    self.engine.message_log.add_message(f"{g(self.entity.name, '이')} {g(item.name, '을')} 주웠다. (x{item.stack_count}).", target=self.entity, fg=color.gray)
                else:
                    self.engine.message_log.add_message(f"{g(self.entity.name, '이')} {g(item.name, '을')} 주웠다.", target=self.entity, fg=color.gray)
                return #prevents picking up everything at once. # TODO : Add feature to pickup everything at once

        raise exceptions.Impossible("주울 만한 물건이 아무 것도 없습니다.")


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
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
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

                    # Adjust things (AI's vision is initialized here)
                    self.engine.adjustments_before_new_map()
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
            raise exceptions.Impossible("이 계단은 위로만 향한다.")
        else:
            raise exceptions.Impossible("올라갈 수 없다.")


class AscendAction(Action):
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self, depth: int=None) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
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
                # Temporary game ending
                elif self.engine.player.inventory.check_if_in_inv("amulet_of_kugah"):
                    from input_handlers import GameClearInputHandler
                    self.engine.event_handler = GameClearInputHandler(engine=self.engine)
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
            raise exceptions.Impossible("이 계단은 아래로만 향한다.")
        else:
            raise exceptions.Impossible("내려갈 수 없다.")


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
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        self.item.throwable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
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
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        self.entity.inventory.split_item(item=self.item, split_amount=self.split_amount)


class ReadItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        self.item.readable.activate(self)


class QuaffItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        self.item.quaffable.activate(self)


class EatItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        self.item.edible.activate(self)


class EquipItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        self.entity.equipments.equip_equipment(self.item)


class UnequipItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
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
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
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
                self.engine.message_log.add_message(f"당신은 휘청거렸다!", color.white)

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
        """
        Return the semiactor at this actions destination.
        """
        return self.engine.game_map.get_semiactor_at_location(*self.dest_xy)

    @property
    def target_semiactor_bump(self) -> Optional[SemiActor]:
        """
        Return the semiactor at this actions destination if it has any bumpaction attached.
        """
        return self.engine.game_map.get_semiactor_with_bumpaction_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def __init__(self, entity: Actor, dx: int, dy: int, effects: List=None, effects_var: List=None):
        """
        Args:
            Check engine.add_effects_to_actors for more info.
        """
        super().__init__(entity, dx, dy)
        self.effects = effects
        self.effects_var = effects_var
                      
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
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        # Set target
        target = self.target_actor

        # If there is no target
        if not target:
            raise exceptions.Impossible("공격 대상이 없다.")

        # Attack missing calculation
        if self.is_miss():
            self.engine.message_log.add_message(
                f"{g(self.entity.name, '이')} {g(target.name, '을')} 공격했지만 빗나갔다.", color.enemy_atk_missed, target=self.entity,
            )
            return None

        # Calculate critical chance, multiplier
        critical_hit = False
        crit_multiplier = self.crit_calculation()
        if crit_multiplier > 1:
            critical_hit = True

        damage = self.damage_calculation(crit_multiplier=crit_multiplier)

        # Messege log
        attack_desc = f"{g(self.entity.name, '이')} {g(target.name, '을')} 공격"
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
                    f"{attack_desc}해 {damage} 데미지를 입혔다.", attack_color
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
                    f"{attack_desc}했지만 아무런 데미지도 주지 못했다.", color.gray
                )
        
        # If the target is alive after calculating the pure melee damage hit, apply melee status effects.
        # Status effects are still applied if the damage is zero
        if not target.actor_state.is_dead:
            self.engine.add_special_effect_to_target(target=target, effects=self.effects, effects_var=self.effects_var)


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None
        
        # Set destination
        dest_x, dest_y = self.dest_xy

        ### Check map boundaries ###
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("길이 막혀 있다.")

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
                self.engine.message_log.add_message(f"{g(self.entity.name, '은')} 구덩이에서 빠져나오려 했으나 실패했다.", color.gray, target=self.entity)
                return None # Turn passes

        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("길이 막혀 있다.")
            
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("길이 막혀 있다.")

        self.entity.move(self.dx, self.dy)


class DoorUnlockAction(ActionWithDirection):
    """
    NOTE: Unlocking something REQUIRES an item to use to unlock the door.
    It is recommended to make ai unable to unlock something.
    The chance of successfully unlocking something depends on both the actor and the item used.
    """
    def unlock(self, item: Item) -> None:
        import semiactor_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        # Get door coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        if not semiactor_on_dir:
            raise exceptions.Impossible("이 곳에는 잠금을 해제할 물건이 없다.")
        elif semiactor_on_dir.entity_id == "closed_door" or semiactor_on_dir.entity_id == "opened_door":
            raise exceptions.Impossible("이 문은 잠기지 않았다.")
        elif semiactor_on_dir.entity_id == "locked_door":
            dexterity = self.entity.status.changed_status["dexterity"]

            tool_bonus = item.lockpickable[0]
            tool_chance_of_breaking = item.lockpickable[1]

            # -1 - Always successful
            if tool_bonus == -1:
                chance_of_unlocking = 1
            else:
                chance_of_unlocking = tool_bonus * min(1, dexterity / 18)

            if random.random() <= chance_of_unlocking:
                # Unlock succeded
                self.engine.message_log.add_message(f"{g(self.entity.name, '이')} {g(item.name, '을')} 사용해 문의 잠금을 해제했다!", color.white, target=self.entity)

                tmp = semiactor_factories.closed_door.spawn(self.engine.game_map, dest_x, dest_y, -1)
                semiactor_on_dir.semiactor_info.move_self_to(tmp)
                semiactor_on_dir.remove_self()
            else:
                # Unlock failed
                self.engine.message_log.add_message(f"{g(self.entity.name, '은')} 문의 잠금을 해제하는 데 실패했다.", color.invalid, target=self.entity)

            # Item can break regardless of the result
            if random.random() <= tool_chance_of_breaking:
                item.remove_self()
                self.engine.message_log.add_message(f"잠금을 해제하는 과정에서 {g(item.name, '이')} 파괴되었다.", color.player_damaged, target=self.entity)

            from input_handlers import MainGameEventHandler
            self.engine.event_handler = MainGameEventHandler(engine=self.engine)

    def perform(self) -> None:
        # If the player is the actor, call input handler
        if self.entity == self.engine.player:
            from input_handlers import InventoryChooseItemAndCallbackHandler
            from order import InventoryOrder
            self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
                self.engine, 
                self.engine.player.inventory, 
                self.unlock,
                title="잠금 해제에 사용할 아이템을 선택하세요.",
                show_only_types=(
                    InventoryOrder.MELEE_WEAPON,
                    InventoryOrder.TOOL,
                )
            )
            return None
        # If the AI is the actor, TODO
        else:
            print("DEBUG::AI TRIED TO UNLOCK THE DOOR")


class DoorBreakAction(ActionWithDirection):
    def break_door(self, door: SemiActor, strength: int) -> None:
        break_fail = random.randint(10, 20)

        if break_fail > strength:
            self.engine.message_log.add_message(f"{g(self.entity.name, '이')} 문을 공격했다.", color.invalid, target=self.entity)
        elif break_fail * 2 <= strength: # if the strength value is higher than the break_fail * 2, break open the door (Minimum str req. for breaking the door: 20)
            self.engine.message_log.add_message(f"{g(self.entity.name, '이')} 문을 파괴했다!", color.invalid, target=self.entity)
            door.remove_self()
            # TODO: drop the wooden door pieces?
        else: # Bust open the door but not break it
            self.engine.message_log.add_message(f"{g(self.entity.name, '이')} 문을 강제로 열었다!", color.invalid, target=self.entity)

            import semiactor_factories
            tmp = semiactor_factories.opened_door.spawn(self.engine.game_map, door.x, door.y, -1)
            door.semiactor_info.move_self_to(tmp)
            door.remove_self()
        
        from input_handlers import MainGameEventHandler
        self.engine.event_handler = MainGameEventHandler(self.engine)
    
    def check_actor_condition(self, strength: int) -> bool:
        can_try_break_door = True

        # If the actorhas enough strength, it can try to break the door open
        # TODO : Adjust numbers
        if strength >= 17:
            can_try_break_door = True
        # Player can always try to break open the door regardless of strength
        if self.entity == self.engine.player:
            can_try_break_door = True
        
        return can_try_break_door

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        # Get door coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        # Get actor status
        strength = self.entity.status.changed_status["strength"]

        if not semiactor_on_dir:
            raise exceptions.Impossible("이 곳에는 문이 없다.")
        elif semiactor_on_dir.entity_id == "closed_door":
            can_try_break_door = self.check_actor_condition(strength)
            
            # If the actor can try to break the door, actor tries it
            if can_try_break_door:
                self.break_door(semiactor_on_dir, strength)
            else:
                # If the actor has ai, but has no capabilities to open/break the door open, discard the current path and find a new path.
                if self.entity.ai:
                    self.entity.ai.path = None

            return None
        elif semiactor_on_dir.entity_id == "opened_door":
            raise exceptions.Impossible("이 문은 이미 열려 있다.")
        elif semiactor_on_dir.entity_id == "locked_door":
            can_try_break_door = self.check_actor_condition(strength)

            if can_try_break_door:
                self.break_door(semiactor_on_dir, strength)
            elif self.entity.ai:
                self.entity.ai.path = None
        else:
            raise exceptions.Impossible("이 곳에는 문이 없다.")


class DoorOpenAction(ActionWithDirection):
    
    def open_door(self, door: SemiActor, dexterity: int, intelligence: int) -> None:
        open_fail = random.randint(0, 18)
            
        if open_fail > dexterity: # check if the actor failed to open the door
            self.engine.message_log.add_message(f"{g(self.entity.name, '은')} 문을 여는 것에 실패했다!", color.invalid, target=self.entity)
            from input_handlers import MainGameEventHandler
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None

        import semiactor_factories
        tmp = semiactor_factories.opened_door.spawn(self.engine.game_map, door.x, door.y, -1)
        door.semiactor_info.move_self_to(tmp)
        door.remove_self()

        from input_handlers import MainGameEventHandler
        self.engine.event_handler = MainGameEventHandler(self.engine)

    def check_actor_condition(self, dexterity: int, intelligence: int) -> bool:
        can_open_door = True

        # If the actor has arm, it can try to open the door regardless of its dexterity
        if self.entity.actor_state.has_left_arm or self.entity.actor_state.has_left_arm:
            can_open_door = True
        # If the actor has no arm, but has enough dexterity and intelligence, it still can try to open the door 
        # TODO : Adjust numbers
        elif dexterity >= 10 and intelligence >= 10:
            can_open_door = True
        
        return can_open_door

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        # Get door coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        # Get actor status
        dexterity = self.entity.status.changed_status["dexterity"]
        strength = self.entity.status.changed_status["strength"]
        intelligence = self.entity.status.changed_status["intelligence"]

        if not semiactor_on_dir:
            raise exceptions.Impossible("이 곳에는 문이 없다.")
        elif semiactor_on_dir.entity_id == "closed_door":
            can_open_door = self.check_actor_condition(dexterity, intelligence)
            can_try_break_door = DoorBreakAction(self.entity, self.dx, self.dy).check_actor_condition(strength)
            
            # Check if the actor can open the door
            if can_open_door:
                self.open_door(semiactor_on_dir, dexterity, intelligence)
            # If the actor can't open the door but can try to break the door, actor tries it
            # NOTE: Yoou can make Player automatically trying to break the door for game-control convenience by un-commenting the lines below.
            # elif can_try_break_door:
            #     DoorBreakAction(self.entity, self.dx, self.dy).break_door(semiactor_on_dir, strength)
            elif self.entity != self.engine.player and self.entity.ai:
                # If the actor has ai, but has no capabilities to open the door open, check if it can break the door open.
                if can_try_break_door: # If it can, try breaking the door
                    DoorBreakAction(self.entity, self.dx, self.dy).break_door(semiactor_on_dir, strength)
                else: # if it can't, discard the current path and find a new path.
                    self.entity.ai.path = None

            return None
        elif semiactor_on_dir.entity_id == "opened_door":
            raise exceptions.Impossible("이 문은 이미 열려 있다.")
        elif semiactor_on_dir.entity_id == "locked_door":
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"문이 굳게 잠겨 열리지 않는다.", color.invalid)

            # NOTE: You can comment out this area to disable the game asking player what to do when the door is locked.
            # If the player is the actor, call input handler to decide what to do
            if self.entity == self.engine.player:
                from input_handlers import LockedDoorEventHandler##DEBUG
                self.engine.event_handler = LockedDoorEventHandler(self.engine, semiactor_on_dir)
                return None
            # If the AI is the actor, It will break the door if it can. if not, it will re-route.
            else:
                can_open_door, can_try_break_door = self.check_actor_condition(strength, dexterity, intelligence)

                if can_try_break_door:
                    self.break_door(semiactor_on_dir, strength)
                elif self.entity.ai:
                    self.entity.ai.path = None
        else:
            raise exceptions.Impossible("이 곳에는 문이 없다.")


class DoorCloseAction(ActionWithDirection):
    def perform(self) -> None:
        import semiactor_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        # Set coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        if not semiactor_on_dir:
            raise exceptions.Impossible("이 곳에는 문이 없다.")
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
                raise exceptions.Impossible("무언가가 막고 있다.")

            # Try to close the door
            close_fail = random.randint(0, 10) # if dex > 10, actor will not fail closing the door by chance
            if not can_close_door or close_fail > dexterity: # check if the actor has no capabilities, or if the actor failed closing it by chance
                self.engine.message_log.add_message(f"{g(self.entity.name, '은')} 문을 닫는 것에 실패했다!", color.invalid, target=self.entity)
                return None

            tmp = semiactor_factories.closed_door.spawn(self.engine.game_map, dest_x, dest_y, -1)
            semiactor_on_dir.semiactor_info.move_self_to(tmp)
            semiactor_on_dir.remove_self()

            return None
        elif semiactor_on_dir.entity_id == "closed_door" or semiactor_on_dir.entity_id == "locked_door":
            raise exceptions.Impossible("이 문은 이미 닫혀 있다.")
        else:
            raise exceptions.Impossible("이 곳에는 문이 없다.")


class ChestOpenAction(ActionWithDirection):
    def perform(self) -> None:
        import chest_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        # Set coordinates
        dest_x, dest_y = self.dest_xy
        semiactor_on_dir = self.engine.game_map.get_semiactor_with_bumpaction_at_location(dest_x, dest_y)

        if not semiactor_on_dir:
            raise exceptions.Impossible("아무 것도 들어있지 않다.")
        elif isinstance(semiactor_on_dir, chest_factories.ChestSemiactor):# Check if the semiactor is chest type
            self.engine.message_log.add_message(f"{g(self.entity.name, '이')} {g(semiactor_on_dir.name, '을')} 열었다.", color.invalid, target=self.entity)

            # If the player is the actor, call input handler
            if self.entity == self.engine.player:
                from input_handlers import ChestEventHandler##DEBUG
                self.engine.event_handler = ChestEventHandler(self.engine, semiactor_on_dir.storage)
                return None
            # If the AI is the actor, TODO
            else:
                print("DEBUG::AI OPENED THE CHEST")
        else:
            raise exceptions.Impossible("아무 것도 들어있지 않다.")


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
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
            return None

        temp_x, temp_y = self.entity.x, self.entity.y
        self.entity.place(self.target.x, self.target.y)
        self.target.place(temp_x, temp_y)

        if self.entity == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.target.name, '와')} 자리를 바꾸었다.", color.white)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(f"아무 것도 할 수 없다!", color.red)
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
        elif self.target_semiactor_bump:
            return self.target_semiactor_bump.bump_action(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

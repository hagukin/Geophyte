from __future__ import annotations
from typing import Optional, Tuple, List, TYPE_CHECKING, Dict

import color
import exceptions
import random

from game import Game
from components.inventory import PickupTempInv
from components.semiactor_info import Door
from korean import grammar as g
from language import interpret as i

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item, SemiActor
    from ability import Ability
    from game_map import GameMap

class Action:
    """
    A generic object to represent almost every type of actions.
    Both player and monster performs actions.
    """
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity
        self.free_action = False # If manually set to True, the action will not cost a turn.

    @property
    def engine(self) -> Engine:
        return Game.engine

    def perform(self) -> None:
        """
        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class ActionWithCoordinate(Action):
    def __init__(self, entity: Actor, x: int, y: int, gamemap: Optional[GameMap]=None):
        """
        Vars:
            x, y:
                coordinates. Must be an absolute (gamemap) coordinates.
            gamemap:
                gamemap that the coordinates belongs to.
                if None, use engine.gamemap.
        """
        super().__init__(entity)
        self.x = x
        self.y = y
        if gamemap:
            self.action_gamemap = gamemap
        else:
            self.action_gamemap = self.engine.game_map


class TeleportAction(ActionWithCoordinate):
    def __init__(self, entity: Actor, x: int, y: int, gamemap: Optional[GameMap]=None, stability: int = 0):
        """
        Vars:
            stability:
                0 - always teleport to given location
                1 - randomly teleport to a safe tile
                2 - randomly teleport to any tile
        """
        super().__init__(entity, x, y, gamemap)
        self.stability = stability

    def teleport_to_random(self) -> None:
        x, y = self.action_gamemap.get_random_tile(should_no_entity=True, should_walkable=True, should_safe_to_walk=True,
                                           should_not_protected=True, should_connected_with_stair=True)
        self.entity.gamemap.remove_entity(self.entity)
        self.entity.place(x, y, gamemap=self.action_gamemap)

    def teleport_to_random_can_be_dangerous(self) -> None:
        x, y = self.action_gamemap.get_random_tile(should_no_entity=True, should_walkable=True, should_safe_to_walk=False,
                                           should_not_protected=True, should_connected_with_stair=True)
        self.entity.gamemap.remove_entity(self.entity)
        self.entity.place(x, y, gamemap=self.action_gamemap)

    def teleport_to_given(self) -> None:
        if self.action_gamemap.get_blocking_entity_at_location(self.x,self.y) \
                or not self.action_gamemap.tiles[self.x, self.y]["walkable"] \
                or not self.action_gamemap.check_if_tile_connected_with_stair(self.x, self.y): # Prevent teleporting to isolated area
            return self.teleport_to_random()
        self.entity.gamemap.remove_entity(self.entity)
        self.entity.place(self.x, self.y, gamemap=self.action_gamemap)

    def perform(self) -> None:
        if self.entity == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_teleport")
            self.engine.message_log.add_message(i("당신은 순간이동했다!",
                                                  "You teleported!"), fg=color.player_neutral_important)
            self.engine.sound_manager.add_sound_queue("fx_teleport")
        else:
            if self.engine.game_map.visible[self.entity.x, self.entity.y]:
                self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} 순간이동했다!",
                                                      f"{self.entity.name} teleported!")) # NOTE: ai's path cleared in .place()

        if self.stability == 0:
            return self.teleport_to_given()
        elif self.stability == 1:
            return self.teleport_to_random()
        elif self.stability == 2:
            return self.teleport_to_random_can_be_dangerous()
        else:
            print(f"ERROR::TeleportAction - inappropriate stability value {self.stability}")
            return self.teleport_to_given()


class PickupAction(Action):

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def transfer_item(self, inventory, item) -> None:
        # Failed to add an item
        if not inventory.try_add_item_if_full_drop(item):
            return None

        # Remove the item from current gamemap
        self.engine.game_map.remove_entity(entity=item)
        item.parent = self.entity.inventory

    def pickup_single_item(self, item: Item) -> None:
        inventory = self.entity.inventory
        # Log
        if self.entity == self.engine.player:
            if item.stack_count > 1:
                self.engine.message_log.add_message(i(f"당신은 {g(item.name, '을')} 주웠다. (x{item.stack_count})",
                                                      f"You pick up {item.name}. (x{item.stack_count})"),
                                                    fg=color.obtain_item)
            else:
                self.engine.message_log.add_message(i(f"당신은 {g(item.name, '을')} 주웠다.",
                                                      f"You pick up {item.name}."), fg=color.obtain_item)

            self.engine.sound_manager.add_sound_queue("fx_pickup")
        else:
            if item.stack_count > 1:
                self.engine.message_log.add_message(
                    i(f"{g(self.entity.name, '이')} {g(item.name, '을')} 주웠다. (x{item.stack_count})",
                      f"{self.entity.name} pick up {item.name}. (x{item.stack_count})"), target=self.entity,
                    fg=color.enemy_unique)
            else:
                self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(item.name, '을')} 주웠다.",
                                                      f"{self.entity.name} pick up {item.name}."),
                                                    target=self.entity, fg=color.enemy_unique)

        self.transfer_item(inventory, item)
        return

    def pickup_given_items(self, items: List[Item]) -> None:
        """Pick up and add all given lists of items to inventory."""
        for item in items:
            self.pickup_single_item(item)

    def perform(self) -> None:
        """
        Pickup an item and add it to the actor's inventory, if there is a room for it.

        NOTE: If you want AI to pickup SPECIFIC item, use pickup_single_item or pickup_given_items instead.
        If you want ai to pickup whatever is on its location, you can use this function.
        """
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        items_at_pos = self.engine.game_map.get_all_items_at_location(self.entity.x, self.entity.y)

        if self.entity == self.engine.player:
            # If only one item exists, pickup immediately.
            if not items_at_pos:
                self.engine.message_log.add_message(i("주울 만한 물건이 아무 것도 없습니다.",
                                                      "There is nothing to pick up."), fg=color.impossible)
                return None

            item_len = len(items_at_pos)
            if item_len == 1:
                return self.pickup_single_item(items_at_pos[0])
            else:
                # else, call inputhandler.
                # The inputhandler will call back PickupItem.perform().
                from input_handlers import PickupMultipleHandler
                tmp = PickupTempInv(10000) # Create a temporary inventory object that contains all items on actor's location. (This is not be the most efficient way)
                for item in items_at_pos:
                    tmp.add_item(item)
                self.engine.event_handler = PickupMultipleHandler(inventory_component=tmp)
                self.free_action = True
                return None
        else:
            # AI will only pickup every items on the location.
            # NOTE: Consider using PickupItem.pickup_single_item() instead.
            print(f"LOG::AI picked up items - item list: {items_at_pos}")
            return self.pickup_given_items(items=items_at_pos)


class DescendAction(Action):
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self, depth: int=None) -> None:
        """
        If the Player is the actor, and the game map is not yet generated, this method will randomize a new gamemap object.
        """
        if depth == None:
            n_depth = self.engine.depth + 1
        else:
            n_depth = depth

        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "descending_stair":
            descend_x, descend_y = self.entity.x, self.entity.y
            actors = []
            if self.entity == self.engine.player:
                self.engine.sound_manager.add_sound_queue("fx_descend")
                for (dx, dy) in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)): # Technically you can make all actors able to follow each other to another depth
                    tmp = self.engine.game_map.get_actor_at_location(descend_x + dx, descend_y + dy)
                    if tmp:
                        actors.append(tmp)
                actors = sorted(actors, key=lambda x: x.status.changed_status["agility"],reverse=True)  # Higher agility first

            # Move entity to other level, change engine.gamemap if entity is player
            self.engine.change_entity_depth(
                self.entity, 
                n_depth, 
                self.engine.world.get_map(n_depth).ascend_loc[0], 
                self.engine.world.get_map(n_depth).ascend_loc[1]
                )
            for actor in actors:
                if not actor.actor_state.can_chase_through_stair or actor.is_dead:
                    continue
                if actor.ai:
                    if actor.ai.owner == self.engine.player or actor.ai.target == self.engine.player:
                        self.engine.game_map.descending_actors.add(actor)
        elif self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "ascending_stair":
            raise exceptions.Impossible(i("이 계단은 위로만 향한다.",
                                          "This stair only goes up."))
        else:
            raise exceptions.Impossible(i("내려갈 수 없다.",
                                          "You can't descend here."))


class AscendAction(Action):
    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self, depth: int=None) -> None:
        if depth == None:
            n_depth = self.engine.depth - 1
        else:
            n_depth = depth

        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "ascending_stair":
            ascend_x, ascend_y = self.entity.x, self.entity.y
            actors = []
            if self.entity == self.engine.player:
                # No fx
                for (dx, dy) in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):  # Technically you can make all actors able to follow each other to another depth
                    tmp = self.engine.game_map.get_actor_at_location(ascend_x + dx, ascend_y + dy)
                    if tmp:
                        actors.append(tmp)
                actors = sorted(actors, key=lambda x: x.status.changed_status["agility"],reverse=True)  # Higher agility first

            if n_depth == 0:
                if self.engine.player.inventory.check_if_in_inv("amulet_of_kugah"):
                    from base.data_loader import delete_saved_game
                    delete_saved_game()
                    self.engine.win_game()
                    self.engine.sound_manager.add_sound_queue("fx_victory")
                    from input_handlers import GameClearInputHandler
                    self.engine.event_handler = GameClearInputHandler()
                    return None
                else:
                    raise exceptions.Impossible(i("당신은 쿠가의 아뮬렛을 탈환해 지상으로 복귀해야 한다. 이대로 돌아갈 수 없다.",
                                                  "You must retrieve the amulet of Kugah to return to the surface.")) # TODO: Surface level contents
                    #NOTE: raising an exception won't cost a turn but if you use msg log and return None it would.

            # Move entity to other level
            self.engine.change_entity_depth(
                self.entity, 
                n_depth, 
                self.engine.world.get_map(n_depth).descend_loc[0], 
                self.engine.world.get_map(n_depth).descend_loc[1]
                )
            for actor in actors:
                if not actor.actor_state.can_chase_through_stair:
                    continue
                if actor.ai:
                    if actor.ai.owner == self.engine.player or actor.ai.target == self.engine.player:
                        self.engine.game_map.ascending_actors.add(actor)
        elif self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"] == "descending_stair":
            raise exceptions.Impossible(i("이 계단은 아래로만 향한다.",
                                          "This stair only goes down."))
        else:
            raise exceptions.Impossible(i("올라갈 수 없다.",
                                          "You can't ascend here."))


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

        # Warning
        self.warn()

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        raise NotImplementedError

    def warn(self) -> None:
        warning = True
        if self.item.parent:
            if self.item.parent.parent:
                if self.item.parent.parent == self.entity:
                    warning = False
        if warning:
            print(f"WARNING::Item Action must only be called from item's owner. entity-{self.entity.entity_id}, item-{self.item.entity_id}")

class ThrowItem(ItemAction):
    def __init__(
            self, entity: Actor, item: Item, throw_range: Optional[int]=None, target_xy: Optional[Tuple[int, int]] = None, item_selected: Optional[Item] = None
    ):
        """
        Args:
            throw_range:
                if None, throw as far as the actor can.
        """
        super().__init__(entity=entity, item=item, target_xy=target_xy, item_selected=item_selected)
        self.throw_range = throw_range

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # Check can remove
        if self.item.item_state.equipped_region:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("장착하고 있는 아이템을 던질 수 없습니다.",
                                                      "You can't throw an equipped item."), color.impossible)
            return None
        if not self.item.droppable:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"{g(self.item.name, '을')} 던질 수 없습니다.",
                                                      f"You can't throw {self.item.name}."), color.impossible)
            return None

        if self.entity.status.experience:
            self.entity.status.experience.gain_dexterity_exp(15)
            self.entity.status.experience.gain_strength_exp(10, 14)

        throw_item = None
        if self.item.stack_count > 1:
            split = self.entity.inventory.split_item(item=self.item, split_amount=1) #TODO : Throw multiple?
            if split:
                throw_item = split
            else:
                raise Exception("FATAL ERROR::Unable to split item when performing throwaction")
        else:
            throw_item = self.item # Throwing an item that has stack count 1

        # Actual throw logic handled here
        if self.entity == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_throw")
            self.engine.message_log.add_message(i(f"당신은 {g(throw_item.name, '을')} 던졌다.",
                                                  f"You throw {throw_item.name}."), fg=color.player_neutral_important)
        else:
            # No sound
            self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(throw_item.name, '을')} 던졌다.",
                                                  f"{self.entity.name} throws {throw_item.name}."), fg=color.enemy_unique, target=self.entity)
        throw_item.throwable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.item.item_state.equipped_region:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("장착하고 있는 아이템을 드랍할 수 없습니다.",
                                                      "You can't drop an equipped item."), color.impossible)
            return None
        if not self.item.droppable:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"{g(self.item.name, '을')} 드랍할 수 없습니다.",
                                                      f"You can't drop {self.item.name}."), color.impossible)
            return None

        if self.entity == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_drop")
            if self.item.stack_count > 1:
                self.engine.message_log.add_message(i(f"당신은 {g(self.item.name, '을')} 땅에 떨어뜨렸다. (x{self.item.stack_count})",
                                                      f"You drop {self.item.name}. (x{self.item.stack_count})"),fg=color.player_neutral_important)
            else:
                self.engine.message_log.add_message(i(f"당신은 {g(self.item.name, '을')} 땅에 떨어뜨렸다.",
                                                      f"You drop {self.item.name}."),fg=color.player_neutral_important)
        else:
            if self.item.stack_count > 1:
                self.engine.message_log.add_message(
                    i(f"{g(self.entity.name, '이')} {g(self.item.name, '을')} 땅에 떨어뜨렸다. (x{self.item.stack_count})",
                      f"{self.entity.name} drops {self.item.name}. (x{self.item.stack_count})"),
                    fg=color.enemy_neutral, target=self.entity)
            else:
                self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(self.item.name, '을')} 땅에 떨어뜨렸다.",
                                                      f"{self.entity.name} drops {self.item.name}."),fg=color.enemy_neutral, target=self.entity)
        self.entity.inventory.drop(self.item)


class SplitItem(Action):
    def __init__(self, entity: Actor, item: Item, split_amount: int):
        super().__init__(entity)
        self.item = item
        self.split_amount = split_amount

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        spliten_item = self.entity.inventory.split_item(item=self.item, split_amount=self.split_amount)
        if spliten_item:
            spliten_item.stackable = False
            self.entity.inventory.try_add_item_if_full_drop(item=spliten_item)
            spliten_item.stackable = True

            if self.entity == self.engine.player:
                self.engine.sound_manager.add_sound_queue("fx_split")
        else:# Something went wrong during spliting.
            print("WARNING::Failed to split")
            return None


class UseItem(ItemAction):
    """
    Handles applying/using a item for its intended purpose. (e.g. using tools)
    """
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.entity.status.experience:
            self.entity.status.experience.gain_dexterity_exp(5, 17)

        self.item.usable.activate(self)


class ReadItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.entity.actor_state.is_confused != [0,0]:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 문자를 읽는 데 어려움을 겪었다.",
                                                      f"You have trouble reading."), color.player_failed)
            else:
                print(f"WARNING::{self.entity} failed to read {self.item}.")
            return None
        
        if self.entity == self.engine.player:
            # No sound
            self.engine.message_log.add_message(i(f"당신은 {g(self.item.name, '을')} 읽었다.",
                                                  f"You read {self.item.name}."), color.player_neutral_important)
        else:
            self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} {g(self.item.name, '을')} 읽었다.",
                                                  f"{self.entity.name} reads {self.item.name}."), color.enemy_unique)
        
        if self.entity.status.experience:
            self.entity.status.experience.gain_intelligence_exp(35, 12)

        self.item.readable.activate(self)


class QuaffItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.entity.status.experience:
            self.entity.status.experience.gain_constitution_exp(5, 15, chance=0.5)

        if self.entity == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_quaff")

        self.item.quaffable.activate(self)


class EatItem(ItemAction):
    def warn(self) -> None:
        if self.entity.ai:
            return None # AI can eat item without owning the item.
        else:
            super().warn()

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.entity.status.experience:
            self.entity.status.experience.gain_constitution_exp(2, 20, chance=0.8)

        if self.entity == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_eat")

        self.item.edible.activate(self)


class EquipItem(ItemAction):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # NOTE: FX handled in equipments.func()
        self.entity.equipments.equip_equipment(self.item)


class UnequipItem(ItemAction):
    """Unequip item that the actor owns. (By itself)"""
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # Check can remove
        if self.entity.equipments.equipments[self.item.item_state.equipped_region] == None:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("당신은 해당 위치에 아무 것도 장착하고 있지 않다.",
                                                      "There's nothing to unequip."), fg=color.impossible)
            return None
        elif self.item.item_state.BUC == -1:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"{g(self.item.name, '이')} 몸에서 떨어지지 않는다!",
                                                      f"Your {self.item.name} sticks to your body and doesn't get off!"),fg=color.player_failed)
                self.item.item_state.identify_self(2)
            return None

        # NOTE: FX handled in equipments.func()
        self.entity.equipments.remove_equipment(self.item.item_state.equipped_region)


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
            return None

        # gaining exp is handled in .activate()
        # Sound handled in activate()
        self.ability.activatable.activate(self)


class WaitAction(Action):
    """
    Skips the turn doing nothing.
    This action DO costs action points.
    """
    def perform(self) -> None:
        pass


class FlyAction(Action):
    """
    Toggle on/pff current flying state.
    """
    def fly(self):
        self.entity.actor_state.is_flying = True
        if self.entity == self.engine.player:
            self.engine.message_log.add_message(i("당신은 공중을 날고 있다!",
                                                  "You start to fly!"), fg=color.player_success)
        else:
            self.engine.message_log.add_message(i(f"{g(self.entity.name,'가')} 공중을 날고 있다.",
                                                  f"{self.entity.name} starts flying."), fg=color.enemy_unique)

    def stop_fly(self):
        self.entity.actor_state.is_flying = False
        if self.entity == self.engine.player:
            self.engine.message_log.add_message(i("당신은 공중을 나는 것을 멈췄다.",
                                                  "You are no longer flying."), fg=color.player_neutral)
        else:
            self.engine.message_log.add_message(i(f"{g(self.entity.name,'가')} 공중을 나는 것을 멈췄다.",
                                                  f"{self.entity.name} stops flying."), fg=color.enemy_neutral)

    def perform(self) -> None:
        if self.entity.actor_state.can_fly:
            if not self.entity.actor_state.is_flying:
                self.fly()
            else:
                self.stop_fly()
        else:
            if self.entity.actor_state.is_flying:
                # Can stop flying whether you have ability to fly or not
                self.stop_fly()
            else:
                # Cant fly
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i("당신은 공중으로 날아오르려 시도했지만 실패했다.",
                                                          "You try to fly but fail."), fg=color.player_failed)
                return None

class TurnPassAction(Action):
    """
    Skips the turn doing nothing.
    Difference with WaitAction:
        You can 'purposely' do an wait action while you cannot purposely do a turnpassaction.
    """
    def perform(self) -> None:
        pass


class MultiEntitiesAction(Action):
    """Handles actions that uses multiple items.
    NOTE: You should not use this function when handling item usage."""
    def __init__(self,  entity: Actor, entities: List[Entity]):
        super().__init__(entity)
        self.entities = entities


class ChestAction(MultiEntitiesAction):
    @property
    def chest_name(self) -> str:
        return self.chest_storage.parent.name

    @property
    def actor_storage(self) -> Inventory:
        return self.entity.inventory

    def __init__(self, entity: Actor, entities: List[Item], chest_storage: Inventory):
        super().__init__(entity, entities)
        self.chest_storage = chest_storage


class ChestTakeAction(ChestAction):
    def perform(self) -> None:
        for item in self.entities:
            # Check can remove
            if item.item_state.equipped_region:
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i("장착되어 있는 아이템을 가져갈 수 없습니다.",
                                                          "You can't take something that's equipped."), color.impossible)
                continue

            if self.actor_storage.try_add_item_if_full_drop(self.chest_storage.delete_item_from_inv(item)):
                if self.entity == self.engine.player:
                    if item.stack_count <= 1:
                        self.engine.message_log.add_message(i(f"{g(item.name, '을')} 얻었다.",
                                                              f"You now have {item.name}."), color.obtain_item)
                    else:
                        self.engine.message_log.add_message(i(f"{g(item.name, '을')} 얻었다. (x{item.stack_count})",
                                                              f"You now have {item.name}. (x{item.stack_count}"), color.obtain_item)
                else:
                    if item.stack_count <= 1:
                        self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(item.name, '을')} {self.chest_name}에서 꺼냈다.",
                                                              f"{self.entity.name} takes {item.name} off from the {self.chest_name}."), color.enemy_unique)
                    else:
                        self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(item.name, '을')} {self.chest_name}에서 꺼냈다. (x{item.stack_count})",
                                                              f"{self.entity.name} takes {item.name} off from the {self.chest_name}. (x{item.stack_count})"), color.enemy_unique)

        self.chest_storage.parent.on_actor_take_trigger(interacted_with=self.entity)


class ChestPutAction(ChestAction):
    def perform(self) -> None:
        for item in self.entities:
            # Check can remove
            if item.item_state.equipped_region:
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i("장착하고 있는 아이템을 넣을 수 없습니다.",
                                                          "You can't put in something that's equipped."), color.impossible)
                continue
            elif not item.droppable and self.entity.inventory.check_if_in_inv_object(item):
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"{g(item.name, '을')} 넣을 수 없습니다.",
                                                          f"You can't put in {item.name}."), color.impossible)
                continue

            self.chest_storage.try_add_item_if_full_drop(self.actor_storage.delete_item_from_inv(item))

            if self.entity == self.engine.player:
                if item.stack_count <= 1:
                    self.engine.message_log.add_message(i(f"{g(item.name, '을')} 집어넣었다.",
                                                          f"You put your {item.name} in."), color.player_success)
                else:
                    self.engine.message_log.add_message(i(f"{g(item.name, '을')} 집어넣었다. (x{item.stack_count})",
                                                          f"You put your {item.name} in. (x{item.stack_count})"), color.player_success)
            else:
                if item.stack_count <= 1:
                    self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(item.name, '을')} {self.chest_name}에 집어넣었다.",
                                                          f"{self.entity.name} puts {item.name} into the {self.chest_name}."), color.enemy_unique)
                else:
                    self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(item.name, '을')} {self.chest_name}에서 집어넣었다. (x{item.stack_count})",
                                                          f"{self.entity.name} puts {item.name} into the {self.chest_name}. (x{item.stack_count}"), color.enemy_unique)


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
                self.engine.message_log.add_message(i(f"당신은 휘청거렸다!",
                                                      f"You stagger!"), color.player_not_good)

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
        return self.engine.game_map.get_semiactor_that_bump(*self.dest_xy)

    @property
    def bump_entity(self) -> Optional[Entity]:
        """
        Priority: Actor > Semiactor
        """
        tmp = self.target_actor
        if tmp:
            return tmp
        tmp = self.target_semiactor_bump
        if tmp:
            return tmp
        return None


    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def __init__(self, entity: Actor, dx: int, dy: int):
        """
        Args:
            Check engine.add_effects_to_actors for more info.
        """
        super().__init__(entity, dx, dy)
        self.effect_set = entity.status.changed_melee_effect_set
                      
    def is_miss(self) -> bool:
        """Returns whether the attack was successful or not."""
        # Your chance of successfully attacking will increas when fighting a bigger opponents. Vice versa.
        size_bonus = 1 + (self.target_actor.actor_state.size - self.entity.actor_state.size) * 0.01
        miss_bonus = 1 + max((self.target_actor.status.changed_status["agility"] - self.entity.status.changed_status["agility"])*0.05, 0)

        miss_calc = min(max(
                (0.75*self.entity.status.changed_status["dexterity"])
                * size_bonus
                / miss_bonus
                , 2), 20)
        # 20 -> always has at least 5% chance of missing
        # 2 -> Max Chance to miss: (1 / 2)
        # The bigger miss_calc is, the higher your chance to hit gets

        if random.random() *  miss_calc < 1:
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
        size_bonus = 1 + (self.entity.actor_state.size - self.target_actor.actor_state.size) * 0.01
        damage *= size_bonus

        # Physical damage fall-off
        damage = target.status.calculate_dmg_reduction(damage=damage, damage_type="physical", ignore_reduction=False, penetration_constant=strength, round_dmg=False)

        # Apply critical multiplier
        damage *= crit_multiplier

        # round the damage to integer
        damage = max(0, round(damage))

        return damage


    def add_melee_effect_to_target(self, target: Actor, effect_set: Dict, caused_by: Optional[Actor] = None) -> None:
        """
        This method takes two lists, applies the status effects to the given actor.

        It is usually done by calling apply_xxxing methods,
        but on some cases, if the special effects should be handled immediatly,
        a function can be directly called from this method. (e.g. electric shock)
        """
        # Check if this melee attack has any special effects
        if effect_set:
            # WARNING: be careful with the translations
            if self.entity == self.engine.player:
                atk_name = i("당신", "your")
                tar_name = i(f"{target.name}",f"{target.name}")
                fg = color.player_crit
            elif target == self.engine.player:
                atk_name = i(f"{self.entity.name}",f"{self.entity.name}'s")
                tar_name = i("당신", "you")
                fg = color.player_bad
            else:
                atk_name = i(f"{self.entity.name}",f"{self.entity.name}'s")
                tar_name = i(f"{target.name}",f"{target.name}")
                fg = color.enemy_unique

            # Apply status effects
            for type, eff in effect_set.items():
                if eff is None:
                    continue

                # Calcultate the odds
                if random.random() <= eff["chance"]:
                    pass
                else:
                    continue

                # Negative status effects
                if type == "burn_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 화염 피해를 가했다!",
                                                          f"{atk_name} attack inflicts fire damage to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_burning(list(eff["var"]))
                elif type == "poison_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 독성 피해를 가했다!",
                                                          f"{atk_name} attack inflicts poison damage to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_poisoning(list(eff["var"]))
                elif type == "freeze_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 냉기 피해를 가했다!",
                                                          f"{atk_name} attack inflicts cold damage to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_freezing(list(eff["var"]))
                elif type == "electrocute_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 전격 피해를 가했다!",
                                                          f"{atk_name} attack inflicts electric damage to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_electrocution(list(eff["var"]))
                    target.actor_state.actor_electrocuted(source_actor=caused_by)
                elif type == "bleed_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 출혈 피해를 가했다!",
                                                          f"{atk_name} attack inflicts bleeding to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_bleeding(list(eff["var"]))
                elif type == "paralyze_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 마비 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts paralyzation to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_paralyzation(list(eff["var"]))
                elif type == "slow_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 속도저하 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts slowness to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_slowness(list(eff["var"]))
                elif type == "sleep_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 수면 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts sleep to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_sleeping(list(eff["var"]), forced=False)
                elif type == "melt_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 산성 피해를 가했다!",
                                                          f"{atk_name} attack inflicts acid damage to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_melting(list(eff["var"]))
                elif type == "sick_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 질병 피해를 가했다!",
                                                          f"{atk_name} attack inflicts sickness to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_sickness(list(eff["var"]))
                elif type == "anger_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 분노 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts anger to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_anger(list(eff["var"]))
                elif type == "confuse_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 혼란 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts confusion to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_confusion(list(eff["var"]))
                elif type == "hallucinate_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 환각 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts hallucination to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_hallucination(list(eff["var"]))

                # Other status effects
                elif type == "fast_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 속도증가 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts swiftness to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_haste(list(eff["var"]))
                elif type == "invisible_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 투명화 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts invisibility to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_invisibility(list(eff["var"]))
                elif type == "phase_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 페이징 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts phasing to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_phasing(list(eff["var"]))
                elif type == "levitate_target":
                    self.engine.message_log.add_message(i(f"{atk_name}의 공격이 {tar_name}에게 공중부양 상태이상을 부여했다!",
                                                          f"{atk_name} attack inflicts levitation to {tar_name}!"), fg=fg, target=self.entity)
                    target.actor_state.apply_levitation(list(eff["var"]))
                    

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # Set target
        target = self.target_actor
        if not target:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("당신은 허공을 공격했다.",
                                                      "You attack nothing."), color.impossible)
                self.engine.sound_manager.add_sound_queue("fx_miss")
                return None
            else:
                print("WARNING::Enemy has no target but attacked. - meleeaction")
                return None

        # Name
        if target == self.engine.player:
            att_name = f"{self.entity.name}"
            tar_name = i("당신","you")
            miss_fg = color.enemy_atk_missed
        elif self.entity == self.engine.player:
            att_name = i("당신","you")
            tar_name = f"{target.name}"
            miss_fg = color.player_not_good
        else:
            att_name = f"{self.entity.name}"
            tar_name = f"{target.name}"
            miss_fg = color.enemy_neutral

        # Attack missing calculation
        if self.is_miss():
            if att_name == "you":
                self.engine.message_log.add_message(f"You attack {tar_name} but miss.", miss_fg,target=self.entity)
            else:
                self.engine.message_log.add_message(i(f"{g(att_name, '은')} {g(tar_name, '을')} 공격했지만 빗나갔다.",
                                                      f"{att_name} attacks {tar_name} but misses."), miss_fg, target=self.entity)
            target.status.take_damage(amount=0, attacked_from=self.entity) #Trigger
            if target.status.experience:
                if self.entity.status.changed_status["agility"] > target.status.changed_status["agility"]: # gain exp when dodged
                    target.status.experience.gain_agility_exp(10, 17, exp_limit=1000)

            if self.entity == self.engine.player:
                self.engine.sound_manager.add_sound_queue("fx_player_miss")
            return None
        else:
            if self.entity.status.experience: # gain exp when attack was successful
                self.entity.status.experience.gain_dexterity_exp(5, dex_limit=16)
                self.entity.status.experience.gain_strength_exp(5, str_limit=17, exp_limit=1000)

        # Calculate critical chance, multiplier
        critical_hit = False
        crit_multiplier = self.crit_calculation()
        if crit_multiplier > 1:
            critical_hit = True
            if self.entity.status.experience:
                self.entity.status.experience.gain_dexterity_exp(10, dex_limit=20)

        damage = self.damage_calculation(crit_multiplier=crit_multiplier)

        # Messege log
        if att_name == "you":
            attack_desc = f"you attack {tar_name}"
        else:
            attack_desc = i(f"{g(att_name, '이')} {g(tar_name, '을')} 공격",
                            f"{att_name} attacks {tar_name}")
        if self.entity is self.engine.player:
            if critical_hit:
                attack_color = color.player_crit
            else:
                attack_color = color.player_atk
        elif target is self.engine.player:
            if critical_hit:
                attack_color = color.player_severe
            else:
                attack_color = color.player_melee_hit
        else:
            attack_color = color.enemy_neutral

        hitsound = None
        # If there is damage
        if damage > 0:
            if self.engine.game_map.visible[self.entity.x, self.entity.y] or self.engine.game_map.visible[target.x, target.y]:
                if att_name == "you":
                    self.engine.message_log.add_message(f"{attack_desc} and deal {damage} damage.", attack_color)
                else:
                    self.engine.message_log.add_message(i(f"{attack_desc}해 {damage} 데미지를 입혔다.",
                                                          f"{attack_desc} and deals {damage} damage."), attack_color)

            if self.entity == self.engine.player:
                if critical_hit:
                    hitsound = "fx_player_crit"
                else:
                    hitsound = "fx_player_hit"

            dmg_sound = "fx_damaged"
            target.status.take_damage(amount=damage, attacked_from=self.entity, fx=dmg_sound)
        else:
            if self.engine.game_map.visible[self.entity.x, self.entity.y] or self.engine.game_map.visible[target.x, target.y]:
                self.engine.message_log.add_message(i(f"{attack_desc}했지만 아무런 데미지도 주지 못했다.",
                                                      f"{attack_desc} but did no damage."), miss_fg)
            target.status.take_damage(amount=0, attacked_from=self.entity)  # Trigger

            if self.entity == self.engine.player:
                hitsound = "fx_player_atk_blocked"
        
        # If the target is alive after calculating the pure melee damage hit, apply melee status effects.
        # Status effects are still applied if the damage is zero
        if not target.actor_state.is_dead:
            self.add_melee_effect_to_target(target=target, effect_set=self.effect_set, caused_by=self.entity)
        else:
            if self.entity == self.engine.player:
                hitsound = "fx_player_kill"

        if self.entity == self.engine.player:
            self.engine.sound_manager.add_sound_queue(hitsound)


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None
        
        # Set destination
        dest_x, dest_y = self.dest_xy

        ### Check map boundaries ###
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("길이 막혀 있다.",
                                                      "It's blocked."), fg=color.impossible)
            return None

        ### Check if actor is on a surface tile but cannot move on surfaces
        if not self.entity.actor_state.can_move_on_surface:
            if self.entity.is_on_air:
                pass
            elif self.entity.actor_state.is_submerged:
                if self.entity.gamemap.check_if_tile_is_surface(dest_x, dest_y):
                    if self.entity == self.engine.player:
                        self.engine.message_log.add_message(i("당신은 해당 위치로 이동할 수 없다.",
                                                              "You can't move to the given location."), fg=color.impossible)
                    return None
                pass
            else:
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i("당신은 이동할 수 없다.",
                                                          "You can't move."), fg=color.impossible)
                return None

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
                    crawl_out_chance = max(0.1,0.005 * self.entity.status.changed_status["dexterity"] * (self.entity.actor_state.size ** 2)) # crawl-out chance calculation

            if random.random() > crawl_out_chance:
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신은 구덩이에서 빠져나오려 시도했으나 실패했다.",
                                                          f"You try to crawl out from the pit but fail."), color.player_failed)
                else:
                    self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} 구덩이에서 빠져나오려 했으나 실패했다.",
                                                          f"{self.entity.name} tries to crawl out from the pit but fails."), color.enemy_neutral, target=self.entity)
                return None # Turn passes

        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("길이 막혀 있다.","It's blocked."), fg=color.impossible)
            return None
            
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("길이 막혀 있다.","It's blocked."), fg=color.impossible)
            return None

        self.entity.move(self.dx, self.dy)

        if self.entity.status.experience:
            self.entity.status.experience.gain_agility_exp(0.2, 18) # 1 exp per 5 tiles
            if self.entity.actor_state.encumbrance > 0:
                self.entity.status.experience.gain_strength_exp(0.3*self.entity.actor_state.encumbrance, str_limit=18)


class DoorUnlockAction(ActionWithDirection):
    """
    If entity is ai, and cannot unlock the door, it will automatically try to break it.
    Player will try to unlock the door.

    NOTE: Unlocking something REQUIRES an item to use to unlock the door.
    It is recommended to make ai unable to unlock something.
    The chance of successfully unlocking something depends on both the actor and the item used.
    """
    def ai_unlock(self) -> None:
        dest_x, dest_y = self.dest_xy
        door = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y, "door")

        if self.entity.ai:
            self.entity.ai.path = None

        if not door or not isinstance(door.semiactor_info, Door):
            print("WARNING::AI tried to unlock something thats not unlockable.")
            return None
        else:
            # Ai's chance of unlocking is dependent to its intelligence as well
            dexterity = self.entity.status.changed_status["dexterity"]
            intelligence = self.entity.status.changed_status["intelligence"]
            chance_of_unlocking = max(0, dexterity + intelligence - 25/50)
            if random.random() <= chance_of_unlocking and intelligence > 10 and dexterity > 7:
                # Unlock succeded
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신은 문의 잠금을 해제하는데 성공했다!",
                                                          f"You successfully unlock the door!"), color.player_success)
                    self.engine.sound_manager.play_sound("fx_unlock")
                else:
                    self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} 문의 잠금을 해제했다!",
                                                          f"{self.entity.name} unlocks the door!"), color.enemy_unique, target=self.entity)

                import semiactor_factories
                tmp = semiactor_factories.closed_door.spawn(self.engine.game_map, dest_x, dest_y, -1)
                door.semiactor_info.move_self_to(tmp)
                door.remove_self()

                if self.entity.status.experience:
                    self.entity.status.experience.gain_dexterity_exp(30, 18, 600)
            else:
                # Unlock failed
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신은 문의 잠금을 해제하는데 실패했다.",
                                                          f"You fail to unlock the door."), color.player_failed)
                else:
                    self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} 문의 잠금을 해제하는데 실패했다.",
                                                          f"{self.entity.name} fails to unlock the door."), color.enemy_unique, target=self.entity)


    def unlock(self, item: Item) -> None:
        import semiactor_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # Get door coordinates
        dest_x, dest_y = self.dest_xy
        door = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y, "door")

        if not door or not isinstance(door.semiactor_info, Door):
            raise exceptions.Impossible(i("이 곳에는 잠금을 해제할 물건이 없다.",
                                          "There is nothing to unlock."))
        else:
            dexterity = self.entity.status.changed_status["dexterity"]

            tool_bonus = item.lockpickable[0]
            tool_chance_of_breaking = item.lockpickable[1]

            # -1 - Always successful
            if tool_bonus == -1:
                chance_of_unlocking = 1
            else:
                chance_of_unlocking = tool_bonus * min(1, dexterity / 18 * door.semiactor_info.unlock_chance)

            if random.random() <= chance_of_unlocking:
                # Unlock succeded
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신은 {g(item.name, '을')} 사용해 문의 잠금을 해제했다!",
                                                        f"You unlock the door with {item.name}!"), color.player_success)
                    self.engine.sound_manager.add_sound_queue("fx_unlock")
                else:
                    self.engine.message_log.add_message(i(f"{g(self.entity.name, '이')} {g(item.name, '을')} 사용해 문의 잠금을 해제했다!",
                                                          f"{self.entity.name} unlock the door with {item.name}!"), color.enemy_unique, target=self.entity)

                tmp = semiactor_factories.closed_door.spawn(self.engine.game_map, dest_x, dest_y, -1)
                door.semiactor_info.move_self_to(tmp)
                door.remove_self()

                if self.entity.status.experience:
                    self.entity.status.experience.gain_dexterity_exp(30, 18, 600)
            else:
                # Unlock failed
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신은 문의 잠금을 해제하는데 실패했다.",
                                                          "You fail to unlock the door."), color.player_failed)

            # Item can break regardless of the result
            if random.random() <= tool_chance_of_breaking:
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"잠금을 해제하는 과정에서 {g(item.name, '이')} 파괴되었다.",
                                                          f"Your {item.name} is broken during the process."), color.player_bad, target=self.entity)
                item.remove_self()

            from input_handlers import MainGameEventHandler
            self.engine.event_handler = MainGameEventHandler()
            return None

    def perform(self) -> None:
        # If the player is the actor, call input handler
        if self.entity == self.engine.player:
            from input_handlers import InventoryChooseItemAndCallbackHandler
            from order import InventoryOrder
            self.free_action = True
            self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
                self.engine.player.inventory, 
                self.unlock,
                title=i("잠금 해제에 사용할 아이템을 선택하세요.","Choose an item to use."),
                show_only_types=(
                    InventoryOrder.MELEE_WEAPON,
                    InventoryOrder.TOOL,
                )
            )
            return None
        else:
            if self.entity.ai:
                if self.entity.status.changed_status["intelligence"] > 13 and self.entity.status.changed_status["dexterity"] > 13:
                    self.ai_unlock()
                else:
                    DoorBreakAction(self.entity, self.dx, self.dy).perform()

class DoorBreakAction(ActionWithDirection):
    def break_door(self) -> None:
        dest_x, dest_y = self.dest_xy
        door = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y, "door")
        strength = self.entity.status.changed_status["strength"]
        if isinstance(door.semiactor_info, Door):
            break_fail = random.randint(*door.semiactor_info.break_str_req)
        else:
            print("ERROR::Door semiactor {door.entity_id} has wrong semiactor_info type.")
            break_fail = random.randint(10,20) # Default value

        if break_fail > strength:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 {g(door.name, '을')} 강제로 열려고 시도했지만 실패했다.",
                                                      f"You try opening the {door.name} by force but fail."),color.player_failed)
                self.engine.sound_manager.add_sound_queue("fx_try_break_door")
            else:
                self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} {g(door.name, '을')} 강제로 열려고 시도했지만 실패했다.",
                                                      f"{self.entity.name} tries opening the {door.name} by force but fail."), color.enemy_neutral, target=self.entity)
        elif break_fail * 1.5 <= strength: # if the strength value is higher than the break_fail * 1.5, break open the door (Minimum str req. for breaking the door: 20)
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 {g(door.name, '을')} 파괴했다!",
                                                      f"You destroy the {door.name}!"), color.player_success)
                self.engine.sound_manager.add_sound_queue("fx_break_door")
            else:
                self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} {g(door.name, '을')} 파괴했다!",
                                                      f"{self.entity.name} destroys the {door.name}!"), color.enemy_unique, target=self.entity)
            door.remove_self()
            if self.entity.status.experience:
                self.entity.status.experience.gain_strength_exp(30, 17, 1000)
            # TODO: drop the wooden door pieces?
        else: # Bust open the door but not break it
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 {g(door.name, '을')} 강제로 열었다!",
                                                      f"You open the {door.name} by force!"), color.player_success)
                self.engine.sound_manager.add_sound_queue("fx_force_open_door")
            else:
                self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} {g(door.name, '을')} 강제로 열었다!",
                                                      f"{self.entity.name} opens the {door.name} by force!"), color.enemy_unique,target=self.entity)

            import semiactor_factories
            tmp = semiactor_factories.opened_door.spawn(self.engine.game_map, door.x, door.y, -1)
            door.semiactor_info.move_self_to(tmp)
            door.remove_self()

            if self.entity.status.experience:
                self.entity.status.experience.gain_strength_exp(30, 17, 500)

        if self.entity == self.engine.player:
            from input_handlers import MainGameEventHandler
            self.engine.event_handler = MainGameEventHandler()

    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # Get door coordinates
        dest_x, dest_y = self.dest_xy
        door = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y, semiactor_id="door")

        if self.entity.ai:
            self.entity.ai.path = None

        if not door or not isinstance(door.semiactor_info, Door):
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("이 곳에는 문이 없다.",
                                                      "There is no door to open."), fg=color.impossible)
        elif door.entity_id[-11:] == "opened_door":
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("이 문은 이미 열려 있다.",
                                                      "The door is already opened."), fg=color.impossible)
        elif door.entity_id[-11:] == "locked_door":
            self.break_door()
            return None
        else:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("이 곳에는 문이 없다.",
                                                      "There is no door to open."), fg=color.impossible)


class DoorOpenAction(ActionWithDirection):
    
    def open_door(self, door: SemiActor, dexterity: int, intelligence: int) -> None:
        open_fail = random.randint(4, 12) # dex lower than 4 always fails to open the door, higher than 12 always success
            
        if open_fail > dexterity: # check if the actor failed to open the door
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 {g(door.name, '을')} 여는 것에 실패했다!",
                                                      f"You fail to open the {door.name}!"), color.player_failed)
                self.engine.sound_manager.add_sound_queue("fx_door_open_fail")
            else:
                self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} {g(door.name, '을')} 여는 것에 실패했다!",
                                                    f"{self.entity.name} fails to open the {door.name}!"), color.enemy_neutral, target=self.entity)
            from input_handlers import MainGameEventHandler
            self.engine.event_handler = MainGameEventHandler()
            return None

        import semiactor_factories
        tmp = semiactor_factories.opened_door.spawn(self.engine.game_map, door.x, door.y, -1)
        door.semiactor_info.move_self_to(tmp)
        door.remove_self()

        if self.entity == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_open_door")

        if self.entity.status.experience:
            self.entity.status.experience.gain_dexterity_exp(5, 15, 300)

        from input_handlers import MainGameEventHandler
        self.engine.event_handler = MainGameEventHandler()

    def check_can_open_door(self, dexterity: int, intelligence: int) -> bool:
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
        """
        If entity cannot open the door, it will automatically try to break it.
        """
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # Get door coordinates
        dest_x, dest_y = self.dest_xy
        door = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y, semiactor_id="door")

        # Get actor status
        dexterity = self.entity.status.changed_status["dexterity"]
        strength = self.entity.status.changed_status["strength"]
        intelligence = self.entity.status.changed_status["intelligence"]

        if not door or not isinstance(door.semiactor_info, Door):
            self.engine.message_log.add_message(i("이 곳에는 문이 없다.",
                                                  "There is no door to open."), fg=color.impossible)
            return None
        elif door.entity_id[-11:] == "closed_door":
            can_open_door = self.check_can_open_door(dexterity, intelligence)
            
            # Check if the actor can open the door
            if can_open_door:
                self.open_door(door, dexterity, intelligence)
            # If the actor can't open the door but can try to break the door, actor tries it
            else: # If it can, try breaking the door
                DoorBreakAction(self.entity, self.dx, self.dy).perform()
            return None
        elif door.entity_id[-11:] == "opened_door":
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i("이 문은 이미 열려 있다.",
                                                      "The door is already opened."), color.impossible)
        elif door.entity_id[-11:] == "locked_door":
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"문이 굳게 잠겨 열리지 않는다.",
                                                      "The door is locked and won't open."), color.player_failed)
                self.engine.sound_manager.add_sound_queue("fx_door_open_fail")
        else:
            if self.entity == self.engine.player:
                self.engine.message_log.add_message(i(f"이 곳에는 문이 없다.",
                                                      "There is no door to open."), color.impossible)


class DoorCloseAction(ActionWithDirection):
    def perform(self) -> None:
        import semiactor_factories

        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        # Set coordinates
        dest_x, dest_y = self.dest_xy
        door = self.engine.game_map.get_semiactor_at_location(dest_x, dest_y)

        if not door or not isinstance(door.semiactor_info, Door):
            raise exceptions.Impossible(i("이 곳에는 문이 없다.", "There is no door to close."))
        elif door.entity_id[-11:] == "opened_door":
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
            if self.engine.game_map.get_any_entity_at_location(dest_x, dest_y, exception=door):
                raise exceptions.Impossible(i("무언가가 막고 있다.", "Something is blocking the door."))

            # Try to close the door
            close_fail = random.randint(0, 10) # if dex > 10, actor will not fail closing the door by chance
            if not can_close_door or close_fail > dexterity: # check if the actor has no capabilities, or if the actor failed closing it by chance
                if self.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신은 {g(door.name, '을')} 닫는 것에 실패했다!",
                                                          f"You fail to close the {door.name}!"), color.player_failed)
                else:
                    self.engine.message_log.add_message(i(f"{g(self.entity.name, '은')} {g(door.name, '을')} 닫는 것에 실패했다!"
                                                          f"{self.entity.name} fails to close the {door.name}!"), color.enemy_neutral, target=self.entity)
                return None

            tmp = semiactor_factories.closed_door.spawn(self.engine.game_map, dest_x, dest_y, -1)
            door.semiactor_info.move_self_to(tmp)
            door.remove_self()

            if self.entity.status.experience:
                self.entity.status.experience.gain_dexterity_exp(5, 15, 300)

            if self.entity == self.engine.player:
                self.engine.sound_manager.add_sound_queue("fx_close_door")

            return None
        elif door.entity_id[-11:] == "closed_door" or door.entity_id[-11:] == "locked_door":
            raise exceptions.Impossible(i("이 문은 이미 닫혀 있다.", "The door is already closed."))
        else:
            raise exceptions.Impossible(i("이 곳에는 문이 없다.", "There is no door to close."))


class ActionWithDirectionAndTarget(ActionWithDirection):
    def __init__(self, entity: Actor, dx: int, dy: int, target: Entity):
        super().__init__(entity, dx, dy)
        self.target = target

    def perform(self) -> None:
        raise NotImplementedError()


class CashExchangeAction(Action):
    def __init__(self, giver: Actor, taker: Actor, cash_amount: int):
        super().__init__(entity=giver)
        self.giver = giver
        self.taker = taker
        self.cash_amount = cash_amount

    def perform(self) -> None:
        """NOTE: The action will not care how much money each actor currently have.
        You should check whether the transaction is valid BEFORE you perform the action."""
        from item_factories import shines
        self.taker.inventory.try_add_item_if_full_drop(shines(self.cash_amount).copy(gamemap=None))

        while self.cash_amount > 0:
            shine = self.giver.inventory.check_if_in_inv("shine")
            if not shine:
                raise Exception("FATAL ERROR::Not enough shines. This should've been prevented before calling the action.perform(). - CashExchangeAction")
            if shine.stack_count >= self.cash_amount:
                self.giver.inventory.decrease_item_stack(shine, self.cash_amount) # Equipped/Cursed/Droppable check in inputhandler
                self.cash_amount -= self.cash_amount
                break
            else:
                self.cash_amount -= shine.stack_count
                self.giver.inventory.decrease_item_stack(shine, shine.stack_count)  # Equipped/Cursed/Droppable check in inputhandler

        if self.giver == self.engine.player or self.taker == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_cash")


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
            return None

        temp_x, temp_y = self.entity.x, self.entity.y
        self.entity.place(self.target.x, self.target.y)
        self.target.place(temp_x, temp_y)

        # path doesn't sync up with current entity location so reset it.
        if hasattr(self.entity, "ai"):
            if self.entity.ai:
                self.entity.ai.path = None
        if hasattr(self.target, "ai"):
            if self.target.ai:
                self.target.ai.path = None

        if self.entity == self.engine.player:
            self.engine.message_log.add_message(i(f"당신은 {g(self.target.name, '와')} 자리를 바꾸었다.",
                                                  f"You swap your position with {self.target.name}."), color.player_neutral)

        # exp
        if self.entity.status.experience:
            self.entity.status.experience.gain_charm_exp(20, 17)
            self.entity.status.experience.gain_dexterity_exp(5, 17)

class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        # Checking for inability
        if self.entity.check_for_immobility():
            return None

        if self.bump_entity:
            from input_handlers import NonHostileBumpHandler
            if self.bump_entity.how_many_bump_action_possible(actor=self.entity) == 1: # Auto-Action when there is only one available action. (e.g. opening a door, attacking a hostile monster etc.)
                action = self.bump_entity.get_bumpaction(actor=self.entity, keyword=self.bump_entity.get_possible_bump_action_keywords(self.entity)[0])
                if action is None:
                    return None
                else:
                    return action.perform()
            else:
                # Force entity to attack when angered
                if self.bump_entity.check_if_bump_action_possible(actor=self.entity, keyword="attack")\
                        and self.entity.actor_state.is_angry != [0,0]: # Actor will attack without being able to decide what to do when angered.
                    action = self.bump_entity.get_bumpaction(actor=self.entity, keyword="attack")
                    if action is None:
                        return None
                    else:
                        return action.perform()

                if self.entity == self.engine.player:
                    self.engine.event_handler = NonHostileBumpHandler(self.bump_entity)
                    self.free_action = True # Force this action to not cost a time so that yime passes after player decides whether to attack or not.
                    return None
                else:
                    if self.entity.ai:
                        tmp = self.entity.ai.get_action_when_bumped_with(bumped_entity=self.bump_entity)
                        if tmp:
                            return tmp.perform()
                        else:
                            print(f"WARNING::{self.entity.entity_id} has no idea what to do when bumped with {self.bump_entity}")
                            return None
        else:
            if self.entity != self.engine.player:
                return MovementAction(self.entity, self.dx, self.dy).perform() # AI should've avoided any danger during ai's path setting (which is before executing this action.)
            else:
                if self.engine.game_map.check_tile_safe(self.engine.player, x=self.entity.x + self.dx, y=self.entity.y + self.dy, ignore_semiactor=True):
                    return MovementAction(self.entity, self.dx, self.dy).perform()
                else:
                    # If next tile is same as current one, ignore warning.
                    if self.engine.game_map.tiles[self.entity.x + self.dx, self.entity.y + self.dy]["tile_id"] == self.engine.game_map.tiles[self.entity.x, self.entity.y]["tile_id"]:
                        return MovementAction(self.entity, self.dx, self.dy).perform()
                    from input_handlers import DangerousTileWalkHandler
                    self.engine.event_handler = DangerousTileWalkHandler(dx=self.dx, dy=self.dy)
                    self.free_action = True # Force this action to not cost a time so that yime passes after player decides whether to attack or not.
                    return None


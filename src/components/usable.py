from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Tuple, List

from components.base_component import BaseComponent
from korean import grammar as g
from order import InventoryOrder

import actions
import color

if TYPE_CHECKING:
    from entity import Item, Actor


class Usable(BaseComponent):
    """NOTE: Based off of readable component."""
    def __init__(self, should_consume: bool=False):
        super().__init__(None)
        self.should_consume = should_consume

    def get_action(self, user: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.UseItem(user, self.parent)

    def activate(self, action: actions.UseItem) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def after_usage(self, user: Actor, show_consume_msg: bool=False) -> None:
        if user == self.engine.player:
            self.parent.item_state.identify_self(identify_level=2)
        if self.should_consume:
            self.consume(user, show_consume_msg)

    def consume(self, consumer: Actor, show_msg: bool=False) -> None:
        """Remove the consumed item from its containing inventory."""
        # fully identify used instance, and semi-identify the same item types.
        if not self.should_consume:
            print("ERROR::Usable.consume() called but the parent should_consume is False. Aborting process.")
            return
        self.parent.parent.decrease_item_stack(self.parent, remove_count=1)
        if show_msg and consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 소모되었다.", color.player_bad)

    def item_use_cancelled(self, actor: Actor) -> actions.Action:
        """
        Called when item usage is cancelled.
        Only the player should be able to call this function.
        """
        self.after_usage(actor, show_consume_msg=True) # Can be consumed
        return actions.WaitAction(actor)


class SelectItemFromInventoryUsable(Usable):
    def get_action(self, user: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=user)

        self.engine.message_log.add_message("아이템을 선택하세요.", color.help_msg)

        from input_handlers import InventoryChooseItemAndCallbackHandler
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            inventory_component=user.inventory,
            show_only_types=None,  # If item_type filter is needed, you should override this entire function.
            show_only_status=None,
            callback=lambda selected_item: actions.UseItem(user, self.parent, (0, 0), selected_item),
            item_cancel_callback=lambda x: self.get_action(user, x),
        )
        return None

    def effects_on_selected_item(self, user: Actor, selected_item: Item):
        raise NotImplementedError()

    def activate(self, action: actions.ReadItem) -> None:
        user = action.entity
        self.effects_on_selected_item(user, action.item_selected)
        self.after_usage(user)


class WaxUsable(SelectItemFromInventoryUsable):
    def get_action(self, user: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=user)

        self.engine.message_log.add_message("아이템을 선택하세요.", color.help_msg)

        from input_handlers import InventoryChooseItemAndCallbackHandler
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            inventory_component=user.inventory,
            show_only_types=(
                InventoryOrder.MELEE_WEAPON,
                InventoryOrder.ARMOR,
                InventoryOrder.AMULET,
                InventoryOrder.RING,
                InventoryOrder.WAND,
                ),# Only display enchantable items.,
            show_only_status=None,
            callback=lambda selected_item: actions.UseItem(user, self.parent, (0, 0), selected_item),
            item_cancel_callback=lambda x: self.get_action(user, x),
        )
        return None


class RustproofWaxUsable(WaxUsable):
    def __init__(self, should_consume: bool, corrodible_modifier:float):
        """
        Args:
            corrodible_modifier:
                value to subtract to item's corrodible value.
        """
        super().__init__(should_consume)
        self.corrodible_modifier = corrodible_modifier
        if corrodible_modifier < 0:
            print(f"WARNING::corrodible_modifier for {self.parent} is lower than 0. Are you sure this is the right value?")

    def effects_on_selected_item(self, user: Actor, selected_item: Item) -> None:
        if user == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} {selected_item.name}에 사용했다.",fg=color.player_neutral_important)
        else:
            self.engine.message_log.add_message(f"{g(user.name, '은')} {g(self.parent.name, '을')} {selected_item.name}에 사용했다.", fg=color.player_neutral_important)

        if selected_item.corrodible <= 0:
            return None # Does nothing if the item is already non-corrodible.

        if self.parent.item_state.BUC == -1:
            selected_item.corrodible = round(min(1, selected_item.corrodible + self.corrodible_modifier), 3)
            if user == self.engine.player:
                self.engine.message_log.add_message(f"당신의 {g(selected_item.name, '으로')}부터 퀴퀴한 냄새가 난다.", fg=color.player_not_good)
        else:
            if self.parent.item_state.BUC == 1:
                self.corrodible_modifier *= 2
            selected_item.corrodible = round(min(max(0.0, selected_item.corrodible - self.corrodible_modifier), selected_item.corrodible), 3)
            if user == self.engine.player:
                self.engine.message_log.add_message(f"당신의 {g(selected_item.name, '으로')}부터 향긋한 냄새가 난다.", fg=color.player_not_good)




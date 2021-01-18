from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item

class Quaffable(BaseComponent):
    parent: Item

    @property
    def owner(self) -> Actor:
        return self.parent.parent.parent

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.QuaffItem(consumer, self.parent)

    def activate(self, action: actions.QuaffItem) -> None:
        """
        Invoke this items ability.
        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        self.parent.parent.remove_item(self.parent, remove_count=1)


class PotionOfHealingQuaffable(Quaffable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.QuaffItem) -> None:
        consumer = action.entity
        amount_recovered = consumer.status.heal(self.amount)

        if amount_recovered > 0:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"Your wounds start to recover!",color.health_recovered,)
            else:
                if self.engine.game_map.visible[consumer.x, consumer.y]:
                    self.engine.message_log.add_message(f"{consumer.name}'s wounds suddenly start to recover!", color.white, target=consumer)
        else:# Gain additional health when quaffed while full-health
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"You feel much more energetic!",color.health_recovered,)

            consumer.status.max_hp += max(1, round(self.amount / 10))#TODO balance
        
        self.consume()


class PotionOfParalysisQuaffable(Quaffable):
    def __init__(self, turn: int):
        self.turn = turn

    def activate(self, action: actions.QuaffItem) -> None:
        consumer = action.entity
        consumer.actor_state.is_paralyzing = [0,self.turn]

        # Log
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"Suddenly you can't move your body!", color.player_damaged,)
        else:
            if self.engine.game_map.visible[consumer.x, consumer.y]:
                self.engine.message_log.add_message(f"{consumer.name} suddenly stops all movements!", color.white, target=consumer)
            
        self.consume()
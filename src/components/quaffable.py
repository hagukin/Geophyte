from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
from components.base_component import BaseComponent
from korean import grammar as g

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
        # fully identify used instance, and semi-identify the same item types.
        self.parent.item_state.identify_self(identify_level=2)
        self.parent.parent.remove_item(self.parent, remove_count=1)


class PotionOfHealingQuaffable(Quaffable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.QuaffItem) -> None:
        consumer = action.entity
        amount_recovered = consumer.status.heal(self.amount)

        if amount_recovered > 0:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"당신의 상처가 낫기 시작한다!",color.health_recovered,)
            else:
                if self.engine.game_map.visible[consumer.x, consumer.y]:
                    self.engine.message_log.add_message(f"{consumer.name}의 상처가 낫기 시작한다!", color.white, target=consumer)
        else:# Gain additional health when quaffed while full-health
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"당신의 몸에 에너지가 넘친다!",color.health_recovered,)

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
            self.engine.message_log.add_message(f"당신은 갑자기 몸을 움직일 수가 없게 되었다!", color.player_damaged,)
        else:
            if self.engine.game_map.visible[consumer.x, consumer.y]:
                self.engine.message_log.add_message(f"{g(consumer.name, '이')} 돌연 모든 움직임을 멈추었다.", color.white, target=consumer)
            
        self.consume()

class PotionOfMonsterDetectionQuaffable(Quaffable):
    """The actor will gain a temporary ability to see far away actors that are on this level."""
    def __init__(self, turn: int):
        self.turn = turn
    
    def activate(self, action: actions.QuaffItem) -> None:
        consumer = action.entity
        consumer.actor_state.is_detecting_obj = [0,self.turn,("actor",)]
        
        # Log
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신은 다른 생명체들의 존재를 감지하기 시작했다.", color.player_damaged,)
        else:
            if self.engine.game_map.visible[consumer.x, consumer.y]:
                self.engine.message_log.add_message(f"{consumer.name} looks more sharp.", color.white, target=consumer)
            
        self.consume()
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from components.base_component import BaseComponent

import actions
import color

if TYPE_CHECKING:
    from entity import Actor, Item

class Edible(BaseComponent):
    parent: Item
    def __init__(self, nutrition: int, spoilage: int, is_cooked: bool, spoil_speed:int=1):
        """
        Args:
            nutrition:
                nutrition ≈ 5 kcal.
            spoil_speed:
                speed of this food rotting.
            spoilage:
                int(range from [-1, 3]). higher the number is, the worse the food's condition is.
                negative value indicates that the food will never go bad.
                0 or lower: fresh
                1: normal
                2: bad
                3: rotten
                higher: rotted out (the food is gone)
        """
        self._nutrition = nutrition
        self.spoil_speed = spoil_speed

        # Values that need manual copying when copying the component
        self.time_after_spawned = 0 # passed time after the food(or the corpse) was generated on the dungeon. (NOTE: This DOES NOT indicate the turn passed. This is a relative value.)
        self.is_cooked = is_cooked
        self.spoilage = spoilage

    @property
    def nutrition(self):
        if self.spoilage > 1:
            return int(self._nutrition / self.spoilage)
        else:
            return self._nutrition

    def time_pass(self) -> None:
        """
        the food slowly rots.
        """
        if self.spoilage < 0:
            return None # The food never rots.

        if self.is_cooked and self.spoil_speed > 1:# cooked foods will rot slowly
            self.spoil_speed = max(1, self.spoil_speed - 2)
        
        self.time_after_spawned += self.spoil_speed

        # each 150 time passed, food's spoilage gets worse
        if self.time_after_spawned >= 150:
            self.spoilage += 1
            self.time_after_spawned = 0

        # foods will rot away if its too rotten
        if self.spoilage > 3:
            if self.parent.parent != None:
                if self.parent.parent.parent == self.engine.player:
                    self.engine.message_log.add_message(f"Your {self.parent.name} rots away!", color.player_damaged,)
            else:
                if self.engine.game_map.visible[self.parent.x, self.parent.y]:
                    self.engine.message_log.add_message(f"{self.parent.name} rots away.", color.gray, target=self.parent)
            self.parent.remove_self()

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.EatItem(consumer, self.parent)

    def gain_nutrition(self, action: actions.EatItem):
        """
        Gain nutrition.
        All the special effects of the food is not handled here.
        """
        consumer = action.entity
        nutrition_gained = self.nutrition
        consumer.actor_state.hunger += nutrition_gained # gain nutrition

        #TODO: Add food poison, over eating debuffs

        # Log
        if consumer == self.engine.player:
            if self.spoilage <= 0: # Fresh
                self.engine.message_log.add_message(
                    f"{self.parent.name} tastes fresh!",
                    color.health_recovered,
                )
            elif self.spoilage == 1: # Normal
                self.engine.message_log.add_message(
                    f"{self.parent.name} tastes fine.",
                    color.white,
                )
            elif self.spoilage == 2: # Bad
                self.engine.message_log.add_message(
                    f"{self.parent.name} doesn't taste good.",
                    color.white,
                )
            elif self.spoilage >= 3: # rotten
                self.engine.message_log.add_message(
                    f"{self.parent.name} tastes awful!",
                    color.player_damaged,
                )

            # Log - status
            if consumer.actor_state.hunger_state == "fainting":
                self.engine.message_log.add_message(
                    f"You are still fainting from hunger...",
                    color.player_damaged,
                )
            elif consumer.actor_state.hunger_state == "starving":
                self.engine.message_log.add_message(
                    f"You are still starving...",
                    color.player_damaged,
                )
            elif consumer.actor_state.hunger_state == "hungry":
                self.engine.message_log.add_message(
                    f"You are still a bit hungry.",
                    color.gray,
                )
            elif consumer.actor_state.hunger_state == "":
                self.engine.message_log.add_message(
                    f"Your stomach feels okay.",
                    color.gray,
                )
            elif consumer.actor_state.hunger_state == "satiated":
                self.engine.message_log.add_message(
                    f"You feel full.",
                    color.gray,
                )
            elif consumer.actor_state.hunger_state == "overeaten":
                self.engine.message_log.add_message(
                    f"You feel terribly full.",
                    color.player_damaged,
                )
        else:
            self.engine.message_log.add_message(
                f"The {action.entity.name} is eating the {self.parent.name}.",
                fg=color.gray,
                target=action.entity,
            )

        self.consume()

    def activate(self, action: actions.EatItem) -> None:
        """
        Invoke this items ability when eaten.
        `action` is the context for this activation.
        """
        self.gain_nutrition(action=action)
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        self.parent.remove_self()


class RawMeatEdible(Edible):
    """
    Provides no special effects.
    The meat is uncooked, and can be cooked by fire.
    The consumer gains nutritions.
    Meat rots faster. (spoil_speed set to 3)
    """
    def __init__(self, nutrition: int, spoilage: int=0, is_cooked: bool=False, spoil_speed: int=3):
        super().__init__(
            nutrition,
            spoilage,
            is_cooked,
            spoil_speed,
            )

    def activate(self, action: actions.QuaffItem) -> None:
        self.gain_nutrition(action=action)


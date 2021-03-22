from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from components.base_component import BaseComponent
from korean import grammar as g

import actions
import color

if TYPE_CHECKING:
    from entity import Actor, Item

class Edible(BaseComponent):
    parent: Item
    def __init__(self, nutrition: int, spoilage: int=0, is_cooked: bool=False, can_cook: bool=False, spoil_speed:int=1, cook_bonus: int = 0):
        """
        Args:
            nutrition:
                1 nutrition ≈ 5 kcal.
            spoil_speed:
                speed of this food rotting. higher number -> faster rotting
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
        self.cook_bonus= cook_bonus
        self.spoil_speed = spoil_speed
        self.can_cook = can_cook

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
                    self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 썩어 사라졌다!", color.player_damaged,)
            else:
                if self.engine.game_map.visible[self.parent.x, self.parent.y]:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 썩어 사라졌다.", color.gray, target=self.parent)
            self.parent.remove_self()

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.EatItem(consumer, self.parent)

    def cook(self):
        if self.can_cook:
            self.is_cooked = True
            self._nutrition += self.cook_bonus
        else:
            return None

    def gain_nutrition(self, action: actions.EatItem):
        """
        Gain nutrition.
        All the special effects of the food is not handled here.
        """
        # gain nutrition
        consumer = action.entity
        nutrition_gained = self.nutrition
        consumer.actor_state.hunger += nutrition_gained

        #TODO: Add food poison, over eating debuffs

        # Log
        if consumer == self.engine.player:
            if self.spoilage <= 0: # Fresh
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 굉장히 맛있었다!",
                    color.health_recovered,
                )
            elif self.spoilage == 1: # Normal
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 나쁘지 않았다.",
                    color.white,
                )
            elif self.spoilage == 2: # Bad
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 맛이 좋지 않았다.",
                    color.white,
                )
            elif self.spoilage >= 3: # rotten
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 맛이 끔찍했다!",
                    color.player_damaged,
                )

            # Log - status
            if consumer.actor_state.hunger_state == "fainting":
                self.engine.message_log.add_message(
                    f"당신은 아직 배고픔에 허덕이고 있다...",
                    color.player_damaged,
                )
            elif consumer.actor_state.hunger_state == "starving":
                self.engine.message_log.add_message(
                    f"당신은 아직 굶주리고 있다...",
                    color.player_damaged,
                )
            elif consumer.actor_state.hunger_state == "hungry":
                self.engine.message_log.add_message(
                    f"당신은 아직 배고프다.",
                    color.gray,
                )
            elif consumer.actor_state.hunger_state == "":
                self.engine.message_log.add_message(
                    f"당신은 배가 고프지 않다.",
                    color.gray,
                )
            elif consumer.actor_state.hunger_state == "satiated":
                self.engine.message_log.add_message(
                    f"당신은 배가 부르다.",
                    color.gray,
                )
            elif consumer.actor_state.hunger_state == "overeaten":
                self.engine.message_log.add_message(
                    f"당신은 끔찍할 정도로 배가 부르다.",
                    color.player_damaged,
                )
        else:
            self.engine.message_log.add_message(
                f"{g(action.entity.name, '이')} {g(self.parent.name, '을')} 먹었다.",
                fg=color.gray,
                target=action.entity,
            )

    def effect_cooked(self, action: actions.EatItem):
        pass

    def effect_uncooked(self, action: actions.EatItem):
        pass

    def effect_always(self, action: actions.EatItem):
        pass

    def apply_effect(self, action: actions.EatItem):
        if self.is_cooked:
            self.effect_cooked(action)
        else:
            self.effect_uncooked(action)
        self.effect_always(action)

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        # fully identify used instance, and semi-identify the same item types.
        self.parent.item_state.identify_self(identify_level=2)
        self.parent.remove_self()

    def activate(self, action: actions.EatItem) -> None:
        """
        Invoke this items ability when eaten.
        `action` is the context for this activation.
        """
        self.gain_nutrition(action=action)
        self.apply_effect(action=action)
        self.consume()


class RawMeatEdible(Edible):
    """
    Provides no special effects.
    The meat is uncooked, and can be cooked by fire.
    The consumer gains nutritions.
    Meat rots faster. (spoil_speed set to 3)
    """
    def __init__(self, nutrition: int, spoilage: int=0, is_cooked: bool=False, can_cook: bool=True, spoil_speed: int=3, cook_bonus:int = None):
        super().__init__(nutrition,spoilage,is_cooked,can_cook,spoil_speed,cook_bonus)




####################################################
###################### a - ants  ###################
####################################################

class FireAntEdible(RawMeatEdible):
    def effect_uncooked(self, action: actions.EatItem):
        consumer = action.entity
        # Log
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신의 입 안에서 약간의 열기가 느껴진다.", color.white)
        return super().effect_cooked()


class VoltAntEdible(RawMeatEdible):
    def effect_uncooked(self, action: actions.EatItem):
        consumer = action.entity
        # Log
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신의 혓바닥이 따끔거린다.", color.white)
        return super().effect_cooked()


####################################################
################  e - eyes & brains  ###############
####################################################

class FloatingEyeEdible(Edible):
    def effect_always(self, action: actions.EatItem):
        consumer = action.entity

        # Log
        if not consumer.actor_state.has_telepathy:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"당신은 다른 생명체들과의 정신적 교감을 느꼈다.", color.status_effect_applied)
            consumer.actor_state.has_telepathy = True
        return super().effect_always(action)


####################################################
############### i = flying insects  ################
####################################################

class GiantWaspEdible(Edible):
    def effect_uncooked(self, action: actions.EatItem):
        consumer = action.entity

        # Log
        if not consumer.actor_state.has_telepathy:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"끔찍한 맛이 났다!", color.player_damaged)
            consumer.actor_state.is_poisoned = [1, 0, 0, 8]
        return super().effect_always(action)
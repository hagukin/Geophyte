from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING, Tuple
from components.base_component import BaseComponent
from korean import grammar as g

import actions
import color

if TYPE_CHECKING:
    from entity import Actor, Item

class Edible(BaseComponent):
    parent: Item
    def __init__(self,
                 nutrition: int,
                 spoilage: int=0,
                 is_cooked: bool=False,
                 can_cook: bool=False,
                 spoil_speed:int=1,
                 cook_bonus: int = 0,
                 edible_type: str = "food",
                 maggot_chance: float=0,
                 maggot_range: Tuple[int,int]=(1,3)):
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
            edible_type:
                Used for determining whether the ai likes certain food or not
                Reference:
                    food (e.g. Every ai who are willing to eat something will gladly eat "food" typed item.)
                    meat
                    insect
                    fruit
                    vegetable
                    snack (e.g. candy bar)
                    misc (e.g. jelly corpse)
        """
        super().__init__()
        self._nutrition = nutrition
        self.cook_bonus= cook_bonus
        self.spoil_speed = spoil_speed
        self.can_cook = can_cook
        self.edible_type = edible_type # String

        # Values that need manual copying when copying the component
        self.time_after_spawned = 0 # passed time after the food(or the corpse) was generated on the dungeon. (NOTE: This DOES NOT indicate the turn passed. This is a relative value.)
        self.is_cooked = is_cooked
        self.spoilage = spoilage

        # maggot related
        self.maggot_chance = maggot_chance
        self.maggot_range = maggot_range

    @property
    def nutrition(self):
        if self.spoilage > 1:
            return int(self._nutrition / self.spoilage)
        else:
            return self._nutrition

    @property
    def owner(self) -> Optional[Actor]:
        if self.parent.parent != None:
            if self.parent.parent.parent != None:
                return self.parent.parent.parent
        return None

    def rot(self) -> None:
        if self.parent.stack_count > 0:  # e.g. black jelly's toxic goo
            if self.parent.parent != None:
                if self.parent.parent.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 썩어 사라졌다!",
                                                        color.player_not_good, )
            else:
                if self.engine.game_map.visible[self.parent.x, self.parent.y]:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 썩어 사라졌다.", color.enemy_neutral,
                                                        target=self.parent)
            self.parent.remove_self()

    def spawn_maggots(self) -> None:
        if random.random() <= self.maggot_chance:
            maggot_num = random.randint(self.maggot_range[0], self.maggot_range[1])
            from util import spawn_entity_8way
            from actor_factories import maggot

            if self.parent.parent == None: # Is not owned by any InventoryComponent
                x, y = self.parent.x, self.parent.y
            else:
                x, y = self.owner.x, self.owner.y
            spawn_entity_8way(entity=maggot, gamemap=self.engine.game_map, center_x=x, center_y=y, spawn_cnt=maggot_num)

            # Log
            if self.parent.parent and self.owner == self.engine.player:
                self.engine.message_log.add_message(text=f"당신의 {self.parent.name} 주변에 구더기가 생겨났다!", fg=color.player_not_good)
            else:
                self.engine.message_log.add_message(text=f"{self.parent.name} 주변에 구더기가 생겨났다!", target=self.parent, fg=color.enemy_unique)

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
            self.spoilage = min(self.spoilage + 1, 4)
            self.time_after_spawned = 0
            if self.spoilage == 3: # spawn maggots when rotten
                if self.parent.parent and self.parent.parent.parent == self.engine.player:
                    self.engine.message_log.add_message(text=f"{g(self.parent.name, '이')} 부패하기 시작한다!", fg=color.purple)
                self.spawn_maggots()

        # foods will rot away if its too rotten
        if self.spoilage > 3:
            self.rot()

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
        consumer.actor_state.gain_nutrition(nutrition_gained)

        #TODO: Add food poison, over eating debuffs

        # Log
        if consumer == self.engine.player:
            if self.spoilage <= 0: # Fresh
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 굉장히 맛있었다!",
                    color.player_buff,
                )
            elif self.spoilage == 1: # Normal
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 나쁘지 않았다.",
                    color.player_neutral,
                )
            elif self.spoilage == 2: # Bad
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 맛이 좋지 않았다.",
                    color.player_not_good,
                )
            elif self.spoilage >= 3: # rotten
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 맛이 끔찍했다!",
                    color.player_bad,
                )

            # Log - status
            if consumer.actor_state.hunger_state == "fainting":
                self.engine.message_log.add_message(
                    f"당신은 아직 배고픔에 허덕이고 있다...",
                    color.player_severe,
                )
            elif consumer.actor_state.hunger_state == "starving":
                self.engine.message_log.add_message(
                    f"당신은 아직 굶주리고 있다...",
                    color.player_bad,
                )
            elif consumer.actor_state.hunger_state == "hungry":
                self.engine.message_log.add_message(
                    f"당신은 아직 배고프다.",
                    color.player_not_good,
                )
            elif consumer.actor_state.hunger_state == "satiated":
                self.engine.message_log.add_message(
                    f"당신은 배가 부르다.",
                    color.player_neutral,
                )
            elif consumer.actor_state.hunger_state == "overeaten":
                self.engine.message_log.add_message(
                    f"당신은 끔찍할 정도로 배가 부르다.",
                    color.player_bad,
                )
        else:
            self.engine.message_log.add_message(
                f"{g(action.entity.name, '이')} {g(self.parent.name, '을')} 먹었다.",
                fg=color.enemy_unique,
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
    def __init__(self, nutrition: int, spoilage: int=0, is_cooked: bool=False, can_cook: bool=True, spoil_speed: int=3, cook_bonus:int = None, edible_type:str = "meat",
                 maggot_chance: float=0.2, maggot_range: Tuple[int,int]=(1,1)):
        super().__init__(nutrition,spoilage,is_cooked,can_cook,spoil_speed,cook_bonus,edible_type,maggot_chance,maggot_range)
        self.maggot_range = (1, max(8, min(int(self.nutrition / 100), 1))) # Number of maggots spawned increase by nutrition value

class InsectEdible(Edible):
    """
    Provides no special effects.
    """
    def __init__(self, nutrition: int, spoilage: int=0, is_cooked: bool=False, can_cook: bool=True, spoil_speed: int=2, cook_bonus:int = None, edible_type:str = "insect",
                 maggot_chance: float=0, maggot_range: Tuple[int,int]=(0,0)):
        super().__init__(nutrition,spoilage,is_cooked,can_cook,spoil_speed,cook_bonus,edible_type,maggot_chance,maggot_range)


####################################################
###################### a - ants  ###################
####################################################

class FireAntEdible(InsectEdible):
    def effect_uncooked(self, action: actions.EatItem):
        consumer = action.entity
        # Log
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신의 입 안에서 약간의 열기가 느껴진다.", color.player_neutral)
        return super().effect_cooked(action)


class VoltAntEdible(InsectEdible):
    def effect_uncooked(self, action: actions.EatItem):
        consumer = action.entity
        # Log
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신의 혓바닥이 따끔거린다.", color.player_neutral)
        return super().effect_cooked(action)


####################################################
###################### d - dogs  ###################
####################################################

class CerberusEdible(RawMeatEdible):
    def effect_always(self, action: actions.EatItem):
        consumer = action.entity
        # Log
        if consumer.status.origin_status["fire_resistance"] < 0.2 and random.random() <= 0.5: # 50% chance resistance gain
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"전신에서 열기가 느껴진다.", color.player_neutral)
                self.engine.message_log.add_message(f"열기에 조금 더 잘 버틸 수 있을 것 같은 기분이 든다.", color.player_buff)
            consumer.status.fire_resistance += round(random.random() * 0.2, 2)
        return super().effect_always(action)



####################################################
################  e - eyes & brains  ###############
####################################################

class FloatingEyeEdible(RawMeatEdible):
    def effect_always(self, action: actions.EatItem):
        consumer = action.entity

        # Log
        if not consumer.actor_state.has_telepathy:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"당신은 다른 생명체들과의 정신적 교감을 느꼈다.", color.player_buff)
            consumer.actor_state.has_telepathy = True
        return super().effect_always(action)


####################################################
############### i = flying insects  ################
####################################################

class GiantWaspEdible(InsectEdible):    
    def effect_uncooked(self, action: actions.EatItem):
        consumer = action.entity

        # Log
        if not consumer.actor_state.has_telepathy:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"입 안에 아무런 감각이 없다!", color.player_bad)
            consumer.actor_state.apply_poisoning([2, 0, 0, 13])
        return super().effect_always(action)



####################################################
############### j - jellies / slimes  ##############
####################################################

class BlackJellyEdible(Edible):
    def __init__(self, nutrition: int = 15, spoilage: int=0, is_cooked: bool=False, can_cook: bool=False, spoil_speed: int=20, cook_bonus:int = None, edible_type="misc"):
        super().__init__(nutrition,spoilage,is_cooked,can_cook,spoil_speed,cook_bonus,edible_type)

    def effect_uncooked(self, action: actions.EatItem):
        consumer = action.entity

        # Log
        if not consumer.actor_state.has_telepathy:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"혀에서 엄청난 고통이 느껴진다!", color.player_bad)
            consumer.actor_state.apply_poisoning([8, 2, 0, 3])
        return super().effect_always(action)
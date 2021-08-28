from __future__ import annotations

import copy
import random
from typing import Optional, TYPE_CHECKING, Tuple
from tiles import TileUtil

import actions
import color
from components.base_component import BaseComponent
from korean import grammar as g

if TYPE_CHECKING:
    from entity import Actor, Item

class Quaffable(BaseComponent):
    def __init__(self):
        super().__init__(None)

    @property
    def owner(self) -> Actor:
        return self.parent.parent.parent

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.QuaffItem(consumer, self.parent)

    def apply_effect(self, apply_to: Actor) -> None:
        """Effect applied if the target quaffed this item.
        This function can be called from Throwable to handle effects during collision."""
        pass

    def activate(self, action: actions.QuaffItem) -> None:
        """
        Invoke this items ability and consume it.
        `action` is the context for this activation.
        """
        self.apply_effect(apply_to=action.entity)
        self.consume()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        # fully identify used instance, and semi-identify the same item types.
        if self.owner == self.engine.player:
            self.parent.item_state.identify_self(identify_level=1)
        self.parent.parent.decrease_item_stack(self.parent, remove_count=1)


class PotionOfHealingQuaffable(Quaffable):
    def __init__(self, heal_range: Tuple[int,int]):
        super().__init__()
        self.amount = random.randint(*heal_range)

    def apply_effect(self, apply_to: Actor) -> None:
        amount = self.amount
        if self.parent.item_state.BUC == 1:
            amount *= 1.3
        elif self.parent.item_state.BUC == -1:
            amount *= 0.8
        amount = round(amount)

        amount_recovered = apply_to.status.heal(amount)

        if amount_recovered > 0:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신의 상처가 낫기 시작한다!",color.player_buff,)
                self.engine.message_log.add_message(f"당신은 {amount_recovered}만큼의 체력을 회복했다.", color.player_neutral_important, )
            else:
                if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                    self.engine.message_log.add_message(f"{apply_to.name}의 상처가 낫기 시작한다!", color.player_sense, target=apply_to)
                    self.parent.item_state.identify_self(identify_level=1)
        else:# Gain additional health when quaffed while full-health
            amount = max(1, round(amount / 8))
            apply_to.status.max_hp += amount
            apply_to.status.heal(amount=amount)

            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신의 몸에 에너지가 넘친다!",color.player_buff,)
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신의 최대 체력이 {amount}만큼 증가했다.", color.player_neutral_important, )

        if apply_to.status.experience:
            apply_to.status.experience.gain_constitution_exp(60, 17)


class PotionOfParalysisQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        temp = copy.copy(apply_to.actor_state.is_paralyzing)
        turn = self.turn
        if self.parent.item_state.BUC == 1:
            turn *= 2
        apply_to.actor_state.apply_paralyzation([0,turn])

        # Log
        if temp == [0, 0]:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신은 갑자기 몸이 뻣뻣해지는 것을 느꼈다!", color.player_debuff, )
            else:
                if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                    self.engine.message_log.add_message(f"{g(apply_to.name, '이')} 갑자기 모든 움직임을 멈추었다.", color.player_sense,
                                                        target=apply_to)
                    self.parent.item_state.identify_self(identify_level=1)
        else:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신의 몸이 더 뻣뻣해졌다!", color.player_bad, )


class PotionOfSleepQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        temp = copy.copy(apply_to.actor_state.is_sleeping)
        turn = self.turn
        if self.parent.item_state.BUC == 1:
            turn *= 2
        apply_to.actor_state.apply_sleeping([0,turn], forced=False)

        # Log
        if temp == [0, 0]:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신은 급격한 나른함을 느낀다!", color.player_debuff, )
            else:
                if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                    self.engine.message_log.add_message(f"{g(apply_to.name, '이')} 잠을 자기 시작한다.", color.player_sense,
                                                        target=apply_to)
                    self.parent.item_state.identify_self(identify_level=1)
        else:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신은 보다 깊은 잠에 빠져든다.", color.player_bad, )


class PotionOfMonsterDetectionQuaffable(Quaffable):
    """The actor will gain a temporary ability to see far away actors that are on this level."""
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn
    
    def apply_effect(self, apply_to: Actor) -> None:
        turn = self.turn
        if self.parent.item_state.BUC == 1:
            turn *= 2
        apply_to.actor_state.apply_object_detection([0,turn,["actor"]])
        
        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 다른 생명체들의 존재를 감지하기 시작했다.", color.player_buff,)
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{g(apply_to.name, '는')} 무언가를 눈치챈 듯 하다.", color.player_sense, target=apply_to)

        if apply_to.status.experience:
            apply_to.status.experience.gain_intelligence_exp(20, 17)


class PotionOfFlameQuaffable(Quaffable):
    """Spawn a flame entity onto its location. (quaff/thrown)"""
    def __init__(self, base_dmg, add_dmg, turn: int, fire_lifetime):
        super().__init__()
        self.base_dmg = base_dmg
        self.add_dmg = add_dmg
        self.turn = turn
        self.fire_lifetime = fire_lifetime

    def apply_effect(self, apply_to: Actor) -> None:
        turn = self.turn
        if self.parent.item_state.BUC == 1:
            turn *= 2
        apply_to.actor_state.apply_burning([
            self.base_dmg,
            self.add_dmg,
            0,
            turn])

        # Spawn fire
        import semiactor_factories
        tmp = semiactor_factories.fire.copy(apply_to.gamemap, exact_copy=False, lifetime=self.fire_lifetime)
        tmp.rule.base_damage = int(self.base_dmg / 2)
        tmp.rule.add_damage = int(self.add_dmg / 2)
        tmp.spawn(apply_to.gamemap, apply_to.x, apply_to.y, self.fire_lifetime)

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신의 몸에서 강렬한 열기가 느껴진다!", color.player_debuff, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{apply_to.name}에게서 불꽃이 피어오르기 시작한다.", color.player_sense, target=apply_to)
                self.parent.item_state.identify_self(identify_level=1)


class PotionOfAcidQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        initial_dmg = max(8, min(13, int(apply_to.status.changed_status["max_hp"] / 10)))
        if self.parent.item_state.BUC == 1:
            initial_dmg = round(initial_dmg * 1.3)
        elif self.parent.item_state.BUC == -1:
            initial_dmg = round(initial_dmg * 0.8)

        apply_to.actor_state.apply_melting([
            initial_dmg,
            1,
            0,
            self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신의 몸이 조금씩 흘러내리기 시작한다.", color.player_debuff, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{apply_to.name}에게서 시큼한 냄새가 나기 시작한다.", color.player_sense, target=apply_to)
                self.parent.item_state.identify_self(identify_level=1)


class PotionOfFrostQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        dmg_per_turn = max(1, min(10, 1+int(apply_to.status.changed_status["max_hp"] / 150)))
        agility_decrease = max(int(apply_to.status.changed_status["agility"] / 10), int(apply_to.status.changed_status["agility"] / 5))
        frozen_chance = random.randint(1,3) * 0.1
        if self.parent.item_state.BUC == 1:
            frozen_chance += 0.7
        elif self.parent.item_state.BUC == -1:
            frozen_chance -= 0.2

        apply_to.actor_state.apply_freezing([
            dmg_per_turn,
            agility_decrease,
            frozen_chance,
            0,
            self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"차가운 냉기가 당신의 뼈를 타고 전해진다.", color.player_debuff, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{apply_to.name}의 움직임이 점점 둔해진다.", color.player_sense, target=apply_to)
                self.parent.item_state.identify_self(identify_level=1)


class PotionOfPoisonQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        init_dmg = max(10, min(20, int(apply_to.status.changed_status["max_hp"] / 5)))
        dmg_increase = int(init_dmg/self.turn/4)
        if self.parent.item_state.BUC == 1:
            dmg_increase = round(dmg_increase * 1.3)
        apply_to.actor_state.apply_poisoning([
            init_dmg,
            dmg_increase,
            0,
            self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 전신의 핏줄이 요동치는 듯한 느낌을 받았다.", color.player_debuff, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{g(apply_to.name, '이')} 고통 속에 몸부림친다.", color.player_sense, target=apply_to)


class PotionOfLevitationQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        turn = self.turn
        if self.parent.item_state.BUC == 1:
            turn *= 2
        apply_to.actor_state.apply_levitation([0,turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 몸이 붕 뜨는 듯한 느낌을 받았다.", color.player_damaged, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                if not apply_to.is_on_air:
                    self.engine.message_log.add_message(f"{g(apply_to.name, '이')} 돌연 공중에 떠오르기 시작한다.", color.player_sense, target=apply_to)
                    self.parent.item_state.identify_self(identify_level=1)


class PotionOfLiquifiedAntsQuaffable(Quaffable):
    """Apply bleed damage and surround consumer with insect type enemies."""
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        dmg = random.randint(2,8)
        apply_to.actor_state.apply_bleeding([
            dmg,
            0,
            self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 몸 속을 무언가가 기어다니는 듯한 느낌을 받았다.", color.player_damaged, )

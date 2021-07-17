from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING

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
        self.parent.item_state.identify_self(identify_level=2)
        self.parent.parent.remove_item(self.parent, remove_count=1)


class PotionOfHealingQuaffable(Quaffable):
    def __init__(self, amount: int):
        super().__init__()
        self.amount = amount

    def apply_effect(self, apply_to: Actor) -> None:
        amount_recovered = apply_to.status.heal(self.amount)

        if amount_recovered > 0:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신의 몸에 에너지가 넘친다!",color.health_recovered,)
            else:
                if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                    self.engine.message_log.add_message(f"{apply_to.name}의 상처가 낫기 시작한다!", color.white, target=apply_to)
        else:# Gain additional health when quaffed while full-health
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신의 몸에 에너지가 넘친다!",color.health_recovered,)

            amount = max(1, round(self.amount / 10))#TODO balance
            apply_to.status.max_hp += amount
            apply_to.status.heal(amount=amount)


class PotionOfParalysisQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        apply_to.actor_state.apply_paralyzation([0,self.turn])

        # Log
        if apply_to.actor_state.is_paralyzing == [0, 0]:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신은 갑자기 몸이 뻣뻣해지는 것을 느꼈다!", color.player_damaged, )
            else:
                if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                    self.engine.message_log.add_message(f"{g(apply_to.name, '이')} 갑자기 모든 움직임을 멈추었다.", color.white,
                                                        target=apply_to)
        else:
            if apply_to == self.engine.player:
                self.engine.message_log.add_message(f"당신의 몸이 더 뻣뻣해졌다!", color.player_damaged, )


class PotionOfMonsterDetectionQuaffable(Quaffable):
    """The actor will gain a temporary ability to see far away actors that are on this level."""
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn
    
    def apply_effect(self, apply_to: Actor) -> None:
        apply_to.actor_state.apply_object_detection([0,self.turn,["actor"]])
        
        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 다른 생명체들의 존재를 감지하기 시작했다.", color.player_damaged,)
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{g(apply_to.name, '는')} 무언가를 눈치챈 듯 하다.", color.white, target=apply_to)


class PotionOfFlameQuaffable(Quaffable):
    """Spawn a flame entity onto its location. (quaff/thrown)"""
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        initial_dmg = random.randint(1, 1+int(apply_to.status.changed_status["max_hp"]/20))
        apply_to.actor_state.apply_burning([
            initial_dmg,
            random.randint(1,1+int(initial_dmg/self.turn)),
            0,
            self.turn])
        # Spawn fire
        import semiactor_factories
        semiactor_factories.fire.spawn(apply_to.gamemap, apply_to.x, apply_to.y, 6)

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신의 몸에서 강렬한 열기가 느껴진다!", color.player_damaged, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{apply_to.name}에게서 연기가 피어오르기 시작한다.", color.white, target=apply_to)


class PotionOfAcidQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        initial_dmg = random.randint(1, 1+int(apply_to.status.changed_status["max_hp"] / 40))
        apply_to.actor_state.apply_melting([
            initial_dmg,
            int(initial_dmg / self.turn),
            0,
            self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신의 몸이 조금씩 흘러내리기 시작한다.", color.player_damaged, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{apply_to.name}에게서 시큼한 냄새가 나기 시작한다.", color.white, target=apply_to)


class PotionOfFrostQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        dmg_per_turn = max(1, 1+int(apply_to.status.changed_status["max_hp"] / 150))
        agility_decrease = max(int(apply_to.status.changed_status["agility"] / 10), int(apply_to.status.changed_status["agility"] / 5))
        frozen_chance = random.randint(1,3) * 0.1
        apply_to.actor_state.apply_freezing([
            dmg_per_turn,
            agility_decrease,
            frozen_chance,
            0,
            self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"차가운 냉기가 당신의 뼈를 타고 전해진다.", color.player_damaged, )
        else:
            if self.engine.game_map.visible[apply_to.x, apply_to.y]:
                self.engine.message_log.add_message(f"{apply_to.name}의 움직임이 점점 둔해진다.", color.white, target=apply_to)


class PotionOfPoisonQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        init_dmg = max(1, int(apply_to.status.changed_status["max_hp"] / 200))
        dmg_increase = int(init_dmg/self.turn)
        apply_to.actor_state.apply_poisoning([
            init_dmg,
            dmg_increase,
            0,
            self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 전신의 핏줄이 요동치는 듯한 느낌을 받았다.", color.player_damaged, )


class PotionOfLevitationQuaffable(Quaffable):
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        apply_to.actor_state.apply_levitation([0,self.turn])

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 몸이 붕 뜨는 듯한 느낌을 받았다.", color.player_damaged, )


class PotionOfLiquifiedAntsQuaffable(Quaffable):
    """Apply bleed damage and surround consumer with insect type enemies."""
    def __init__(self, turn: int):
        super().__init__()
        self.turn = turn

    def apply_effect(self, apply_to: Actor) -> None:
        dmg = 8
        apply_to.actor_state.apply_bleeding([
            dmg,
            0,
            self.turn])

        # Spawn 8 ants maximum surrounding the consumer.
        from actor_factories import ant
        for dx in (1, 0, -1):
            for dy in (1, 0, -1):
                if apply_to.gamemap.check_tile_monster_spawnable(apply_to.x + dx, apply_to.y + dy):
                    ant.spawn(apply_to.gamemap, apply_to.x + dx, apply_to.y + dy, is_active=True)

        # Log
        if apply_to == self.engine.player:
            self.engine.message_log.add_message(f"당신은 몸 속을 무언가가 기어다니는 듯한 느낌을 받았다.", color.player_damaged, )
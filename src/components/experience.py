from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from math import inf
from korean import grammar as g

import random
import color

if TYPE_CHECKING:
    from components.status import Status


class Experience(BaseComponent):
    """
    Component that handles overall experience of certain actor.
    Regular monsters will probably not own this component.
    
    Each parts of the status will have its own experience points, and they will "level up" seperately.
    """
    def __init__(
        self,
        hp_exp: float=0,
        mp_exp: float=0,
        strength_exp: float=0,
        dexterity_exp: float=0,
        constitution_exp: float=0,
        agility_exp: float=0,
        intelligence_exp: float=0,
        charm_exp: float=0,
    ):
        self.parent: Status = None
        self.hp_exp = hp_exp
        self.mp_exp = mp_exp
        self.strength_exp = strength_exp
        self.dexterity_exp = dexterity_exp
        self.constitution_exp = constitution_exp
        self.agility_exp = agility_exp
        self.intelligence_exp = intelligence_exp
        self.charm_exp = charm_exp

    def lvl_up_msg(self, level_type: str) -> None:
        """
        Determine whether the game should notify the player about this level change.
        Only display log when the actor is player or player's pet.
        """
        flag = False
        if self.parent.parent == self.parent.engine.player:
            flag = True
            msg_color = color.player_lvl_up
        elif self.parent.parent.ai:
            if self.parent.parent.ai.owner == self.parent.engine.player:
                flag = True
                msg_color = color.pet_lvl_up
        
        if not flag:
            return None

        if level_type == "hp":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 강인해졌다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 최대 체력이 상승했습니다.", msg_color)
        elif level_type == "mp":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 많은 에너지를 내재할 수 있게 되었다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 최대 마나가 상승했습니다.", msg_color)
        elif level_type == "strength":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 강해졌다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 힘 수치가 상승했습니다.", msg_color)
        elif level_type == "dexterity":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 능숙하게 물건을 다룰 수 있게 되었다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 손재주 수치가 상승했습니다.", msg_color)
        elif level_type == "constitution":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 활력이 넘치게 되었다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 활력 수치가 상승했습니다.", msg_color)
        elif level_type == "agility":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 민첩해졌다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 민첩 수치가 상승했습니다.", msg_color)
        elif level_type == "intelligence":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 깊게 생각할 수 있게 되었다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 지능 수치가 상승했습니다.", msg_color)
        elif level_type == "charm":
            self.parent.engine.message_log.add_message(f"{g(self.parent.parent.name, '이')} 더 매력적인 모습이 되었다!", msg_color)
            self.parent.engine.message_log.add_message(f"{self.parent.parent.name}의 매력 수치가 상승했습니다.", msg_color)

    def level_up(self) -> bool:
        """Check if certain status has enough exp to "level up", and if it has, increase the status points."""

        #TODO: Need to make adjustments for game balance

        while True:
            if self.hp_exp >= self.parent.max_hp**2:
                self.parent.max_hp += 10
                self.lvl_up_msg("hp")
                continue

            if self.mp_exp >= self.parent.max_mp**2:
                self.parent.max_mp += 10
                self.lvl_up_msg("mp")
                continue

            if self.strength_exp >= self.parent.strength**2 * 8:
                self.parent.gain_strength(1)
                self.lvl_up_msg("strength")
                continue

            if self.dexterity_exp >= self.parent.dexterity**2 * 8:
                self.parent.gain_dexterity(1)
                self.lvl_up_msg("dexterity")
                continue

            if self.constitution_exp >= self.parent.constitution**2 * 8:
                self.parent.gain_constitution(1)
                self.lvl_up_msg("constitution")
                continue

            if self.agility_exp >= self.parent.agility**2 * 8:
                self.parent.gain_agility(1)
                self.lvl_up_msg("agility")
                continue

            if self.intelligence_exp >= self.parent.intelligence**2 * 8:
                self.parent.gain_intelligence(1)
                self.lvl_up_msg("intelligence")
                continue

            if self.charm_exp >= self.parent.charm**2 * 8:
                self.parent.gain_charm(1)
                self.lvl_up_msg("charm")
                continue
        
            # break the loop when there are no more status that can be level up-ed.
            break
    
    def gain_strength_exp(self, amount, str_limit=inf, exp_limit=inf, chance:float = 1) -> None:
        """
        NOTE: exp gain of the 6 basic status will also effect hp status and mp status.
        There are no direct way of increasing hp/mp for now.

        Args:
            str_limit:
                If the actor's strength is above the limit, actor cannot gain any experience.
            exp_limit:
                If the actor's experience is above the limit, actor cannot gain any experience.
            chance:
                chance of getting an experiecne point

        hp exp amp. x2
        mp exp amp. x0.5
        """
        if random.random() > chance:
            return

        if self.parent.strength > str_limit or self.strength_exp > exp_limit:
            return

        self.strength_exp += amount
        self.hp_exp += int(amount * 2)
        self.mp_exp += int(amount * 0.5)
        self.level_up()
    
    def gain_dexterity_exp(self, amount, dex_limit=inf, exp_limit=inf, chance:float = 1) -> None:
        """
        hp exp amp. x1
        mp exp amp. x1
        """
        if random.random() > chance:
            return

        if self.parent.dexterity > dex_limit or self.dexterity_exp > exp_limit:
            return

        self.dexterity_exp += amount
        self.hp_exp += int(amount * 1)
        self.mp_exp += int(amount * 1)
        self.level_up()

    def gain_constitution_exp(self, amount, con_limit=inf, exp_limit=inf, chance: float = 1) -> None:
        """
        hp exp amp. x1
        mp exp amp. x1.5
        """
        if random.random() > chance:
            return

        if self.parent.constitution > con_limit or self.constitution_exp > exp_limit:
            return

        self.constitution_exp += amount
        self.hp_exp += int(amount * 1)
        self.mp_exp += int(amount * 1.5)
        self.level_up()

    def gain_agility_exp(self, amount, agi_limit=inf, exp_limit=inf, chance: float = 1) -> None:
        """
        hp exp amp. x1
        mp exp amp. x1
        """
        if random.random() > chance:
            return

        if self.parent.agility > agi_limit or self.agility_exp > exp_limit:
            return

        self.agility_exp += amount
        self.hp_exp += int(amount * 1)
        self.mp_exp += int(amount * 1)
        self.level_up()

    def gain_intelligence_exp(self, amount, int_limit=inf, exp_limit=inf, chance: float = 1) -> None:
        """
        hp exp amp. x0.5
        mp exp amp. x2.5
        """
        if random.random() > chance:
            return

        if self.parent.intelligence > int_limit or self.intelligence_exp > exp_limit:
            return
    
        self.intelligence_exp += amount
        self.hp_exp += int(amount * 0.5)
        self.mp_exp += int(amount * 2.5)
        self.level_up()

    def gain_charm_exp(self, amount, char_limit=inf, exp_limit=inf, chance: float = 1) -> None:
        """
        hp exp amp. x0.5
        mp exp amp. x0.5
        """
        if random.random() > chance:
            return

        if self.parent.charm > char_limit or self.charm_exp > exp_limit:
            return

        self.charm_exp += amount
        self.hp_exp += int(amount * 0.5)
        self.mp_exp += int(amount * 0.5)
        self.level_up()

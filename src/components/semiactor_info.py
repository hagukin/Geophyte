from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from components.base_component import BaseComponent
from korean import grammar as g
from language import interpret as i

import random
import color

if TYPE_CHECKING:
    pass

class SemiactorInfo(BaseComponent):
    """
    Equivalent to items' "ItemState" component.
    """
    def __init__(
        self,
        flammable: float,
        corrodable: float,
        was_burning: bool = False,
        is_burning: bool = False,
        burntness: int = 0,
        corrosion: int = 0,
    ):
        """
        Args:
            burntness:
                0 - Not burnt
                1 - partly burnt
                2 - severly burnt
                3 - burnt out (its gone)
            corrosion:
                0 - Not corroded
                1 - partly corroded
                2 - severly corroded
                3 - gone
        """
        super().__init__(None) #parent: SemiActor

        self.flammable = flammable
        self.corrodable = corrodable
        self.was_burning = was_burning
        self.is_burning = is_burning
        self.burntness = burntness
        self.corrosion = corrosion

    def burn(self):
        # Catch on fire log
        if self.was_burning == False:
            self.was_burning = True
            self.engine.message_log.add_message(i(f"{self.parent.name}에 불이 붙었다.",
                                                  f"{self.parent.name} catches fire."), fg=color.white, target=self.parent)

        # Further burning calculation
        will_burn = random.random()
        if will_burn < self.flammable:
            self.burntness += 1

        # if Burnt out
        if self.burntness == 3:
            # Delete item from the game
            self.parent.remove_self()
            self.engine.message_log.add_message(i(f"{g(self.parent.name, '이')} 완전히 연소했다!",
                                                  f"{self.parent.name} is burnt out!"), fg=color.red, target=self.parent)
            
            #Adjust variables
            self.is_burning = False
            self.was_burning = False

        # Extinguish Chance
        extinguish_chance = random.random()
        if extinguish_chance >= self.flammable:
            self.engine.message_log.add_message(i(f"{g(self.parent.name, '이')} 타는 것을 멈췄다.",
                                                  f"{self.parent.name} stops burning."), fg=color.gray, target=self.parent)
            self.is_burning = False
            self.was_burning = False

    def corrode(self, amount: int=1):
        if random.random() <= self.parent.corrodible:
            self.corrosion += amount
        else:
            return None

        if self.corrosion > 2:
            self.engine.message_log.add_message(i(f"{g(self.parent.name, '이')} 완전히 부식되어 사라졌다!",
                                                  f"{self.parent.name} corrodes away!"), fg=color.red, target=self.parent)
            # Completely corroded
            self.parent.remove_self()
        elif self.corrosion == 2:
            self.engine.message_log.add_message(i(f"{g(self.parent.name, '이')} 심하게 부식되었다.",
                                                  f"{self.parent.name} is severly corroded."), fg=color.white, target=self.parent)
        elif self.corrosion == 1:
            self.engine.message_log.add_message(i(f"{g(self.parent.name, '이')} 다소 부식되었다.",
                                                  f"{self.parent.name} is corroded."), fg=color.white, target=self.parent)

    def move_self_to(self, semiactor) -> None:
        """
        Copy self, and swap its parent to given semiactor.
        And set given semiactor's semiactor_info to this.

        NOTE: This feature is not meant to be used for copying semiactor_info.
        This function is mainly used when a certain semiactor has to change into other similar semiactor while remaining its semiactor_info.
        e.g. opening door: deletes closed_door entity, spawn opened_door entity, and transfer closed_door.semiactor_info to opened_door entity.
        """
        import copy
        tmp = copy.copy(self)
        tmp.parent = semiactor
        semiactor.semiactor_info = tmp

class Default(SemiactorInfo):
    """
    Dafault. The semiactor cannot be affected by any status effects.
    """
    def __init__(
        self,
        flammable: float = 0,
        corrodable: float = 0,
        was_burning: bool = False,
        is_burning: bool = False,
        burntness: int = 0,
        corrosion: int = 0,
    ):
        super().__init__(flammable, corrodable, was_burning, is_burning, burntness, corrosion)


class Door(SemiactorInfo):
    def __init__(
        self,
        flammable: float = 0.5,
        corrodable: float = 0.2,
        was_burning: bool = False,
        is_burning: bool = False,
        burntness: int = 0,
        corrosion: int = 0,
        break_str_req: Tuple[int,int] = (17,20),
        unlock_chance: float = 1
    ):
        """
        Args:
            unlock_chance:
                0~1.
                game will multiply this value to player's unlock chance.
                if the value is 0, the door cannot be unlocked.
        """
        super().__init__(flammable, corrodable, was_burning, is_burning, burntness, corrosion)
        self.break_str_req = break_str_req
        self.unlock_chance = unlock_chance


    def burn(self):
        super().burn()


class Chest(SemiactorInfo):
    def __init__(
        self,
        flammable: float = 0.1,
        corrodable: float = 0.01,
        was_burning: bool = False,
        is_burning: bool = False,
        burntness: int = 0,
        corrosion: int = 0,
    ):
        super().__init__(flammable, corrodable, was_burning, is_burning, burntness, corrosion)

    def burn(self):
        super().burn()
        if self.burntness == 3: # if burnt out, drop all items to the ground and light them
            if hasattr(self.parent, "storage"):
                for item in self.parent.storage.items:
                    self.parent.storage.drop(item=item)
                    item.collided_with_fire()
            else:
                print(f"ERROR: A NON-CHEST SEMIACTOR {self.parent.name} HAS CHEST SEMIACTION_INFO.")


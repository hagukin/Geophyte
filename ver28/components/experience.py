from typing import TYPE_CHECKING
from components.base_component import BaseComponent

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
        hp_exp=0,
        mp_exp=0,
        strength_exp=0,
        dexterity_exp=0,
        constitution_exp=0,
        agility_exp=0,
        intelligence_exp=0,
        charm_exp=0,
    ):
        self.parent = None
        self.hp_exp = hp_exp
        self.mp_exp = mp_exp
        self.strength_exp = strength_exp
        self.dexterity_exp = dexterity_exp
        self.constitution_exp = constitution_exp
        self.agility_exp = agility_exp
        self.intelligence_exp = intelligence_exp
        self.charm_exp = charm_exp

    def level_up(self) -> bool:
        """Check if certain status has enough exp to "level up", and if it has, increase the status points."""

        #TODO: Need to make adjustments for game balance

        while True:
            if self.hp_exp >= self.parent.max_hp * 10:
                self.hp_exp -= self.parent.max_hp * 10
                self.parent.max_hp += 10
                continue

            if self.mp_exp >= self.parent.max_mp * 10:
                self.mp_exp -= self.parent.max_mp * 10
                self.parent.max_mp += 10
                continue

            if self.strength_exp >= self.parent.strength * 10:
                self.strength_exp -= self.parent.strength * 10
                self.parent.gain_strength(1)
                continue

            if self.dexterity_exp >= self.parent.dexterity * 10:
                self.dexterity_exp -= self.parent.dexterity * 10
                self.parent.gain_dexterity(1)
                continue

            if self.constitution_exp >= self.parent.constitution * 10:
                self.constitution_exp -= self.parent.constitution * 10
                self.parent.gain_constitution(1)
                continue

            if self.agility_exp >= self.parent.agility * 10:
                self.agility_exp -= self.parent.agility * 10
                self.parent.gain_agility(1)
                continue

            if self.intelligence_exp >= self.parent.intelligence * 10:
                self.intelligence_exp -= self.parent.intelligence * 10
                self.parent.gain_intelligence(1)
                continue

            if self.charm_exp >= self.parent.charm * 10:
                self.charm_exp -= self.parent.charm * 10
                self.parent.gain_charm(1)
                continue
        
            # break the loop when there are no more status that can be level up-ed.
            break
    
    def gain_strength_exp(self, amount):
        """
        NOTE: exp gain of the 6 basic status will also effect hp status and mp status.
        There are no direct way of increasing hp/mp for now.
        hp exp amp. x2
        mp exp amp. x0.5
        """
        self.strength_exp += amount
        self.hp_exp += int(amount * 2)
        self.mp_exp += int(amount * 0.5)
        self.level_up()
    

    def gain_dexterity_exp(self, amount):
        """
        hp exp amp. x1
        mp exp amp. x1
        """
        self.dexterity_exp += amount
        self.hp_exp += int(amount * 1)
        self.mp_exp += int(amount * 1)
        self.level_up()


    def gain_constitution_exp(self, amount):
        """
        hp exp amp. x1
        mp exp amp. x1.5
        """
        self.constitution_exp += amount
        self.hp_exp += int(amount * 1)
        self.mp_exp += int(amount * 1.5)
        self.level_up()

    
    def gain_agility_exp(self, amount):
        """
        hp exp amp. x1
        mp exp amp. x1
        """
        self.agility_exp += amount
        self.hp_exp += int(amount * 1)
        self.mp_exp += int(amount * 1)
        self.level_up()

    
    def gain_intelligence_exp(self, amount):
        """
        hp exp amp. x0.5
        mp exp amp. x2.5
        """
        self.intelligence_exp += amount
        self.hp_exp += int(amount * 0.5)
        self.mp_exp += int(amount * 2.5)
        self.level_up()

    
    def gain_charm_exp(self, amount):
        """
        hp exp amp. x0.5
        mp exp amp. x0.5
        """
        self.charm_exp += amount
        self.hp_exp += int(amount * 0.5)
        self.mp_exp += int(amount * 0.5)
        self.level_up()

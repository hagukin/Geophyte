from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible

if TYPE_CHECKING:
    from entity import Actor, Item

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

class Equipable(BaseComponent):
    parent: Item

    def __init__(
        self,

        equip_region: str,
        upgrade: int = 0,
        str_requirement: int = 0,

        # Stats
        hp: int = 0,
        mp: int = 0,
        max_hp: int = 0,
        max_mp: int = 0,
        strength: int = 0,
        dexterity: int = 0,
        agility: int = 0,
        intelligence: int = 0,
        constitution: int = 0,
        charm: int = 0,

        # Melee Damages
        base_melee: int = 0,
        additional_melee: int = 0,

        # Protections
        protection: int = 0,

        # Eyesight
        eyesight: int = 0,

        # Resistances (0 ~ 1)
        fire_resistance: float = 0,
        poison_resistance: float = 0,
        cold_resistance: float = 0,
        acid_resistance: float = 0,
        psychic_resistance: float = 0,
        sleep_resistance: float = 0,
        shock_resistance: float = 0,
        magic_resistance: float = 0,
    ):
        """
        Args:
            equip_region:
                main equipping region for this component's parent.
                It is possible to equip items other than the given region, by passing region as a string to equipments.equip_equipments().
            str_requirement:
                recommended strength requirement to use this item efficiently.
                Each items can have different bonuses when the wielder's strength exceeded the requirement.
        """
        super().__init__()
        self.upgrade = upgrade # When copying a item, you must manually copy the upgrade value.
        self.equip_region = equip_region
        self.str_requirement = str_requirement
        
        # Default status of this item (no upgrades, no downgrades)
        self.eq_hp = hp
        self.eq_mp = mp
        self.eq_max_hp = max_hp
        self.eq_max_mp = max_mp
        self.eq_strength = strength
        self.eq_dexterity = dexterity
        self.eq_agility = agility
        self.eq_intelligence = intelligence
        self.eq_constitution = constitution
        self.eq_charm = charm
        self.eq_base_melee = base_melee
        self.eq_additional_melee = additional_melee
        self.eq_protection = protection
        self.eq_eyesight = eyesight
        self.eq_fire_resistance = fire_resistance
        self.eq_poison_resistance = poison_resistance
        self.eq_cold_resistance = cold_resistance
        self.eq_acid_resistance = acid_resistance
        self.eq_psychic_resistance = psychic_resistance
        self.eq_sleep_resistance = sleep_resistance
        self.eq_shock_resistance = shock_resistance
        self.eq_magic_resistance = magic_resistance

        # status bonus given when the item is upgraded (bonus are added to the stat each time)
        self.add_hp = 0
        self.add_mp = 0
        self.add_max_hp = 0
        self.add_max_mp = 0
        self.add_strength = 0
        self.add_dexterity = 0
        self.add_agility = 0
        self.add_intelligence = 0
        self.add_constitution = 0
        self.add_charm = 0
        self.add_base_melee = 0
        self.add_additional_melee = 0
        self.add_protection = 0
        self.add_eyesight = 0
        self.add_fire_resistance = 0
        self.add_poison_resistance = 0
        self.add_cold_resistance = 0
        self.add_acid_resistance = 0
        self.add_psychic_resistance = 0
        self.add_sleep_resistance = 0
        self.add_shock_resistance = 0
        self.add_magic_resistance = 0

        if upgrade > 0:
            self.upgrade_stat_change()

    @property
    def origin_status(self):
        """Status of the equipment's original bonus status."""
        origin_status = {
            "eq_max_hp":self.eq_max_hp,
            "eq_hp":self.eq_hp,
            "eq_max_mp":self.eq_max_mp,
            "eq_mp":self.eq_mp,
            "eq_strength":self.eq_strength,
            "eq_dexterity":self.eq_dexterity,
            "eq_agility":self.eq_agility,
            "eq_intelligence":self.eq_intelligence,
            "eq_constitution":self.eq_constitution,
            "eq_charm":self.eq_charm,
            "eq_base_melee":self.eq_base_melee,
            "eq_additional_melee":self.eq_additional_melee,
            "eq_protection":self.eq_protection,
            "eq_eyesight":self.eq_eyesight,
            "eq_fire_resistance":self.eq_fire_resistance,
            "eq_poison_resistance":self.eq_poison_resistance,
            "eq_cold_resistance":self.eq_cold_resistance,
            "eq_acid_resistance":self.eq_acid_resistance,
            "eq_psychic_resistance":self.eq_psychic_resistance,
            "eq_sleep_resistance":self.eq_sleep_resistance,
            "eq_shock_resistance":self.eq_shock_resistance,
            "eq_magic_resistance":self.eq_magic_resistance,
            }
        return origin_status

    @property
    def changed_status(self):
        """Status of the equipment's changed bonus status."""
        origin_status = {
            "eq_max_hp":max(0, self.eq_max_hp + self.add_max_hp),
            "eq_hp":max(0, self.eq_hp + self.add_hp),
            "eq_max_mp":max(0, self.eq_max_mp + self.add_max_mp),
            "eq_mp":max(0, self.eq_mp + self.add_mp),
            "eq_strength":max(0, self.eq_strength + self.add_strength),
            "eq_dexterity":max(0, self.eq_dexterity + self.add_dexterity),
            "eq_agility":max(0, self.eq_agility + self.add_agility),
            "eq_intelligence":max(0, self.eq_intelligence + self.add_intelligence),
            "eq_constitution":max(0, self.eq_constitution + self.add_constitution),
            "eq_charm":max(0, self.eq_charm + self.add_charm),
            "eq_base_melee":max(0, self.eq_base_melee + self.add_base_melee),
            "eq_additional_melee":max(0, self.eq_additional_melee + self.add_additional_melee),
            "eq_protection":max(0, self.eq_protection + self.add_protection),
            "eq_eyesight":max(0, self.eq_eyesight + self.add_eyesight),
            "eq_fire_resistance":clamp(self.eq_fire_resistance + self.add_fire_resistance, 0, 1),
            "eq_poison_resistance":clamp(self.eq_poison_resistance + self.add_poison_resistance, 0, 1),
            "eq_cold_resistance":clamp(self.eq_cold_resistance + self.add_cold_resistance, 0, 1),
            "eq_acid_resistance":clamp(self.eq_acid_resistance + self.add_acid_resistance, 0, 1),
            "eq_psychic_resistance":clamp(self.eq_psychic_resistance + self.add_psychic_resistance, 0, 1),
            "eq_sleep_resistance":clamp(self.eq_sleep_resistance + self.add_sleep_resistance, 0, 1),
            "eq_shock_resistance":clamp(self.eq_shock_resistance + self.add_shock_resistance, 0, 1),
            "eq_magic_resistance":clamp(self.eq_magic_resistance + self.add_magic_resistance, 0, 1),
            }
        return origin_status

    @property
    def owner(self) -> Actor:
        try:
            return self.parent.parent.parent # item >> inventory >> actor
        except:
            return None # Has no owner

    def upgrade_stat_change(self):
        """
        Actual increase/decrease of equipper's status are handled here.
        """
        raise NotImplementedError

    def upgrade_this(self, amount:int):
        """
        Upgrade this equipment.
        And refresh the equiper's status bonus values.
        """
        # temporary bonus removal
        self.owner.equipments.remove_equipable_bonuses(self.parent)

        # actual upgrading parts
        self.upgrade += amount
        self.upgrade_stat_change()

        # add bonuses
        self.owner.equipments.add_equipable_bonuses(self.parent)


#################################################
################### ARMORS ######################
#################################################

class LeatherArmorEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            equip_region="torso",
            str_requirement=10,
            protection=4,
            )

    def upgrade_stat_change(self):
        # upgrade bonus
        self.add_protection = self.upgrade * 2

        if self.owner:
            str_diff = self.str_requirement - self.owner.status.changed_status["strength"]
            # lacks strength
            if str_diff > 0:
                # reduce protection bonus
                self.add_protection -= str_diff


#################################################
################### WEAPONS #####################
#################################################

class ShortswordEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            equip_region="main hand",
            str_requirement=12,
            base_melee=6,
            additional_melee=3,
            )

    def upgrade_stat_change(self):
        # upgrade bonus
        self.add_base_melee = self.upgrade
        self.add_additional_melee = self.upgrade

        if self.owner:
            str_diff = self.str_requirement - self.owner.status.changed_status["strength"]
            # lacks strength
            if str_diff > 0:
                # reduce bonuses
                self.add_base_melee -= str_diff
                self.add_additional_melee -= str_diff
            # strength bonus
            elif str_diff < 3:
                self.add_base_melee += min(3, str_diff * (-1) - 2)
                self.add_additional_melee += min(3, str_diff * (-1) - 2)


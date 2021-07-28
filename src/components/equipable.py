from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Tuple

import actions
import color
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible

if TYPE_CHECKING:
    from entity import Actor, Item

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

class Equipable(BaseComponent):
    def __init__(
        self,
        possible_regions: Tuple[str, ...],
        equip_size: Tuple[int, int] = (3, 5),
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

        # Senses
        hearing: int = 0,
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
            possible_regions:
                main equipping region for this component's parent.
                It is possible to equip items other than the given region, by passing region as a string to equipments.equip_equipments().
            equip_size:
                range of actor's size who can equip this item.
                default set to 3~5
            str_requirement:
                recommended strength requirement to use this item efficiently.
                Each items can have different bonuses when the wielder's strength exceeded the requirement.
        """
        super().__init__()
        self.upgrade = upgrade # When copying a item, you must manually copy the upgrade value.
        self.possible_regions = possible_regions  # To get current equipped region, go item_state.equipped_region
        self.str_requirement = str_requirement
        self.equip_size = equip_size
        
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
        self.eq_hearing = hearing
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
        self.add_hearing = 0
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
            self.update_stat()

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
            "eq_hearing": self.eq_hearing,
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
            "eq_hearing": max(0, self.eq_hearing + self.add_hearing),
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

    def update_stat(self) -> None:
        """
        Actual increase/decrease of equipper's status are handled here.
        """
        return None

    def upgrade_this(self, amount:int):
        """
        Upgrade this equipment.
        And refresh the equiper's status bonus values.
        """
        # temporary bonus removal
        self.owner.equipments.remove_equipable_bonuses(self.parent)

        # actual upgrading parts
        self.upgrade += amount
        self.update_stat()

        # add bonuses
        self.owner.equipments.add_equipable_bonuses(self.parent)


#################################################
################### ARMORS ######################
#################################################

class LeatherArmorEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            possible_regions=("torso",),
            str_requirement=10,
            protection=5,
            )

    def update_stat(self):
        super().update_stat()
        self.add_protection = self.upgrade



#################################################
################ MELEE WEAPONS ##################
#################################################

################### BLADES ######################
class IronDaggerEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            possible_regions=("main hand", "off hand"),
            str_requirement=10,
            base_melee=6,
            additional_melee=5,
            )

    def update_stat(self):
        super().update_stat()
        self.add_base_melee = round(self.upgrade * 1.1)
        self.add_additional_melee = round(self.upgrade * 1.3)


class ShortswordEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            possible_regions=("main hand", "off hand"),
            str_requirement=13,
            base_melee=8,
            additional_melee=3,
            )

    def update_stat(self):
        super().update_stat()
        self.add_base_melee = self.upgrade
        self.add_additional_melee = round(self.upgrade * 1.3)


class LongswordEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            possible_regions=("main hand", "off hand"),
            str_requirement=15,
            base_melee=10,
            additional_melee=8,
            )

    def update_stat(self):
        super().update_stat()
        self.add_base_melee = round(self.upgrade * 1.3)
        self.add_additional_melee = round(self.upgrade * 1.3)


class GiantWoodClubEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            possible_regions=("main hand", "off hand"),
            equip_size=(5,6),
            str_requirement=15,
            base_melee=25,
            additional_melee=15,
            )

    def update_stat(self):
        super().update_stat()
        self.add_base_melee = round(self.upgrade * 1.3)
        self.add_additional_melee = round(self.upgrade * 1.3)



#################################################
################### AMULETS #####################
#################################################

class AmuletOfKugahEquipable(Equipable):
    def __init__(self, upgrade=0):
        super().__init__(
            upgrade=upgrade,
            possible_regions=("amulet",),
            )

    def update_stat(self):
        super().update_stat()
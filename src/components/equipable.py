from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING, Tuple, List
from order import EquipableOrder
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
        equipable_type:EquipableOrder = EquipableOrder.MISC,

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

        # Melee Effects
        melee_effects: Tuple[Tuple] = (),
        melee_effects_var: Tuple[Tuple] = (),


        # Magnifiers
        hp_mag: float = 0,
        mp_mag: float = 0,
        max_hp_mag: float = 0,
        max_mp_mag: float = 0,
        strength_mag: float = 0,
        dexterity_mag: float = 0,
        agility_mag: float = 0,
        intelligence_mag: float = 0,
        constitution_mag: float = 0,
        charm_mag: float = 0,

        # Melee Damages
        base_melee_mag: float = 0,
        additional_melee_mag: float = 0,

        # Protections
        protection_mag: float = 0,

        # Senses
        hearing_mag: float = 0,
        eyesight_mag: float = 0,

        # Resistances (0 ~ 1)
        fire_resistance_mag: float = 0,
        poison_resistance_mag: float = 0,
        cold_resistance_mag: float = 0,
        acid_resistance_mag: float = 0,
        psychic_resistance_mag: float = 0,
        sleep_resistance_mag: float = 0,
        shock_resistance_mag: float = 0,
        magic_resistance_mag: float = 0,

        # TODO: Melee Effects magnifier
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
            hp_mag, ...:
                magnifiers.
                is multiplied to status when upgraded.
        """
        super().__init__()
        self.equipable_type = equipable_type

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
        self.eq_melee_effects = list(melee_effects)
        self.eq_melee_effects_var = list(melee_effects_var)

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
        self.add_melee_effects = []
        self.add_melee_effects_var = []

        # Magnifiers
        self.hp_mag = hp_mag
        self.mp_mag = mp_mag
        self.max_hp_mag = max_hp_mag
        self.max_mp_mag = max_mp_mag
        self.strength_mag = strength_mag
        self.dexterity_mag = dexterity_mag
        self.agility_mag = agility_mag
        self.intelligence_mag = intelligence_mag
        self.constitution_mag = constitution_mag
        self.charm_mag = charm_mag
        self.base_melee_mag = base_melee_mag
        self.additional_melee_mag = additional_melee_mag
        self.protection_mag = protection_mag
        self.hearing_mag = hearing_mag
        self.eyesight_mag = eyesight_mag
        self.fire_resistance_mag = fire_resistance_mag
        self.poison_resistance_mag = poison_resistance_mag
        self.cold_resistance_mag = cold_resistance_mag
        self.acid_resistance_mag = acid_resistance_mag
        self.psychic_resistance_mag = psychic_resistance_mag
        self.sleep_resistance_mag = sleep_resistance_mag
        self.shock_resistance_mag = shock_resistance_mag
        self.magic_resistance_mag = magic_resistance_mag

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
            "eq_melee_effects":self.eq_melee_effects,
            "eq_melee_effects_var":self.eq_melee_effects_var,
            }
        return origin_status

    @property
    def changed_melee_effects_var(self) -> List:
        """
        e.g.
        eq_melee_effects_var = [(3,3,0,4), (2,2,0,5)]
        add_melee_effects_var = [(-1,1,0,0), None]

        ->
        changed = [(2,4,0,4), (2,2,0,5)]
        None - does nothing
        """
        if len(self.add_melee_effects_var) == 0:
            return self.eq_melee_effects_var # No add_melee_effects_var given

        changed = []
        if len(self.eq_melee_effects_var) != len(self.add_melee_effects_var):
            print("ERROR::Equipable - melee_effects_var differs in length")
            return self.eq_melee_effects_var

        for i in range(len(self.eq_melee_effects_var)):
            eq = self.eq_melee_effects_var[i]
            add = self.add_melee_effects_var[i]

            if add is None:
                changed.append(eq)
            else:
                if len(eq) != len(add):
                    print("ERROR::Equipable - values in melee_effects_var differs in length")
                    return self.eq_melee_effects_var
                else:
                    new = []
                    for j in range(len(eq)):
                        changed.append(eq[j] + add[j])
                    changed.append(tuple(new))
        return changed

    @property
    def changed_melee_effects(self):
        """
        e.g.
        eq_melee_effects = [("burn_target", 0.4), ("bleed_target", 0.4)]
        add_melee_effects = [("electrocute_target", 0.2), ("bleed_target", 0.1)]

        ->
        changed = [("electrocute_target", 0.2), ("bleed_target", 0.5)]
        NOTE: first value has been overwritten since they are completely different
        """
        if len(self.add_melee_effects) == 0:
            return self.eq_melee_effects # No add_melee_effects given

        changed = []
        if len(self.eq_melee_effects) != len(self.add_melee_effects):
            print(f"ERROR::Equipable - melee_effects differs in length - {self.eq_melee_effects}, {self.add_melee_effects}")
            return self.eq_melee_effects

        for i in range(len(self.eq_melee_effects)):
            eq = self.eq_melee_effects[i]
            add = self.add_melee_effects[i]

            if add is None:
                changed.append(eq)
            else:
                if len(eq) != 2 or len(add) != 2:
                    print("ERROR::Equipable - values in melee_effects has length other than 2")
                    return self.eq_melee_effects
                else:
                    new = []
                    if eq[0] != add[0]:
                        # Different type of effect
                        changed.append(tuple(add))
                    else:
                        new.append(eq[0]) # maintain same effect type
                        new.append(eq[1] + add[1])
                        changed.append(tuple(new))
        return changed

    @property
    def changed_status(self):
        """Status of the equipment's changed bonus status."""
        changed_status = {
            "eq_max_hp":self.eq_max_hp + self.add_max_hp,
            "eq_hp":self.eq_hp + self.add_hp,
            "eq_max_mp":self.eq_max_mp + self.add_max_mp,
            "eq_mp":self.eq_mp + self.add_mp,
            "eq_strength":self.eq_strength + self.add_strength,
            "eq_dexterity":self.eq_dexterity + self.add_dexterity,
            "eq_agility":self.eq_agility + self.add_agility,
            "eq_intelligence":self.eq_intelligence + self.add_intelligence,
            "eq_constitution":self.eq_constitution + self.add_constitution,
            "eq_charm":self.eq_charm + self.add_charm,
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
            "eq_melee_effects": self.changed_melee_effects,
            "eq_melee_effects_var": self.changed_melee_effects_var,
            }
        return changed_status

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
        self.eq_protection = round(self.eq_protection * self.corrosion_debuf * self.burnt_debuf)
        self.eq_base_melee = round(self.eq_base_melee * self.corrosion_debuf * self.burnt_debuf)
        self.eq_additional_melee = round(self.eq_additional_melee * self.corrosion_debuf * self.burnt_debuf)

        self.add_hp = round(self.upgrade * self.hp_mag)
        self.add_mp = round(self.upgrade * self.mp_mag)
        self.add_max_hp = round(self.upgrade * self.max_hp_mag)
        self.add_max_mp = round(self.upgrade * self.max_mp_mag)
        self.add_strength = round(self.upgrade * self.strength_mag)
        self.add_dexterity = round(self.upgrade * self.dexterity_mag)
        self.add_agility = round(self.upgrade * self.agility_mag)
        self.add_intelligence = round(self.upgrade * self.intelligence_mag)
        self.add_constitution = round(self.upgrade * self.constitution_mag)
        self.add_charm = round(self.upgrade * self.charm_mag)
        self.add_base_melee = round(self.upgrade * self.base_melee_mag)
        self.add_additional_melee = round(self.upgrade * self.additional_melee_mag)
        self.add_protection = round(self.upgrade * self.protection_mag)
        self.add_hearing = round(self.upgrade * self.hearing_mag)
        self.add_eyesight = round(self.upgrade * self.eyesight_mag)
        self.add_fire_resistance = round(self.upgrade * self.fire_resistance_mag)
        self.add_poison_resistance = round(self.upgrade * self.poison_resistance_mag)
        self.add_cold_resistance = round(self.upgrade * self.cold_resistance_mag)
        self.add_acid_resistance = round(self.upgrade * self.acid_resistance_mag)
        self.add_psychic_resistance = round(self.upgrade * self.psychic_resistance_mag)
        self.add_sleep_resistance = round(self.upgrade * self.sleep_resistance_mag)
        self.add_shock_resistance = round(self.upgrade * self.shock_resistance_mag)
        self.add_magic_resistance = round(self.upgrade * self.magic_resistance_mag)

    def reset_upgrade(self):
        """Reset upgrade to 0"""
        self.upgrade = 0
        self.update_stat()
        if self.owner:
            self.owner.equipments.update_equipment_bonus(self.parent)  # Change bonus values

    def upgrade_this(self, amount:int):
        """
        Upgrade this equipment.
        And refresh the equiper's status bonus values.
        """
        self.upgrade += amount
        self.update_stat()
        if self.owner:
            self.owner.equipments.update_equipment_bonus(self.parent) # Change bonus values

    @property
    def corrosion_debuf(self) -> float:
        """Can be overwritten."""
        if self.parent.item_state:
            if self.parent.item_state.burntness == 0:
                return 1
            return 0.8 ** self.parent.item_state.corrosion
        return 1

    @property
    def burnt_debuf(self) -> float:
        """Can be overwritten."""
        if self.parent.item_state:
            if self.parent.item_state.burntness == 0:
                return 1
            return 0.8 ** self.parent.item_state.burntness
        return 1


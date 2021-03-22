from __future__ import annotations

from typing import List, TYPE_CHECKING, Optional

from components.base_component import BaseComponent
from components.equipable import Equipable
from korean import grammar as g
import exceptions

import color

if TYPE_CHECKING:
    from entity import Actor, Item

class Equipments(BaseComponent):
    parent: Actor

    def __init__(self):
        self.equipments = {# Save items
            "main hand":None, #NOTE: Every equipments that can be equipped on main hand can also be equipped on off hand
            "off hand":None,
            "head":None,
            "face":None, # For goggles, bandana, mask, etc.
            "torso":None,
            "hand":None, # For Gauntlets
            "belt":None,
            "leg":None,
            "feet":None, # For Boots
            "cloak":None,
            "amulet":None,
            "left ring":None,
            "right ring":None,
            }

    def add_equipable_bonuses(self, item: Item):
        """Change parent entity's status.bonuses. (Add)"""

        self.parent.status.bonus_hp += item.equipable.changed_status["eq_hp"]
        self.parent.status.bonus_mp += item.equipable.changed_status["eq_mp"]
        self.parent.status.bonus_max_hp += item.equipable.changed_status["eq_max_hp"]
        self.parent.status.bonus_max_mp += item.equipable.changed_status["eq_max_mp"]
        self.parent.status.bonus_strength += item.equipable.changed_status["eq_strength"]
        self.parent.status.bonus_dexterity += item.equipable.changed_status["eq_dexterity"]
        self.parent.status.bonus_intelligence += item.equipable.changed_status["eq_intelligence"]
        self.parent.status.bonus_agility += item.equipable.changed_status["eq_agility"]
        self.parent.status.bonus_charm += item.equipable.changed_status["eq_charm"]
        self.parent.status.bonus_constitution += item.equipable.changed_status["eq_constitution"]

        self.parent.status.bonus_base_melee += item.equipable.changed_status["eq_base_melee"]
        self.parent.status.bonus_additional_melee += item.equipable.changed_status["eq_additional_melee"]

        self.parent.status.bonus_protection += item.equipable.changed_status["eq_protection"]

        self.parent.status.bonus_fire_resistance += item.equipable.changed_status["eq_fire_resistance"]
        self.parent.status.bonus_poison_resistance += item.equipable.changed_status["eq_poison_resistance"]
        self.parent.status.bonus_acid_resistance += item.equipable.changed_status["eq_acid_resistance"]
        self.parent.status.bonus_cold_resistance += item.equipable.changed_status["eq_cold_resistance"]
        self.parent.status.bonus_psychic_resistance += item.equipable.changed_status["eq_psychic_resistance"]
        self.parent.status.bonus_sleep_resistance += item.equipable.changed_status["eq_sleep_resistance"]
        self.parent.status.bonus_shock_resistance += item.equipable.changed_status["eq_shock_resistance"]
        self.parent.status.bonus_magic_resistance += item.equipable.changed_status["eq_magic_resistance"]


    def remove_equipable_bonuses(self, item: Item):
        """Change parent entity's status.bonuses. (Remove)"""

        self.parent.status.bonus_hp -= item.equipable.changed_status["eq_hp"]
        self.parent.status.bonus_mp -= item.equipable.changed_status["eq_mp"]
        self.parent.status.bonus_max_hp -= item.equipable.changed_status["eq_max_hp"]
        self.parent.status.bonus_max_mp -= item.equipable.changed_status["eq_max_mp"]
        self.parent.status.bonus_strength -= item.equipable.changed_status["eq_strength"]
        self.parent.status.bonus_dexterity -= item.equipable.changed_status["eq_dexterity"]
        self.parent.status.bonus_intelligence -= item.equipable.changed_status["eq_intelligence"]
        self.parent.status.bonus_agility -= item.equipable.changed_status["eq_agility"]
        self.parent.status.bonus_charm -= item.equipable.changed_status["eq_charm"]
        self.parent.status.bonus_constitution -= item.equipable.changed_status["eq_constitution"]

        self.parent.status.bonus_base_melee -= item.equipable.changed_status["eq_base_melee"]
        self.parent.status.bonus_additional_melee -= item.equipable.changed_status["eq_additional_melee"]

        self.parent.status.bonus_protection -= item.equipable.changed_status["eq_protection"]

        self.parent.status.bonus_fire_resistance -= item.equipable.changed_status["eq_fire_resistance"]
        self.parent.status.bonus_poison_resistance -= item.equipable.changed_status["eq_poison_resistance"]
        self.parent.status.bonus_acid_resistance -= item.equipable.changed_status["eq_acid_resistance"]
        self.parent.status.bonus_cold_resistance -= item.equipable.changed_status["eq_cold_resistance"]
        self.parent.status.bonus_psychic_resistance -= item.equipable.changed_status["eq_psychic_resistance"]
        self.parent.status.bonus_sleep_resistance -= item.equipable.changed_status["eq_sleep_resistance"]
        self.parent.status.bonus_shock_resistance -= item.equipable.changed_status["eq_shock_resistance"]
        self.parent.status.bonus_magic_resistance -= item.equipable.changed_status["eq_magic_resistance"]
            
    
    def equip_equipment(self, item: Item, forced: bool=False):
        """Equip item at region."""
        # You tried to re-equip the item you are already equipping
        if item.item_state.is_equipped:
            if not forced:
                if self.parent == self.engine.player:
                    raise exceptions.Impossible(f"당신은 이미 {g(item.name, '을')} 장착하고 있다.")

            return None

        # TODO: check whether the equipper has the body part required for equipping

        # Remove item that was equipped on the region you are currently trying to equip
        if self.equipments[item.equipable.equip_region]:
            self.remove_equipment(item.equipable.equip_region)

        # Equip item, gain bonuses
        self.equipments[item.equipable.equip_region] = item
        item.equipable.upgrade_stat_change()
        self.add_equipable_bonuses(item)

        if not forced:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 {g(item.name, '을')} 장착했다.", fg=color.health_recovered)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(item.name, '을')} 장착했다.", fg=color.gray, target=self.parent)
        item.item_state.is_equipped = item.equipable.equip_region
    

    def remove_equipment(self, region: str, forced: bool=False):# forced는 parent의 의지에 의해 이루어진 게 아닐 경우 True.
        """
        Remove item from certain region.

        Args:
            forced:
                If the removing an equipments was not intended by the equipper, set to True.
        """

        # Nothing to remove
        if self.equipments[region] == None: 
            if not forced:
                if self.parent == self.engine.player:
                    raise exceptions.Impossible("당신은 해당 위치에 아무 것도 장착하고 있지 않다.")

            return None
        else:
            self.remove_equipable_bonuses(self.equipments[region])
            self.equipments[region].item_state.is_equipped = None

            if not forced: # If the equipments is burned, rotted, etc(forced), do not display the log message.
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 {g(self.equipments[region].name, '을')} 장착 해제했다.", fg=color.health_recovered)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(self.equipments[region].name, '을')} 장착 해제했다.", fg=color.gray, target=self.parent)

            self.equipments[region] = None

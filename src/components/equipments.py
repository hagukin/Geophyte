from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional, Tuple
from components.base_component import BaseComponent
from components.equipable import Equipable
from korean import grammar as g
from util import equip_region_name_to_str
from components.status import Bonus
import exceptions

import color

if TYPE_CHECKING:
    from entity import Actor, Item

class Equipments(BaseComponent):
    parent: Actor

    def __init__(self):
        super().__init__()
        self.equipments = {# Save items
            "main hand":None, #NOTE: Every equipments that can be equipped on main hand can also be equipped on off hand
            "off hand":None,
            "head":None,
            "face":None, # For goggles, bandana, mask, etc.
            "torso":None,
            "fist":None, # For Gauntlets
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
        bonus = Bonus(
            bonus_id = item.item_state.equipped_region, # id: equipped region
            bonus_hp = item.equipable.changed_status["eq_hp"],
            bonus_mp = item.equipable.changed_status["eq_mp"],
            bonus_max_hp = item.equipable.changed_status["eq_max_hp"],
            bonus_max_mp = item.equipable.changed_status["eq_max_mp"],
            bonus_strength = item.equipable.changed_status["eq_strength"],
            bonus_dexterity = item.equipable.changed_status["eq_dexterity"],
            bonus_intelligence = item.equipable.changed_status["eq_intelligence"],
            bonus_agility = item.equipable.changed_status["eq_agility"],
            bonus_charm = item.equipable.changed_status["eq_charm"],
            bonus_constitution = item.equipable.changed_status["eq_constitution"],

            bonus_base_melee = item.equipable.changed_status["eq_base_melee"],
            bonus_additional_melee = item.equipable.changed_status["eq_additional_melee"],

            bonus_protection = item.equipable.changed_status["eq_protection"],

            bonus_hearing = item.equipable.changed_status["eq_hearing"],
            bonus_eyesight = item.equipable.changed_status["eq_eyesight"],

            bonus_fire_resistance = item.equipable.changed_status["eq_fire_resistance"],
            bonus_poison_resistance = item.equipable.changed_status["eq_poison_resistance"],
            bonus_acid_resistance = item.equipable.changed_status["eq_acid_resistance"],
            bonus_cold_resistance = item.equipable.changed_status["eq_cold_resistance"],
            bonus_psychic_resistance = item.equipable.changed_status["eq_psychic_resistance"],
            bonus_sleep_resistance = item.equipable.changed_status["eq_sleep_resistance"],
            bonus_shock_resistance = item.equipable.changed_status["eq_shock_resistance"],
            bonus_magic_resistance = item.equipable.changed_status["eq_magic_resistance"],
        )
        self.parent.status.add_bonus(bonus)

    def remove_equipable_bonuses(self, item: Item) -> None:
        """Change parent entity's status.bonuses. (Remove)"""
        self.parent.status.remove_bonus(item.item_state.equipped_region)

    def update_equipment_bonus(self, item):
        """Function called when equipment's stat has been changed.
        Upgrade, debuff etc."""
        self.remove_equipable_bonuses(item)
        self.add_equipable_bonuses(item)

    def check_all_equipments_if_equipable(self):
        """Check all equipments this parent is equipping, and check if the parent satisfies the necessary condition to equip those items.
        e.g. this function is called right after an actor lose its arms/legs."""
        pass

    def can_equip_size_check(self, item: Item) -> Tuple[bool, Optional[bool]]:
        """
        Return:
            boolean, boolean.
            Possible outcome:
                True, None
                False, True
                False, False
            First boolean indicates whether the actor can equip this or not.
            Second boolean contains the reason why the actor cannot equip the item. (Is set to None is the actor can equip)
            If True, it means the item is too big.
            If False, It means the item is too small.
        """
        if item.equipable.equip_size[0] > self.parent.actor_state.size:
            return False, True
        elif item.equipable.equip_size[1] < self.parent.actor_state.size:
            return False, False
        else:
            return True, None

    def can_equip_region_check(self, item: Item, region: str) -> Tuple[bool, str]:
        """
        Return:
            boolean, string.
            string contains the region name for the given item.
        """
        # Cannot equip item to the given region.
        if region not in item.equipable.possible_regions:
            return False, ""

        if region == "main hand":
            if self.parent.actor_state.is_right_handed:
                if self.parent.actor_state.has_right_arm:
                    return True, "오른팔"
                else:
                    return False, "오른팔"
            else:
                if self.parent.actor_state.has_left_arm:
                    return True, "왼팔"
                else:
                    return False, "왼팔"
        elif region == "off hand":
            if self.parent.actor_state.is_right_handed:
                if self.parent.actor_state.has_left_arm:
                    return True, "왼팔"
                else:
                    return False, "왼팔"
            else:
                if self.parent.actor_state.has_right_arm:
                    return True, "오른팔"
                else:
                    return False, "오른팔"
        elif region == "head" or region == "face" or region == "amulet":
            if self.parent.actor_state.has_head >= 1:
                return True, "머리"
            else:
                return False, "머리"
        elif region == "torso" or region == "belt" or region == "cloak":
            if self.parent.actor_state.has_torso:
                return True, "상반신"
            return False, "상반신"
        elif region == "fist":
            if self.parent.actor_state.has_left_arm or self.parent.actor_state.has_right_arm:
                return True, "손"
            return False, "손"
        elif region == "leg" or region == "feet":
            if self.parent.actor_state.has_leg:
                return True, "다리"
            return False, "다리"
        elif region == "left ring":
            if self.parent.actor_state.has_left_arm:
                return True, "팔"
            return False, "팔"
        elif region == "right ring":
            if self.parent.actor_state.has_left_arm:
                return True, "팔"
            return False, "팔"
        else:
            raise Exception(f"FATAL ERROR::CAN'T FIND THE APPROPRIATE EQUIP REGION FOR THE GIVEN ITEM {item.entity_id}")


    def can_equip_physically(self, item: Item, region: str) -> bool:
        return self.can_equip_size_check(item)[0] and self.can_equip_region_check(item, region)[0]


    def try_equip(self, item: Item, possible_equip_regions: Tuple[str, ...]) -> Optional[str]:
        """
        Check if parent is physically capable of equipping the item (body parts).
        If so, return the equip region as string.
        If not, return None

        Args:
            possible_equip_regions:
                Tuple of strings.
                Contains the possible candidates of the equip region.
        """
        chosen_region = None
        for region in possible_equip_regions:
            # If there is already something on the region
            if self.equipments[region]:
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(
                        f"당신은 {equip_region_name_to_str(region)} 부위에 이미 {g(self.equipments[region].name, '을')} 장착하고 있다.",
                        fg=color.impossible)
                else:
                    print(f"DEBUG::{self.parent.entity_id} cannot equip {item.name} on {region} region because it is already equipping {self.equipments[region].name}.")
                continue

            can_equip_region, region_name = self.can_equip_region_check(item, region)
            if not can_equip_region:
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(
                        f"당신은 {g(region_name, '이')} 없기 때문에 {g(item.name, '을')} {equip_region_name_to_str(region)} 부위에 장착할 수 없다.",
                        fg=color.impossible)
                else:
                    print(f"DEBUG::{self.parent.entity_id} cannot equip {item.name} on {region} region due to its lack of {region_name}.")
                continue

            # Check if parent is physically capable of equipping the item (size)
            can_equip_size, item_is_too_big = self.can_equip_size_check(item)
            if not can_equip_size:
                if self.parent == self.engine.player:
                    if item_is_too_big:
                        self.engine.message_log.add_message(
                            f"{g(item.name, '는')} 당신이 장착하기에 너무 크다.",
                            fg=color.impossible)
                    else:
                        self.engine.message_log.add_message(
                            f"{g(item.name, '는')} 당신이 장착하기에 너무 작다.",
                            fg=color.impossible)
                else:
                    print(f"DEBUG::{self.parent.entity_id} cannot equip {item.name} due to its size.")
                continue

            # region is available, stop the iteration
            chosen_region = region
            break
        return chosen_region


    def equip_equipment(self, item: Item, forced: bool=False, equip_region: Optional[str] = None):
        """
        Equip item at region.

        Args:
            equip_region:
                if None, the game will decide where to equip the item from the possible candidates.
                Or you can pass in a value to specify where to equip the item.
        """
        # You tried to re-equip the item you are already equipping
        if item.item_state.equipped_region:
            if not forced:
                if self.parent == self.engine.player:
                    raise exceptions.Impossible(f"당신은 이미 {g(item.name, '을')} 장착하고 있다.")
            return None

        # If equip region is specified, pass a tuple of size = 1.
        # By default, use tuple value that is stored in item's equipable component.
        if equip_region == None:
            possible_equip_regions = item.equipable.possible_regions
        else:
            possible_equip_regions = (equip_region, )
        curr_equipped_region = self.try_equip(item, possible_equip_regions=possible_equip_regions)

        # Check if available region was found. If not, return None
        if not curr_equipped_region:
            return None

        # Equip item, gain bonuses
        self.equipments[curr_equipped_region] = item
        item.equipable.update_stat()
        item.item_state.equipped_region = curr_equipped_region
        self.add_equipable_bonuses(item)

        if not forced:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 {g(item.name, '을')} {equip_region_name_to_str(curr_equipped_region)} 부위에 장착했다.", fg=color.health_recovered)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(item.name, '을')} {equip_region_name_to_str(curr_equipped_region)} 부위에 장착했다.", fg=color.gray, target=self.parent)
    

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
            self.equipments[region].item_state.equipped_region = None

            if not forced: # If the equipments is burned, rotted, etc(forced), do not display the log message.
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 {g(self.equipments[region].name, '을')} {equip_region_name_to_str(region)} 부위에서 장착 해제했다.", fg=color.health_recovered)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(self.equipments[region].name, '을')} 장착 해제했다.", fg=color.gray, target=self.parent)

            self.equipments[region] = None

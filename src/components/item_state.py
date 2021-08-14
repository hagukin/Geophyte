from __future__ import annotations

from typing import TYPE_CHECKING

import random
import color

from components.base_component import BaseComponent
from korean import grammar as g

if TYPE_CHECKING:
    from entity import Item, Actor

class ItemState(BaseComponent):
    def __init__(self,
        was_burning = False,
        is_burning: bool = False,
        burntness: int = 0,
        corrosion: int = 0,
        BUC: int = 0,
        is_identified: int = 0,
        equipped_region: str = None,
        is_being_sold_from: int = None,
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
            BUC:
                -1 - cursed
                0 - uncursed (regular)
                1 - blessed
            is_identified:
                0 - unidentified
                1 - semi-identified (You know the id(type) of an item, but BUC is unknown)
                2 - full-identified (You know the id(type) AND the BUC.)
            equipped_region:
                string value that indicates the equip region this item if currently equipped on. (if there is one)
            is_being_sold_from:
                Integer. a memory location of a actor that is selling this item. This doesn't necesserily means the owner. (Warning: The value is a integer, not a reference.)
                NOTE: use python id() to get id.
        """
        super().__init__(None)

        # values that are not stored in item_state dictionaty
        self.was_burning = was_burning
        self.equipped_region = equipped_region

        # values that are stored in item_state dictionaty (entity.Item.set_info())
        self.is_burning = is_burning #NOTE: 'flaming sword' should have this value as FALSE no true. this is merely a systemic value.
        self.burntness = burntness
        self.corrosion = corrosion
        self.BUC = BUC
        self.is_identified = is_identified
        self.is_being_sold_from = is_being_sold_from

    def identify_self(self, identify_level: int=1):
        """
        NOTE: When identifying an entire type, use item_manager.identify_type instead.
        """
        if identify_level == 0:
            self.unidentify_self()
            self.engine.item_manager.unidentify_type(self.parent.entity_id)
            print("WARNING::Use unidentify_self() instead.")
            return None
        self.is_identified = max(identify_level, self.is_identified)
        self.engine.item_manager.identify_type(self.parent.entity_id, 1) # "semi identify" the entire item type.
    
    def unidentify_self(self):
        self.is_identified = 0 # Full-identification
        self.engine.item_manager.unidentify_type(self.parent.entity_id)
    
    def check_if_semi_identified(self):
        """
        return True if item is semi-identified OR full-identified.
        """
        if self.is_identified >= 1 or self.engine.item_manager.items_identified[self.parent.entity_id] >= 1:
            return True
        else:
            return False

    def check_if_full_identified(self):
        """
        return True if item is full-identified.
        """
        if self.is_identified >= 2 or self.engine.item_manager.items_identified[self.parent.entity_id] >= 2: 
            #NOTE: On regular occasion, item_factories.item_identified is either 0 or 1, 
            # since full-identification can differ from indivisual instances.
            return True
        else:
            return False

    def change_buc(self, BUC: int) -> bool:
        """Change BUC to given value
        BUC 1 0 -1
        Return:
            Boolean. Whether the change was successful or not.
            """
        if BUC == 1:
            if self.parent.blessable:
                self.BUC = 1
                return True
            else:
                return False
        elif BUC == -1:
            if self.parent.cursable:
                self.BUC = -1
                return True
            else:
                return False
        elif BUC == 0:
            if self.BUC == -1:
                if self.parent.uncursable:
                    self.BUC = 0
                    return True
                else:
                    return False
            self.BUC = 0
            return True
        else:
            print(f"ERROR::Cannot change {self.parent.entity_id}'s BUC to {BUC}")
            return False

    def check_if_state_identical(self, comparing_item: Item, compare_stack_count: bool = False) -> bool:
        """
        Check if the two items received as arguments are the "same". (they might have different memory address)
        We only care about certain status that could affect the item's in-game abilities.
        This includes:
        name, item_state, upgrades, etc.

        NOTE: This function will only check the item_state component, meaning xpos, ypos, etc. is ignored.
        ALL ITEMS THAT ARE UPGRADABLE OR EDIBLE SHOULD NEVER BE IDENTICAL WITH OTHER ITEMS.
        THIS IS THE REASON WHY THEY ARE NOT STACKABLE FROM THE BEGINNING.

        NOTE: DO NOT change this function into simple memory address comparing function.
        The main reason for this is when you pick up an item,
        it should stack with the item that is in your inventory
        that has different memory address but has the exact same informations.
        """
        # 0. compare memory address
        if id(self.parent) == id(comparing_item):
            print(f"DEBUG::item_state.check_if_identical - Identical memory")
            return True

        # 1. Compare stack count and names
        if compare_stack_count and self.parent.stack_count != comparing_item.stack_count:
            return False
        if self.parent.name == comparing_item.name and self.parent.entity_id == comparing_item.entity_id:
            # 2. Compare item states
            if self.BUC != comparing_item.item_state.BUC:
                return False
            if self.check_if_semi_identified() != comparing_item.item_state.check_if_semi_identified()\
                and self.check_if_full_identified() != comparing_item.item_state.check_if_full_identified():
                return False
            if(
                self.burntness != comparing_item.item_state.burntness or
                self.is_burning != comparing_item.item_state.is_burning or
                self.corrosion != comparing_item.item_state.corrosion or
                self.is_being_sold_from != comparing_item.item_state.is_being_sold_from
            ):
                return False
            return True
        return False

    def burn(self, owner: Actor=None):
        """NOTE: It is recommended not to call this function directly. engine.handle_item_states will call this function most of the time.
        Use item_state.is_burning = True instead."""
        # Catch on fire log
        if self.was_burning == False:
            self.was_burning = True
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"당신의 {self.parent.name}에 불이 붙었다.", fg=color.player_severe)
                #else:
                    #self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} is burning.", fg=color.white)
            else:
                if self.engine.game_map.visible[self.parent.x, self.parent.y]:
                    self.engine.message_log.add_message(f"{self.parent.name}에 불이 붙었다.", fg=color.world)
                else:
                    self.engine.message_log.add_message("당신은 무언가 타는 듯한 냄새를 맡았다.", fg=color.player_sense, show_once=True)

        # Further burning calculation
        will_burn = random.random()
        if will_burn < self.parent.flammable:

            self.burntness += 1
            if self.parent.equipable:
                self.parent.equipable.update_stat()

            # Burning state log
            if owner:
                if self.burntness == 1:
                    if owner == self.engine.player:
                        self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 다소 그을렸다.", fg=color.player_not_good)
                    #else:
                        #self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} is slightly burnt.", fg=color.white)
                elif self.burntness == 2:
                    if owner == self.engine.player:
                        self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 상당히 그을렸다.", fg=color.player_severe)
                    #else:
                        #self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} is very burnt", fg=color.white)
            else:
                if self.burntness == 1:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 다소 그을렸다.", fg=color.world, target=self.parent)
                elif self.burntness == 2:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 상당히 그을렸다.", fg=color.world, target=self.parent)

        # if Burnt out
        if self.burntness == 3:
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 연소했다!", fg=color.player_severe)
                else:
                    if self.parent in owner.equipments.equipments.values(): # prints log only if the item is equipped
                        self.engine.message_log.add_message(f"{owner.name}의 {g(self.parent.name, '이')} 연소했다!", fg=color.enemy_unique, target=owner)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 연소했다!", fg=color.world, target=self.parent)
        
            #Adjust variables
            self.is_burning = False
            self.was_burning = False

            # Delete item from the game
            self.parent.remove_self()

        # Extinguish Chance
        extinguish_chance = random.random()
        if extinguish_chance >= self.parent.flammable:
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 타는 것을 멈췄다.", fg=color.player_neutral)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 타는 것을 멈췄다.", fg=color.world, target=self.parent)
            
            self.is_burning = False
            self.was_burning = False

    def corrode(self, owner: Actor=None, amount: int=1):
        if random.random() <= self.parent.corrodible:
            self.corrosion += amount
            if self.parent.equipable:
                self.parent.equipable.update_stat()
        else:
            return None

        if self.corrosion > 2:
            # Log
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 완전히 부식되어 사라졌다.", fg=color.player_severe)
                else:
                    if self.parent in owner.equipments.equipments.values(): # prints log only if the item is equipped
                        self.engine.message_log.add_message(f"{owner.name}의 {g(self.parent.name, '이')} 완전히 부식되어 사라졌다.", fg=color.enemy_unique, target=owner)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 완전히 부식되어 사라졌다.", fg=color.world, target=self.parent)

            # Completely corroded
            self.parent.remove_self()
        elif self.corrosion == 2:
            # Log
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 심하게 부식되었다.", fg=color.player_bad)
        elif self.corrosion == 1:
            # Log
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 다소 부식되었다.", fg=color.player_not_good)


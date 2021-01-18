from __future__ import annotations

from typing import TYPE_CHECKING

import random
import color

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Item, Actor

class ItemState(BaseComponent):
    def __init__(self,
        was_burning = False,
        is_burning: bool = False,
        burntness: int = 0,
        BUC: int = 0,
        is_identified: int = 0,
        is_equipped: str = None,
    ):
        """
        Args:
            burntness:
                0 - Not burnt
                1 - partly burnt
                2 - severly burnt
                3 - burnt out (its gone)
            BUC:
                -1 - cursed
                0 - uncursed (regular)
                1 - blessed
            is_identified:
                0 - unidentified
                1 - semi-identified (You know the id(type) of an item, but BUC is unknown)
                2 - full-identified (You know the id(type) AND the BUC.)
            is_equipped:
                string value that indicates the equip region this item if currently equipped on. (if there is one)
        """
        # parent: Item 
        self.parent = None

        # values that are not stored in item_state dictionaty
        self.was_burning = was_burning
        self.is_equipped = is_equipped

        # values that are stored in item_state dictionaty
        self.is_burning = is_burning
        self.burntness = burntness
        self.BUC = BUC
        self.is_identified = is_identified

    def identify_self(self, identify_level: int=1):
        self.is_identified = identify_level # Full-identification
        self.engine.item_manager.items_identified[self.parent.entity_id] = 1 # Cannot "fully identify" the entire item type.
    
    def unidentify_self(self):
        self.is_identified = 0 # Full-identification
        self.engine.item_manager.items_identified[self.parent.entity_id] = 0
    
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

    def uncurse_self(self):
        """
        Remove this parent's curse
        """
        self.BUC = 0

    def check_if_identical(self, comparing_item: Item) -> bool:
        """
        Check if the two items received as arguments are the "same". (they might have different memory address)
        We only care about certain status that could affect the item's in-game abilities.
        This includes:
        name, item_state, upgrades, etc.

        NOTE: This function will only check the item_state component.
        ALL ITEMS THAT ARE UPGRADABLE OR EDIBLE SHOULD NEVER BE IDENTICAL WITH OTHER ITEMS.
        THIS IS THE REASON WHY THEY ARE NOT STACKABLE FROM THE BEGINNING.
        """
        # 1. Compare names
        if self.parent.name == comparing_item.name and self.parent.entity_id == comparing_item.entity_id:

            # 2. Compare item states
            if self.parent.item_state.BUC != comparing_item.item_state.BUC:
                return False
            if self.check_if_semi_identified() != comparing_item.item_state.check_if_semi_identified()\
                and self.check_if_full_identified() != comparing_item.item_state.check_if_full_identified():
                return False
            if(
                self.parent.item_state.burntness != comparing_item.item_state.burntness or
                self.parent.item_state.is_burning != comparing_item.item_state.is_burning
            ):
                return False
            
            return True

        return False

    def burn(self, owner: Actor=None):
        # Catch on fire log
        if self.was_burning == False:
            self.was_burning = True
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"Your {self.parent.name} catches on fire.", fg=color.red)
                #else:
                    #self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} is burning.", fg=color.white)
            else:
                if self.engine.game_map.visible[self.parent.x, self.parent.y]:
                    self.engine.message_log.add_message(f"{self.parent.name} catches on fire.", fg=color.white)
                else:
                    self.engine.message_log.add_message("You smell something burning.", fg=color.white)

        # Further burning calculation
        will_burn = random.random()
        if will_burn < self.parent.flammable:

            self.burntness += 1

            # Burning state log
            if owner:
                if self.burntness == 1:
                    if owner == self.engine.player:
                        self.engine.message_log.add_message(f"Your {self.parent.name} is slightly burnt.", fg=color.player_damaged)
                    #else:
                        #self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} is slightly burnt.", fg=color.white)
                elif self.burntness == 2:
                    if owner == self.engine.player:
                        self.engine.message_log.add_message(f"Your {self.parent.name} is very burnt.", fg=color.player_damaged)
                    #else:
                        #self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} is very burnt", fg=color.white)
            else:
                if self.burntness == 1:
                    self.engine.message_log.add_message(f"{self.parent.name} is slightly burnt.", fg=color.white, target=self.parent)
                elif self.burntness == 2:
                    self.engine.message_log.add_message(f"{self.parent.name} is very burnt.", fg=color.white, target=self.parent)

        # if Burnt out
        if self.burntness == 3:
            # Delete item from the game
            self.parent.remove_self()
            
            # Log
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"Your {self.parent.name} burns out!", fg=color.red)
                else:
                    self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} burns out!", fg=color.white, target=owner)
            else:
                self.engine.message_log.add_message(f"{self.parent.name} burns out!", fg=color.white, target=self.parent)
        
            #Adjust variables
            self.is_burning = False
            self.was_burning = False

        # Extinguish Chance
        extinguish_chance = random.random()
        if extinguish_chance >= self.parent.flammable:
            if owner:
                if owner == self.engine.player:
                    self.engine.message_log.add_message(f"Your {self.parent.name} stops burning.", fg=color.gray)
                else:
                    self.engine.message_log.add_message(f"{owner.name}\'s {self.parent.name} stops burning.", fg=color.gray, target=owner)
            else:
                self.engine.message_log.add_message(f"{self.parent.name} stops burning.", fg=color.gray, target=self.parent)
            
            self.is_burning = False
            self.was_burning = False


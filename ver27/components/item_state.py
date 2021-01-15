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
        is_equipped: str = None,
    ):
        """
        Args:
            burntness:
                0 - Not burnt
                1 - partly burnt
                2 - severly burnt
                3 - burnt out (its gone)
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
        if self.parent.name == comparing_item.name:

            # 2. Compare item cursed / blessed status
            #TODO: add BUC?
            #TODO: add identification?

            # 3. Compare item states
            #NOTE: update the code when new features are added to item_states!
            if(
                self.parent.item_state.burntness == comparing_item.item_state.burntness and
                self.parent.item_state.is_burning == comparing_item.item_state.is_burning
            ):
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


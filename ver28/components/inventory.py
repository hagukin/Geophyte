from __future__ import annotations

from typing import List, TYPE_CHECKING
from components.base_component import BaseComponent
from exceptions import Impossible

import color

if TYPE_CHECKING:
    from entity import Actor, Item

class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int, is_fireproof: bool=False):
        self.capacity = capacity # max 52
        self.is_fireproof = is_fireproof
        self.items: List[Item] = []
        self.item_hotkeys = {
            "a":None,"b":None,"c":None,"d":None,"e":None,"f":None,"g":None,"h":None,"i":None,"j":None,"k":None,"l":None,"m":None,"n":None,"o":None,"p":None,"q":None,"r":None,"s":None,"t":None,"u":None,"v":None,"w":None,"x":None,"y":None,"z":None,
            "A":None,"B":None,"C":None,"D":None,"E":None,"F":None,"G":None,"H":None,"I":None,"J":None,"K":None,"L":None,"M":None,"N":None,"O":None,"P":None,"Q":None,"R":None,"S":None,"T":None,"U":None,"V":None,"W":None,"X":None,"Y":None,"Z":None
        }

    def check_if_in_inv(self, item_id: str):
        """
        Check if the inventory has an item of a the given id.
        If so, return the item.
        """
        for item in self.items:
            if item.entity_id == item_id:
                return item
            else:
                continue
        
        return False

    def check_if_full(self) -> bool:
        return len(self.items) >= self.capacity

    def drop(self, item: Item, show_msg: bool=True) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        item.parent = None
        item.item_state.is_equipped = None
        
        self.remove_item(item=item, remove_count=-1) # remove all stack
        item.place(self.parent.x, self.parent.y, self.gamemap)# self.gamemap belongs to BaseComponent, which is equivalent to self.parent.gamemap.

        if show_msg:
            if self.parent == self.engine.player:
                if item.stack_count > 1:
                    self.engine.message_log.add_message(f"You dropped the {item.name} (x{item.stack_count}).")
                else:
                    self.engine.message_log.add_message(f"You dropped the {item.name}.")
            else:
                if item.stack_count > 1:
                    self.engine.message_log.add_message(f"{self.parent.name} threw the {item.name} (x{item.stack_count}).", fg=color.gray, target=self.parent)
                else:
                    self.engine.message_log.add_message(f"{self.parent.name} threw the {item.name}.", fg=color.gray, target=self.parent)

        return True
    
    def throw(self, item: Item, x: int, y: int, show_msg: bool=True) -> None:
        """
        Remove an item from the inventory and place it on the given location.
        This process is more of a "teleporting item" rather than throwing, since the actual throwing/collision is handled in throwable component of an item.
        
        NOTE: You can only throw one item at a time.

        Args:
            show_msg:
                Whether to show a message to the log or not.
        """
        # Duplicate and place the item
        spliten_item = item.duplicate_self(quantity=1)
        self.remove_item(item, remove_count=1)
        spliten_item.place(x, y, self.gamemap)

        if show_msg:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"You threw the {item.name}.")
            else:
                self.engine.message_log.add_message(f"{self.parent.name} threw the {item.name}.", fg=color.gray, target=self.parent)

        return True

    def sort_inventory(self) -> None:
        """
        Sort inventory by type.
        Using enum from order.InventoryOrder
        """
        self.items = sorted(self.items, key = lambda item : item.item_type.value)

        def sort_hotkeys(item):
            """
            Args:
                item:
                    a pair of inventory hotkey dictionary's key and value. (Tuple)
            """
            if item[1]:
                try:
                    return item[1].item_type.value
                except:
                    print("DEBUG::INVENTORY SORTING SOMETHING WENT WRONG")
                    return 999
            else:
                # return 999 if there is no item bound to the hotkey.
                # This will make empty keys to move towards the back.
                return 999
            
        self.item_hotkeys = dict(sorted(self.item_hotkeys.items(), key=sort_hotkeys))

    def add_item(self, item: Item) -> None:
        """
        Add item to inventory. Also stack items if possible.
        Using this function is recommended instead of using .append()
        """
        if item.stackable:
            for inv_item in self.items:
                if item.item_state.check_if_identical(inv_item):
                    inv_item.stack_count += item.stack_count # Stack item
                    return None

        item.parent = self
        self.items.append(item)

        # Allocate alphabets
        for key, value in self.item_hotkeys.items():
            if value == None:
                self.item_hotkeys[key] = item
                break

    def remove_item(self, item: Item, remove_count: int=1) -> None:
        """
        Remove item from inventory.
        if remove_count == -1, remove all stack.
        You can remove multiple items at once by giving this function a "remove_count" value.
        If item is stacked, stack_count will decrease instead of removing the item from inventory.
        """
        for inv_item in self.items:
            if item is inv_item:
                if remove_count == -1:# if -1, remove entire stack
                    # remove from item_hotkey
                    for key, value in self.item_hotkeys.items():
                        if value is item:
                            self.item_hotkeys[key] = None
                    # remove from items
                    self.items.remove(inv_item)
                    return None
                else:
                    inv_item.stack_count -= remove_count # Stack item

            if inv_item.stack_count == 0:
                # remove from item_hotkey
                for key, value in self.item_hotkeys.items():
                    if value is item: # using "is" to check if they have the same memory address
                        self.item_hotkeys[key] = None
                # remove from items
                self.items.remove(inv_item)
                return None
            elif inv_item.stack_count < 0:
                # If remove_count is set to negative, do nothing.
                # This feature exist in case of using an item infinitly. (e.g. black jelly throwing a toxic goo)
                return None

    def split_item(self, item: Item, split_amount: int=1) -> None:
        """
        De-stack / Split an item from a pile.
        """
        if item.stack_count > split_amount:
            if  split_amount >= 1:
                # Create new stack
                spliten_item = item.duplicate_self(quantity=split_amount)
                spliten_item.stackable = False

                # Remove item from stack
                self.remove_item(item, split_amount)

                # Drop item to the floor if there is no room in the inventory
                if len(self.items) >= self.capacity:
                    spliten_item.place(self.parent.x, self.parent.y, self.gamemap)
                else:
                    self.add_item(spliten_item)

                # Reset the stackable of the copied item.
                # NOTE: This line of code is important, since it lets items to be stacked again even after they are spliten.
                spliten_item.stackable = True
                
                # set gamemap
                spliten_item.gamemap = item.gamemap

                # return the copy
                return spliten_item
            else:
                raise Impossible(f"The minimum amount you can split is 1.")
        else:
            raise Impossible(f"The maximum amount you can split is {item.stack_count - 1}.")
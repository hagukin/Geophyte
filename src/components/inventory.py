from __future__ import annotations
import random
import color
from typing import List, TYPE_CHECKING, Optional, Tuple
from components.base_component import BaseComponent
from components.status import Bonus
from exceptions import Impossible
from korean import grammar as g

if TYPE_CHECKING:
    from entity import Actor, Item

class Inventory(BaseComponent):
    def __init__(self, capacity: int, is_fireproof: bool=False):
        super().__init__(None)
        self.parent = None
        self.capacity = capacity # max 52
        self.is_fireproof = is_fireproof
        self.item_hotkeys = {
            "a":None,"b":None,"c":None,"d":None,"e":None,"f":None,"g":None,"h":None,"i":None,"j":None,"k":None,"l":None,"m":None,"n":None,"o":None,"p":None,"q":None,"r":None,"s":None,"t":None,"u":None,"v":None,"w":None,"x":None,"y":None,"z":None,
            "A":None,"B":None,"C":None,"D":None,"E":None,"F":None,"G":None,"H":None,"I":None,"J":None,"K":None,"L":None,"M":None,"N":None,"O":None,"P":None,"Q":None,"R":None,"S":None,"T":None,"U":None,"V":None,"W":None,"X":None,"Y":None,"Z":None
        }

    @property
    def items(self):
        return [x for x in self.item_hotkeys.values() if x is not None]

    @property
    def inv_weight(self):
        tmp = 0
        for i in self.items:
            tmp += i.weight * i.stack_count
        return tmp

    def is_empty(self) -> bool:
        for item in self.item_hotkeys.values():
            if item != None:
                return False
        return True

    def update_burden(self):
        """Check current inventory weight and apply actor state.
        Must be called when either inventory or strength is updated.
        Actual debuff is handled in actor_state.actor_burdened"""
        from entity import Actor
        if not isinstance(self.parent, Actor): # Non-actor cannot be burdened.
            return None
        w = self.inv_weight
        strength = self.parent.status.changed_status["strength"]
        if w < strength * 2:
            self.parent.actor_state.encumbrance = 0
            self.parent.status.add_bonus(Bonus("burden_bonus", bonus_agility=0, bonus_dexterity=0))
        elif w < strength * 3:
            self.parent.actor_state.encumbrance = 1
            self.parent.status.add_bonus(Bonus("burden_bonus", bonus_agility=-1, bonus_dexterity=-1))
        elif w < strength * 4:
            self.parent.actor_state.encumbrance = 2
            self.parent.status.add_bonus(Bonus("burden_bonus", bonus_agility=-5, bonus_dexterity=-5))
        elif w < strength * 5:
            self.parent.actor_state.encumbrance = 3
            self.parent.status.add_bonus(Bonus("burden_bonus", bonus_agility=-10, bonus_dexterity=-10))
        else:
            self.parent.actor_state.encumbrance = 4
            self.parent.status.add_bonus(Bonus("burden_bonus",
                                               bonus_agility=min(0, -self.parent.status.changed_status["agility"]),
                                               bonus_dexterity=-20))

    def check_if_in_inv(self, item_id: str) -> Optional[Item]:
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
        item.item_state.equipped_region = None
        
        self.delete_item_from_inv(item=item) # remove all stack
        if item.change_stack_count_when_dropped != None: # set new drop count if it has one. (e.g. toxic goo drop from black jelly)
            new_stack_count = random.randint(item.change_stack_count_when_dropped[0], item.change_stack_count_when_dropped[1])
            item.stack_count = new_stack_count
        item.place(self.parent.x, self.parent.y, self.gamemap)# self.gamemap belongs to BaseComponent, which is equivalent to self.parent.gamemap.

        if show_msg:
            if self.parent == self.engine.player:
                if item.stack_count > 1:
                    self.engine.message_log.add_message(f"당신은 {g(item.name, '을')} 땅에 떨어뜨렸다. (x{item.stack_count}).")
                else:
                    self.engine.message_log.add_message(f"당신은 {g(item.name, '을')} 땅에 떨어뜨렸다.")
            else:
                if item.stack_count > 1:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(item.name, '을')} 땅에 떨어뜨렸다. (x{item.stack_count}).", fg=color.gray, target=self.parent)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(item.name, '을')} 땅에 떨어뜨렸다.", fg=color.gray, target=self.parent)

        self.update_burden()
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
        spliten_item = item.copy(gamemap=item.gamemap)
        spliten_item.stack_count = 1
        self.decrease_item_stack(item, remove_count=1)
        spliten_item.place(x, y, self.gamemap)

        if show_msg:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 {g(item.name, '을')} 던졌다.")
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(item.name, '을')} 던졌다.", fg=color.gray, target=self.parent)

        self.update_burden()
        return True

    def sort_inventory(self) -> None:
        """
        Sort inventory by type.
        Using enum from order.InventoryOrder
        """
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
                if item.item_state.check_if_state_identical(inv_item):
                    inv_item.stack_count += item.stack_count # Stack item
                    return None
        item.parent = self

        # Allocate alphabets
        for key, value in self.item_hotkeys.items():
            if value == None:
                self.item_hotkeys[key] = item
                break

        self.update_burden()
        return None

    def get_key_of(self, item: Item) -> Optional[str]:
        for key, inv_item in self.item_hotkeys.items():
            if item is inv_item:
                return key
        print("WARNING::Item not found in inventory.")
        return None

    def delete_item_from_inv(self, item: Item) -> Item:
        """
        Delete item from inventory and return the deleted item.
        WARNING: Stack count is not being changed whatsoever.
        """
        item.parent = None
        self.item_hotkeys[self.get_key_of(item)] = None
        self.update_burden()
        return item

    def decrease_item_stack(self, item: Item, remove_count: int=1) -> None:
        """
        Remove item from inventory.
        if remove_count == -1, remove all stack.
        You can remove multiple items at once by giving this function a "remove_count" value.
        If item is stacked, stack_count will decrease instead of removing the item from inventory.
        """
        if item.stack_count > 0 and remove_count > item.stack_count:
            raise Exception("FATAL ERROR::Cannot remove item stack count higher than its original stack count. - inventory.decrease_item_stack")
        elif remove_count < 0:
            raise Exception("FATAL ERROR::Cannot remove stack count by negative integer. - inventory.decrease_item_stack")
        elif remove_count == 0:
            print("WARNING::Tried to remove stack count by 0. Possibly an error?")
        else:
            item.stack_count -= remove_count
            if item.stack_count == 0:
                self.delete_item_from_inv(item)
            elif item.stack_count < 0:# If remove_count is set to negative, do nothing. This feature exist in case of using an item infinitly. (e.g. black jelly throwing a toxic goo)
                return None
        self.update_burden()
        return None

    def split_item(self, item: Item, split_amount: int=1) -> None:
        """
        De-stack / Split an item from a pile.
        """
        if item.stack_count > split_amount:
            if  split_amount >= 1:
                # Create new stack
                spliten_item = item.copy(gamemap=item.gamemap)
                spliten_item.stack_count = split_amount
                spliten_item.stackable = False

                # Remove item from stack
                self.decrease_item_stack(item, split_amount)

                # Drop item to the floor if there is no room in the inventory
                if len(self.items) >= self.capacity:
                    spliten_item.place(self.parent.x, self.parent.y, self.gamemap)
                else:
                    self.add_item(spliten_item)

                # Reset the stackable of the copied item.
                # NOTE: This line of code is important, since it lets items to be stacked again even after they are spliten.
                spliten_item.stackable = True
                spliten_item.gamemap = item.gamemap
                return spliten_item
            else:
                raise Impossible(f"최소한 하나 이상을 선택하세요.")
        else:
            raise Impossible(f"최대 {item.stack_count - 1}개 까지만 선택할 수 있습니다.")

    def check_has_enough_money(self, amount: int) -> bool:
        """check if there is enough money(shine) in this inventory component as given amount."""
        cash = self.check_if_in_inv("shine")
        if cash:
            if cash.stack_count >= amount:
                return True
        return False

    def get_total_price_to_pay(self) -> int:
        """Return the price that the player owes to someone."""
        price = 0
        for item in self.items:
            if item.item_state.is_being_sold_from:
                price += item.price_of(self.parent)
        return price

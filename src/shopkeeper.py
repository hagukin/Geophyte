import components.ai as ai
import copy
import color

from actions import Action
from typing import List, Tuple, Optional
from actions import WaitAction, CashExchangeAction
from entity import Actor, Item
from korean import grammar as g


class Shopkeeper_Ai(ai.BaseAI):
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        """
        Vars:
            customers:
                Dictionary.
                Key: customers in the shop. All actor are handled as customers.
                Value: the money they own.
            thieves:
                List of thieves. All actor can become a thief.
            picked_up:
                Dictionary.                
                Keys: The item the customer picked up.
                Value: Customer who picked up the item. Set to None if its not picked up.
        """
        super().__init__(alignment, do_melee_atk, use_ability, do_ranged_atk)
        self.room = None # Initialized during custom_terrgen.spawn_shopkeeper() FIXME
        self.customers = dict()
        self.thieves = set()
        self.picked_up = dict()

    def get_target_shopkeeper(self) -> Optional[Actor]:
        """
        Set target only if the actor fits this ai's condition of being hostile to.
        If there is this ai has no hostile types, species, or entities, it will act peacefully.
        Return: the target actor
        """
        # The AI will start targeting only when its in player's sight due to performance issues.
        # NOTE: Ai's vision is already up to date if it is active and in player's sight
        tmp = None
        while True:
            if len(self.thieves) > 0:
                tmp = self.thieves.pop()
            else:
                break

            if tmp.actor_state.is_dead:
                self.thieves.add(tmp)
                break
            else:
                continue
        return tmp

    def idle_action(self) -> Action: #Override
        return self.wait_for_customer()

    def perform_shopkeeping(self) -> None:
        """
        NOTE: Shopkeeper will stop tracking down the target if its out of sight and it didn't stole anything.
        """
        # If attacked, react to the attacker first
        self.set_revenge_target()

        if self.target and not self.target.actor_state.is_dead:
            # shopkeeper will keep chase its target until they die.
            # during this process, if anyone steals an item from their (unprotected) shop, they are going to become a target as well.
            return self.perform_hostile()
        else:
            self.target = self.get_target_shopkeeper()
        
        # Update values
        self.update_pickup_items()
        self.update_customers()
        self.update_thieves()

        action = self.wait_for_customer
        for picked_by in self.picked_up.values():
            if picked_by:
                action = self.waiting_for_payment
                break
                
        return action()

    def update_customers(self) -> None:
        """Refresh current customers' information and their dept."""
        curr_customers = self.room.get_actors_in_room()
        prev_customer = copy.copy(self.customers)
        self.customers = {} # Reset customer status

        for customer in curr_customers:
            if customer in self.customers:
                continue
            elif customer in prev_customer:
                self.customers[customer] = prev_customer[customer]
            else:
                self.customers[customer] = 0 # Has no dept

    def update_pickup_items(self) -> None:
        for shop_item in self.room.terrain.items_on_stock:
            if shop_item.parent:
                self.picked_up[shop_item] = shop_item.parent.parent
            else:
                self.picked_up[shop_item] = None

    def update_thieves(self) -> None:
        for picked_actor in self.picked_up.values():
            if picked_actor != None and picked_actor not in self.customers.keys():
                # Found a thief
                self.thieves.add(picked_actor)

    def wait_for_customer(self) -> None:
        """
        There are no customers in the shop, or the customer doesn't own anything from the shop yet.
        The shopkeeper will not block the exit.
        """
        if self.parent.x != self.room.terrain.shopkeeper_loc[0] and self.parent.y != self.room.terrain.shopkeeper_loc[1]\
            and not self.path:
            self.path = self.get_path_to(self.room.terrain.shopkeeper_loc[0], self.room.terrain.shopkeeper_loc[1])
        return self.move_path()

    def waiting_for_payment(self):
        """
        The customer has picked up an item and still has it.
        The shopkeeper will try to block the exit, and if customer leaves the shop, the shopkeeper will consider that customer as a thief.
        """
        if self.parent.x != self.room.doors[0][0] and self.parent.y != self.room.doors[0][1]\
            and not self.path:
            self.path = self.get_path_to(self.room.doors[0][0], self.room.doors[0][1])
        return self.move_path()
        
    def add_item_to_shop(self, item: Item) -> None:
        item.item_state.is_being_sold_from = id(self.parent)
        self.room.terrain.items_on_stock.append(item)
        self.picked_up[item] = None

    def remove_item_from_shop(self, item: Item) -> None:
        item.item_state.is_being_sold_from = None
        item.stackable = True
        self.room.terrain.items_on_stock.remove(item)
        self.picked_up.pop(item)

    def has_dept(self, customer: Actor) -> bool:
        """Return whether the customer has any bills to pay."""
        for picked_actor in self.picked_up.values():
            if picked_actor == customer:
                return True
        return False
   
    def dept_of_actor(self, customer: Actor) -> int:
        """Return how much money does the given customer owes."""
        dept = 0
        for item, buyer in self.picked_up.items():
            if buyer == customer:
                dept += item.price_of(customer, discount=1)
        return dept

    def take_cash(self, customer: Actor, cash_amount: int) -> None:
        """Take cash from the customer."""
        CashExchangeAction(customer, self.parent, cash_amount).perform()

    def give_cash(self, customer: Actor, cash_amount: int) -> None:
        """Give cash to the customer."""
        CashExchangeAction(self.parent,customer, cash_amount).perform()

    def purchase_item(self, customer: Actor, item: Item) -> None:
        """
        Purchase item from the customer.
        NOTE: You should check whether the shopkeeper has enough money or not before calling this method.
        NOTE: in order to sell an item, item should have no owner, and it should be located in shop's inner area.
        """
        if not self.room.check_if_in_room(item.x, item.y): # Check if item is in the shop
            raise Exception() #Should not try to purchase items that are located outside of the shop

        buying_price = item.price_of(item, 0.7)
        if self.parent.inventory.check_has_enough_money(buying_price):
            self.give_cash(customer, buying_price)
            self.add_item_to_shop(item)
            self.engine.message_log.add_message(f"{g(item.name, '이')} {g(item.name, '을')} {buying_price}샤인에 판매했다.", fg=color.shop_sold)
        else:
            return None

    def sell_item(self, customer: Actor, item: Item) -> None:
        """Sell item to the customer."""
        selling_price = item.price_of(item, 1)
        if customer.inventory.check_has_enough_money(selling_price):
            self.take_cash(customer, selling_price)
            self.remove_item_from_shop(item)
            self.engine.message_log.add_message(f"{g(customer.name, '이')} {g(item.name, '을')} {selling_price}샤인에 구매했다.", fg=color.shop_purchased)
        else:
            return None

    def sell_all_picked_ups(self, customer: Actor) -> None:
        """Sell all items that the customer picked up."""
        bill = 0
        buyings = []
        for item, buyer in self.picked_up.items():
            if buyer == customer:
                bill += item.price_of(customer, discount=1)
                buyings.append(item)
        # bill is 0
        if bill <= 0:
            print("ERROR::CUSTOMER TRIED TO PURCHASE WHILE NOT PICKING UP ANYTHING FROM THE SHOP. - shopkeeper.py")
            return None

        # Customer has insufficient money
        if not customer.inventory.check_has_enough_money(bill):
            self.engine.message_log.add_speech(f"가지고 계신 돈이 부족한 것 같습니다.", speaker=self.parent, stack=False)
            return None

        # Purchase everything
        for buying in buyings:
            self.sell_item(customer, buying)
        self.engine.message_log.add_speech("좋은 거래였습니다.", speaker=self.parent, stack=False)

    def perform(self) -> None:
        """
        Check if this actor is in player's sight.
        Actor's self.active will be set to True after being seen once.
        """
        # active check
        self.check_active()

        # Shopkeepers will update vision even if ai's not in player's sight. #TODO: check for perf issue
        if self.active:
            self.update_vision()

        # immobility check
        if self.parent.check_for_immobility():
            return WaitAction(self.parent).perform()
        
        # target check
        self.disable_targeting_ally()

        return self.perform_shopkeeping()

    

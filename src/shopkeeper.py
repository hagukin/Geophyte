import components.ai as ai
import copy

from actions import WaitAction
from entity import Actor, Item
from korean import grammar as g


class Shopkeeper_Ai(ai.BaseAI):
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False,):
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
                Value: Customer who picked up the item.
        """
        super().__init__(alignment, do_melee_atk, use_ability, do_ranged_atk)
        self.room = None # Initialized during custom_terrgen.spawn_shopkeeper() FIXME
        self.customers = dict()
        self.thieves = set()
        self.picked_up = dict()

    @staticmethod
    def price_of(self, buyer: Actor, item: Item) -> int:
        """Return the price of the given item for given actor."""
        #TODO
        raise NotImplementedError()

    def perform_shopkeeping(self) -> None:
        # Hunt down thieves
        if not self.target and len(self.thieves) != 0:
            self.target = self.thieves.pop()
        if self.target:
            return self.perform_hostile()
        
        # Update values
        self.update_pickup_items()
        self.update_customers()
        self.update_thieves()

        action = self.wait_for_customer
        for picked_by in self.picked_up.values():
            if picked_by:
                action = self.waiting_for_payment
                
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

        if self.target or self.attacked_from:
            return self.perform_hostile()
        return self.perform_shopkeeping()

    

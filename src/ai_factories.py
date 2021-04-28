import components.ai as ai
import color
import explosion_action
import copy

from actions import WaitAction
from room import Room
from order import InventoryOrder
from korean import grammar as g

class Melee_Ai(ai.BaseAI):
    """Melee AI that only attacks humans."""
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

class Melee_Neutral_Ai(ai.BaseAI):
    """Neutral melee AI."""
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, use_ability, do_ranged_atk)

class Test_Ai(ai.BaseAI):
    """Pickup Eat testing"""
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, attracted_eat_type: set=set(["meat"]), attracted_own_type: set=set([InventoryOrder.POTION])):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, attracted_eat_type=attracted_eat_type, attracted_own_type=attracted_own_type)


####################################################
#################### @ - humans  ###################
####################################################

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


####################################################
###################### a - ants  ###################
####################################################

class Fire_Ant_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

        # Fire dmg, 50%
        self.melee_effects_var.append([1, 0, 0, 4])
        self.melee_effects.append(("burn_target", 0.5))

class Volt_Ant_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

        # Elec dmg, 80%
        self.melee_effects_var.append([2, 0.5])
        self.melee_effects.append(("electrocute_target", 0.8))


####################################################
################  e - eyes & brains  ###############
####################################################

class Floating_Eye_Ai(ai.BaseAI):
    def __init__(self, alignment:str="peaceful", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):#do_ranged_atk은 마법과 투사체 모두 포함한다.
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)

    def perform_peaceful(self):
        # When the AI is attacked, and the attacker is in sight, paralyze the actor and reset the target.
        if self.attacked_from:
            import numpy as np
            import tcod

            # Set vision
            monster_vision = np.full(
                (self.parent.gamemap.width, self.parent.gamemap.height), fill_value=False, order="F"
            )

            # Update the vision (The size of the visible area is proportional to this actor's eyesight)
            monster_vision[:] = tcod.map.compute_fov(
                self.parent.gamemap.tiles["transparent"],
                (self.parent.x, self.parent.y),
                radius=self.parent.status.changed_status["eyesight"],
            )

            # Check if the target is in radius, and if the target is not already paralyzed
            if monster_vision[self.attacked_from.x, self.attacked_from.y] and self.attacked_from.actor_state.is_paralyzing == [0,0]:
                self.attacked_from.actor_state.apply_paralyzation([0, 15])

                # Message log
                if self.engine.game_map.visible[self.parent.x, self.parent.y] or self.engine.game_map.visible[self.attacked_from.x, self.attacked_from.y]:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(self.attacked_from.name, '을')} 바라본다.", color.white)

                self.attacked_from = None

        return super().perform_peaceful()


####################################################
############### i = flying insects  ################
####################################################

class Giant_Wasp_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

        # Poison dmg, 20%
        self.melee_effects_var.append([1, 1, 0, 3])
        self.melee_effects.append(("poison_target", 0.2))


####################################################
############### j - jellies / slimes  ##############
####################################################

class Black_Jelly_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=True,  use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

        # Poison dmg, 10%
        self.melee_effects_var.append([2, 1, 0, 2])
        self.melee_effects.append(("poison_target", 0.3))

    def check_is_ranged_atk_possible(self, attacker, target):
        # Check for ammo
        ammo = attacker.inventory.check_if_in_inv(item_id="toxic_goo")
        if not ammo:
            return False

        # Set direction and Check if the target is in attackable radius
        direction = self.get_ranged_direction(attacker=attacker, target=target, valid_range=ammo.throwable.throw_distance(attacker))

        if direction:
            return direction, ammo
        else:
            return False


####################################################
#################### n - nymphs  ###################
####################################################

class Nymph_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=True, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

    def check_is_use_ability_possible(self, attacker, target):
        ### FLOW
        # 1. Check if the AI has the abilities that they can use.
        # 2. Check for valid range, mana, etc.
        # 3. If it all satisfies the conditions, return ability object from this AI's parent.
        ###
        ability_chosen = None
        coordinate = None
        
        # A. Steal
        if not ability_chosen:
            if not self.parent.inventory.check_if_full():
                # Check if this actor has the ability
                steal = self.parent.ability_inventory.get_ability_by_id("sk_steal")
                # Set the direction and check the range
                dxdy = self.get_ranged_direction(attacker=attacker, target=target, valid_range=1)
                if dxdy:
                    coordinate = self.parent.x + dxdy[0], self.parent.y + dxdy[1]
                # Ignore mana since this is a "Skill" not a "Spell"
                if steal and coordinate:
                    ability_chosen = steal

        # B. Lightning Bolt
        if not ability_chosen:
            # Check if this actor has the ability
            lightning_bolt = self.parent.ability_inventory.get_ability_by_id("m_lightning_bolt")
            # Set the direction and check the range (Lightning bolt spell has no direction)
            coordinate = None
            # Check mana
            if lightning_bolt and self.parent.status.changed_status["mp"] >= lightning_bolt.activatable.mana_cost:
                ability_chosen = lightning_bolt

        # Return coordinate, target, and ability object
        if ability_chosen:
            return coordinate, target, ability_chosen
        else:
            return False


####################################################
#################### o - spheres  ##################
####################################################

class Sphere_Of_Acid_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

    def get_melee_action(self, dx, dy):
        """
        Return the action this ai will perform when its melee attacking something.
        If the ai has any sort of special effects to its melee attack, its passed as a parameter.
        """
        explosion_action.AcidExplodeAction(self.parent, False, True, radius=2, expl_dmg=50, dmg_reduction_by_dist=10, cause_fire=0).perform()
        self.parent.status.die()


####################################################
############# s - spiders & scorpions  #############
####################################################

class Jumping_Spider_Ai(ai.BaseAI):
    """Only attacks earthworms"""
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_id=set('maggot')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_id=hostile_id)


####################################################
#####################  w - worms  ##################
####################################################


####################################################
################## E - ELEMENTALS  #################
####################################################

class Ice_Elemental_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

        # Cold dmg, 50%
        self.melee_effects_var.append([2, 1, 0.2, 0, 3]) # 20% chance of freezing target
        self.melee_effects.append(("freeze_target", 0.5))


####################################################
################## I - IMPOSTERS  ##################
####################################################

class Chatterbox_Ai(ai.BaseAI):
    #TODO: make Chatterbox chatter
    def __init__(self, alignment:str="allied", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, allied_id:set = set("chatterbox")):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, allied_id=allied_id)

        # Bleed dmg, 30%
        self.melee_effects_var.append([1, 0, 4])
        self.melee_effects.append(("bleed_target", 0.3))

#@
shopkeeper_ai = Shopkeeper_Ai()
#a
ant_ai = Melee_Ai()
fire_ant_ai = Fire_Ant_Ai()
volt_ant_ai = Volt_Ant_Ai()
#b
bat_ai = Melee_Neutral_Ai()
#c
kitten_ai = Melee_Ai()
cat_ai = Melee_Ai()
large_cat_ai = Melee_Ai()
#d
puppy_ai = Melee_Ai()
dog_ai = Melee_Ai()
large_dog_ai = Melee_Ai()
#e
floating_eye_ai = Floating_Eye_Ai()
#s
jumping_spider_ai = Melee_Ai()
#i
fly_ai = Melee_Ai()
giant_wasp_ai = Giant_Wasp_Ai()
#j
black_jelly_ai = Black_Jelly_Ai()
#n
nymph_ai = Nymph_Ai()
#o
sphere_of_acid_ai = Sphere_Of_Acid_Ai()
#w
earthworm_ai = Melee_Neutral_Ai()
maggot_ai = Melee_Neutral_Ai()
#E
ice_elemental_ai = Ice_Elemental_Ai()
#I
chatterbox_ai = Chatterbox_Ai()
#T
giant_ai = Melee_Ai()

DEBUG_ai = Melee_Ai()
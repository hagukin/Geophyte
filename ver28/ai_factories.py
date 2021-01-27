import components.ai as ai
import color
import actions

class Melee_Ai(ai.BaseAI):
    """Melee AI that only attacks humans."""
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False, hostile_type: set=set('@')):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type)

class Melee_Neutral_Ai(ai.BaseAI):
    """Neutral melee AI."""
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, use_ability, do_ranged_atk)


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
                self.attacked_from.actor_state.is_paralyzing = [0, 15]

                # Message log
                if self.engine.game_map.visible[self.parent.x, self.parent.y] or self.engine.game_map.visible[self.attacked_from.x, self.attacked_from.y]:
                    self.engine.message_log.add_message(f"{self.parent.name} stares at the {self.attacked_from.name}.", color.white)

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
        self.melee_effects_var.append([1, 1, 0, 2])
        self.melee_effects.append(("melt_target", 0.3))

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


#a
ant_ai = Melee_Ai()
fire_ant_ai = Fire_Ant_Ai()
volt_ant_ai = Volt_Ant_Ai()
#b
bat_ai = Melee_Ai()
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
giant_wasp_ai = Giant_Wasp_Ai()
#j
black_jelly_ai = Black_Jelly_Ai()
#n
nymph_ai = Nymph_Ai()
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
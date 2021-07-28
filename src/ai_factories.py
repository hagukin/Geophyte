import random

import components.ai as ai
import color
import explosion_action
import copy
from shopkeeper import Shopkeeper_Ai
from order import InventoryOrder
from korean import grammar as g

class Melee_Ai(ai.BaseAI):
    """Melee AI that only attacks humans."""
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

class Melee_Neutral_Ai(ai.BaseAI):
    """Neutral melee AI."""
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, use_ability, do_ranged_atk)

class Test_Ai(ai.BaseAI):
    """Pickup Eat testing"""
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.attracted_eat_type.add("meat")
        self.attracted_own_type.add(InventoryOrder.POTION)


####################################################
#################### @ - humans  ###################
####################################################




####################################################
###################### a - ants  ###################
####################################################

class Fire_Ant_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')
        # Fire dmg, 50%
        self.melee_effects_var.append((1, 0, 0, 4))
        self.melee_effects.append(("burn_target", 0.5))

class Volt_Ant_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')
        # Elec dmg, 80%
        self.melee_effects_var.append((2, 0.5))
        self.melee_effects.append(("electrocute_target", 0.8))


####################################################
#####################  d - dogs  ###################
####################################################

class Cerberus_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')
        # Fire dmg, 50%
        self.melee_effects_var.append((3, 1, 0, 6))
        self.melee_effects.append(("burn_target", 0.2))


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
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')
        # Poison dmg, 20%
        self.melee_effects_var.append((1, 1, 0, 3))
        self.melee_effects.append(("poison_target", 0.2))

class Fly_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')
        self.attracted_eat_type.add('meat')
        self.attracted_eat_type.add('insect')

####################################################
############### j - jellies / slimes  ##############
####################################################

class Black_Jelly_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=True,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')
        # Poison dmg, 10%
        self.melee_effects_var.append((2, 1, 0, 2))
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
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=True):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

####################################################
#################### o - spheres  ##################
####################################################

class Sphere_Of_Acid_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

    def get_melee_action(self, dx, dy):
        """
        Return the action this ai will perform when its melee attacking something.
        If the ai has any sort of special effects to its melee attack, its passed as a parameter.
        """
        explosion_action.AcidExplodeAction(self.parent, False, True, radius=2, expl_dmg=50, dmg_reduction_by_dist=10, cause_fire=0).perform()
        self.parent.status.death()


####################################################
############# s - spiders & scorpions  #############
####################################################

class Jumping_Spider_Ai(ai.BaseAI):
    """Only attacks earthworms"""
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_id.add('maggot')

####################################################
#####################  w - worms  ##################
####################################################

class Maggot_Ai(Melee_Neutral_Ai):
    """Prioritize eating over fighting (is neutral)"""
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.attracted_eat_type.add('meat')
        self.attracted_eat_type.add('insect')

####################################################
################## E - ELEMENTALS  #################
####################################################

class Fire_Elemental_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

        # Fire dmg, 50%
        self.melee_effects_var.append((5, 5, 0, 6)) # 20% chance of freezing target
        self.melee_effects.append(("burn_target", 0.5))

class Ice_Elemental_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

        # Cold dmg, 50%
        self.melee_effects_var.append((2, 1, 0.2, 0, 3)) # 20% chance of freezing target
        self.melee_effects.append(("freeze_target", 0.5))

class Earth_Elemental_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')
        # No special melee effect

class Acid_Elemental_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

        # Acid dmg, 50%
        self.melee_effects_var.append((9, 1, 0, 6))
        self.melee_effects.append(("melt_target", 0.5))

class Poison_Elemental_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)

        # Poison dmg, 20%
        self.melee_effects_var.append((4, 2, 0, 10))
        self.melee_effects.append(("poison_target", 0.2))

class Lightning_Elemental_Ai(ai.BaseAI):
    def __init__(self, alignment:str="hostile", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

        # Electrical dmg, 100%
        self.melee_effects_var.append((5, 0.7))
        self.melee_effects.append(("electrocute_target", 1))


####################################################
################## I - IMPOSTERS  ##################
####################################################

class Chatterbox_Ai(ai.BaseAI):
    #TODO: make Chatterbox chatter
    def __init__(self, alignment:str="allied", do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.allied_id.add('chatterbox')

        # Bleed dmg, 30%
        self.melee_effects_var.append((1, 0, 4))
        self.melee_effects.append(("bleed_target", 0.3))

    def lure_speech(self):
        lure = random.choice(self.engine.item_manager.items_lists)
        speech = random.choice(
            [
                "누가 좀 도와주세요! 거기 아무도 없어요?",
                "살려줘! 이 괴물이 나를 공격하고 있어!",
                "날 좀 도와주게... 답례는 충분히 하겠네...",
                "살려주세요... 목숨만은 제발...",
                "좋아, 이 정도 돈이면 충분하겠어.",
                "거기 누구 있나요? 있다면 대답해주세요!",
                "(노래를 흥얼거리는 소리)",
                "오늘은 운수가 좋은 날이군, 이런 귀한 걸 얻게 되다니.",
                "어이, 이 쪽으로 잠깐 와봐."
            ]
        )
        self.engine.message_log.add_speech(text=speech, speaker=self.parent, stack=False)

    def move_path(self) -> None:
        if random.random() < 0.05:
            self.lure_speech()
        super().move_path()


####################################################
################ M - Mythical Beasts  ##############
####################################################)

class Baby_Phoenix_Ai(ai.BaseAI):
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)

        # Fire dmg, 90%
        self.melee_effects_var.append((7, 2, 0, 4))
        self.melee_effects.append(("burn_target", 0.8))


class Phoenix_Ai(ai.BaseAI):
    def __init__(self, alignment:str="neutral", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)

        # Fire dmg, 90%
        self.melee_effects_var.append((10, 5, 0, 6))
        self.melee_effects.append(("burn_target", 0.9))


####################################################
################ O - Orcs & Ogres ##################
####################################################

class Ogre_Ai(ai.BaseAI):
    def __init__(self, alignment:str="allied", do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.allied_id.add('ogre')


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
cerberus_ai = Cerberus_Ai()
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
maggot_ai = Maggot_Ai()
#E
fire_elemental_ai = Fire_Elemental_Ai()
ice_elemental_ai = Ice_Elemental_Ai()
earth_elemental_ai = Earth_Elemental_Ai()
poison_elemental_ai = Poison_Elemental_Ai()
acid_elemental_ai = Acid_Elemental_Ai()
lightning_elemental_ai = Lightning_Elemental_Ai()
#I
chatterbox_ai = Chatterbox_Ai()
#M
baby_phoenix_ai = Baby_Phoenix_Ai()
phoenix_ai = Phoenix_Ai()
#O
ogre_ai = Ogre_Ai()
#T
giant_ai = Melee_Ai()

DEBUG_ai = Melee_Ai()
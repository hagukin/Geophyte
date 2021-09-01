import random
from typing import Tuple

import components.ai as ai
import color
import explosion_action
import copy
from shopkeeper import Shopkeeper_Ai
from order import InventoryOrder
from korean import grammar as g


####################################################
#################### @ - humans  ###################
####################################################


####################################################
################  e - eyes & brains  ###############
####################################################

class Floating_Eye_Ai(ai.BaseAI):
    def __init__(self, alignment:Tuple=(("peaceful",),(1,)), do_melee_atk:bool=True, do_ranged_atk: bool=False,  use_ability: bool=False):#do_ranged_atk은 마법과 투사체 모두 포함한다.
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
                # Message log
                if self.engine.game_map.visible[self.parent.x, self.parent.y] or self.engine.game_map.visible[self.attacked_from.x, self.attacked_from.y]:
                    if self.attacked_from.name == self.engine.player:
                        self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 당신을 바라본다.", color.player_debuff)
                    else:
                        self.engine.message_log.add_message(f"{g(self.parent.name, '이')} {g(self.attacked_from.name, '을')} 바라본다.", color.enemy_unique)

            if self.attacked_from.actor_state.has_eye:
                self.attacked_from.actor_state.apply_paralyzation([0, 15])
            self.attacked_from = None

        return super().perform_peaceful()


####################################################
############### i = flying insects  ################
####################################################


####################################################
############### j - jellies / slimes  ##############
####################################################

class Black_Jelly_Ai(ai.BaseAI):
    def __init__(self, alignment:Tuple=(("hostile",),(1,)), do_melee_atk:bool=True, do_ranged_atk: bool=True,  use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

    def check_is_ranged_atk_possible(self, attacker, target):
        # Check for ammo
        from item_factories import toxic_goo
        ammo = toxic_goo.copy(gamemap=attacker.gamemap)

        # Set direction and Check if the target is in attackable radius
        direction = self.get_ranged_direction(attacker=attacker, target=target, valid_range=999) # Use ammo.throwable.throw_distance(attacker) when making other ais.

        if direction:
            return direction, ammo
        else:
            return False


####################################################
#################### n - nymphs  ###################
####################################################

class Nymph_Ai(ai.BaseAI):
    def __init__(
            self,
            alignment=(("hostile",), (1,)),
            do_melee_atk=True,
            do_ranged_atk=False,
            use_ability=True,
            hostile_type=('@',),
            attracted_own_type=(InventoryOrder.GEM, InventoryOrder.CASH, InventoryOrder.AMULET, )
    ):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability, hostile_type=hostile_type, attracted_own_type=attracted_own_type)

    def nymph_check_if_should_teleport(self) -> bool:
        """
        'should_teleport' != 'can_teleport'
        Even if this fucntion returns True, it does not mean that nymph will always teleport.
        """
        if self.parent.inventory.check_if_full() and self.target:
            return True
        return False

    def nymph_check_if_can_teleport(self) -> bool:
        if self.parent.inventory.check_if_in_inv(item_id="scroll_of_teleportation"):
            return True
        else:
            return False

    def nymph_read_scroll_of_teleportation(self) -> None:
        from actions import ReadItem
        scroll = self.parent.inventory.check_if_in_inv(item_id="scroll_of_teleportation")
        if scroll:
            return ReadItem(self.parent, item=scroll, target_xy=(self.parent.x, self.parent.y)).perform() # NOTE: target_xy is not used. ai will teleport to randomized location regardless of BUC.
        else:
            print("ERROR::nymph_check_if_can_teleport is True, but nymph has no scroll of teleportation. This should've been prevented.")
            return None

    def perform_hostile(self) -> None:
        # If inventory is full, and ai has target, ai will set target to None and try read teleportation scroll.
        # (the better way to approach is to check whether nymph has successfully stolen an item, but it could make ai structure unstable
        if self.nymph_check_if_should_teleport():
            if self.nymph_check_if_can_teleport():
                self.target = None
                return self.nymph_read_scroll_of_teleportation()

        return super().perform_hostile()



####################################################
#################### o - spheres  ##################
####################################################

class Sphere_Of_Acid_Ai(ai.BaseAI):
    def __init__(self, alignment:Tuple=(("hostile",),(1,)), do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.hostile_type.add('@')

    def perform_melee_action(self, dx, dy):
        """
        Return the action this ai will perform when its melee attacking something.
        If the ai has any sort of special effects to its melee attack, its passed as a parameter.
        """
        explosion_action.AcidExplodeAction(self.parent, False, True, radius=2, expl_dmg=50, dmg_reduction_by_dist=10, cause_fire=0).perform()


####################################################
############# s - spiders & scorpions  #############
####################################################

####################################################
#####################  w - worms  ##################
####################################################

####################################################
################## E - ELEMENTALS  #################
####################################################

####################################################
################## I - IMPOSTERS  ##################
####################################################

class Chatterbox_Ai(ai.BaseAI):
    #TODO: make Chatterbox chatter
    def __init__(self, alignment:Tuple=(("allied",),(1,)), do_melee_atk:bool=True, do_ranged_atk: bool=False, use_ability: bool=False):
        super().__init__(alignment, do_melee_atk, do_ranged_atk, use_ability)
        self.allied_id.add('chatterbox')

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
####################################################

####################################################
################ O - Orcs & Ogres ##################
####################################################
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, List, Set, Tuple, Any

from numpy.core.fromnumeric import sort
from components.base_component import BaseComponent
from korean import grammar as g
from components.status import Bonus

import random
import math
import copy
import color

if TYPE_CHECKING:
    from entity import Item, Actor

class ActorState(BaseComponent):
    """
    Values that are directly related to the actor's state of being are stored here.
    """
    def __init__(self,
        ### Hunger
        # Negative value indicates not being hungry at all.
        # 1 points of hunger is about 5 kcal irl, and if the actor will consume 1 points of hunger each turn. TODO: Maybe make some actions costs hunger more?
        hunger: int = -1,

        ### Regeneration of health
        # If set to True, the actor will regenerate health in proportion to the actor's constitution.
        heal_wounds: bool = False,
        regain_mana: bool = True,

        ### Death
        # This value indicates the whether the actor is completely out of the game or not.
        # This does not indicates the in-game state of death. 
        # (Undead type characters will still have this value as True, as long as they are 'alive' in the game.)
        is_dead: bool = False,

        ### Physical attributes
        ### Size
        # Reference
        # 1 : Under 10cm height or has no physical size 
        # 2 : Under 50cm height
        # 3 : Under 1m height (Dwarves)
        # 4 : Under 2m height (Humans)
        # 5 : Under 4m height (Trolls, Small dragons)
        # 6 : Under 8m height (Nightwalkers, Adult dragons)
        # 7 : Over 8m height (Giant worm, Elder dragons)
        size: int = 4,

        ### Sexuality
        # If it has a sexuality, save it as a string form. (ex. "male")
        # If it has no sexuality, save it as a "None". NOTE: This is a string value. N,o,t,e "None"
        # If it has other sexuality besides male and female, save it as "GENDER_TYPE" (ex. "Helicopter")
        sexuality: str = random.choice(("male", "female")),

        # Used in equipments.py
        is_right_handed: bool = True,

        ### Status effects - Physical
        # NOTE: WARNING - If any of the default values of the status effects is changed, make sure to change actor_state.remove_all_actor_states() as well.
        # NOTE: 'Effect lasting for negative turns' are considered as lasting infinitly. = if max turn is negative, effects goes on forever
        # Actor is on fire / Actor is emitting fire from its body
        # Value: [Initial damage, Damage decrease per turn, Current turn, Max lasting turn]
         is_burning=None,
        # Actor is poisoned
        # Value: [Initial damage, Damage increase per turn, Current turn, Max lasting turn]
         is_poisoned=None,
        # Actor is freezing
        # Value: [Damage per turn, Agility decrease per turn(will stack), Chance of getting frozen per turn, Current turn, Max lasting turn]
         is_freezing=None,
        # Actor is completely frozen
        # Value: [Damage per turn, Current turn, Max lasting turn]
         is_frozen=None,
        # Actor is being electrocuted / Actor is emitting electricity from its body
        # Value: [Damage taken by this actor, Damage taken by adjacent actor indicated as ratio(0~1) to the damage taken by this actor]
         is_electrocuting=None,
        # Actor is invisible
        # Value: [Current turn, Max lasting turn]
         is_invisible=None,
        # Actor is phasing (or is able to phase)
        # Value: [Current turn, Max lasting turn]
         is_phasing=None,
        # Actor is paralyzed
        # Value: [Current turn, Max lasting turn]
         is_paralyzing=None,
        # Actor is bleeding
        # Value: [Damage per turn, Current turn, Max lasting turn]
         is_bleeding=None,
        # Actor is slowed down
        # Value: [Agility decrease each turn(will not stack), Current turn, Max lasting turn]
         is_acting_slower=None,
        # Actor is sped up
        # Value: [Agility increase each turn(will not stack), Current turn, Max lasting turn]
         is_acting_faster=None,
        # Actor is melting from acid
        # Value: [Damage per turn, Damage decrease per turn, Current turn, Max lasting turn]
         is_melting=None,
        # Actor is sick (besides from poison)
        # Value: [Damage per turn(Percentage of maximum health, range from 0~1), Current turn, Max lasting turn]
         is_sick=None,
        # Actor is floating unwillingly
        # NOTE: To check whether the actor is on air or not, use entity.is_on_air instead.
        # is_levitating value's sole purpose is to give actor a status effect of floation.
        # Value: [Current turn, Max lasting turn]
         is_levitating=None,
        # Actor is drowning
        # Value: [Current turn, Turns needed for drowning(this is NOT turns left before drowning)]
         is_drowning=None,

        ### Status effects - Non-physical
        # Actor is sleeping
        # Value: [Current turn, Max lasting turn]
         is_sleeping=None,
        # Actor is angry (most possibly unwillingly)
        # Value: [Current turn, Max lasting turn]
         is_angry=None,
        # Actor is confused
        # Value: [Current turn, Max lasting turn]
         is_confused=None,
        # Actor is hallucinating
        # Value: [Current turn, Max lasting turn]
         is_hallucinating=None,
        # Actor can detect things that are out of sight
        # Value: [Current turn, Max lasting turn, List with strings: object type]
        # NOTE: Detection != telepathy
         is_detecting_obj=None,

        ### Spatial states
        # Actor is on air (whether willingly or unwillingly)
        # NOTE: all flying actors' entity.is_on_air must be True
        is_flying: bool = False,
        # Actor is in a deep pit
        is_in_deep_pit: bool = False,
        # Actor is in a shallow pit
        is_in_shallow_pit: bool = False,
        # Actor is submerged partially or fully
        is_submerged: int = False,
        # Actor was submerged partially or fully
        was_submerged: int = False,
        # Actor is submerged completely
        is_underwater: bool = False,

        ### Physical states
        has_head: int = 1,
        has_left_arm: bool = True,
        has_right_arm: bool = True,
        has_leg: bool = True, # has one or more leg
        has_wing: bool = False, # NOTE: Warning) If creature has wing and can fly, it is interpreted as the creature cannot fly without its wings.
        has_eye: bool = True, # has one or more eye (A sensor that can work as an eye is also considered an eye)
        has_torso: bool = True, # has torso (Arms are unnecessary)
        has_blood: bool = True, # has blood
        has_soul: bool = True, # has soul
        need_breathe: bool = True, # need to breathe oxygen to live

        ### Physical capabilities
        can_swim: bool = False,
        can_breathe_underwater: bool = False,
        can_fly: bool = False,
        can_move_on_surface: bool = True, # including walking, crawling, etc. NOTE: This does not include flying, levitating, etc. #TODO make fly-only creatures unable to move without its flying ability
        has_immortality: bool = False,
        has_telepathy: bool = False,
        can_revive_self: bool = False, # can revive after actor dies
        revive_as: Actor = None, # If set to None, and can_revive_self is True, revive as this actor.

        ### Mental capabilities
        can_think: bool = True, # Has ability to make the most basic level of logical decision (e.g. feels pain -> moves away)
        can_talk: bool = False, # Is capable of speaking a language
    ):
        """
        Vars:
            encumbrance:
                Current state of burden.
                This value is only affected by inventory weight.
                0 - not burdened
                1 - burdened
                2 - stressed
                3 - overloaded
                4 - immovable
        """
        super().__init__(None)

        if is_burning is None:
            is_burning = [0, 0, 0, 0]
        if is_poisoned is None:
            is_poisoned = [0, 0, 0, 0]
        if is_freezing is None:
            is_freezing = [0, 0, 0, 0, 0]
        if is_frozen is None:
            is_frozen = [0, 0, 0]
        if is_electrocuting is None:
            is_electrocuting = [0, 0]
        if is_invisible is None:
            is_invisible = [0, 0]
        if is_phasing is None:
            is_phasing = [0, 0]
        if is_paralyzing is None:
            is_paralyzing = [0, 0]
        if is_bleeding is None:
            is_bleeding = [0, 0, 0]
        if is_acting_slower is None:
            is_acting_slower = [0, 0, 0]
        if is_acting_faster is None:
            is_acting_faster = [0, 0, 0]
        if is_melting is None:
            is_melting = [0, 0, 0, 0]
        if is_sick is None:
            is_sick = [0.0, 0, 0]
        if is_levitating is None:
            is_levitating = [0, 0]
        if is_drowning is None:
            is_drowning = [0, 0]
        if is_sleeping is None:
            is_sleeping = [0, 0]
        if is_angry is None:
            is_angry = [0, 0]
        if is_confused is None:
            is_confused = [0, 0]
        if is_hallucinating is None:
            is_hallucinating = [0, 0]
        if is_detecting_obj is None:
            is_detecting_obj = [0, 0, []]
        self.hunger = hunger
        self.previous_hunger_state = self.hunger

        self.heal_wounds = heal_wounds
        self.heal_interval = 0 # Interval between health regenerations
        self.regain_mana = regain_mana
        self.regain_interval = 0 # Interval between mana regenerations

        self.is_dead = is_dead
    
        self.size = size
        self.sexuality = sexuality
        self.is_right_handed = is_right_handed

        self.encumbrance = 0 # Burden bonus is handled in inventory.
        self.previous_encumbrance = self.encumbrance

        self.is_burning = is_burning
        self.is_poisoned = is_poisoned
        self.is_freezing = is_freezing
        self.is_frozen = is_frozen
        self.is_electrocuting = is_electrocuting
        self.is_invisible = is_invisible
        self.is_phasing = is_phasing
        self.is_paralyzing = is_paralyzing
        self.is_bleeding = is_bleeding
        self.is_acting_slower = is_acting_slower
        self.is_acting_faster = is_acting_faster
        self.is_melting = is_melting
        self.is_sick = is_sick
        self.is_levitating = is_levitating
        self.is_drowning = is_drowning

        self.is_sleeping = is_sleeping
        self.is_angry = is_angry
        self.is_confused = is_confused
        self.is_hallucinating = is_hallucinating
        self.is_detecting_obj = is_detecting_obj

        self.is_flying = is_flying
        if is_flying:
            self.actor_fly()
        self.is_in_deep_pit = is_in_deep_pit
        self.is_in_shallow_pit = is_in_shallow_pit
        self.is_submerged = is_submerged
        self.was_submerged = was_submerged
        self.is_underwater = is_underwater

        self.has_head = has_head
        self.has_left_arm = has_left_arm
        self.has_right_arm = has_right_arm
        self.has_leg = has_leg
        self.has_wing = has_wing
        self.has_eye = has_eye
        self.has_torso = has_torso
        self.has_blood = has_blood
        self.has_soul = has_soul
        self.need_breathe = need_breathe

        self.can_swim = can_swim
        self.can_breathe_underwater = can_breathe_underwater
        self.can_fly = can_fly
        self.can_move_on_surface = can_move_on_surface

        self.has_immortality = has_immortality
        self.has_telepathy = has_telepathy
        self.can_revive_self = can_revive_self
        self.revive_as = revive_as

        self.can_think = can_think
        self.can_talk = can_talk

    @property
    def hunger_state(self) -> str:
        """
        hunger_measure = size * 25
        Size 4 actor has hunger_measure of 100.

        Reference:
            hunger 0 = Starved to death
            hunger 1 ~ hunger_measure(hm) = fainting
            hunger hm ~ hm*2 = starving
            hunger hm*2 ~ hm*4 = hungry
            hunger hm*4 ~ hm*12 = normal
            hunger hm*12 ~ hm*15 = satiated
            hunger hm*15 ~ hm*50 = overeaten
            hunger hm*50 ~ = death from food choking
        """
        if self.hunger < 0:
            # Never gets hungry
            return ""

        hunger_measure = int(25 * self.size)

        if self.hunger == 0:
            return "starved to death"
        elif self.hunger <= hunger_measure * 1:
            return "fainting"
        elif self.hunger <= hunger_measure * 3:
            return "starving"
        elif self.hunger <= hunger_measure * 7:
            return "hungry"
        elif self.hunger <= hunger_measure * 12:
            return ""
        elif self.hunger <= hunger_measure * 17:
            return "satiated"
        elif self.hunger <= hunger_measure * 48:
            return "overeaten"
        else:
            return "choked by food"

    def actor_gets_hungry(self):
        loss_per_turn = 1
        if self.is_sleeping != [0, 0]:
            loss_per_turn = 5 # x5
        self.hunger -= loss_per_turn
        hunger_state = self.hunger_state

        if self.previous_hunger_state != hunger_state:
            from components.status import Status
            if self.parent.status.check_if_has_bonus("hunger"): # remove prev hunger bonus
                self.parent.status.remove_bonus(bonus_id="hunger")

            self.previous_hunger_state = hunger_state
            if hunger_state == "overeaten":
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 불쾌할 정도로 배가 부르다.", fg=color.player_severe)
                self.parent.status.add_bonus(Bonus(bonus_id="hunger", bonus_agility=-4))
            elif hunger_state == "satiated":
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 배가 부르다.", fg=color.player_not_good)
                self.parent.status.add_bonus(Bonus(bonus_id="hunger", bonus_agility=-2, bonus_constitution=+1, bonus_strength=+1))
            elif hunger_state == "hungry":
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 배가 고프다.", fg=color.player_not_good)
                self.parent.status.add_bonus(Bonus(bonus_id="hunger", bonus_constitution=-2, bonus_strength=-1))
            elif hunger_state == "starving":
                self.parent.actor_state.apply_wake_up()
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 굶주리고 있다!", fg=color.player_bad)
                self.parent.status.add_bonus(Bonus(bonus_id="hunger", bonus_constitution=-4, bonus_strength=-2,bonus_intelligence=-1, bonus_dexterity=-1))
            elif hunger_state == "fainting":
                self.parent.actor_state.apply_wake_up()
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 배고픔에 허덕이고 있다!", fg=color.player_severe)
                self.parent.status.add_bonus(Bonus(bonus_id="hunger", bonus_constitution=-8, bonus_strength=-3,bonus_intelligence=-1, bonus_dexterity=-1))
            elif hunger_state == "starved to death":
                self.parent.status.death(cause="starvation")

    def gain_nutrition(self, nutrition: int) -> None:
        if self.parent.ai:
            if self.parent.ai.owner == self.engine.player: # Among all monsters only player's pets can gain nutrition.
                pass
            return None
        self.hunger += nutrition

    def actor_fly(self) -> None:
        self.is_flying = True
        if self.parent != None: # Actor State might not have parent when first initialized.
            # If it doesn't have a parent, entity.do_environment_effects() will make the actor float instead.
            self.parent.float(start_floating=True)

    def actor_stop_fly(self) -> None:
        self.is_flying = False
        if self.parent != None:
            # If it doesn't have a parent, entity.do_environment_effects() will make the actor float instead.
            self.parent.float(start_floating=False)

    def actor_heal_wounds(self):
        """
        constitution will affect both heal amount and heal interval.
        TODO: maybe change the way of calculating?
        """
        if self.heal_interval <= 0:
            constitution = self.parent.status.changed_status["constitution"]
            max_hp = self.parent.status.changed_status["max_hp"]

            heal_percent = constitution * 0.001 # amount of healing indicated as a percentage of maximum health
            heal_amount = int(max(1, max_hp * heal_percent)) # absolute amount of healing
            self.parent.status.heal(amount=heal_amount)
            self.heal_interval = round(100 / constitution)

            if self.parent.status.experience:
                self.parent.status.experience.gain_constitution_exp(5, exp_limit=3000)
        else:
            self.heal_interval -= 1

    def actor_regain_mana(self):
        """
        charisma(charm) will affect regain amount and intelligence will affect regain interval.
        NOTE: Logical explantaion for why charisma affects mana regeneration
        - Charisma is not merely a visual attractiveness of one. It is also related to the inner energy the person possess.
        Thus, a man with higher charisma is more likely to heal its inner energy than who is not.
        """
        if self.regain_interval <= 0:
            charm = self.parent.status.changed_status["charm"]
            intelligence = self.parent.status.changed_status["intelligence"]
            max_mp = self.parent.status.changed_status["max_mp"]
            regain_percent = (1 + math.log2(charm + 1)) * 0.004 # amount of regaining indicated as a percentage of maximum mana
            regain_amount = int(max(1, max_mp * regain_percent)) # absolute amount of healing
            self.parent.status.gain_mana(amount=regain_amount)
            self.regain_interval = round(500 / intelligence)

            if self.parent.status.experience:
                self.parent.status.experience.gain_intelligence_exp(5, exp_limit=3000)
        else:
            self.regain_interval -= 1

    def actor_burn(self):
        if self.parent.status.changed_status["fire_resistance"] >= 1:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 화염에 저항했다!", fg=color.player_success)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 화염에 저항했다!", fg=color.enemy_unique, target=self.parent)
            self.apply_burning([0, 0, 0, 0])
        else:
            if self.is_burning[3] > 0 and self.is_burning[2] >= self.is_burning[3]: # Stop burning
                self.apply_burning([0, 0, 0, 0])
            else:
                if self.is_burning[3] >= 0: # INf
                    self.is_burning[2] += 1 # current turn += 1

                # Calculate dmg for current turn
                fire_dmg = max(min(self.is_burning[0] + self.is_burning[1] * (self.is_burning[2] - 1), self.is_burning[0] * 3), 0) # Theoretical max dmg = initial dmg * 3

                # Damage reduction
                fire_dmg = self.parent.status.calculate_dmg_reduction(damage=fire_dmg, damage_type="fire")

                # Inventory on fire
                self.parent.inventory_on_fire()

                # Log before actual damage
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 화염으로부터 {fire_dmg} 데미지를 받았다.", fg=color.player_bad)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 화염으로부터 {fire_dmg} 데미지를 받았다.", fg=color.enemy_neutral, target=self.parent)
                self.parent.status.take_damage(amount=fire_dmg)

            # Chance of fire going off
            extinguish_chance = random.random()
            if extinguish_chance <= self.parent.status.changed_status["fire_resistance"]:
                self.apply_burning([0, 0, 0, 0])
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 더 이상 불타고 있지 않다.", fg=color.player_neutral)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 불타고 있지 않다.", fg=color.enemy_neutral, target=self.parent)

    def actor_paralyzing(self):
        """
        Actor is currently paralyzed.
        """
        # Reduce turn
        if self.is_paralyzing[0] >= self.is_paralyzing[1] and self.is_paralyzing[1] > 0: # Stop paralyzing
            # Log
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 다시 움직일 수 있게 되었다.", fg=color.white)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 다시 움직이기 시작한다.", fg=color.white, target=self.parent)
            # Remove paralyzation
            self.apply_paralyzation([0,0])
            return None
        else:
            if self.is_paralyzing[1] >= 0: # Last infinitly if negative
                self.is_paralyzing[0] += 1

    def actor_sleeping(self):
        """
        Actor is currently sleeping.
        """
        # Reduce turn
        if self.is_sleeping[0] >= self.is_sleeping[1] and self.is_sleeping[1] > 0: # Stop sleeping
            # Remove sleeping
            self.apply_wake_up()
            return None
        else:
            if self.is_sleeping[1] >= 0: # Last infinitly if negative
                self.parent.status.add_bonus(bonus=Bonus(
                    bonus_id="sleep_bonus",
                    bonus_constitution=min(50, max(10, round(self.parent.status.origin_status["constitution"] * 1.5)))), # Using origin status
                    ignore_warning=True
                )
                self.is_sleeping[0] += 1

    def actor_freeze(self):
        """
        Actor is freezing.
        """
        # No additional effect if the actor is already frozen.
        if self.is_frozen != [0,0,0]:
            self.apply_freezing([0, 0, 0, 0, 0])
            return None

        if self.parent.status.changed_status["cold_resistance"] >= 1:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 냉기에 저항했다!", fg=color.player_success)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 냉기에 저항했다!", fg=color.enemy_unique,target=self.parent)
            self.apply_freezing([0, 0, 0, 0, 0])
            # Reset this actor's agility value
            self.parent.status.remove_bonus("freeze_bonus")
        else:
            if self.is_freezing[3] >= self.is_freezing[4] and self.is_freezing[4] > 0: # Stop freezing
                self.apply_freezing([0, 0, 0, 0, 0])
                self.parent.status.remove_bonus("freeze_bonus")
            else:
                if self.is_freezing[4] >= 0: # Last infinitly if negative
                    self.is_freezing[3] += 1 # current_turn += 1
                
                # Damage reduction
                cold_dmg = self.is_freezing[0]
                cold_dmg = self.parent.status.calculate_dmg_reduction(damage=cold_dmg, damage_type="cold")

                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 얼어붙고 있다. {cold_dmg} 데미지를 받았다.",fg=color.player_bad)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 얼어붙고 있다. {cold_dmg} 데미지를 받았다.",fg=color.enemy_neutral, target=self.parent)

                self.parent.status.take_damage(amount=cold_dmg)

                # Slows actor down (not stacked)
                self.parent.status.add_bonus(Bonus("freeze_bonus", bonus_agility=-1 * self.is_freezing[1]))

                # Chance of getting frozen
                if random.random() <= self.is_freezing[2]:
                    # Make actor frozen
                    # dmg = is_freezing dmg * 1.5
                    # max lasting turn = is_freezing max lasting turn * 2
                    dmg = round(self.is_freezing[0] * 1.5)
                    turn = round(self.is_freezing[4] * 2)
                    self.apply_frozen([dmg, 0, turn])
                    
                    self.apply_freezing([0, 0, 0, 0, 0])
                    self.parent.status.remove_bonus("freeze_bonus")

                    # Run frozen state handling method
                    self.actor_frozen()
                    return None

            # Resistances
            resist_chance = random.random()
            if resist_chance <= self.parent.status.changed_status["cold_resistance"]:
                self.apply_freezing([0, 0, 0, 0, 0])
                self.parent.status.remove_bonus("freeze_bonus")
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 더 이상 얼어붙고 있지 않다.", fg=color.player_neutral)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 얼어붙고 있지 않다.", fg=color.enemy_neutral, target=self.parent)

    def actor_frozen(self):
        """
        Actor is completely frozen
        """
        if self.is_frozen[1] >= self.is_frozen[2] and self.is_frozen[2] > 0: # Stop frozen
            self.apply_frozen([0,0,0])
            self.parent.status.remove_bonus("frozen_bonus")
        else:
            if self.is_frozen[2] >= 0: # will last infinitly if negetive
                self.is_frozen[1] += 1 #current_turn += 1

            # dmg calc
            cold_dmg = self.is_frozen[0]
            cold_dmg = self.parent.status.calculate_dmg_reduction(damage=cold_dmg, damage_type="cold")

            # log before dmg
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 완전히 얼어붙었다. {cold_dmg} 데미지를 받았다!", fg=color.player_severe)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 완전히 얼어붙었다. {cold_dmg} 데미지를 받았다!",fg=color.enemy_unique, target=self.parent)

            # dmg apply
            self.parent.status.take_damage(amount=cold_dmg)

            # slows actor down (will not stack)
            self.parent.status.add_bonus(Bonus("frozen_bonus", bonus_agility=-1000)) # agility value will be set to 1 (it will get clamped)

        # Resistance
        resist_chance = random.random()
        if resist_chance <= self.parent.status.changed_status["cold_resistance"]:
            self.apply_frozen([0,0,0])
            self.parent.status.remove_bonus("frozen_bonus")
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 더 이상 얼어있지 않다.", fg=color.player_neutral)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 얼어있지 않다.", fg=color.enemy_neutral, target=self.parent)

    def get_connected_actors(self, prev_actors:Set = None):
        """
        Returns a set of connected swarm of actors which includes this component's parent.
        This function uses recursion.
        """
        # Prevent circular function call
        if prev_actors:
            conn_actors = prev_actors
        else:
            conn_actors = set()
        conn_actors.add(self.parent)
        temp_conn_actors = copy.copy(conn_actors)

        # List of actors who will also get electrocuted
        targets = [self.parent]

        # Get adjacent actors around parent (Including the tile that the parent is located at)
        for xy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            new_target = self.parent.gamemap.get_actor_at_location(x=self.parent.x + xy[0], y=self.parent.y + xy[1])
            if new_target:
                if not new_target.actor_state.is_dead:
                    targets.append(new_target)

        # Recursion
        for target in targets:
            if target not in temp_conn_actors:
                target.actor_state.get_connected_actors(conn_actors)
        
        for actor in conn_actors:
            conn_actors.add(actor)
        
        return conn_actors

    def actor_electrocuted(self, source_actor: Optional[Actor] = None):
        """
        Electrocute this component's parent, and its connected actors.
        Damage can be decreased denpending on the chebyshenv distance between the electricity's starting location, and the actor's location.
        """
        # Sort connected_actors, so that the game will calculate the damage from closest to furthest.
        targets = sorted(self.get_connected_actors(), key=lambda actor : abs(actor.x - self.parent.x) + abs(actor.y - self.parent.y))

        # Backup parent's x, y value and actor_state.is_electrocuting values in case of parent dying from electrical shock
        # (When actor dies, its actor_state.is_electrocuting is resetted to [0,0])
        elec_core = (self.parent.x, self.parent.y)
        elec_value = copy.copy(self.is_electrocuting)

        for target in targets:
            # If there is a source actor, trigger target to that source actor.
            if source_actor:
                target.status.take_damage(amount=0, attacked_from=source_actor)

            # Resistance
            if target.status.changed_status["shock_resistance"] >= 1:
                if target == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 전격에 저항했다!", fg=color.player_success)
                else:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} 전격에 저항했다!", fg=color.enemy_unique, target=target)
                self.is_electrocuting = [0, 0]
            else:
                # Damage differs from targets depending on the distance
                dist_from_core = round(math.sqrt((target.x - elec_core[0]) ** 2 + (target.y - elec_core[1]) ** 2))
                shock_dmg = elec_value[0] * (elec_value[1] ** dist_from_core)
                shock_dmg = target.status.calculate_dmg_reduction(damage=shock_dmg, damage_type="shock")

                # Log
                if target == self.engine.player:
                    if shock_dmg == 0:
                        self.engine.message_log.add_message(f"당신은 전격으로부터 아무런 데미지도 받지 않았다.",fg=color.player_success, target=target)
                    else:
                        self.engine.message_log.add_message(f"당신은 전격으로부터 {shock_dmg} 데미지를 받았다.",fg=color.player_bad, target=target)
                else:
                    if shock_dmg == 0:
                        self.engine.message_log.add_message(f"{g(target.name, '은')} 전격으로부터 아무런 데미지도 받지 않았다.", fg=color.enemy_neutral, target=target)
                    else:
                        self.engine.message_log.add_message(f"{g(target.name, '은')} 전격으로부터 {shock_dmg} 데미지를 받았다.", fg=color.enemy_neutral, target=target)
                
                # Apply dmg
                target.status.take_damage(amount=shock_dmg)

    def actor_confused(self):
        """
        NOTE: This method only handles counting the turns left for the effect to go off.
        Actual features are usually handled in action. (e.g. MovementAction handles staggering effect)
        """
        # Check turns
        if self.is_confused[0] >= self.is_confused[1] and self.is_confused[1] > 0: # stop confused
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 다시 정신을 차렸다.", fg=color.player_neutral)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 정신을 차린 듯 하다.", target=self.parent, fg=color.enemy_neutral)
            self.apply_confusion([0,0])
        elif self.is_confused[0] >= 0: # lasts forever if negative
            self.is_confused[0] += 1
    
    def actor_melting(self):
        """
        Actor is melting from the acid.
        """
        # Check resistance
        if random.random() <= self.parent.status.changed_status["acid_resistance"]:
            self.apply_melting([0, 0, 0, 0])
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 더 이상 산으로부터 데미지를 받고 있지 않다.", fg=color.player_neutral)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 산으로부터 데미지를 받고 있지 않다.",fg=color.enemy_neutral, target=self.parent)
            return None
                
        # Check turns
        if self.is_melting[2] >= self.is_melting[3] and self.is_melting[3] > 0: # Stop melting
            self.apply_melting([0, 0, 0, 0])
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 더 이상 산으로부터 데미지를 받고 있지 않다.", fg=color.player_neutral)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 산으로부터 데미지를 받고 있지 않다.",fg=color.enemy_neutral, target=self.parent)
            return None
        else:
            if self.is_melting[3] >= 0: # lasts forever if negative
                self.is_melting[2] += 1

            self.is_melting[0] = max(1, self.is_melting[0] - self.is_melting[1])
            
            # Apply damage
            acid_dmg = self.is_melting[0]
            acid_dmg = self.parent.status.calculate_dmg_reduction(damage=acid_dmg, damage_type="acid")

            # Inventory on acid
            self.parent.inventory_on_acid()

            # Log before dmg
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 산성 물질로 인해 녹아내리고 있다. {acid_dmg} 데미지를 받았다.", fg=color.player_bad, target=self.parent)
            else:
                self.engine.message_log.add_message(
                    f"{g(self.parent.name, '은')} 산성 물질로 인해 녹아내리고 있다. {acid_dmg} 데미지를 받았다.", fg=color.enemy_neutral, target=self.parent)

            # dmg
            self.parent.status.take_damage(amount=acid_dmg)


    def actor_bleed(self):
        """
        Actor is bleeding.
        """
        # Check if the parent actor can even bleed in the first place.
        if not self.has_blood:
            self.apply_bleeding([0,0,0])
            return None

        # Check turns
        if self.is_bleeding[1] >= self.is_bleeding[2] and self.is_bleeding[2] > 0: # Stop bleeding
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 더 이상 출혈 상태가 아니다.", fg=color.player_neutral)
            else:
                self.engine.message_log.add_message(f"{self.parent.name}의 출혈이 멎은 듯 하다.", fg=color.enemy_neutral, target=self.parent)
            self.apply_bleeding([0,0,0])
        else:
            if self.is_bleeding[2] >= 0: # lasts forever if negative
                self.is_bleeding[1] += 1

            blood_dmg = self.is_bleeding[0]

            # Log before dmg
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 출혈로 인해 {blood_dmg} 데미지를 받았다.",fg=color.player_bad)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 출혈로 인해 {blood_dmg} 데미지를 받았다.", fg=color.enemy_neutral, target=self.parent)

            # Apply damage
            self.parent.status.take_damage(amount=blood_dmg)

        # Check if the bleeding has stopped (Similar to resistance)
        # Each turn, there is cons / cons + 60 chance of stop bleeding
        constitution = self.parent.status.changed_status["constitution"]
        if random.random() <= (constitution / (constitution + 60)):
            self.is_bleeding[1] = self.is_bleeding[2] # The bleeding will stop next game loop.

    def actor_levitating(self):
        """
        Actor is levitating.
        """
        if self.is_levitating[0] >= self.is_levitating[1] and self.is_levitating[1] > 0: # Stop levitating
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 더 이상 공중 부양 상태가 아니다.", fg=color.player_neutral)
            self.apply_levitation([0, 0])
            self.parent.float(False)
        elif self.is_levitating[1] >= 0:  # lasts forever if negative
            self.is_levitating[0] += 1

        if self.is_levitating != [0, 0]:
            self.parent.float(True)

    def actor_poisoned(self):
        """
        Actor is poisoned.
        """
        if self.parent.status.changed_status["poison_resistance"] >= 1:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 독에 저항했다!", fg=color.player_success)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 독에 저항했다!", fg=color.enemy_unique, target=self.parent)
            self.apply_poisoning([0, 0, 0, 0])
            self.parent.status.remove_bonus("poison_bonus")
        else:
            if self.is_poisoned[2] >= self.is_poisoned[3] and self.is_poisoned[3] > 0: # Stop poisoning
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 더 이상 중독 상태가 아니다.", fg=color.player_neutral)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 기운을 차린 듯 하다.", target=self.parent, fg=color.enemy_neutral)
                self.apply_poisoning([0, 0, 0, 0])
                self.parent.status.remove_bonus("poison_bonus")
            else:
                if self.is_poisoned[3] >= 0: # lasts forever if negative
                    self.is_poisoned[2] += 1
                    # Damage will rise each turn
                    self.is_poisoned[0] += self.is_poisoned[1]

                # Apply damage
                poison_dmg = self.is_poisoned[0]
                poison_dmg = self.parent.status.calculate_dmg_reduction(damage=poison_dmg, damage_type="poison")

                # Log before dmg
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 독으로 인해 {poison_dmg} 데미지를 받았다.", fg=color.player_bad)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 독으로 인해 {poison_dmg} 데미지를 받았다.", fg=color.enemy_neutral, target=self.parent)

                # dmg
                self.parent.status.take_damage(amount=poison_dmg)

                # Lowers constitution (Debuff will stack, But there is no specific value. Constitution will reduce in half each turn.)
                self.parent.status.add_bonus(Bonus("poison_bonus", bonus_constitution=-1 * int(self.parent.status.changed_status["constitution"] / 2)))
        
            # Resistance
            resist_chance = random.random()
            if resist_chance <= self.parent.status.changed_status["poison_resistance"]:
                self.apply_poisoning([0, 0, 0, 0])
                self.parent.status.remove_bonus("poison_bonus")
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 더 이상 중독 상태가 아니다.", fg=color.player_neutral)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 기운을 차린 듯 하다.", target=self.parent, fg=color.enemy_neutral)
    
    def actor_submerged(self):
        """
        The actor is submerged partially or fully.

        This function is called when actor_state.is_submerged is True.
        NOTE: This function is called even if is_underwater is set to False
        """
        # Remove fire unless the fire lasts eternally (Check if current turn value is negative or not)
        # NOTE: Items in actor's inv will not be effected. TODO: fix? add wet items?
        self.apply_burning([0, 0, 0, 0])
        self.parent.inventory_extinguish()
        self.apply_melting([0, 0, 0, 0])

        # Debuffs on agi and dex if you cant swim
        if self.is_underwater:
            self.parent.inventory_on_water()

            if not self.can_swim and self.size <= 5: #TODO: Size
                if self.is_drowning == [0,0] and not self.can_breathe_underwater and self.need_breathe:
                    self.apply_drowning([0, 80])

                # agility, dexterity reduce in half (will not stack)
                self.parent.status.add_bonus(Bonus("submerged_bonus",
                                                   bonus_agility=-10,
                                                   bonus_dexterity=-10), ignore_warning=True)
            else:
                if self.is_drowning != [0, 0]:
                    self.apply_drowning([0, 0])

                # agility, dexterity reduce in half (will not stack)
                self.parent.status.add_bonus(Bonus("submerged_bonus",
                                                   bonus_agility=-5,
                                                   bonus_dexterity=-5), ignore_warning=True)
        else:
            if self.is_drowning != [0, 0]:
                self.apply_drowning([0, 0])


    def actor_drowning(self):
        """
        Actor is drowning
        """
        if self.need_breathe:
            self.is_drowning[0] += 1

            # Check if the actor passed its limit
            if self.is_drowning[0] >= self.is_drowning[1]:
                self.parent.status.death(cause="drowning")
        else:
            self.apply_drowning([0, 0])
            return None

    def actor_detecting(self):
        """
        Make player detect(see) certain types of entities regardless of sight range.
        Actual detection calculation occurs during update_fov()
        """
        # Check turns
        if self.is_detecting_obj[0] >= self.is_detecting_obj[1] and self.is_detecting_obj[1] > 0: # Stop detecting
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 감각이 다시 원래대로 돌아오는 것을 느꼈다.", target=self.parent, fg=color.player_neutral)
            self.apply_object_detection([0,0,[]])
        elif self.is_detecting_obj[1] >= 0: # lasts forever if negative
            self.is_detecting_obj[0] += 1

    def remove_all_actor_states(self, include_spatial_states: bool = False):
        """
        Reset everything related to this actor's state.

        WARNING: This function FORCES to remove ALL actor states regardless of situations.
        So any permanent actor state (e.g. burning state of Fire Elemental) will be removed as well.
        If you forcefully want to remove certain states only, use change the instance variable directly insted. (ex. self.burning = [0,0,0,0])
        If you want to remove certain states non-forcefully, and let the game decide whether the state should be removed or not, use apply_xxxing methods instead. (ex. self.apply_burning([0,0,0,0]))

        NOTE: This function's main purpose is to prevent any unwanted behaviour from dead entities by removing their actor states.
        This function should NOT be called for the purpose of removing status effects from a living actor.
        """
        # hunger
        self.hunger = -1
        # regen
        self.heal_wounds = False
        # physical states
        self.apply_burning([0, 0, 0, 0])
        self.apply_poisoning([0, 0, 0, 0])
        self.apply_freezing([0, 0, 0, 0, 0])
        self.apply_frozen([0, 0, 0])
        self.apply_electrocution([0, 0])
        self.apply_invisibility([0, 0])
        self.apply_phasing([0, 0])
        self.apply_paralyzation([0, 0])
        self.apply_bleeding([0, 0, 0])
        self.apply_slowness([0, 0, 0])
        self.apply_haste([0, 0, 0])
        self.apply_melting([0, 0, 0, 0])
        self.apply_sickness([0.0, 0, 0])
        self.apply_levitation([0, 0])
        self.apply_drowning([0, 0])
        # nonphysical states
        self.apply_wake_up()
        self.apply_anger([0, 0])
        self.apply_confusion([0, 0])
        self.apply_hallucination([0, 0])
        self.apply_object_detection([0, 0, []])
        if include_spatial_states:
            # spatial states
            self.actor_stop_fly() # NOTE: entity.is_on_air will remain its value since its technically not actor state.
            self.is_in_deep_pit = False
            self.is_in_shallow_pit = False
            self.is_submerged = False
            self.is_underwater = 0

    def apply_burning(self, value: List[int, int, int, int]) -> None:
        """
        ### FLOW ###
        # Am I burning eternally?
        # Yes)
        #       Am I receiving a value to start burn for eternity?
        #       Yes)
        #           Overwrite.
        #       No)
        #           ignore given value.
        # No)
        #       Am I receiving a value to start burn for eternity?
        #       Yes)
        #           Overwrite.
        #       No)
        #           Am I currently burning?
        #           Yes)
        #               Set dmg to higher value, set dmg decrement to lower value, keep current turn unchanged, prolong max turn
        #           No)
        #               Set is_burning to given value
        #############
        """
        if self.is_burning[3] < 0:
            if value[3] < 0:
                self.is_burning = value
                return None
            else:
                return None
        else:
            if value[3] < 0:
                self.is_burning = value
            else:
                if self.is_burning != [0,0,0,0] and value != [0,0,0,0]:
                    self.is_burning[0] = max(self.is_burning[0], value[0]) # set to higher dmg
                    self.is_burning[1] = min(self.is_burning[1], value[1]) # set to lower decrement
                    # keep current turn unchanged
                else:
                    self.is_burning = value

    def apply_poisoning(self, value: List[int, int, int, int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_poisoned[3] < 0:
            if value[3] < 0:
                self.is_poisoned = value
                return None
            else:
                return None
        else:
            if value[3] < 0:
                self.is_poisoned = value
            else:
                if self.is_poisoned != [0,0,0,0] and value != [0,0,0,0]:
                    self.is_poisoned[0] = max(self.is_poisoned[0], value[0]) # set to higher dmg
                    self.is_poisoned[1] = max(self.is_poisoned[1], value[1]) # set to higher increment
                    # keep current turn unchanged
                    self.is_poisoned[3] = max(self.is_poisoned[3], value[3]) # set to higher max turn
                else:
                    self.is_poisoned = value

    def apply_freezing(self, value: List[int, int, int, int, int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_freezing[4] < 0:
            if value[4] < 0:
                self.is_freezing = value
                return None
            else:
                return None
        else:
            if value[4] < 0:
                self.is_freezing = value
            else:
                if self.is_freezing != [0,0,0,0,0] and value != [0,0,0,0,0]:
                    self.is_freezing[0] = max(self.is_freezing[0], value[0]) # set to higher dmg
                    self.is_freezing[1] = max(self.is_freezing[1], value[1]) # set to higher agility decrement
                    self.is_freezing[2] = max(self.is_freezing[2], value[2]) # set to higher chance of being frozen
                    # keep current turn unchanged
                    self.is_freezing[4] = max(self.is_freezing[4], value[4]) # set to higher max turn
                else:
                    self.is_freezing = value

    def apply_frozen(self, value: List[int, int, int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_frozen[2] < 0:
            if value[2] < 0:
                self.is_frozen = value
                return None
            else:
                return None
        else:
            if value[2] < 0:
                self.is_frozen = value
            else:
                if self.is_frozen != [0,0,0] and value != [0,0,0]:
                    self.is_frozen[0] = max(self.is_frozen[0], value[0]) # set to higher dmg
                    # keep current turn unchanged
                    # no prolonging
                else:
                    self.is_frozen = value

    def apply_bleeding(self, value: List[int, int, int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_bleeding[2] < 0:
            if value[2] < 0:
                self.is_bleeding = value
                return None
            else:
                return None
        else:
            if value[2] < 0:
                self.is_bleeding = value
            else:
                if self.is_bleeding != [0,0,0] and value != [0,0,0]:
                    self.is_bleeding[0] += value[0] # dmg stacks
                    # keep current turn unchanged
                    self.is_bleeding[2] = max(self.is_bleeding[2], value[2]) # No prolonging but set to higher value
                else:
                    self.is_bleeding = value

    def apply_slowness(self, value: List[int, int, int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_acting_slower[2] < 0:
            if value[2] < 0:
                self.is_acting_slower = value
                return None
            else:
                return None
        else:
            if value[2] < 0:
                self.is_acting_slower = value
            else:
                if self.is_acting_slower != [0,0,0] and value != [0,0,0]:
                    self.is_acting_slower[0] = max(self.is_acting_slower[0], value[0])
                    # keep current turn unchanged
                    self.is_acting_slower[1] += value[1] # prolong max turn
                else:
                    self.is_acting_slower = value

    def apply_haste(self, value: List[int, int, int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_acting_faster[2] < 0:
            if value[2] < 0:
                self.is_acting_faster = value
                return None
            else:
                return None
        else:
            if value[2] < 0:
                self.is_acting_faster = value
            else:
                if self.is_acting_faster != [0,0,0] and value != [0,0,0]:
                    self.is_acting_faster[0] = max(self.is_acting_faster[0], value[0])
                    # keep current turn unchanged
                    self.is_acting_faster[1] += value[1] # prolong max turn
                else:
                    self.is_acting_faster = value

    def apply_melting(self, value: List[int,int,int,int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_melting[3] < 0:
            if value[3] < 0:
                self.is_melting = value
                return None
            else:
                return None
        else:
            if value[3] < 0:
                self.is_melting = value
            else:
                if self.is_melting != [0,0,0,0] and value != [0,0,0,0]:
                    self.is_melting[0] = max(self.is_melting[0], value[0])
                    self.is_melting[1] = max(0, self.is_melting[1] - int(value[0]/2)) # lower dmg decrement by the newly taken dmg
                    # keep current turn unchanged
                    self.is_melting[2] += value[2] # prolong max turn
                else:
                    self.is_melting = value

    def apply_sickness(self, value: List[float,int,int]) -> None:
        """
        Flow similar to apply_burning()
        """
        if self.is_sick[2] < 0:
            if value[2] < 0:
                self.is_sick = value
                return None
            else:
                return None
        else:
            if value[2] < 0:
                self.is_sick = value
            else:
                if self.is_sick != [0.0,0,0] and value != [0,0,0,0]:
                    self.is_sick[0] = max(self.is_sick[0], value[0])
                    # keep current turn unchanged
                    # keep max turn unchanged
                else:
                    self.is_sick = value

    def apply_electrocution(self, value: List[int,float]) -> None:
        if self.is_electrocuting != [0,0]:
            self.is_electrocuting[0] = max(self.is_electrocuting[0], value[0]) # set to higher dmg
            self.is_electrocuting[1] = max(self.is_electrocuting[1], value[1]) # set to higher dmg ratio
        else:
            self.is_electrocuting = value

    def apply_invisibility(self, value: List[int,int]) -> None:
        if self.is_invisible[1] < 0:
            return None
        if self.is_invisible != [0,0] and value != [0,0]:
            # keep current turn unchanged
            self.is_invisible[1] += value[1] # prolong max turn
        else:
            self.is_invisible = value

    def apply_phasing(self, value: List[int,int]) -> None:
        if self.is_phasing[1] < 0:
            return None
        if self.is_phasing != [0,0] and value != [0,0]:
            # keep current turn unchanged
            self.is_phasing[1] += value[1] # prolong max turn
        else:
            self.is_phasing = value

    def apply_paralyzation(self, value: List[int,int]) -> None:
        if self.is_paralyzing[1] < 0 and value != [0,0]: # Ignore less fatal paralyzation. although you can still unparalyze infinitely paralyzing actor
            return None
        if self.is_paralyzing != [0,0] and value != [0,0]:
            # keep current turn unchanged
            self.is_paralyzing[1] = max(self.is_paralyzing[1], value[1]) # No prolonging to prevent paralyzing indefinitely, but set to higher value
        else:
            self.is_paralyzing = value

    def apply_levitation(self, value: List[int,int]) -> None:
        if self.is_levitating[1] < 0:
            raise NotImplementedError("ERROR::You should not be able to obtain levitation state eternally. Consider using is_flying instead.")
        if self.is_levitating != [0,0] and value != [0,0]:
            # keep current turn unchanged and prolong the max time
            self.is_levitating[1] += value[1]
        else:
            self.is_levitating = value

    def apply_drowning(self, value: List[int,int]) -> None:
        if self.is_drowning != [0,0] and value != [0,0]:
            # keep current turn unchanged
            # keep max turn unchanged
            pass
        else:
            self.is_drowning = value

    def apply_wake_up(self):
        """If actor is sleeping, wake actor up."""
        #NOTE: Log handled in apply_sleeping
        self.parent.status.remove_bonus(bonus_id="sleep_bonus", ignore_warning=True)
        self.apply_sleeping([0, 0], forced=True)

    def apply_sleeping(self, value: List[int,int], forced:bool=False) -> None:
        """
        Args:
            Sleep on will:
                indicates whether the actor is sleeping on its own will.
                if True, ignore sleep resistance.
        """
        # NOTE: Sleeping is the only state effect that checks for resistance BEFORE actually handle the state effects.
        if forced or (value != [0,0] and self.parent.status.changed_status["sleep_resistance"] < random.random()):
            if self.is_sleeping[1] < 0 and value != [0,0]:  # Ignore less fatal sleeping. Althoguh you can wake up infinitely sleeping actor
                return None
            if self.is_sleeping != [0,0] and value != [0,0]:
                # keep current turn unchanged
                self.is_sleeping[1] = max(self.is_sleeping[1], value[1])
            else:
                # Wakeup log
                if self.is_sleeping != [0,0] and value == [0,0]:
                    if self.parent == self.engine.player:
                        self.engine.message_log.add_message(f"당신은 잠에서 깨어났다!", fg=color.player_neutral_important)
                    else:
                        self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 잠에서 깨어났다!", fg=color.enemy_unique, target=self.parent)
                self.is_sleeping = value
        else:
            if value != [0,0]:
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 잠에 저항했다!", fg=color.player_success)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 잠에 저항했다!", fg=color.enemy_unique, target=self.parent)

    def apply_anger(self, value: List[int,int]) -> None:
        if self.is_angry[1] < 0:
            return None
        if self.is_angry != [0,0] and value != [0,0]:
            # keep current turn unchanged
            # keep max turn unchanged
            pass
        else:
            self.is_angry = value
    
    def apply_confusion(self, value: List[int,int]) -> None:
        if self.is_confused[1] < 0:
            return None
        if self.is_confused != [0,0] and value != [0,0]:
            # keep current turn unchanged
            self.is_confused[1] += value[1] # prolong max turn
        else:
            self.is_confused = value

    def apply_hallucination(self, value: List[int,int]) -> None:
        if self.is_hallucinating[1] < 0:
            return None
        if self.is_hallucinating != [0,0] and value != [0,0]:
            # keep current turn unchanged
            self.is_hallucinating[1] += value[1] # prolong max turn
        else:
            self.is_hallucinating = value

    def apply_object_detection(self, value: List[int,int]) -> None:
        if self.is_detecting_obj[1] < 0:
            raise NotImplementedError("ERROR::You should not be able to obtain object detection state eternally")
        if self.is_detecting_obj != [0,0,[]] and value != [0,0,[]]:
            # keep current turn unchanged
            self.is_detecting_obj[1] += value[1] # prolong max turn
            self.is_detecting_obj[2] = list(set(self.is_detecting_obj[2] + value[2])) # Add both lists, delete duplicates, and make it back to list type
        else:
            self.is_detecting_obj = value

    def apply_actor_state(self, state_name: str, value: Any) -> None:
        """
        Alter this actor's actor_state.
        This function will prevent actor_state being overwritten by smaller values.
        Using this function is highly recommended over directly manipulating actor_state values or directly calling apply_xxxing functions.
        
        NOTE: Function currently unused. aplly_xxxing() methods are being called directly. (20210323)
        """
        if state_name == "is_burning":
            self.apply_burning(value)
        elif state_name == "is_poisoned":
            self.apply_poisoning(value)
        elif state_name == "is_freezing":
            self.apply_freezing(value)
        elif state_name == "is_frozen":
            self.apply_frozen(value)
        elif state_name == "is_electrocuting":
            self.apply_electrocution(value)
        elif state_name == "is_invisible":
            self.apply_invisibility(value)
        elif state_name == "is_phasing":
            self.apply_phasing(value)
        elif state_name == "is_paralyzing":
            self.apply_paralyzation(value)
        elif state_name == "is_bleeding":
            self.apply_bleeding(value)
        elif state_name == "is_acting_slower":
            self.apply_slowness(value)
        elif state_name == "is_acting_faster":
            self.apply_haste(value)
        elif state_name == "is_melting":
            self.apply_melting(value)
        elif state_name == "is_sick":
            self.apply_sickness(value)
        elif state_name == "is_levitating":
            self.apply_levitation(value)
        elif state_name == "is_drowning":
            self.apply_drowning(value)
        elif state_name == "is_sleeping":
            self.apply_sleeping(value, forced=False)
        elif state_name == "is_angry":
            self.apply_anger(value)
        elif state_name == "is_confused":
            self.apply_confusion(value)
        elif state_name == "is_hallucinating":
            self.apply_hallucination(value)
        elif state_name == "is_detecting_obj":
            self.apply_object_detection(value)


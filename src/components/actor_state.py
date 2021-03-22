from __future__ import annotations
from typing import TYPE_CHECKING, List, Set, Tuple

from numpy.core.fromnumeric import sort
from components.base_component import BaseComponent
from korean import grammar as g

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

        ### Weight
        # measurement: kg
        weight: float = 70,

        ### Sexuality
        # If it has a sexuality, save it as a string form. (ex. "male")
        # If it has no sexuality, save it as a "None". NOTE: This is a string value. N,o,t,e "None"
        # If it has other sexuality besides male and female, save it as "GENDER_TYPE" (ex. "Helicopter")
        sexuality: str = random.choice(("male", "female")),

        ### Status effects - Physical
        # NOTE: WARNING - If any of the default values of the status effects is changed, make sure to change actor_state.remove_all_actor_states() as well.
        # NOTE: 'Effect lasts for negative turns' are considered as lasting infinitly.
        # Actor is on fire / Actor is emitting fire from its body
        # Value: [Initial damage, Damage decrease per turn, Current turn, Max lasting turn]
        is_burning: list = [0, 0, 0, 0], 
        # Actor is poisoned
        # Value: [Initial damage, Damage increase per turn, Current turn, Max lasting turn]
        is_poisoned: list = [0, 0, 0, 0], 
        # Actor is freezing
        # Value: [Damage per turn, Agility decrease per turn(will stack), Chance of getting frozen per turn, Current turn, Max lasting turn]
        is_freezing: list = [0, 0, 0, 0, 0],
        # Actor is completely frozen
        # Value: [Damage per turn, Current turn, Max lasting turn]
        is_frozen: list = [0, 0, 0],
        # Actor is being electrocuted / Actor is emitting electricity from its body
        # Value: [Damage taken by this actor, Damage taken by adjacent actor indicated as ratio(0~1) to the damage taken by this actor]
        is_electrocuting: list = [0, 0],
        # Actor is invisible
        # Value: [Current turn, Max lasting turn]
        is_invisible: list = [0, 0],
        # Actor is phasing (or is able to phase)
        # Value: [Current turn, Max lasting turn]
        is_phasing: list = [0, 0],
        # Actor is paralyzed
        # Value: [Current turn, Max lasting turn]
        is_paralyzing: list = [0, 0],
        # Actor is bleeding
        # Value: [Damage per turn, Current turn, Max lasting turn]
        is_bleeding: list = [0, 0, 0],
        # Actor is slowed down
        # Value: [Agility decrease each turn(will not stack), Current turn, Max lasting turn]
        is_acting_slower: list = [0, 0, 0],
        # Actor is sped up
        # Value: [Agility increase each turn(will not stack), Current turn, Max lasting turn]
        is_acting_faster: list = [0, 0, 0],
        # Actor is melting from acid
        # Value: [Damage per turn, Damage decrease per turn, Current turn, Max lasting turn]
        is_melting: list = [0, 0, 0, 0],
        # Actor is sick (besides from poison)
        # Value: [Damage per turn(Percentage of maximum health, range from 0~1), Current turn, Max lasting turn]
        is_sick: list = [0.0, 0, 0],
        # Actor is floating unwillingly
        # NOTE: To check whether the actor is on air or not, use is_flying instead.
        # is_levitating value's sole purpose is to give actor a status effect of floation.
        is_levitating: list = [0, 0],
        # Actor is drowning
        # Value: [Current turn, Turns needed for drowning(this is NOT turns left before drowning)]
        is_drowning: list = [0, 0],

        ### Status effects - Non-physical
        # Actor is sleeping
        # Value: [Current turn, Max lasting turn]
        is_sleeping: list = [0, 0],
        # Actor is angry (most possibly unwillingly)
        # Value: [Current turn, Max lasting turn]
        is_angry: list = [0, 0],
        # Actor is confused
        # Value: [Current turn, Max lasting turn]
        is_confused: list = [0, 0],
        # Actor is hallucinating
        # Value: [Current turn, Max lasting turn]
        is_hallucinating: list = [0, 0],
        # Actor can detect things that are out of sight
        # Value: [Current turn, Max lasting turn, List with strings: object type]
        # NOTE: Detection != telepathy
        is_detecting_obj: list = [0, 0, None],

        ### Spatial states
        # Actor is on air (whether willingly or unwillingly)
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

        ### Mental capabilities
        can_think: bool = True, # Has ability to make the most basic level of logical decision (e.g. feels pain -> moves away)
        can_talk: bool = True, # Is capable of speaking a language
    ):
        self.parent = None

        self.hunger = hunger
        self.previous_hunger_state = None

        self.heal_wounds = heal_wounds
        self.heal_interval = 0 # Interval between health regenerations

        self.is_dead = is_dead
    
        self.size = size
        self.weight = weight
        self.sexuality = sexuality

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
        self.is_in_deep_pit = is_in_deep_pit
        self.is_in_shallow_pit = is_in_shallow_pit
        self.is_submerged = is_submerged
        self.was_submerged = was_submerged
        self.is_underwater = is_underwater

        self.has_left_arm = has_right_arm
        self.has_right_arm = has_left_arm
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
        
        ex. Human(hunger_measure 100):
            hunger 0 = Starved to death
            hunger 1 ~ 100 = fainting
            hunger 100 ~ 200 = starving
            hunger 200 ~ 400 = hungry
            hunger 400 ~ 1200 = normal
            hunger 1200 ~ 1500 = satiated
            hunger 1500 ~ 5000 = overeaten
            hunger 5000 or higher = death from food choking
        """
        if self.hunger < 0:
            # Never gets hungry
            return ""

        hunger_measure = int(25 * self.size)

        if self.hunger == 0:
            return "starved to death"
        elif self.hunger <= hunger_measure:
            return "fainting"
        elif self.hunger <= hunger_measure * 2:
            return "starving"
        elif self.hunger <= hunger_measure * 4:
            return "hungry"
        elif self.hunger <= hunger_measure * 12:
            return ""
        elif self.hunger <= hunger_measure * 15:
            return "satiated"
        elif self.hunger <= hunger_measure * 50:
            return "overeaten"
        else:
            return "choked by food"

    def actor_gets_hungry(self):
        self.hunger -= 1

        hunger_state = self.hunger_state

        if self.parent == self.engine.player: #Currently the message log will only print messages about player's hunger. (TODO: when pets are added, add pets' hunger)
            if self.previous_hunger_state != hunger_state:
                self.previous_hunger_state = hunger_state
                if hunger_state == "hungry":
                    self.engine.message_log.add_message(f"당신은 배가 고프다.", fg=color.player_damaged)
                elif hunger_state == "starving":
                    self.engine.message_log.add_message(f"당신은 굶주리고 있다!", fg=color.red)
                elif hunger_state == "fainting":
                    self.engine.message_log.add_message(f"당신은 배고픔에 허덕이고 있다!", fg=color.red)
                elif hunger_state == "starved to death":
                    self.parent.status.die(cause="starvation")
        else:
            if hunger_state == "starved to death":
                self.parent.status.die(cause="starvation")

    def actor_heal_wounds(self):
        """
        constitution will affect both heal amount and heal interval.
        TODO: maybe change the way of calculating?
        """
        if self.heal_interval <= 0:
            constitution = self.parent.status.changed_status["constitution"]
            max_hp = self.parent.status.changed_status["max_hp"]

            heal_percent = 1 + math.log2(constitution + 1) # amount of healing indicated as a percentage of maximum health
            heal_amount = int(max(1, max_hp * heal_percent * 0.01)) # absolute amount of healing
            self.parent.status.heal(amount=heal_amount)
            self.heal_interval = round(250 / constitution)
        else:
            self.heal_interval -= 1

    def actor_burn(self):
        if self.parent.status.changed_status["fire_resistance"] >= 1:
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 화염에 저항했다!", fg=color.white, target=self.parent)
            self.is_burning = [0, 0, 0, 0]
        else:
            if self.is_burning[2] >= self.is_burning[3]: # No damage if the fire goes off
                self.is_burning = [0, 0, 0, 0]
            else:
                if self.is_burning[2] >= 0: # Last infinitly if negetive
                    self.is_burning[2] += 1 # current turn += 1

                # Calculate dmg for current turn
                fire_dmg = max(self.is_burning[0] + self.is_burning[1] * (self.is_burning[2] - 1), 0)

                # Damage reduction
                fire_dmg = self.parent.status.calculate_dmg_reduction(damage=fire_dmg, damage_type="fire")

                # Deal damage
                self.parent.status.take_damage(amount=fire_dmg)

                # Log
                if self.parent == self.engine.player:
                    dmg_color = color.player_damaged
                else:
                    dmg_color = color.enemy_damaged
                
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 화염으로부터 {fire_dmg} 데미지를 받았다.", fg=dmg_color, target=self.parent)
            
            # Chance of fire going off
            extinguish_chance = random.random()
            if extinguish_chance <= self.parent.status.changed_status["fire_resistance"]:
                self.is_burning = [0, 0, 0, 0]
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 불타고 있지 않다.", fg=color.gray, target=self.parent)

    def actor_paralyzing(self):
        """
        Actor is currently paralyzed.
        """
        # Reduce turn
        if self.is_paralyzing[0] >= self.is_paralyzing[1]:
            # Log
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 다시 움직일 수 있게 되었다.", fg=color.white)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 다시 움직이기 시작한다.", fg=color.white, target=self.parent)
            # Remove paralyzation
            self.is_paralyzing = [0,0]
            return None
        else:
            if self.is_paralyzing[0] >= 0: # Last infinitly if negative
                self.is_paralyzing[0] += 1

    def actor_freeze(self):
        """
        Actor is freezing.
        """
        # No additional effect if the actor is already frozen.
        if self.is_frozen != [0,0,0]:
            self.is_freezing = [0, 0, 0, 0, 0]
            return None

        if self.parent.status.changed_status["cold_resistance"] >= 1:
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 냉기에 저항했다!", fg=color.white, target=self.parent)
            self.is_freezing = [0, 0, 0, 0, 0]
            # Reset this actor's agility value
            self.parent.status.reset_bonuses(["bonus_agility"]) #TODO: Might need serious reworks. currently when yoou reset the bonus the entire buffs/debuffs are resetted.
        else:
            if self.is_freezing[3] >= self.is_freezing[4]: # If past max turn, reset stats
                self.is_freezing = [0, 0, 0, 0, 0]
                self.parent.status.reset_bonuses(["bonus_agility"])
            else:
                if self.is_freezing[3] >= 0: # Last infinitly if negative
                    self.is_freezing[3] += 1 # current_turn += 1
                
                # Damage reduction
                cold_dmg = self.is_freezing[0]
                cold_dmg = self.parent.status.calculate_dmg_reduction(damage=cold_dmg, damage_type="cold")

                # Apply damage
                self.parent.status.take_damage(amount=cold_dmg)

                # Log
                if self.parent == self.engine.player:
                    dmg_color = color.player_damaged
                else:
                    dmg_color = color.enemy_damaged
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 얼어붙고 있다. {cold_dmg} 데미지를 받았다.", fg=dmg_color, target=self.parent)

                # Slows actor down (stacked)
                self.parent.status.bonus_agility -= self.is_freezing[1]

                # Chance of getting frozen
                if random.random() <= self.is_freezing[2]:
                    # Make actor frozen
                    # dmg = is_freezing dmg * 1.5
                    # max lasting turn = is_freezing max lasting turn * 2
                    dmg = round(self.is_freezing[0] * 1.5)
                    turn = round(self.is_freezing[4] * 2)
                    self.is_frozen = [dmg, 0, turn]
                    
                    self.is_freezing = [0, 0, 0, 0, 0]
                    self.parent.status.reset_bonuses(["bonus_agility"])

                    # Run frozen state handling method
                    self.actor_frozen()
                    return None

            # Resistances
            resist_chance = random.random()
            if resist_chance <= self.parent.status.changed_status["cold_resistance"]:
                self.is_freezing = [0, 0, 0, 0, 0]
                self.parent.status.reset_bonuses(["bonus_agility"])
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 얼어붙고 있지 않다.", fg=color.gray, target=self.parent)

    def actor_frozen(self):
        """
        Actor is completely frozen
        """
        if self.is_frozen[1] >= self.is_frozen[2]:# Stats reset after max turn
            self.is_frozen = [0, 0, 0]
            self.parent.status.reset_bonuses(["bonus_agility"])
        else:
            if self.is_frozen[1] >= 0: # will last infinitly if negetive
                self.is_frozen[1] += 1 #current_turn += 1

            # dmg calc
            cold_dmg = self.is_frozen[0]
            cold_dmg = self.parent.status.calculate_dmg_reduction(damage=cold_dmg, damage_type="cold")

            # dmg apply
            self.parent.status.take_damage(amount=cold_dmg)

            # log
            if self.parent == self.engine.player:
                dmg_color = color.player_damaged
            else:
                dmg_color = color.enemy_damaged
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 완전히 얼어붙었다. {cold_dmg} 데미지를 받았다!", fg=dmg_color, target=self.parent)

            # slows actor down (will not stack)
            self.parent.status.bonus_agility = -1000 # agility value will be set to 1 (it will get clamped)

        # Resistance
        resist_chance = random.random()
        if resist_chance <= self.parent.status.changed_status["cold_resistance"]:
            self.is_frozen = [0, 0, 0]
            self.parent.status.reset_bonuses(["bonus_agility"])
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 얼어있지 않다.", fg=color.white, target=self.parent)

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

    def actor_electrocuted(self):
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
            # Resistance
            if target.status.changed_status["shock_resistance"] >= 1:
                self.engine.message_log.add_message(f"{g(target.name, '은')} 전격에 저항했다!", fg=color.white, target=target)
                self.is_electrocuting = [0, 0]
            else:
                # Damage differs from targets depending on the distance
                dist_from_core = round(math.sqrt((target.x - elec_core[0]) ** 2 + (target.y - elec_core[1]) ** 2))
                shock_dmg = elec_value[0] * (elec_value[1] ** dist_from_core)
                shock_dmg = target.status.calculate_dmg_reduction(damage=shock_dmg, damage_type="shock")

                # Log
                if target == self.engine.player:
                    dmg_color = color.player_damaged
                else:
                    dmg_color = color.enemy_damaged
                if shock_dmg == 0:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} 전격으로부터 아무런 데미지도 받지 않았다.", fg=color.gray, target=target)
                else:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} 전격으로부터 {shock_dmg} 데미지를 받았다.", fg=dmg_color, target=target)
                
                # Apply dmg
                target.status.take_damage(amount=shock_dmg)

    def actor_confused(self):
        """
        NOTE: This method only handles counting the turns left for the effect to go off.
        Actual features are usually handled in action. (e.g. MovementAction handles staggering effect)
        """
        # Check turns
        if self.is_confused[0] >= self.is_confused[1]:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 다시 정신을 차렸다.")
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 정신을 차린 듯 하다.", target=self.parent)
            self.is_confused = [0,0]
        elif self.is_confused[0] >= 0: # lasts forever if negative
            self.is_confused[0] += 1
    
    def actor_melting(self):
        """
        Actor is melting from the acid.
        """
        # Check resistance
        if random.random() <= self.parent.status.changed_status["acid_resistance"]:
            self.is_melting = [0, 0, 0, 0]
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 산으로부터 데미지를 받고 있지 않다.", fg=color.gray, target=self.parent)

        # Check turns
        if self.is_melting[2] >= self.is_melting[3]:
            self.is_melting = [0, 0, 0, 0]
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 더 이상 산으로부터 데미지를 받고 있지 않다.", fg=color.gray, target=self.parent)
        else:
            if self.is_melting[3] >= 0: # lasts forever if negative
                self.is_melting[2] += 1

            self.is_melting[0] = max(1, self.is_melting[0] - self.is_melting[1])
            
            # Apply damage
            acid_dmg = self.is_melting[0]
            acid_dmg = self.parent.status.calculate_dmg_reduction(damage=acid_dmg, damage_type="acid")
            self.parent.status.take_damage(amount=acid_dmg)

            # Log
            if self.parent == self.engine.player:
                dmg_color = color.player_damaged
            else:
                dmg_color = color.enemy_damaged
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 산성 물질로 인해 천천히 녹아내리고 있다. {acid_dmg} 데미지를 받았다.", fg=dmg_color, target=self.parent)

            # corrode equipped items if possible (chance of getting corroded is calculated inside of corrode() function.)
            for equipment in self.parent.equipments.equipments.values():
                if equipment:
                    equipment.item_state.corrode(owner=self.parent, amount=1)

    def actor_bleed(self):
        """
        Actor is bleeding.
        """
        # Check if the parent actor can even bleed in the first place.
        if not self.has_blood:
            self.is_bleeding = [0,0,0]
            return None

        # Check turns
        if self.is_bleeding[1] >= self.is_bleeding[2]:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 더 이상 출혈 상태가 아니다.")
            else:
                self.engine.message_log.add_message(f"{self.parent.name}의 출혈이 멎은 듯 하다.")
            self.is_bleeding = [0,0,0]
        else:
            if self.is_bleeding[1] >= 0: # lasts forever if negative
                self.is_bleeding[1] += 1

            # Apply damage
            blood_dmg = self.is_bleeding[0]
            self.parent.status.take_damage(amount=blood_dmg)

            # Log
            if self.parent == self.engine.player:
                dmg_color = color.player_damaged
            else:
                dmg_color = color.enemy_damaged
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 출혈로 인해 {blood_dmg} 데미지를 받았다.", fg=dmg_color, target=self.parent)

        # Check if the bleeding has stopped (Similar to resistance)
        # Each turn, there is cons / cons + 60 chance of stop bleeding
        constitution = self.parent.status.changed_status["constitution"]
        if random.random() <= (constitution / (constitution + 60)):
            self.is_bleeding[1] = self.is_bleeding[2] # The bleeding will stop next game loop.

    def actor_poisoned(self):
        """
        Actor is poisoned.
        """
        if self.parent.status.changed_status["poison_resistance"] >= 1:
            self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 독에 저항했다!", fg=color.white, target=self.parent)
            self.is_poisoned = [0, 0, 0, 0]
            self.parent.status.reset_bonuses(["bonus_constitution"]) # TODO: Improve buff/debuff system
        else:
            if self.is_poisoned[2] >= self.is_poisoned[3]:
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 더 이상 중독 상태가 아니다.", target=self.parent)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 기운을 차린 듯 하다.", target=self.parent)
                self.is_poisoned = [0,0,0,0]
                self.parent.status.reset_bonuses(["bonus_constitution"])
            else:
                if self.is_poisoned[2] >= 0: # lasts forever if negative
                    self.is_poisoned[2] += 1
                    # Damage will rise each turn
                    self.is_poisoned[0] += self.is_poisoned[1]

                # Apply damage
                poison_dmg = self.is_poisoned[0]
                poison_dmg = self.parent.status.calculate_dmg_reduction(damage=poison_dmg, damage_type="poison")
                self.parent.status.take_damage(amount=poison_dmg)

                # Log
                if self.parent == self.engine.player:
                    dmg_color = color.player_damaged
                else:
                    dmg_color = color.enemy_damaged
                self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 독으로 인해 {poison_dmg} 데미지를 받았다.", fg=dmg_color, target=self.parent)

                # Lowers constitution (Debuff will stack, But there is no specific value. Constitution will reduce in half each turn.)
                self.parent.status.bonus_constitution -= int(self.parent.status.changed_status["constitution"] / 2)
        
            # Resistance
            resist_chance = random.random()
            if resist_chance <= self.parent.status.changed_status["poison_resistance"]:
                self.is_poisoned = [0, 0, 0, 0]
                self.parent.status.reset_bonuses(["bonus_constitution"])
                if self.parent == self.engine.player:
                    self.engine.message_log.add_message(f"당신은 더 이상 중독 상태가 아니다.", target=self.parent)
                else:
                    self.engine.message_log.add_message(f"{g(self.parent.name, '은')} 기운을 차린 듯 하다.", target=self.parent)
    
    def actor_submerged(self):
        """
        The actor is submerged partially or fully.

        This function is called when actor_state.is_submerged is True.
        NOTE: This function is called even if is_underwater is set to False
        """
        # Remove fire unless the fire lasts eternally (Check if current turn value is negative or not)
        # NOTE: Items in actor's inv will not be effected. TODO: fix? add wet items?
        if self.is_burning[2] >= 0:
            self.is_burning = [0,0,0,0]

        # Debuffs on agi and dex if you cant swim
        if not self.parent.actor_state.can_swim:
            
            # Fully submerged
            if self.parent.actor_state.is_underwater:
                # agility, dexterity reduce in half (will not stack)
                self.parent.status.bonus_agility = min(-int(self.parent.status.changed_status["agility"] / 2), self.parent.status.bonus_agility)
                self.parent.status.bonus_dexterity = min(-int(self.parent.status.changed_status["dexterity"] / 2), self.parent.status.bonus_dexterity)
            # No debuff when partially submerged.
        
        # Actor will slowly drown if it can't swim nor breathe underwater, and it needs to breathe to live
        if self.parent.actor_state.is_drowning == [0,0] and not self.parent.actor_state.can_swim and not self.parent.actor_state.can_breathe_underwater and self.parent.actor_state.need_breathe:
            self.is_drowning = [0, 80]##TODO
        # Moved from deep water to shallow water while drowning (The actor is still submerged, but is_underwater is set to False)
        elif self.parent.actor_state.is_drowning != [0,0] and not self.parent.actor_state.is_underwater:
            self.is_drowning = [0,0]

    def actor_drowning(self):
        """
        Actor is drowning
        """
        if self.need_breathe:
            self.is_drowning[0] += 1

            # Check if the actor passed its limit
            if self.is_drowning[0] >= self.is_drowning[1]:
                self.parent.status.die(cause="drowning")
        else:
            self.is_drowning = [0,0]
            return None

    def actor_detecting(self):
        """
        Make player detect(see) certain types of entities regardless of sight range.
        Actual detection calculation occurs during update_fov()
        """
        # Check turns
        if self.is_detecting_obj[0] >= self.is_detecting_obj[1]:
            if self.parent == self.engine.player:
                self.engine.message_log.add_message(f"당신은 감각이 다시 원래대로 돌아오는 것을 느꼈다.", target=self.parent)
            self.is_detecting_obj = [0,0,None]
        elif self.is_detecting_obj[0] >= 0: # lasts forever if negative
            self.is_detecting_obj[0] += 1

    def remove_all_actor_states(self):
        """
        Reset everything related to this actor's state.

        NOTE: This function's main purpose is to prevent any unwanted behaviour from dead entities by removing their actor states.
        This function should NOT be called to remove status effects from a living actor, 
        since its just modifying the values so the game engine will ignore this actor when handling actors status.
        """
        # hunger
        self.hunger = -1
        # regen
        self.heal_wounds = False
        # physical states
        self.is_burning = [0, 0, 0, 0]
        self.is_poisoned = [0, 0, 0, 0]
        self.is_freezing = [0, 0, 0, 0, 0]
        self.is_frozen = [0, 0, 0]
        self.is_electrocuting = [0, 0]
        self.is_invisible = [0, 0]
        self.is_phasing = [0, 0]
        self.is_paralyzing = [0, 0]
        self.is_bleeding = [0, 0, 0]
        self.is_acting_slower = [0, 0, 0]
        self.is_acting_faster = [0, 0, 0]
        self.is_melting = [0, 0, 0, 0]
        self.is_sick = [0.0, 0, 0]
        self.is_levitating = [0, 0]
        self.is_drowning = [0, 0]
        # nonphysical states
        self.is_sleeping = [0, 0]
        self.is_angry = [0, 0]
        self.is_confused = [0, 0]
        self.is_hallucinating = [0, 0]
        self.is_detecting_obj = [0, 0, None]
        # spatial states
        self.is_flying = False
        self.is_in_deep_pit = False
        self.is_in_shallow_pit = False
        self.is_submerged = False
        self.is_underwater = 0


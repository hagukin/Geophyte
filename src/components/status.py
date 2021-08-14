from __future__ import annotations

import copy

from components.experience import Experience

from typing import List, TYPE_CHECKING, Optional, Tuple

import random
import color
import math

from components.base_component import BaseComponent
from korean import grammar as g

if TYPE_CHECKING:
    from entity import Actor

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

class Bonus():
    """Indicates a single buff/debuff effect."""
    def __init__(self,
        bonus_id: str,
        bonus_hp=0,
        bonus_max_hp=0,
        bonus_mp=0,
        bonus_max_mp=0,
        bonus_strength=0,
        bonus_dexterity=0,
        bonus_agility=0,
        bonus_intelligence=0,
        bonus_constitution=0,
        bonus_charm=0,

        bonus_base_melee=0,
        bonus_additional_melee=0,
        bonus_protection=0,
        bonus_eyesight=0,
        bonus_hearing=0,

        bonus_fire_resistance: float=0,
        bonus_poison_resistance: float=0,
        bonus_cold_resistance: float=0,
        bonus_acid_resistance: float=0,
        bonus_psychic_resistance: float=0,
        bonus_sleep_resistance: float=0,
        bonus_shock_resistance: float=0,
        bonus_magic_resistance: float=0,

        bonus_melee_effects: Tuple=(),
        bonus_melee_effects_var: Tuple=(),
        ):
        self.bonus_id = bonus_id

        self.bonus_hp = bonus_hp
        self.bonus_max_hp = bonus_max_hp
        self.bonus_mp = bonus_mp
        self.bonus_max_mp = bonus_max_mp
        self.bonus_strength = bonus_strength
        self.bonus_dexterity = bonus_dexterity
        self.bonus_agility = bonus_agility
        self.bonus_intelligence = bonus_intelligence
        self.bonus_constitution = bonus_constitution
        self.bonus_charm = bonus_charm
        self.bonus_base_melee = bonus_base_melee
        self.bonus_additional_melee = bonus_additional_melee
        self.bonus_protection = bonus_protection

        self.bonus_eyesight = bonus_eyesight
        self.bonus_hearing = bonus_hearing

        self.bonus_fire_resistance = bonus_fire_resistance
        self.bonus_poison_resistance = bonus_poison_resistance
        self.bonus_cold_resistance = bonus_cold_resistance
        self.bonus_acid_resistance = bonus_acid_resistance
        self.bonus_psychic_resistance = bonus_psychic_resistance
        self.bonus_sleep_resistance = bonus_sleep_resistance
        self.bonus_shock_resistance = bonus_shock_resistance
        self.bonus_magic_resistance = bonus_magic_resistance

        self.bonus_melee_effect_set = {
            "burn_target": None,
            "poison_target": None,
            "freeze_target": None,
            "electrocute_target": None,
            "bleed_target": None,
            "paralyze_target": None,
            "slow_target": None,
            "sleep_target": None,
            "melt_target": None,
            "sick_target": None,
            "anger_target": None,
            "confuse_target": None,
            "hallucinate_target": None,
            "fast_target": None,
            "invisible_target": None,
            "phase_target": None,
            "levitate_target": None
        }
        if bonus_melee_effects and bonus_melee_effects_var:
            if len(bonus_melee_effects) == len(bonus_melee_effects_var):
                for i in range(len(bonus_melee_effects)):
                    self.bonus_melee_effect_set[bonus_melee_effects[i][0]] = {"chance": bonus_melee_effects[i][1],"var": bonus_melee_effects_var[i]}
            else:
                print("ERROR::melee effects != melee effects var")


class Status(BaseComponent):
    def __init__(self,
    hp,
    mp,
    strength,
    dexterity,
    constitution,
    agility,
    intelligence,
    charm,

    # Difficulty (if player, set to None)
    difficulty=None,

    # Melee Damages
    base_melee=1,
    additional_melee=1,

    # Protections
    protection=1,

    # Eyesight(vision radius)
    eyesight=6,

    # Hearing(listening radius)
    hearing=15,

    # Resistances
    fire_resistance: float=0,
    poison_resistance: float=0,
    cold_resistance: float=0,
    acid_resistance: float=0,
    psychic_resistance: float=0,
    sleep_resistance: float=0,
    shock_resistance: float=0,
    magic_resistance: float=0,

    # melee effects
    # NOTE: Pass in arguments if the actor has natural power of effecting the target when melee attacking.
    # If not, use equipable instead.
    melee_effects: Optional[Tuple] = None,
    melee_effects_var: Optional[Tuple] = None,
    ):
        super().__init__(None)
        self.difficulty = None

        self.experience: Experience = None # If the actor has an experience component, it is initalized in Actor.__init__()

        self.max_hp = hp
        self._hp = hp
        self.max_mp = mp
        self._mp = mp
        self._strength = strength
        self._dexterity = dexterity
        self._agility = agility
        self._intelligence = intelligence
        self._constitution = constitution
        self._charm = charm
        self.base_melee = base_melee
        self.additional_melee = additional_melee
        self.protection = protection

        self.difficulty = difficulty

        self.eyesight = eyesight
        self.hearing = hearing

        self.bonuses = {}

        self.fire_resistance = fire_resistance
        self.poison_resistance = poison_resistance
        self.cold_resistance = cold_resistance
        self.acid_resistance = acid_resistance
        self.psychic_resistance = psychic_resistance
        self.sleep_resistance = sleep_resistance
        self.shock_resistance = shock_resistance
        self.magic_resistance = magic_resistance

        # Use engine.add_special_effects_to_actor() as a reference
        # Apply these effects to target
        # e.g. burn_target: {"chance":0.8, "var":(1,1,0,5)}
        self.melee_effect_set = {
            "burn_target":None,
            "poison_target":None,
            "freeze_target":None,
            "electrocute_target":None,
            "bleed_target":None,
            "paralyze_target":None,
            "slow_target":None,
            "sleep_target":None,
            "melt_target":None,
            "sick_target":None,
            "anger_target":None,
            "confuse_target":None,
            "hallucinate_target":None,
            "fast_target":None,
            "invisible_target":None,
            "phase_target":None,
            "levitate_target":None
        }
        if melee_effects and melee_effects_var:
            if len(melee_effects) == len(melee_effects_var):
                for i in range(len(melee_effects)):
                    self.melee_effect_set[melee_effects[i][0]] = {"chance":melee_effects[i][1], "var":melee_effects_var[i]}
            else:
                print("ERROR::melee effects != melee effects var")

    @property
    def bonus_hp(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_hp
        return tmp

    @property
    def bonus_max_hp(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_max_hp
        return tmp

    @property
    def bonus_mp(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_mp
        return tmp

    @property
    def bonus_max_mp(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_max_mp
        return tmp

    @property
    def bonus_strength(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_strength
        return tmp

    @property
    def bonus_dexterity(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_dexterity
        return tmp

    @property
    def bonus_agility(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_agility
        return tmp

    @property
    def bonus_intelligence(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_intelligence
        return tmp

    @property
    def bonus_constitution(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_constitution
        return tmp

    @property
    def bonus_charm(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_charm
        return tmp

    @property
    def bonus_base_melee(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_base_melee
        return tmp

    @property
    def bonus_additional_melee(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_additional_melee
        return tmp

    @property
    def bonus_protection(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_protection
        return tmp

    @property
    def bonus_eyesight(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_eyesight
        return tmp

    @property
    def bonus_hearing(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_hearing
        return tmp

    @property
    def bonus_fire_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_fire_resistance
        return tmp

    @property
    def bonus_poison_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_poison_resistance
        return tmp

    @property
    def bonus_cold_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_cold_resistance
        return tmp

    @property
    def bonus_acid_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_acid_resistance
        return tmp

    @property
    def bonus_psychic_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_psychic_resistance
        return tmp

    @property
    def bonus_sleep_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_sleep_resistance
        return tmp

    @property
    def bonus_shock_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_shock_resistance
        return tmp

    @property
    def bonus_magic_resistance(self):
        tmp = 0
        for bonus in self.bonuses.values():
            tmp += bonus.bonus_magic_resistance
        return tmp

    @property
    def origin_melee_effect_set(self):
        return self.melee_effect_set

    @property
    def changed_melee_effect_set(self):
        melee_effect_set = copy.deepcopy(self.origin_melee_effect_set)
        for bonus in self.bonuses.values():
            for k, v in bonus.bonus_melee_effect_set.items():
                if v == None:
                    continue
                else:
                    if melee_effect_set[k] == None:
                        melee_effect_set[k] = {}
                        melee_effect_set[k]["chance"] = v["chance"]
                        melee_effect_set[k]["var"] = v["var"]
                    else:
                        melee_effect_set[k]["chance"] = max(melee_effect_set[k]["chance"], v["chance"])
                        melee_effect_set[k]["var"] = tuple(map(sum, zip(melee_effect_set[k]["var"], v["var"])))
        return melee_effect_set

    @property
    def origin_status(self):
        """Status of the entity's origin form. No Equipments, or buffs applied."""
        origin_status = {
            "max_hp":self.max_hp,
            "hp":self._hp,
            "max_mp":self.max_mp,
            "mp":self._mp,
            "strength":self._strength,
            "dexterity":self._dexterity,
            "agility":self._agility,
            "intelligence":self._intelligence,
            "constitution":self._constitution,
            "charm":self._charm,
            "base_melee":self.base_melee,
            "additional_melee":self.additional_melee,
            "protection":self.protection,
            "eyesight":self.eyesight,
            "hearing":self.hearing,
            "fire_resistance":self.fire_resistance,
            "poison_resistance":self.poison_resistance,
            "cold_resistance":self.cold_resistance,
            "acid_resistance":self.acid_resistance,
            "psychic_resistance":self.psychic_resistance,
            "sleep_resistance":self.sleep_resistance,
            "shock_resistance":self.shock_resistance,
            "magic_resistance":self.magic_resistance,
            }
        return origin_status

    @property
    def changed_status(self):
        """Status used for actual in-game combat calculations."""
        changed_status = {
            "max_hp":max(0, self.max_hp + self.bonus_max_hp),
            "hp":max(0, self._hp + self.bonus_hp),
            "max_mp":max(0, self.max_mp + self.bonus_max_mp),
            "mp":max(0, self._mp + self.bonus_mp),
            "strength":max(0, self._strength + self.bonus_strength),
            "dexterity":max(0, self._dexterity + self.bonus_dexterity),
            "agility":max(1, self._agility + self.bonus_agility),
            "intelligence":max(0, self._intelligence + self.bonus_intelligence),
            "constitution":max(0, self._constitution + self.bonus_constitution),
            "charm":max(0, self._charm + self.bonus_charm),
            "base_melee":max(0, self.base_melee + self.bonus_base_melee),
            "additional_melee":max(0, self.additional_melee + self.bonus_additional_melee),
            "protection":clamp(self.protection + self.bonus_protection, 1, 1000),
            "eyesight":max(1,self.eyesight + self.bonus_eyesight),
            "hearing":max(1,self.hearing + self.bonus_hearing),
            "fire_resistance":clamp(self.fire_resistance + self.bonus_fire_resistance, 0, 1),
            "poison_resistance":clamp(self.poison_resistance + self.bonus_poison_resistance, 0, 1),
            "cold_resistance":clamp(self.cold_resistance + self.bonus_cold_resistance, 0, 1),
            "acid_resistance":clamp(self.acid_resistance + self.bonus_acid_resistance, 0, 1),
            "psychic_resistance":clamp(self.psychic_resistance + self.bonus_psychic_resistance, 0, 1),
            "sleep_resistance":clamp(self.sleep_resistance + self.bonus_sleep_resistance, 0, 1),
            "shock_resistance":clamp(self.shock_resistance + self.bonus_shock_resistance, 0, 1),
            "magic_resistance":clamp(self.magic_resistance + self.bonus_magic_resistance, 0, 1),
            }
        return changed_status

    def check_if_has_bonus(self, bonus_id: str) -> bool:
        for b in self.bonuses.keys():
            if b == bonus_id:
                return True
        return False

    def add_bonus(self, bonus: Bonus) -> None:
        # Removed the lines below because there are too many cases of overwriting a bonus.
        # if bonus.bonus_id in self.bonuses.keys(): # If there is bonus of same id, replace it.
        #     print(f"WARNING::status - bonus {bonus.bonus_id} has been overwritten.")
        if self.check_if_has_bonus(bonus.bonus_id):
            print(f"WARNING::{bonus.bonus_id} Bonus already exists. Overwritten.")
        self.bonuses[bonus.bonus_id] = bonus

    def remove_bonus(self, bonus_id: str, ignore_warning: bool=False) -> None:
        try:
            del self.bonuses[bonus_id]
        except KeyError:
            if not ignore_warning:
                print(f"WARNING::TRIED TO REMOVE key-{bonus_id} BONUS BUT IT DOES NOT EXIST.")
            return None
        except:
            raise Exception("FATAL ERROR::status.remove_bonus()")

    def remove_all_bonuses(self):
        self.bonuses.clear()

    def death(self, cause: str="low_hp") -> None:
        self.parent.actor_state.is_dead = True
        self.parent.actor_state.remove_all_actor_states(include_spatial_states=True)
        self.remove_all_bonuses()

        # death cause
        if cause == "low_hp":
            death_message = ""
        elif cause == "lack_of_strength":
            death_message = f"{g(self.parent.name, '은')} 스스로를 가누지 못할 만큼 약해졌다!\n"
        elif cause == "starvation":
            death_message = f"{g(self.parent.name, '은')} 충분한 영양분을 얻지 못했다!\n"
        elif cause == "drowning":
            death_message = f"{g(self.parent.name, '은')} 충분한 산소를 공급받지 못했다!\n"
        else:
            death_message = "UNDEFINED"

        if self.engine.player is self.parent:
            death_message += "당신은 죽었다!"
            death_message_color = color.player_die
            from input_handlers import GameOverEventHandler
            self.engine.event_handler = GameOverEventHandler()
        elif self.engine.game_map.visible[self.parent.x, self.parent.y]:  # if dead entity is in player's visible range
            death_message += f"{g(self.parent.name, '이')} 죽었다!"
            death_message_color = color.enemy_unique
        else:
            death_message_color = color.white
            pass  # Show nothing if entity is not in visible radius.
        # Add messagen to log
        self.engine.message_log.add_message(death_message, fg=death_message_color, target=self.parent)

        # Delete dead entity
        self.parent.remove_self()

    ### Health Point
    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and not self.parent.actor_state.has_immortality:
            self.parent.die("low_hp")

    def heal(self, amount) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def calculate_dmg_reduction(self, damage: int, damage_type: str=None, ignore_reduction: bool = False, penetration_constant:int=10,  round_dmg:bool = True) -> int:
        """
        Calculate the damage reduction, and return the actual damage that is applied.

        Args:
            damage_type: 
                "fire" / "poison" / "cold" / "acid" / "psychic" / "shock" / "magic" / "physical" / None

                Melee, throwing impact is considered "physical".
                if None, the damage is considered pure type, and nothing will happen.
                "magic" only applies to pure magic attacks. For example fire ray magic is considered "fire".

            penetration_constant:
                When additional values should be passed use this.
                Attacker's Strength is generally passed here.
                E.g. When calculating physical type damages, attacker's strength is passed to penetration_constant.
        """
        dmg = damage

        # Damage reduction
        if damage_type and not ignore_reduction:
            if damage_type == "physical":
                # if dmg type is physical, use protection to calculate reduction
                protection = self.changed_status["protection"]
                penetration = 1 + math.log10(penetration_constant/10 + 1)
                dmg_absorbed = random.randint(int(protection * 0.3 /penetration), int(protection * 0.9 /penetration))
                dmg_reduced = 1 + protection * math.log2(protection / 700 + 1)
                dmg = (dmg - dmg_absorbed) / dmg_reduced
            elif damage_type == "explosion":
                # NOTE: explosion damages are exactly like physical damage, except that is ignores any penetration constants given.
                protection = self.changed_status["protection"]
                dmg_absorbed = random.randint(0, int(protection))
                dmg_reduced = 1 + math.log2(protection/5 + 1)
                dmg = (dmg - dmg_absorbed) / dmg_reduced
            elif damage_type == "fire":
                dmg *= (1 - self.changed_status["fire_resistance"])
            elif damage_type == "poison":
                dmg *= (1 - self.changed_status["poison_resistance"])
            elif damage_type == "cold":
                dmg *= (1 - self.changed_status["cold_resistance"])
            elif damage_type == "acid":
                dmg *= (1 - self.changed_status["acid_resistance"])
            elif damage_type == "psychic":
                dmg *= (1 - self.changed_status["psychic_resistance"])
            elif damage_type == "shock":
                dmg *= (1 - self.changed_status["shock_resistance"])
            elif damage_type == "magic":
                protection = self.origin_status["protection"] # when calculating magic dmg, use origin_status["protection"]. -> armor will have no effects.
                dmg_absorbed = random.randint(0, int(protection/4)) # absorb protection/4
                dmg_reduced = self.changed_status["magic_resistance"]
                dmg = (dmg - dmg_absorbed) * (1 - dmg_reduced)

        if round_dmg:
            dmg = max(0, round(dmg))
        else:
            dmg = max(0, dmg)
        return dmg

    def take_damage(self, amount, attacked_from:Actor=None) -> None:
        """Reduce the health point by the exact given amount.
        This function can be used for triggering certain actors."""
        # set attacker (trigger ai)
        if attacked_from:
            if self.parent.ai and attacked_from != self.parent: #Cannot target self
                self.parent.ai.attacked_from = attacked_from
        
        self.hp -= amount

        # When damaged, delete all queued actions.
        if self.parent == self.engine.player:
            self.engine.player_path.clear()
            self.engine.player_dir = None

    ### Magic Power
    @property
    def mp(self) -> int:
        return self._mp

    @mp.setter
    def mp(self, value) -> None:
        self._mp = max(0, min(value, self.max_mp))

    def gain_mana(self, amount) -> int:
        if self.mp == self.max_hp:
            return 0

        new_mp_value = self.mp + amount

        if new_mp_value > self.max_mp:
            new_mp_value = self.max_mp

        amount_gained = new_mp_value - self.mp

        self.mp = new_mp_value

        return amount_gained

    def lose_mana(self, amount) -> None:
        self.mp -= amount


    ### Strength
    @property
    def strength(self) -> int:
        return self._strength

    @strength.setter
    def strength(self, value) -> None:
        self._strength = value
        if self._strength == 0 and self.parent.ai:
            self.parent.die("lack_of_strength")

    def gain_strength(self, amount):
        self._strength += amount
        self.parent.inventory.update_burden()
        return amount
    
    def lose_strength(self, amount):
        self._strength -= amount
        self.parent.inventory.update_burden()
        return amount


    ### Dexterity
    @property
    def dexterity(self) -> int:
        return self._dexterity

    @dexterity.setter
    def dexterity(self, value) -> None:
        self._dexterity = value

    def gain_dexterity(self, amount):
        self._dexterity += amount
        return amount
    
    def lose_dexterity(self, amount):
        self._dexterity -= amount
        return amount


    ### Agility
    @property
    def agility(self) -> int:
        return self._agility

    @agility.setter
    def agility(self, value) -> None:
        self._agility = value

    def gain_agility(self, amount):
        self._agility += amount
        return amount
    
    def lose_agility(self, amount):
        self._agility -= amount
        return amount


    ### Intelligence
    @property
    def intelligence(self) -> int:
        return self._intelligence

    @intelligence.setter
    def intelligence(self, value) -> None:
        self._intelligence = value

    def gain_intelligence(self, amount):
        self._intelligence += amount
        return amount
    
    def lose_intelligence(self, amount):
        self._intelligence -= amount
        return amount

    
    ### Constitution
    @property
    def constitution(self) -> int:
        return self._constitution

    @constitution.setter
    def constitution(self, value) -> None:
        self._constitution = value

    def gain_constitution(self, amount):
        self._constitution += amount
        return amount
    
    def lose_constitution(self, amount):
        self._constitution -= amount
        return amount


    ### Charm
    @property
    def charm(self) -> int:
        return self._charm

    @charm.setter
    def charm(self, value) -> None:
        self._charm = value

    def gain_charm(self, amount):
        self._charm += amount
        return amount
    
    def lose_charm(self, amount):
        self._charm -= amount
        return amount


    ### Resistances
    def change_resistance(self, resistance_type: str, value):
        """
        The original(natural) resistance of the actor.
        """
        if resistance_type == "fire":
            self.fire_resistance = clamp(self.fire_resistance + value, 0, 1)
        if resistance_type == "poison":
            self.poison_resistance = clamp(self.poison_resistance + value, 0, 1)
        if resistance_type == "cold":
            self.cold_resistance = clamp(self.cold_resistance + value, 0, 1)
        if resistance_type == "acid":
            self.acid_resistance = clamp(self.acid_resistance + value, 0, 1)
        if resistance_type == "psychic":
            self.psychic_resistance = clamp(self.psychic_resistance + value, 0, 1)
        if resistance_type == "sleep":
            self.sleep_resistance = clamp(self.sleep_resistance + value, 0, 1)
        if resistance_type == "shock":
            self.shock_resistance = clamp(self.shock_resistance + value, 0, 1)

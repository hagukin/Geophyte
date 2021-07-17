from __future__ import annotations
from components.experience import Experience

from typing import List, TYPE_CHECKING

import random
import color
import item_factories
import copy
import math

from components.base_component import BaseComponent
from input_handlers import GameOverEventHandler
from korean import grammar as g

if TYPE_CHECKING:
    from entity import Actor

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

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

    # Bonus
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

    # Resistances
    fire_resistance: float=0,
    poison_resistance: float=0,
    cold_resistance: float=0,
    acid_resistance: float=0,
    psychic_resistance: float=0,
    sleep_resistance: float=0,
    shock_resistance: float=0,
    magic_resistance: float=0,

    # Bonus Resistances
    bonus_fire_resistance: float=0,
    bonus_poison_resistance: float=0,
    bonus_cold_resistance: float=0,
    bonus_acid_resistance: float=0,
    bonus_psychic_resistance: float=0,
    bonus_sleep_resistance: float=0,
    bonus_shock_resistance: float=0,
    bonus_magic_resistance: float=0,
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

        self.fire_resistance = fire_resistance
        self.poison_resistance = poison_resistance
        self.cold_resistance = cold_resistance
        self.acid_resistance = acid_resistance
        self.psychic_resistance = psychic_resistance
        self.sleep_resistance = sleep_resistance
        self.shock_resistance = shock_resistance
        self.magic_resistance = magic_resistance

        self.bonus_fire_resistance = bonus_fire_resistance
        self.bonus_poison_resistance = bonus_poison_resistance
        self.bonus_cold_resistance = bonus_cold_resistance
        self.bonus_acid_resistance = bonus_acid_resistance
        self.bonus_psychic_resistance = bonus_psychic_resistance
        self.bonus_sleep_resistance = bonus_sleep_resistance
        self.bonus_shock_resistance = bonus_shock_resistance
        self.bonus_magic_resistance = bonus_magic_resistance

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

    def reset_bonuses(self, status_types: List[str]=None):
        """
        reset all status bonuses (except for equipments bonuses)

        Args:
            status_types:
                ex. ["bonus_strength", "bonus_agility"] to remove bonus for strength and agility
        """
        # Get list of equipped items
        equipments_list = list(self.parent.equipments.equipments.values())

        if equipments_list:
            # temporarily remove bonuses granted from equipments
            for item in equipments_list:
                if item:
                    self.parent.equipments.remove_equipable_bonuses(item)

        # reset bonus
        for stat_type in status_types:
            if stat_type == "bonus_hp":
                self.bonus_hp = 0
            elif stat_type == "bonus_mp":
                self.bonus_mp = 0
            elif stat_type == "bonus_max_hp":
                self.bonus_max_hp = 0
            elif stat_type == "bonus_max_mp":
                self.bonus_max_mp = 0
            elif stat_type == "bonus_strength":
                self.bonus_strength = 0
            elif stat_type == "bonus_dexterity":
                self.bonus_dexterity = 0
            elif stat_type == "bonus_intelligence":
                self.bonus_intelligence = 0
            elif stat_type == "bonus_agility":
                self.bonus_agility = 0
            elif stat_type == "bonus_charm":
                self.bonus_charm = 0
            elif stat_type == "bonus_constitution":
                self.bonus_constitution = 0
            elif stat_type == "bonus_base_melee":
                self.bonus_base_melee = 0
            elif stat_type == "bonus_additional_melee":
                self.bonus_additional_melee = 0
            elif stat_type == "bonus_protection":
                self.bonus_protection = 0
            elif stat_type == "bonus_fire_resistance":
                self.bonus_fire_resistance = 0
            elif stat_type == "bonus_poison_resistance":
                self.bonus_poison_resistance = 0
            elif stat_type == "bonus_acid_resistance":
                self.bonus_acid_resistance = 0
            elif stat_type == "bonus_cold_resistance":
                self.bonus_cold_resistance = 0
            elif stat_type == "bonus_psychic_resistance":
                self.bonus_psychic_resistance = 0
            elif stat_type == "bonus_sleep_resistance":
                self.bonus_sleep_resistance = 0
            elif stat_type == "bonus_shock_resistance":
                self.bonus_shock_resistance = 0
            elif stat_type == "bonus_magic_resistance":
                self.bonus_magic_resistance = 0

        if equipments_list:
            # re-apply bonuses for each equipments
            for item in equipments_list:
                if item:
                    self.parent.equipments.add_equipable_bonuses(item)
    
    def die(self, cause: str="low_hp") -> None:
        self.parent.actor_state.is_dead = True

        # Drop Everything
        drop_list = []
        for item in self.parent.inventory.items:
            drop_list.append(item)
        for drop_item in drop_list:
            self.parent.inventory.drop(item=drop_item, show_msg=False)

        # Remove all actor state
        self.parent.actor_state.remove_all_actor_states(include_spatial_states=True)

        # Spawn corpse entity
        if self.parent.edible: # if edible is None, no corpse is spawned.
            new_corpse = item_factories.corpse.spawn(self.parent.gamemap, self.parent.x, self.parent.y)
            new_corpse.weight = max(round(self.parent.actor_state.weight / 2, 2), 0.01)
            new_corpse.change_name(self.parent.name + " 시체")
            new_corpse.edible = self.parent.edible # copy edible value from parent
            new_corpse.edible.parent = new_corpse

            #TODO: might have to save self.parent to new_corpse (for resurrection feature)

        # Remove all actor states to prevent bugs
        self.parent.actor_state.remove_all_actor_states()

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
            self.engine.event_handler = GameOverEventHandler()
        elif self.engine.game_map.visible[self.parent.x, self.parent.y]:  # if dead entity is in player's visible range
            death_message += f"{g(self.parent.name, '이')} 죽었다!"
            death_message_color = color.enemy_die
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
            self.die()

    def heal(self, amount) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def calculate_dmg_reduction(self, damage: int, damage_type: str=None, ignore_reduction: bool = False, penetration_constant: float = 0) -> int:
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
                E.g. When calculating physical type damages, attacker's strength is passed to penetration_constant.
        """
        dmg = damage

        # Damage reduction
        if damage_type and not ignore_reduction:
            if damage_type == "physical":
                # if dmg type is physical, use protection to calculate reduction
                protection = self.changed_status["protection"]
                penetration = 1 + math.log10(penetration_constant/10 + 1) # y = log2(x/10 + 1) + 1 # TODO: adjust the constant 10
                dmg_absorbed = random.randint(0, int(protection * 0.3 /penetration))
                dmg_reduced = 1 + protection * math.log2(protection / 700 + 1) # y = 1 + x*log2(x/700 + 1)
                dmg = (dmg - dmg_absorbed) / dmg_reduced
            elif damage_type == "explosion":
                # NOTE: explosion damages are exactly like physical damage, except that is ignores any penetration constants given.
                protection = self.changed_status["protection"]
                dmg_absorbed = random.randint(0, int(protection))
                dmg_reduced = 1 + math.log2(protection/5 + 1) # y = 1 + log2(x/5 + 1)
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

        dmg = max(0, round(dmg))

        return dmg

    def take_damage(self, amount, attacked_from:Actor=None) -> None:
        """Reduce the health point by the exact given amount.
        This function can be used for triggering certain actors."""
        # set attacker (trigger ai)
        if attacked_from:
            if self.parent.ai and attacked_from != self.parent: #Cannot target self
                self.parent.ai.attacked_from = attacked_from
        
        self.hp -= amount

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
            self.die("lack_of_strength")

    def gain_strength(self, amount):
        self._strength += amount
        return amount
    
    def lose_strength(self, amount):
        self._strength -= amount
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

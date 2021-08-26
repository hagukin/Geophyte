from __future__ import annotations

from typing import List, Tuple, Optional
from entity import Actor, SemiActor, Entity, Item
from ability import Ability
from components.activatable import SpellActivateable


class Skill_AI():
    """
    Contains functions that let ai to decide whether to use a skill/spell or not.
    Functions are static, so you don't have to initialize Skill_AI instance for each AIs.

    Functions will return True if the AI decided to try cast/apply that spell/skill.

        ### FLOW
        # 1. Check if the AI has the abilities that they can use.
        # 2. Check for valid range, mana, etc.
        # 3. If it all satisfies the conditions, return the coordinates.
        ###
    """

    def __init__(self) -> None:
        """
        """
        pass

    @staticmethod
    def skill(actor: Actor, target: Actor) -> Optional[Tuple[bool, Optional[Tuple[int,int]]]]:
        # NOTE: This function does nothing, and should not be used/called.
        """
        Return:
            Tuple[whether the ai will use this skill or not, the coordinates of the tile to use the skill(can be None)]
            Coordinates of the location to apply the skill.
            If there is no coordinates needed, return None.
            If something went wrong and you couldn't get the coordinate, return
        """
        coordinate = None
        raise NotImplementedError()

    @staticmethod
    def check_mana(actor: Actor, spell: Ability):
        if spell != None and actor.status.changed_status["mp"] >= spell.activatable.mana_cost:
            return True
        return False

    @staticmethod
    def skill_steal(actor: Actor, target: Actor) -> Optional[Tuple[bool, Optional[Tuple[int,int]]]]:
        coordinate = None
        if not actor.inventory.check_if_full():
            # Check if this actor has the ability
            steal = actor.ability_inventory.get_ability_by_id("sk_steal")
            # Set the direction and check the range
            dxdy = actor.ai.get_ranged_direction(attacker=actor, target=target, valid_range=1)
            if dxdy:
                coordinate = actor.x + dxdy[0], actor.y + dxdy[1]
            # Ignore mana since this is a "Skill" not a "Spell"
            if steal and coordinate != None:
                return True, coordinate
        return False, coordinate

    @staticmethod
    def spell_lightning_bolt(actor: Actor, target: Actor) -> Optional[Tuple[bool, Optional[Tuple[int,int]]]]:
        coordinate = None
        # Check if this actor has the ability
        lightning_bolt = actor.ability_inventory.get_ability_by_id("sp_lightning_bolt")
        if Skill_AI.check_mana(actor=actor, spell=lightning_bolt):
            return True, coordinate
        return False, coordinate

    @staticmethod
    def spell_spectral_beam(actor: Actor, target: Actor) -> Optional[Tuple[bool, Optional[Tuple[int,int]]]]:
        coordinate = None
        # Check if this actor has the ability
        spectral_beam = actor.ability_inventory.get_ability_by_id("sp_spectral_beam")
        if Skill_AI.check_mana(actor=actor, spell=spectral_beam):
            # Set the direction and check the range
            dxdy = actor.ai.get_ranged_direction(attacker=actor, target=target, valid_range=999)
            if dxdy:
                coordinate = actor.x + dxdy[0], actor.y + dxdy[1]

            if coordinate != None:
                return True, coordinate
        return False, coordinate

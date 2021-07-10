from __future__ import annotations

import random

from typing import TYPE_CHECKING
from numpy.lib.twodim_base import tri
from components.base_component import BaseComponent
from entity import Actor, Item
from korean import grammar as g


class Walkable(BaseComponent):
    parent: Item
    def __init__(self):
        pass

    def perform(self, target) -> None:
        raise NotImplementedError


class TrapWalkable(Walkable):
    def __init__(self, trigger_once: bool, untrap_chance: float, check_item: bool, check_actor: bool, continuous_effect: bool = False):
        """
        Args:
            triggered:
                Boolean. If the trap is triggered once or more before, set to True
            trigger_once:
                Boolean. If the trap only works once, set to True.
            untrap_chance:
                Boolean. Effects the chance of successfully untrapping this trap.
                NOTE: Currently unused.
            check_item:
                Boolean. If True, the trap will check whether there is item entity on top of it every single turn.
            check_actor:
                Boolean. If True, the trap will check whether there is actor entity on top of it every single turn.
            previous_entity:
                Save the last entity that triggered(activated) this trap.
            continuous_effect:
                Boolean. If True, the trap will continuously apply the effect to the target even if the target stays still on the trap.
        """
        super().__init__()
        self.triggered = False
        self.trigger_once = trigger_once
        self.untrap_chance = untrap_chance
        self.check_item = check_item
        self.check_actor = check_actor
        self.previous_entity = None
        self.continuous_effect = continuous_effect

    def when_item_on_trap(self, target) -> None:
        pass

    def when_actor_on_trap(self, target) -> None:
        pass

    def perform(self, target) -> None:
        """
        Unlike regular semiactors, traps does not use Rule component to handle actions.
        Instead, trap is called from entities' do_environmental_effects().
        """
        # Check if trap is one-time-use only and has already been used.
        if self.trigger_once and self.triggered:
            return None

        if target:
            # If trap applies effect continuosly
            if not self.continuous_effect:
                if target == self.previous_entity:
                    return None

            # Prevent performing multiple times in a single turn
            if self.check_actor and isinstance(target, Actor):
                self.triggered = True
                self.previous_entity = target
                self.when_actor_on_trap(target)
                return None
            if self.check_item and isinstance(target, Item):
                self.triggered = True
                self.previous_entity = target
                self.when_item_on_trap(target)
                return None
        else:
            # If there is no target currently, set previous_entity back to None
            self.previous_entity = None


class SpikeTrapWalkable(TrapWalkable):
    def __init__(self, trigger_once, untrap_chance, check_item, check_actor, continuous_effect, base_damage, add_damage):
        super().__init__(trigger_once, untrap_chance, check_item, check_actor, continuous_effect)

        self.base_damage = base_damage
        self.add_damage = add_damage

    def when_actor_on_trap(self, target):
        # No damage when something is equipped on feet
        feet_item = target.equipments.equipments["feet"]
        if feet_item:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '은')} 가시 함정을 밟았지만, {g(feet_item.name, '이')} {g(target.name, '을')} 보호했다!", target=target)

            return None

        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} 가시 함정 위를 넘어갔다.", target=target)

            return None

        # else
        dmg = self.base_damage + random.randint(0, self.add_damage)
        if self.gamemap.visible[target.x, target.y]:
            self.engine.message_log.add_message(f"{g(target.name, '이')} 가시 함정을 밟아 {dmg} 데미지를 받았다.", target=target)
        target.status.take_damage(dmg)


############################################################
############################################################
############################################################


low_dmg_spike_trap_walkable = SpikeTrapWalkable(trigger_once=False, untrap_chance=0.5, check_item=False, check_actor=True, continuous_effect=False, base_damage=1, add_damage=3)
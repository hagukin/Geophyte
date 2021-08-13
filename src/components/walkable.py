from __future__ import annotations

import random
import color

from typing import TYPE_CHECKING, List, Tuple
from numpy.lib.twodim_base import tri
from components.base_component import BaseComponent
from entity import Actor, Item, Entity
from korean import grammar as g


class Walkable(BaseComponent):
    def __init__(self):
        super().__init__(None) #parent: Entity

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
                self.previous_entity = target
                self.when_actor_on_trap(target)
                self.triggered = True
                if self.trigger_once:
                    self.parent._fg = color.black
                    self.parent._name += "(해제됨)"
                return None
            if self.check_item and isinstance(target, Item):
                self.previous_entity = target
                self.when_item_on_trap(target)
                self.triggered = True
                if self.trigger_once:
                    self.parent._fg = color.black
                    self.parent._name += "(해제됨)"
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
        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} {self.parent.name} 위를 넘어갔다.", target=target)

            return None

        # No damage when something is equipped on feet
        feet_item = target.equipments.equipments["feet"]
        if feet_item:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '은')} {g(self.parent.name, '을')} 밟았지만, {g(feet_item.name, '이')} {g(target.name, '을')} 보호했다!", target=target)

            return None

        # else
        dmg = self.base_damage + random.randint(0, self.add_damage)
        if target == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 밟아 {dmg} 데미지를 받았다.")
        else:
            self.engine.message_log.add_message(f"{g(target.name, '이')} {g(self.parent.name, '을')} 밟아 {dmg} 데미지를 받았다.",
                                                target=target)
        target.status.take_damage(dmg)


class FlameTrapWalkable(TrapWalkable):
    def __init__(self,
                 untrap_chance,
                 check_item,
                 check_actor,
                 burn_value: Tuple[int, int, int, int],
                 trigger_once=True,
                 continuous_effect=False,
                 ):
        super().__init__(trigger_once, untrap_chance, check_item, check_actor, continuous_effect)
        self.burn_value = burn_value

    def when_item_on_trap(self, target) -> None:
        target.collided_with_fire()

    def when_actor_on_trap(self, target):
        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} {self.parent.name} 위를 넘어갔다.", target=target)

            return None

        # No damage when something is equipped on feet
        feet_item = target.equipments.equipments["feet"]
        if feet_item:
            feet_item.collided_with_fire()

        # else
        if target == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 밟았다.", target=target)
        else:
            self.engine.message_log.add_message(f"{g(target.name, '이')} {g(self.parent.name, '을')} 밟았다.", target=target)
        if not target.actor_state.is_dead:
            target.actor_state.apply_burning(list(self.burn_value))


class IcicleTrapWalkable(TrapWalkable):
    def __init__(self,
                 untrap_chance,
                 check_item,
                 check_actor,
                 base_damage,
                 add_damage,
                 freeze_value: Tuple[int, int, float, int, int],
                 bleed_value: Tuple[int,int,int],
                 trigger_once=False,
                 continuous_effect=False,
                 ):
        super().__init__(trigger_once, untrap_chance, check_item, check_actor, continuous_effect)
        self.base_damage = base_damage
        self.add_damage = add_damage
        self.freeze_value = freeze_value
        self.bleed_value = bleed_value

    def when_actor_on_trap(self, target):
        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} {self.parent.name} 위를 넘어갔다.", target=target)

            return None

        # else
        dmg = self.base_damage + random.randint(0, self.add_damage)
        if target == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 밟아 {dmg} 데미지를 받았다.")
        else:
            self.engine.message_log.add_message(f"{g(target.name, '이')} {g(self.parent.name, '을')} 밟아 {dmg} 데미지를 받았다.",
                                                target=target)
        target.status.take_damage(dmg)
        if not target.actor_state.is_dead:
            target.actor_state.apply_freezing(list(self.freeze_value))
        if not target.actor_state.is_dead:
            target.actor_state.apply_bleeding(list(self.bleed_value))


class AcidSprayTrapWalkable(TrapWalkable):
    def __init__(self, trigger_once, untrap_chance, check_item, check_actor, continuous_effect, melt_value: Tuple[int, int, int, int]):
        super().__init__(trigger_once, untrap_chance, check_item, check_actor, continuous_effect)
        self.melt_value = melt_value

    def when_actor_on_trap(self, target):
        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} {self.parent.name} 위를 넘어갔다.", target=target, fg=color.player_sense)

            return None

        # else
        if target == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 밟았다.", target=target, fg=color.player_not_good)
            self.engine.message_log.add_message(f"{g(target.name, '이')} 산성 물질을 분사한다!", target=target, fg=color.player_bad)
        else:
            self.engine.message_log.add_message(f"{g(target.name, '이')} {g(self.parent.name, '을')} 밟았다.", target=target, fg=color.enemy_neutral)
        if not target.actor_state.is_dead:
            target.actor_state.apply_melting(list(self.melt_value))


class PoisonSpikeTrapWalkable(TrapWalkable):
    def __init__(self, trigger_once, untrap_chance, check_item, check_actor, continuous_effect, base_damage,
                 add_damage, poison_value: Tuple[int, int, int, int]):
        super().__init__(trigger_once, untrap_chance, check_item, check_actor, continuous_effect)
        self.base_damage = base_damage
        self.add_damage = add_damage
        self.poison_value = poison_value

    def when_actor_on_trap(self, target):
        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} {self.parent.name} 위를 넘어갔다.", target=target,
                                                    fg=color.player_sense)
            return None

        # No damage when something is equipped on feet
        feet_item = target.equipments.equipments["feet"]
        if feet_item:
            if feet_item.equipable:
                if feet_item.equipable.eq_protection > 0: # Solid boots
                    if target == self.engine.player:
                        self.engine.message_log.add_message(
                            f"당신은 {g(self.parent.name, '을')} 밟았지만, {g(feet_item.name, '이')} {g(target.name, '을')} 보호했다!",
                            fg=color.player_neutral)

                    return None

        # else
        dmg = self.base_damage + random.randint(0, self.add_damage)
        if target == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 밟아 {dmg} 데미지를 받았다.", fg=color.player_bad)
        else:
            self.engine.message_log.add_message(f"{g(target.name, '이')} {g(self.parent.name, '을')} 밟아 {dmg} 데미지를 받았다.",
                                                target=target, fg=color.enemy_unique)
        target.status.take_damage(dmg)
        if not target.actor_state.is_dead:
            target.actor_state.apply_poisoning(list(self.poison_value))


class SonicBoomTrapWalkable(TrapWalkable):
    def __init__(self,
                 untrap_chance,
                 check_item,
                 check_actor,
                 continuous_effect,
                 confuse_value: Tuple[int, int],
                 trigger_once=True
    ):
        super().__init__(trigger_once, untrap_chance, check_item, check_actor, continuous_effect)
        self.confuse_value = confuse_value

    def sonic_boom(self, target) -> None:
        from util import get_distance
        if self.parent == self.engine.player:
            self.engine.message_log.add_message(f"던전 전체에 굉음이 울린다!", fg=color.world, target=self.parent)
        elif self.engine.game_map.visible[self.parent.x, self.parent.y]:
            self.engine.message_log.add_message(f"던전 전체에 굉음이 울린다!", fg=color.world, target=self.parent)
        elif get_distance(self.parent.x, self.parent.y, self.engine.player.x, self.engine.player.y) <= self.engine.player.status.changed_status["hearing"]:
            self.engine.message_log.add_message(f"던전 어디에선가 굉음이 들린다.", fg=color.player_sense, target=self.parent)
        for actor in self.engine.game_map.actors:
            if actor.ai:
                if get_distance(self.parent.x, self.parent.y, actor.x, actor.y) <= actor.status.changed_status["hearing"]:
                    actor.ai.activate()

    def when_item_on_trap(self, target) -> None:
        self.sonic_boom(target)

    def when_actor_on_trap(self, target):
        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} {self.parent.name} 위를 넘어갔다.", target=target,
                                                    fg=color.player_sense)
            return None

        if target == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 밟았다.", target=target)
        else:
            self.engine.message_log.add_message(f"{g(target.name, '이')} {g(self.parent.name, '을')} 밟았다.", target=target)

        self.sonic_boom(target)
        if not target.actor_state.is_dead:
            target.actor_state.apply_confusion(list(self.confuse_value))


class ExplosionTrapWalkable(TrapWalkable):
    def __init__(self,
                 untrap_chance,
                 check_item,
                 check_actor,
                 trigger_once=True,
                 continuous_effect=False,
                 expl_dmg=30,
                 radius=1,
                 dmg_reduction_by_dist=10,
                 cause_fire: int = 3
                 ):
        super().__init__(trigger_once, untrap_chance, check_item, check_actor, continuous_effect)
        self.expl_dmg = expl_dmg
        self.radius = radius
        self.dmg_reduction_by_dist = dmg_reduction_by_dist
        self.cause_fire = cause_fire

    def explode(self, entity: Entity) -> None:
        self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 폭발했다!", target=self.parent, fg=color.world)
        from explosion_action import ExplodeAction
        expl = ExplodeAction(
            self.parent,
            True,
            True,
            radius=self.radius,
            expl_dmg=self.expl_dmg,
            dmg_reduction_by_dist=self.dmg_reduction_by_dist,
            cause_fire=self.cause_fire
        )
        expl.perform()

    def when_item_on_trap(self, target) -> None:
        self.explode(target)

    def when_actor_on_trap(self, target):
        # No effects when levitating(flying)
        if target.is_on_air:
            if self.gamemap.visible[target.x, target.y]:
                self.engine.message_log.add_message(f"{g(target.name, '이')} {self.parent.name} 위를 넘어갔다.", target=target,
                                                    fg=color.player_sense)
            return None

        # else
        if target == self.engine.player:
            self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 밟았다.", fg=color.player_not_good)
        else:
            self.engine.message_log.add_message(f"{g(target.name, '이')} {g(self.parent.name, '을')} 밟았다.", target=target, fg=color.enemy_unique)
        self.explode(target)

############################################################
############################################################
############################################################


low_dmg_spike_trap_walkable = SpikeTrapWalkable(
    trigger_once=False,
    untrap_chance=0.5,
    check_item=False,
    check_actor=True,
    continuous_effect=False,
    base_damage=6,
    add_damage=6
)

low_dmg_flame_trap_walkable = FlameTrapWalkable(
    trigger_once=True,
    untrap_chance=0.3,
    check_item=True,
    check_actor=True,
    continuous_effect=False,
    burn_value=(5, 3, 0, 6),
)

low_dmg_icicle_trap_walkable = IcicleTrapWalkable(
    trigger_once=False,
    untrap_chance=0.5,
    check_item=False,
    check_actor=True,
    continuous_effect=False,
    base_damage=2,
    add_damage=2,
    freeze_value=(2, 1, 0.1, 0, 3),
    bleed_value=(1, 0, 3),
)

low_dmg_acid_spray_trap_walkable = AcidSprayTrapWalkable(
    trigger_once=True,
    untrap_chance=0.2,
    check_item=True,
    check_actor=True,
    continuous_effect=False,
    melt_value=(7,3,0,3)
)

low_dmg_poison_spike_trap_walkable = PoisonSpikeTrapWalkable(
    trigger_once=False,
    untrap_chance=0.5,
    check_actor=True,
    check_item=False,
    base_damage=6,
    add_damage=6,
    continuous_effect=False,
    poison_value=(1,2,0,6)
)

sonic_boom_trap_walkable = SonicBoomTrapWalkable(
    trigger_once=True,
    untrap_chance=0.3,
    check_item=True,
    check_actor=True,
    continuous_effect=False,
    confuse_value=(0,6),
)

low_dmg_explosion_trap_walkable = ExplosionTrapWalkable(
    trigger_once=True,
    untrap_chance=0.2,
    check_item=True,
    check_actor=True,
    continuous_effect=False,
    expl_dmg=30,
    radius=2,
    dmg_reduction_by_dist=10,
    cause_fire=3,
)

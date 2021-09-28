from __future__ import annotations
from os import dup
from animation import Animation
from typing import Optional, TYPE_CHECKING, Tuple
from components.base_component import BaseComponent
from input_handlers import RayDirInputHandler, RayRangedInputHandler, SingleRangedAttackHandler
from korean import grammar as g
from entity import Actor, Entity

import random
import actions
import color

if TYPE_CHECKING:
    from ability import Ability


class Activatable(BaseComponent):
    """
    A component for ability classes.
    When abilities are used, methods from this component are called.
    """
    def __init__(self):
        super().__init__(None)

    def get_action(self, caster: Actor, x: int=None, y: int=None, target: Actor=None) -> Optional[actions.Action]:
        """
        NOTE: This function MUST be overriden indivisually.

        If the caster is player, 
        there are probably no parameter passed in to this function except for the caster information, which is perfectly normal.
        This function will set input_handler to appropriate type of input handler and return None.
        The input handler will then return an action as a callback, and the action will include necessary parameters like x, y, and target.

        If the caster is AI,
        parameters will be passed in from the AI, and this function will return an action object.
        """
        return actions.AbilityAction(entity=caster, ability=self.parent, x=x, y=y, target=target)

    def activate(self, action: actions.ReadItem) -> None:
        """
        NOTE: This function MUST be overriden indivisually.

        Actual activation of the ability.
        """
        raise NotImplementedError()


####################
###### SKILLS ######
####################

class StealActivatable(Activatable):
    """
    Steal a random item from the target actor.
    """
    def get_action(self, caster: Actor, x: int=None, y: int=None, target: Actor=None):
        if caster == self.engine.player:
            self.engine.message_log.add_message("대상을 선택하세요.", color.help_msg)
            self.engine.event_handler = RayDirInputHandler(
                actor=caster,
                max_range=1,
                callback=lambda dx, dy: actions.AbilityAction(entity=caster, ability=self.parent, x=caster.x + dx, y=caster.y + dy, target=self.gamemap.get_actor_at_location(x=caster.x + dx, y=caster.y + dy)),
            )
            return None
        else:
            return super().get_action(caster, x, y, target)

    def activate(self, action: actions.AbilityAction):
        attacker = action.entity
        target = action.target

        # If there is no target
        if not target:
            if attacker == self.engine.player:
                self.engine.message_log.add_message(f"당신은 허공에서 훔칠만한 것을 찾아보았지만 실패했다.", target=attacker, fg=color.player_failed)
            else:
                self.engine.message_log.add_message(f"{g(attacker.name, '은')} 허공에서 훔칠만한 것을 찾아보았지만 실패했다.",target=attacker, fg=color.enemy_unique)
            return None

        # Chance of successfully stealing depends on the caster's dexterity.
        k = max(25 - attacker.status.changed_status["dexterity"], 1)
        success_rate = (k + 2) / (k * 2)

        # A. Stealing Succeeded
        if random.random() <= success_rate:
            if len(target.inventory.items):
                # Select random item from inv, and select random amount
                item = target.inventory.items[random.randint(0,len(target.inventory.items)-1)]
                if item.stack_count < 1:# If item has 0 or negative value as a stack_count, steal only one of them.
                    item_count = 1
                else:
                    item_count = random.randint(1,item.stack_count)

                # If the selected item is equipped, remove it from it's owner.
                if item.equipable:
                    if item.equipable.parent == item:
                        if item.item_state.equipped_region != None:
                            item.parent.parent.equipments.remove_equipment(region=item.item_state.equipped_region, forced=True)

                # Make duplicate
                dup_item = item.copy(gamemap=item.gamemap, exact_copy=True)
                dup_item.stack_count = item_count
                target.inventory.decrease_item_stack(item=item, remove_count=item_count)

                if len(attacker.inventory.items) >= attacker.inventory.capacity:
                    dup_item.place(x=attacker.x, y=attacker.y, gamemap=attacker.gamemap)
                else:
                    attacker.inventory.try_add_item_if_full_drop(dup_item)

                # Log
                if attacker == self.engine.player:
                    if item_count > 1:
                        self.engine.message_log.add_message(
                            f"당신은 {g(target.name, '로')}부터 {g(dup_item.name, '을')} 훔쳤다! (x{dup_item.stack_count})", fg=color.player_success)
                    else:
                        self.engine.message_log.add_message(
                            f"당신은 {g(target.name, '로')}부터 {g(dup_item.name, '을')} 훔쳤다!", fg=color.player_success)
                else:
                    if item_count > 1:
                        self.engine.message_log.add_message(f"{g(attacker.name, '은')} {g(target.name, '로')}부터 {g(dup_item.name, '을')} 훔쳤다! (x{dup_item.stack_count})", target=attacker, fg=color.enemy_unique)
                    else:
                        self.engine.message_log.add_message(f"{g(attacker.name, '은')} {g(target.name, '로')}부터 {g(dup_item.name, '을')} 훔쳤다!", target=attacker, fg=color.enemy_unique)

                target.status.take_damage(amount=0, attacked_from=attacker)# make target hostile
            else:
                if attacker == self.engine.player:
                    self.engine.message_log.add_message(
                        f"당신은 {g(target.name, '로')}부터 무언가를 훔치려 시도했지만 훔칠 만한 것이 아무 것도 없었다.", fg=color.player_failed)
                else:
                    self.engine.message_log.add_message(f"{g(attacker.name, '은')} {g(target.name, '로')}부터 무언가를 훔치려 시도했지만 훔칠 만한 것이 아무 것도 없었다.", target=attacker, fg=color.enemy_unique)
                target.status.take_damage(amount=0, attacked_from=attacker)# make target hostile
        # B. Stealing Failed
        else:
            if attacker == self.engine.player:
                self.engine.message_log.add_message(f"당신은 {g(target.name, '로')}부터 무언가를 훔치려 시도했지만 실패했다.", fg=color.player_failed)
            else:
                self.engine.message_log.add_message(f"{g(attacker.name, '은')} {g(target.name, '로')}부터 무언가를 훔치려 시도했지만 실패했다.", target=attacker, fg=color.enemy_unique)
            target.status.take_damage(amount=0, attacked_from=attacker)# make target hostile


####################
###### SPELLS ######
####################

class SpellActivateable(Activatable):
    """
    Almost identical as a activatable object, 
    except that all magic related abilities will use this instead as a component.
    """
    def __init__(self, mana_cost: int, difficulty: int):
        self.mana_cost = mana_cost
        self.difficulty = difficulty

    def spend_mana(self, caster: Actor, amount: int=0) -> None:
        """Spend caster's mana."""
        caster.status.lose_mana(amount)

    def cast(self, action: actions.AbilityAction) -> None:
        """
        NOTE: cast() method will not check if the caster has sufficient mana.
        Checking a mana is done by activate() method.
        """
        raise NotImplementedError()

    def activate(self, action: actions.AbilityAction):
        """
        Check whether the caster has sufficient mana for casting the spell or not.

        TODO: Add difficulty to spells.
        Chance of successfully casting a spell should be effected by its difficulty.
        """
        if action.entity.status.changed_status["mp"] >= self.mana_cost:
            self.cast(action=action)
            self.spend_mana(caster=action.entity, amount=self.mana_cost)
        else:
            if action.entity == self.engine.player:
                self.engine.message_log.add_message(f"당신은 마나 부족으로 인해 마법 사용에 실패했다.", fg=color.player_not_good)
            else:
                self.engine.message_log.add_message(f"{g(action.entity.name, '은')} 마나 부족으로 인해 마법 사용에 실패했다.", target=action.entity, fg=color.enemy_neutral)

class SelectTargetSpellActivatable(SpellActivateable):
    def __init__(self, mana_cost: int, difficulty: int):
        super().__init__(mana_cost, difficulty)
        self.mana_cost = mana_cost
        self.difficulty = difficulty

    def get_action(self, caster: Actor, x: int = None, y: int = None, target: Actor = None):
        if caster == self.engine.player:
            self.engine.message_log.add_message("대상을 선택하세요.", color.help_msg)
            self.engine.event_handler = SingleRangedAttackHandler(
                callback=lambda xy: actions.AbilityAction(entity=caster, ability=self.parent, x=xy[0], y=xy[1],
                                                          target=self.gamemap.get_actor_at_location(x=xy[0], y=xy[1])),
            )
            return None
        else:
            return super().get_action(caster, x, y, target)


class CureWoundActivatable(SelectTargetSpellActivatable):
    """
    Steal a random item from the target actor.
    """
    def __init__(self, mana_cost: int, difficulty: int, heal_range: Tuple[int,int]):
        super().__init__(mana_cost, difficulty)
        self.mana_cost = mana_cost
        self.difficulty = difficulty
        self.heal_range = heal_range # Heal range when multiplier is 1

    def cast(self, action: actions.AbilityAction):
        caster = action.entity
        target = action.target

        # If there is no target
        if not target:
            if caster == self.engine.player:
                self.engine.message_log.add_message(f"당신은 허공을 향해 마법을 사용했다.", target=caster, fg=color.player_failed)
            else:
                self.engine.message_log.add_message(f"{g(caster.name, '은')} 허공을 향해 마법을 사용했다.",target=caster, fg=color.enemy_unique)
            return None

        # amound
        amount = random.randint(*self.heal_range)
        amount *= round(min(2, max(0, caster.status.changed_status["intelligence"] / 16)))
        amount_recovered = target.status.heal(amount)

        if amount_recovered > 0:
            if target == self.engine.player:
                self.engine.message_log.add_message(f"당신의 상처가 낫기 시작한다!", color.player_buff, )
                self.engine.message_log.add_message(f"당신은 {amount_recovered}만큼의 체력을 회복했다.",
                                                    color.player_neutral_important, )
            else:
                if self.engine.game_map.visible[target.x, target.y]:
                    self.engine.message_log.add_message(f"{target.name}의 상처가 낫기 시작한다!", color.player_sense,
                                                        target=target)
        else:
            if target == self.engine.player:
                self.engine.message_log.add_message(f"당신은 조금 더 건강해진 느낌이 든다.", color.player_buff, )
            else:
                if self.engine.game_map.visible[target.x, target.y]:
                    self.engine.message_log.add_message(f"{target.name}의 상처가 낫기 시작한다!", color.player_sense,
                                                        target=target)
            if target.status.experience:
                target.status.experience.gain_constitution_exp(10, 17)


class MesmerizeSpellActivatable(SelectTargetSpellActivatable):
    def cast(self, action: actions.AbilityAction):
        caster = action.entity
        target = action.target

        # If there is no target
        if not target:
            if caster == self.engine.player:
                self.engine.message_log.add_message(f"당신은 허공을 향해 마법을 사용했다.", target=caster, fg=color.player_failed)
            else:
                self.engine.message_log.add_message(f"{g(caster.name, '은')} 허공을 향해 마법을 사용했다.",target=caster, fg=color.enemy_unique)
            return None

        if not target.ai or target == caster: # TODO: Currently ai cannot mesmerize player
            # Log
            if caster == self.engine.player:
                self.engine.message_log.add_message(f"당신의 자신감이 차오른다.", color.player_buff)
            # else:
            #     self.engine.message_log.add_message(f"{g(caster.name, '은')} 자신감이 넘쳐 보인다.", color.player_sense, target=caster)
            # NOTE: Ignore ai log

            if caster.status.experience:
                caster.status.experience.gain_charm_exp(200)
        else:
            tame_bonus = min(2, max(caster.status.changed_status["intelligence"] - 16, -2))
            if target.ai.try_tame(caster, tame_bonus=tame_bonus):
                # Log
                if caster == self.engine.player:
                    self.engine.message_log.add_message(f"{g(target.name, '을')} 길들였다!", color.player_success, target=target)
                    if target.actor_state.can_talk:
                        self.engine.message_log.add_message(f"{g(target.name, '이')} 당신에게 충성을 표했다.", color.player_success, target=target)
                    else:
                        self.engine.message_log.add_message(f"{g(target.name, '이')} 당신에 대한 신뢰를 보였다.", color.player_success, target=target)
                else:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} 이제 {g(caster.name, '을')} 주인으로 섬긴다!", color.enemy_unique, target=target)

                if caster.status.experience:
                    caster.status.experience.gain_charm_exp(100, exp_limit=1000)
            else:
                if caster == self.engine.player:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} 당신의 정신적 지배에 저항했다!", color.player_failed, target=target)
                else:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} {caster.name}의 명령을 거부했다!", color.enemy_unique, target=target)


class TeleportSpellActivatable(SelectTargetSpellActivatable):
    def cast(self, action: actions.AbilityAction):
        caster = action.entity
        target = action.target

        if caster == self.engine.player:
            stability = 0
            if not self.engine.game_map.visible[action.x,action.y] and not self.engine.game_map.explored[action.x,action.y]: # NOTE: Can select explored but not visible tiles
                stability = 1

            actions.TeleportAction(entity=caster, x=action.x, y=action.y, gamemap=self.engine.game_map,
                           stability=stability).perform()
        else:
            stability = 1
            # NOTE: Ai will always teleport to randomized location.
            actions.TeleportAction(entity=caster, x=action.x, y=action.y, gamemap=caster.gamemap,
                           stability=stability).perform()


class LightningStrikeActivatable(SpellActivateable):
    def __init__(self, mana_cost: int, difficulty: int, damage: int, maximum_range: int):
        super().__init__(mana_cost, difficulty)
        self.damage = damage
        self.maximum_range = maximum_range

    def cast(self, action: actions.AbilityAction) -> None:
        caster = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not caster and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = caster.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            if target == self.engine.player:
                self.engine.message_log.add_message(f"번개가 당신을 내리쳤다!", fg=color.player_bad)
            else:
                self.engine.message_log.add_message(f"번개가 {g(target.name, '을')} 내리쳤다!", target=caster, fg=color.enemy_unique)

            target.status.take_damage(amount=0, attacked_from=caster) # trigger target
            target.actor_state.apply_electrocution([self.damage, 0.5])
            target.actor_state.actor_electrocuted(source_actor=caster)


class RaySpellActivatable(SpellActivateable):
    """
    Handles all sort of ray typed spells. (including projectile types)

    NOTE: Based off of RayReadable.
    """
    def __init__(self, mana_cost: int, difficulty: int, anim_graphic, damage_range: Tuple[int, int] = (0, 0), penetration: bool = False, max_range: int = 1000, stack_anim_frame: bool = True):
        super().__init__(mana_cost, difficulty)
        self._anim_graphic = anim_graphic
        self.damage_range = damage_range
        self.penetration = penetration
        self.max_range = max_range
        self.stack_anim_frame = stack_anim_frame

    @property
    def anim_graphic(self):
        if callable(self._anim_graphic): # Dynamic graphic
            return self._anim_graphic()
        else:
            return self._anim_graphic

    @property
    def damage(self):
        return random.randint(*self.damage_range)

    def get_action(self, caster: Actor, x: int=None, y: int=None, target: Actor=None):
        if caster == self.engine.player:
            self.engine.message_log.add_message("방향을 선택하세요.", color.help_msg)
            self.engine.event_handler = RayRangedInputHandler(
                actor=caster,
                max_range=999,
                callback=lambda dxdy: actions.AbilityAction(entity=caster, ability=self.parent, x=caster.x + dxdy[0], y=caster.y + dxdy[1], target=self.gamemap.get_actor_at_location(x=caster.x + dxdy[0], y=caster.y + dxdy[1])),
            )
            return None
        else:
            return super().get_action(caster, x, y, target)

    def effects_on_path(self, x: int, y: int):
        """effects applied to the tiles on the path."""
        pass

    def effects_on_collided_entity(self, caster: Actor, entity: Entity):
        """
        effects applied to the entity that the ray collided with.
        If the entity was an actor, effects_on_collided_actor() is called.
        """
        if isinstance(entity, Actor):
            self.effects_on_collided_actor(caster=caster, target=entity)
        else:
            pass

    def effects_on_collided_actor(self, caster: Actor, target: Actor):
        """effects applied to the actor that the ray collided with."""
        pass

    def cast(self, action: actions.AbilityAction) -> None:
        caster = action.entity
        target = None # Added during calc

        dx = action.x - caster.x
        dy = action.y - caster.y
        dest_x, dest_y = caster.x + dx, caster.y + dy
        path = []
        targets = []

        while True:
            # ray is out of the map border
            if not self.engine.game_map.in_bounds(dest_x, dest_y):
                break
            # ray is blocked by a tile
            if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
                break

            # check collision with entities
            collided = self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
            if collided:
                # collided with the reader
                if collided == caster:
                    self.effects_on_collided_actor(caster=caster, target=caster)
                    return None

                # if not add all entities collided to a list
                targets.append(collided)

                # if penetration=False, stop calculating collision after the first contact
                if self.penetration == False:
                    break

            # Save previous paths and set next destination
            path.append((dest_x, dest_y))
            dest_x += dx
            dest_y += dy

        # Animation
        frames = []
        while len(path) > 0:
            loc = path.pop(0)

            # Using relative coordinates for rendering animations
            relative_x, relative_y = self.engine.camera.abs_to_rel(abs_x=loc[0], abs_y=loc[1])
            frames.append([(relative_x, relative_y, self.anim_graphic, None)])

            # effects on the paths
            self.effects_on_path(x=loc[0], y=loc[1])

        # instantiate animation and render it
        ray_animation = Animation(engine=self.engine, frames=frames,stack_frames=self.stack_anim_frame)  # sec_per_frames = default
        ray_animation.render()

        # effects on the entities
        for target in targets:
            if len(targets) >= 1:
                self.effects_on_collided_entity(caster, target)


class SpectralBeamActivatable(RaySpellActivatable):
    """
    Fire a magical ray that drains enemy's mp and absorb it as hp.
    """
    def effects_on_collided_actor(self, caster: Actor, target: Actor):
        """effects applied to the actor that the ray collided with."""
        real_damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="magic")
        real_damage = round(real_damage)
        # Log
        if target == self.engine.player:
            self.engine.message_log.add_message(f"형형색색의 광선이 당신을 강타해 {real_damage} 데미지를 입혔다.", fg=color.player_bad)
        else:
            self.engine.message_log.add_message(f"형형색색의 광선이 {g(target.name, '을')} 강타해 {real_damage} 데미지를 입혔다.",
                                                target=target, fg=color.enemy_unique)
        target.status.take_damage(amount=real_damage, attacked_from=caster)


class SoulBoltActivatable(RaySpellActivatable):
    """
    Fires a magical bolt that deals damage if the target has soul.
    """
    def effects_on_collided_actor(self, caster: Actor, target: Actor):
        """effects applied to the actor that the ray collided with."""
        real_damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="magic")
        real_damage = round(real_damage)

        if target.actor_state.has_soul:
            # Log
            if target == self.engine.player:
                self.engine.message_log.add_message(f"청록색 마탄이 당신의 영혼에 충돌해 {real_damage} 데미지를 입혔다.", fg=color.player_bad)
            else:
                self.engine.message_log.add_message(f"청록색 마탄이 {target.name}의 영혼에 충돌해 {real_damage} 데미지를 입혔다.",
                                                    target=target, fg=color.enemy_unique)
            target.status.take_damage(amount=real_damage, attacked_from=caster)
        else:
            # Log
            if target == self.engine.player:
                self.engine.message_log.add_message(f"청록색 마탄은 당신에게 아무런 피해도 주지 못한 채 당신을 통과해 지나갔다. ", fg=color.player_neutral_important)
            else:
                self.engine.message_log.add_message(f"청록색 마탄은 아무런 피해도 주지 못한 채 {g(target.name, '을')} 통과해 지나갔다. ",fg=color.enemy_unique)
            # No trigger


class EffectToAllEntityInGamemapSpellActivatable(SelectTargetSpellActivatable):
    """
    Will effect every actors on caster's gamemap.
    """
    def get_action(self, caster: Actor, x: int=None, y: int=None, target: Actor=None):
        if caster == self.engine.player:
            self.engine.message_log.add_message("타겟을 선택하세요.", color.help_msg)
            self.engine.event_handler = SingleRangedAttackHandler(
                callback=lambda xy: actions.AbilityAction(entity=caster, ability=self.parent, x=xy[0], y=xy[1], target=self.gamemap.get_actor_at_location(x=xy[0], y=xy[1])),
            )
            return None
        else:
            return super().get_action(caster, x, y, target)

    def check_if_target(self, entity: Entity, action: actions.AbilityAction) -> bool:
        # Override to specify conditions.
        return False

    def effect_to_target(self, entity: Entity, action: actions.AbilityAction) -> None:
        raise NotImplementedError()

    def cast(self, action: actions.AbilityAction) -> None:
        """
        NOTE: cast() method will not check if the caster has sufficient mana.
        Checking a mana is done by activate() method.
        """
        for e in action.entity.gamemap.entities:
            if self.check_if_target(e, action):
                self.effect_to_target(e, action)


class CallOfTheOrcLordActivatable(EffectToAllEntityInGamemapSpellActivatable):
    """Will make all orcs (except for orc lords) in the gamemap hostile to given target actor."""
    def check_if_target(self, entity: Entity, action: actions.AbilityAction) -> bool:
        # Override to specify conditions.
        if isinstance(entity, Actor):
            if entity.char == 'O':
                if entity.entity_id != "orc_lord":
                    return True
        return False

    def effect_to_target(self, entity: Entity, action: actions.AbilityAction) -> None:
        if action.target == None:
            print("ERROR::Has no action.target - CallOfOrcLordActivatable")
            return None

        if isinstance(entity, Actor):
            if entity.ai:
                entity.ai.target = action.target
                entity.ai.path = entity.ai.get_path_to(action.target.x, action.target.y)
                if action.target == self.engine.player:
                    self.engine.message_log.add_message(f"{g(entity.name, '이')} 당신을 향해 적대감을 드러낸다!", fg=color.player_bad, target=entity, stack=False)
                else:
                    self.engine.message_log.add_message(f"{g(entity.name, '이')} {g(action.target.name, '을')} 향해 적대감을 드러낸다!", fg=color.enemy_unique, target=entity, stack=False)

    def cast(self, action: actions.AbilityAction) -> None:
        if self.engine.game_map.visible[action.entity.x, action.entity.y]:
            if action.entity == self.engine.player:
                self.engine.message_log.add_message(f"당신은 던전 전체에 울리는 쩌렁쩌렁한 포효를 내질렀다!",fg=color.player_buff, target=action.entity, stack=False)
            else:
                self.engine.message_log.add_message(f"{g(action.entity.name, '이')} 던전 전체에 울리는 쩌렁쩌렁한 포효를 내지른다!", fg=color.enemy_unique,target=action.entity, stack=False)
        else:
            self.engine.message_log.add_message(f"던전 전체에 오크의 포효소리가 울린다!", fg=color.world)
        return super().cast(action)
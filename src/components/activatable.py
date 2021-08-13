from __future__ import annotations
from os import dup
from typing import Optional, TYPE_CHECKING
from components.base_component import BaseComponent
from input_handlers import RayDirInputHandler
from korean import grammar as g

import random
import actions
import color

if TYPE_CHECKING:
    from entity import Actor
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
            self.engine.message_log.add_message("타겟의 위치를 선택하세요.", color.help_msg)
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
                        item.parent.parent.equipments.remove_equipment(region=item.item_state.equipped_region, forced=True)

                # Make duplicate
                dup_item = item.copy(gamemap=item.gamemap)
                dup_item.stack_count = item_count
                target.inventory.decrease_item_stack(item=item, remove_count=item_count)

                if len(attacker.inventory.items) >= attacker.inventory.capacity:
                    dup_item.place(x=attacker.x, y=attacker.y, gamemap=attacker.gamemap)
                else:
                    attacker.inventory.add_item(dup_item)

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
        raise NotImplementedError

    def activate(self, action: actions.AbilityAction):
        """
        Check whether the caster has sufficient mana for casting the spell or not.

        TODO: Add difficulty to spells. 
        Chance of successfully casting a spell should be effected by its difficulty.
        """
        if action.entity.status.changed_status["mp"] >= self.mana_cost:
            self.cast(action=action)
        else:
            if action.entity == self.engine.player:
                self.engine.message_log.add_message(f"당신은 마나 부족으로 인해 마법 사용에 실패했다.", fg=color.player_not_good)
            else:
                self.engine.message_log.add_message(f"{g(action.entity.name, '은')} 마나 부족으로 인해 마법 사용에 실패했다.", target=action.entity, fg=color.enemy_neutral)
        

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

        self.spend_mana(caster=caster, amount=30)
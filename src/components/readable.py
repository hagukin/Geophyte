from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING, Tuple, List

import tiles
from animation import Animation
from components.base_component import BaseComponent
from exceptions import Impossible
from order import InventoryOrder, TilemapOrder
from korean import grammar as g
from tiles import TileUtil
from entity import Actor
from util import spawn_monster_of_appr_diff_8way
from language import interpret as i

import actions
import color

if TYPE_CHECKING:
    from entity import Item, Actor

class Readable(BaseComponent):
    def __init__(self):
        super().__init__(None)
        
    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.ReadItem(consumer, self.parent)

    def activate(self, action: actions.ReadItem) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self, consumer: Actor) -> None:
        """Remove the consumed item from its containing inventory."""
        # fully identify used instance, and semi-identify the same item types.
        if consumer == self.engine.player:
            self.parent.item_state.identify_self(identify_level=2)
        self.parent.parent.decrease_item_stack(self.parent, remove_count=1)

    def item_use_cancelled(self, actor: Actor) -> actions.Action:
        """
        Called when item usage is cancelled.
        Only the player should be able to call this function.
        """
        self.consume(actor)
        if actor == self.engine.player:
            self.engine.message_log.add_message(i(f"당신의 {g(self.parent.name, '이')} 먼지가 되어 사라졌다.",
                                                  f"Your {self.parent.name} crumbles to dust."), color.player_bad)
        return actions.WaitAction(actor)


class SelectTileReadable(Readable):
    def __init__(self,
                 can_select_not_visible_tile: bool=True,
                 can_select_not_explored_tile: bool=True,
                 ):
        super().__init__()
        self.can_select_not_visible_tile = can_select_not_visible_tile
        self.can_select_not_explored_tile = can_select_not_explored_tile

    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(i("목표 지점을 선택하세요.",
                                              f"Choose a tile."), color.help_msg)

        from input_handlers import SingleRangedAttackHandler
        self.engine.event_handler = SingleRangedAttackHandler(
            callback=lambda xy: actions.ReadItem(consumer, self.parent, xy),
            item_cancel_callback=lambda x: self.get_action(consumer, x),
        )
        return None

    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        pass

    def effects_on_selected_tile_with_actor(self, consumer: Actor, target: Actor):
        pass

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.can_select_not_visible_tile and not self.engine.game_map.visible[action.target_xy]:
            self.engine.sound_manager.add_sound_queue("fx_invalid")
            raise Impossible(i("보이지 않는 지역을 선택할 수는 없습니다.",
                               f"You can't choose a non-visible area."))
        if not self.can_select_not_explored_tile and not self.engine.game_map.explored[action.target_xy]:
            self.engine.sound_manager.add_sound_queue("fx_invalid")
            raise Impossible(i("모험하지 않은 지역을 선택할 수는 없습니다.",
                               f"You can't choose a non-explored area."))

        if not target:
            self.effects_on_selected_tile_with_no_actor(consumer=consumer)
        else:
            self.effects_on_selected_tile_with_actor(consumer=consumer, target=target)

        self.consume(consumer)


class ScrollOfTeleportationReadable(SelectTileReadable):
    def __init__(self):
        super().__init__()
        self.can_select_not_visible_tile = True
        self.can_select_not_explored_tile = False

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = action.target_actor

        from actions import TeleportAction

        if consumer == self.engine.player:
            if not self.can_select_not_visible_tile and not self.engine.game_map.visible[action.target_xy]:
                self.engine.sound_manager.add_sound_queue("fx_invalid")
                raise Impossible(i("보이지 않는 지역을 선택할 수는 없습니다.",
                                   f"You can't choose a non-visible area."))
            if not self.can_select_not_explored_tile and not self.engine.game_map.explored[action.target_xy]:
                self.engine.sound_manager.add_sound_queue("fx_invalid")
                raise Impossible(i("모험하지 않은 지역을 선택할 수는 없습니다.",
                                   f"You can't choose a non-explored area."))

            if self.parent.item_state.BUC == 1:
                stability = 0
            elif self.parent.item_state.BUC == 0:
                stability = 1
            else:
                stability = 2

            TeleportAction(entity=consumer, x=action.target_xy[0], y=action.target_xy[1], gamemap=self.engine.game_map,stability=stability).perform()
            return self.consume(consumer)
        else:
            if self.parent.item_state.BUC == 1:
                stability = 1
            else:
                stability = 2

            # NOTE: Ai will always teleport to randomized location.
            TeleportAction(entity=consumer, x=action.target_xy[0], y=action.target_xy[1], gamemap=consumer.gamemap,stability=stability).perform()
            return self.consume(consumer)


class ScrollOfConfusionReadable(SelectTileReadable):
    def __init__(self, number_of_turns: int):
        super().__init__()
        self.can_select_not_visible_tile = False
        self.number_of_turns = number_of_turns
    
    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        if consumer == self.engine.player:
            self.engine.message_log.add_message(i(f"당신은 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.",
                                                  f"You read the scroll to nothing, and nothing happened."), color.player_neutral)
        else:
            self.engine.message_log.add_message(i(f"{g(consumer.name, '은')} 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.",
                                                  f"{consumer.name} reads the scroll to nothing, and nothing happened."),color.player_neutral, target=consumer)

    def effects_on_selected_tile_with_actor(self, consumer: Actor, target: Actor):
        if self.parent.item_state.BUC == -1:
            # Log
            new_target = consumer
            if new_target == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 굉장히 어지럽다.",
                                                      f"You feel dizzy."), color.player_not_good, )
            else:
                self.engine.message_log.add_message(i(f"{g(new_target.name, '이')} 휘청거리기 시작한다.",
                                                      f"{new_target.name} starts to stumble."), color.player_sense, target=target)

            new_target.actor_state.apply_confusion([0, self.number_of_turns])
        else:
            # Log
            if target == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 굉장히 어지럽다.",
                                                      f"You feel dizzy."), color.player_not_good,)
            else:
                self.engine.message_log.add_message(i(f"{g(target.name, '이')} 휘청거리기 시작한다.",
                                                      f"{target.name} starts to stumble."), color.player_sense, target=target)

            target.actor_state.apply_confusion([0,self.number_of_turns])


class ScrollOfTameReadable(SelectTileReadable):
    def __init__(self):
        super().__init__()
        self.can_select_not_visible_tile = False
    
    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        if consumer == self.engine.player:
            self.engine.message_log.add_message(i(f"당신은 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.",
                                                  f"You read the scroll to nothing, and nothing happened."),color.player_neutral)
        else:
            self.engine.message_log.add_message(i(f"{g(consumer.name, '은')} 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.",
                                                  f"{consumer.name} reads the scroll to nothing, and nothing happened."),color.player_neutral, target=consumer)

    def effects_on_selected_tile_with_actor(self, consumer: Actor, target: Actor):
        if not target.ai or target == consumer:
            # Log
            if consumer == self.engine.player:
                self.engine.message_log.add_message(i(f"당신의 자신감이 차오른다.",
                                                      f"You feel confident."), color.player_buff)
            else:
                self.engine.message_log.add_message(i(f"{g(consumer.name, '은')} 자신감이 넘쳐 보인다.",
                                                      f"{consumer.name} looks more confident."), color.player_sense, target=consumer)

            if consumer.status.experience:
                consumer.status.experience.gain_charm_exp(200)
        else:
            if self.parent.item_state.BUC == 1:
                tame_bonus = 4
            elif self.parent.item_state.BUC == -1:
                tame_bonus = -1
                target.status.take_damage(amount=0, attacked_from=consumer) # trigger
            else:
                tame_bonus = 0

            if target.ai.try_tame(consumer, tame_bonus=tame_bonus):
                # Log
                if consumer == self.engine.player:
                    self.engine.message_log.add_message(i(f"{g(target.name, '을')} 길들였다!",
                                                          f"You successfully tamed {target.name}!"), color.player_success, target=target)
                    if target.actor_state.can_talk:
                        self.engine.message_log.add_message(i(f"{g(target.name, '이')} 당신에게 충성을 표했다.",
                                                              f"{target.name} shows its loyalty towards you."), color.player_success, target=target)
                    else:
                        self.engine.message_log.add_message(i(f"{g(target.name, '이')} 당신에 대한 신뢰를 보였다.",
                                                              f"{target.name} trusts you as an ally."), color.player_success, target=target)
                else:
                    self.engine.message_log.add_message(i(f"{g(target.name, '은')} 이제 {g(consumer.name, '을')} 주인으로 섬긴다!",
                                                          f"{target.name} is now a servant of {consumer.name}!"), color.enemy_unique, target=target)

                if consumer.status.experience:
                    consumer.status.experience.gain_charm_exp(100, exp_limit=1000)
            else:
                if consumer == self.engine.player:
                    self.engine.message_log.add_message(i(f"{g(target.name, '은')} 당신의 정신적 지배에 저항했다!",
                                                          f"{target.name} resists your command!"), color.player_failed, target=target)
                else:
                    self.engine.message_log.add_message(i(f"{g(target.name, '은')} {consumer.name}의 명령을 거부했다!",
                                                          f"{target.name} resists {consumer.name}'s command!"), color.enemy_unique, target=target)


class SelectItemFromInventoryReadable(Readable):
    def get_action(self, consumer: Actor, cancelled: bool=False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(i("아이템을 선택하세요.",
                                              f"Choose an item."), color.help_msg)

        from input_handlers import InventoryChooseItemAndCallbackHandler
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            inventory_component=consumer.inventory,
            show_only_types=None, # If item_type filter is needed, you should override this entire function.
            show_only_status=None,
            callback=lambda selected_item : actions.ReadItem(consumer, self.parent, (0,0), selected_item),
            item_cancel_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        raise NotImplementedError()

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        self.effects_on_selected_item(consumer, action.item_selected)
        self.consume(consumer)


class ScrollOfEnchantmentReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(i("마법 강화할 아이템을 선택하세요.",
                                              f"Choose an item to enchant."), color.help_msg)

        from input_handlers import InventoryChooseItemAndCallbackHandler
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            inventory_component=consumer.inventory,
            show_only_types=(
                InventoryOrder.MELEE_WEAPON,
                InventoryOrder.ARMOR,
                InventoryOrder.AMULET,
                InventoryOrder.RING,
                InventoryOrder.WAND,
                ),# Only display enchantable items.
            callback=lambda selected_item : actions.ReadItem(consumer, self.parent, (0,0), selected_item),
            item_cancel_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        # Log
        if consumer == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_enchant")
            if self.parent.item_state.BUC == 1:
                if selected_item.equipable:
                    selected_item.equipable.upgrade_this(random.randint(1,2))
                self.engine.message_log.add_message(i(f"당신의 {g(selected_item.name, '이')} 황금색 빛을 내뿜었다!",
                                                      f"Your {selected_item.name} emits a golden flashes of light!"),color.player_success, target=consumer)
            else:
                if selected_item.equipable:
                    selected_item.equipable.upgrade_this(1)
                self.engine.message_log.add_message(i(f"당신의 {g(selected_item.name, '이')} 밝은 빛을 내뿜었다!",
                                                      f"Your {selected_item.name} emits a flashes of light!"), color.player_success, target=consumer)
            if selected_item.item_state.equipped_region:
                self.engine.message_log.add_message(i(f"당신의 {selected_item.name}에서 이전보다 더 강한 힘이 느껴진다.",
                                                      f"Your {selected_item.name} feels stronger."), color.player_success, target=consumer)
        else:
            if selected_item.equipable:
                selected_item.equipable.upgrade_this(1)
            self.engine.message_log.add_message(i(f"{consumer.name}의 {g(selected_item.name, '이')} 빛을 내뿜었다.",
                                                  f"{consumer.name}'s {selected_item.name} emits a flashes of light."), color.player_sense, target=consumer)


class ScrollOfIdentifyReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(i("감정할 아이템을 선택하세요.",
                                              f"Choose an item to identify."), color.help_msg)

        from input_handlers import InventoryChooseItemAndCallbackHandler
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            inventory_component=consumer.inventory,
            show_only_status=("unidentified-all", "semi-identified-all"), # NOTE: WARNING - If you pass only one parameter, additional comma is needed inside tuple to prevent passing the data in string form
            callback=lambda selected_item : actions.ReadItem(consumer, self.parent, (0,0), selected_item),
            item_cancel_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        if consumer == self.engine.player:
            items = [selected_item]
            if self.parent.item_state.BUC == 1:
                for inv_item in consumer.inventory.items:
                    items.append(inv_item)
            if items:
                self.engine.sound_manager.add_sound_queue("fx_identify")
            for item in items:
                item.item_state.identify_self(2)
                self.engine.message_log.add_message(i(f"당신은 {g(item.name, '을')} 감정했다.",
                                                      f"You identify {item.name}."), color.player_success)

        if consumer.status.experience:
            consumer.status.experience.gain_intelligence_exp(20, exp_limit=2000)

        # Log TODO
        #TODO: identify multiple when blessed?
        #NOTE: Currently self-identification is possible


class ScrollOfRemoveCurseReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(i("저주를 해제할 아이템을 선택하세요.",
                                              f"Choose an item to remove curse."), color.help_msg)

        from input_handlers import InventoryChooseItemAndCallbackHandler
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            inventory_component=consumer.inventory,
            show_only_status=("unidentified-all", "semi-identified-all", "full-identified-cursed",),
            callback=lambda selected_item : actions.ReadItem(consumer, self.parent, (0,0), selected_item),
            item_cancel_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        buc = selected_item.item_state.BUC

        if self.parent.item_state.BUC == 1 or self.parent.item_state.BUC == 0:
            success = selected_item.item_state.change_buc(BUC=0)

            # Log
            if consumer == self.engine.player:
                if buc == -1 and success: #If item was cursed before
                    self.engine.sound_manager.add_sound_queue("fx_remove_curse")
                    self.engine.message_log.add_message(i(f"당신의 {g(selected_item.name, '로')}부터 사악한 기운이 사라졌다!",
                                                          f"Your {selected_item.name} is no longer cursed!"), color.player_success, target=consumer)
                elif buc == -1 and not success:
                    self.engine.message_log.add_message(i(f"당신의 {g(selected_item.name, '로')}부터 뿜어져 나오는 사악한 기운이 너무 강력해, 저주를 해제할 수 없다!",
                                                          f"The curse upon your {selected_item.name} was too strong to get rid of!"),color.player_failed, target=consumer)
                else:
                    self.engine.message_log.add_message(i(f"백색 빛이 당신의 {g(selected_item.name, '을')} 감쌌다.",
                                                          f"A white light surrounds your {selected_item.name}."), color.player_sense, target=consumer)
            #NOTE: Currently self-uncursing is possible
        else:
            success = selected_item.item_state.change_buc(BUC=-1)
            # Log
            if consumer == self.engine.player:
                if buc != -1 and success:  # If item was not cursed before
                    self.engine.sound_manager.add_sound_queue("fx_evil")
                    self.engine.message_log.add_message(i(f"당신의 {g(selected_item.name, '로')}부터 사악한 기운이 느껴진다!",
                                                          f"You sense something evil from your {selected_item.name}!"),color.player_bad, target=consumer)
                elif buc != -1 and not success:
                    self.engine.message_log.add_message(
                        i(f"당신의 {g(selected_item.name, '은')} 사악한 기운에 저항했다!",
                          f"Your {selected_item.name} resists a evil curse!"),color.player_failed, target=consumer)
                else:
                    self.engine.message_log.add_message(i(f"검은 빛이 당신의 {g(selected_item.name, '을')} 감쌌다.",
                                                          f"A black light surrounds your {selected_item.name}."),color.player_sense, target=consumer)

        if consumer.status.experience:
            consumer.status.experience.gain_intelligence_exp(10)


class ScrollOfMagicMappingReadable(Readable):
    """
    Unlike most items that receives input and call callback function,
    or items that receives no inputs,
    this readable will first apply the effect and after wait for an input. 
    When input is reveived, this will return 0 to callback and finish the whole process. (0 is just a trash value it doesn't matter what you pass)
    """
    def activate(self, action: actions.ReadItem) -> None:
        self.engine.update_fov()
        self.consume(consumer=action.entity)

    def get_action(self, consumer):
        if consumer == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_magic_mapping")
            if self.parent.item_state.BUC == 1:
                self.engine.message_log.add_message(i(f"당신의 머리 속에 이 층의 모든 비밀들이 전해졌다.",
                                                      f"You begin to notice every secrets of this level."), color.player_sense,)
            elif self.parent.item_state.BUC == -1:
                self.engine.message_log.add_message(i(f"주문서에서 사악한 기운이 뿜어져 나와 당신의 머릿속을 기괴한 문양들로 가득 채운다!",
                                                      f"An evil energy fills your mind with odd shapes and glyphs!"), color.player_sense, )
            else:
                self.engine.message_log.add_message(i(f"당신의 머리 속이 기하학적 정보들로 가득 차기 시작했다.",
                                                      f"Your mind is full of geometrical shapes."), color.player_sense,)

            for y in range(len(self.engine.game_map.visible[0])):
                for x in range(len(self.engine.game_map.visible)):
                    self.engine.game_map.visible[x, y] = True
            for y in range(len(self.engine.game_map.explored[0])):
                for x in range(len(self.engine.game_map.explored)):
                    self.engine.game_map.explored[x, y] = True

            self.engine.camera.clear_visuals()
            self.engine.refresh_screen()
            from input_handlers import MagicMappingLookHandler
            self.engine.event_handler = MagicMappingLookHandler(
                callback=lambda trash_value: actions.ReadItem(consumer, self.parent),
            )#NOTE: Has no item_cancel_callback parameter, since the item already has been consumed.
        else:
            print("WARNING::AI read magic mapping")

        if self.parent.item_state.BUC == -1:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(i(f"무언가를 머릿속에서 잊어버린 듯한 기분이 든다.",
                                                      f"You feel like you forgot something."), color.player_bad, )
                for y in range(len(self.engine.game_map.explored[0])):
                    for x in range(len(self.engine.game_map.explored)):
                        self.engine.game_map.explored[x, y] = False
            else:
                print("WARNING::AI read cursed magic mapping. ignoring amnesia effect.")
        return None


class ScrollOfMeteorStormReadable(Readable): #TODO: Make parent class like other readables
    def __init__(self, damage_range: Tuple[int, int], radius: int):
        super().__init__()
        self.damage_range = damage_range
        self.radius = radius

    @property
    def damage(self):
        return random.randint(*self.damage_range)

    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(
            i(f"{g(self.parent.name, '을')} 사용할 영역을 선택하세요.",
              f"Choose an area to use {self.parent.name}."), color.help_msg
        )

        from input_handlers import AreaRangedAttackHandler
        self.engine.event_handler = AreaRangedAttackHandler(
            radius=self.radius,
            callback=lambda xy: actions.ReadItem(consumer, self.parent, xy),
            item_cancel_callback=lambda x: self.get_action(consumer, x),
        )
        return None

    def activate(self, action: actions.ReadItem) -> None:
        target_xy = action.target_xy
        consumer = action.entity

        if not self.engine.game_map.visible[target_xy]:
            self.engine.sound_manager.add_sound_queue("fx_invalid")
            raise Impossible(i("보이지 않는 지역을 선택할 수는 없습니다.",
                               f"You can't choose a non-visible area."))

        self.engine.message_log.add_message(i(f"허공에서 운석이 나타났다!",
                                              f"A meteor appears from nowhere!"), target=consumer, fg=color.world)

        # Set fire on the given radius
        import semiactor_factories
        for dx in range(-self.radius, self.radius+1):
            for dy in range(-self.radius, self.radius+1):
                semiactor_factories.fire.spawn(self.engine.game_map, target_xy[0] + dx, target_xy[1] + dy, 6)

        targets_hit = False
        for target in self.engine.game_map.actors:
            if target.chebyshevDist(*target_xy) <= self.radius:
                # damage
                real_damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="physical")
                if self.parent.item_state.BUC == 1:
                    real_damage *= 1.2
                elif self.parent.item_state.BUC == -1:
                    real_damage *= 0.8
                real_damage = round(real_damage)
                target.status.take_damage(amount=real_damage, attacked_from=consumer)

                # Log
                if self.engine.game_map.visible[target_xy[0], target_xy[1]]:
                    if target == self.engine.player:
                        self.engine.message_log.add_message(i(f"당신은 운석에 맞아 {real_damage} 데미지를 받았다!",
                                                              f"You took {real_damage} damage from a meteor strike."),target=target, fg=color.player_bad)
                    else:
                        self.engine.message_log.add_message(i(f"{g(target.name, '이')} 운석에 맞아 {real_damage} 데미지를 받았다!",
                                                              f"{target.name} took {real_damage} damage from a meteor strike."), target=target, fg=color.enemy_unique)
                targets_hit = True

        if not targets_hit and self.engine.game_map.visible[target_xy[0], target_xy[1]]:# nothing was hit
            self.engine.message_log.add_message(i(f"운석이 바닥과 충돌했다.",
                                                  f"Meteor collides with the ground."), fg=color.player_sense)
        self.engine.sound_manager.add_sound_queue("fx_low_impact")
        self.consume(consumer)

        
class AutoTargetingHarmfulReadable(Readable):
    def __init__(self, maximum_range: int, fx_id: Optional[str]=None):
        super().__init__()
        self.maximum_range = maximum_range
        self.fx_id = fx_id

    def play_fx(self):
        """Play when activated."""
        if self.fx_id:
            self.engine.sound_manager.add_sound_queue(self.fx_id)

    def effects_on_target_actor(self, consumer:Actor, target: Actor):
        pass

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0


        if self.parent.item_state.BUC == 1:
            targets = []
            for actor in self.engine.game_map.actors:
                if actor is not consumer:
                    if self.engine.check_entity_in_sight_of_actor(actor, consumer):
                        targets.append(actor)

            if not targets: # List empty
                targets.append(consumer)

            for target in set(targets):
                self.effects_on_target_actor(consumer=consumer, target=target)
        elif self.parent.item_state.BUC == -1:
            self.effects_on_target_actor(consumer=consumer, target=consumer)
        else:
            for actor in self.engine.game_map.actors:
                if actor is not consumer:
                    if self.engine.check_entity_in_sight_of_actor(actor, consumer):
                        distance = consumer.distance(actor.x, actor.y)
                        if distance <= closest_distance:
                            target = actor
                            closest_distance = distance
            if target:
                # apply effect
                self.effects_on_target_actor(consumer=consumer, target=target)
            else:
                # if there is no valid target, it will target the reader instead.
                self.effects_on_target_actor(consumer=consumer, target=consumer)

        self.play_fx()
        self.consume(consumer)


class RayReadable(Readable):
    def __init__(self, anim_graphic, damage_range: Tuple[int,int]=(0,0), penetration: bool=False, wall_penetration_cnt: int=0, max_range: int=1000, stack_anim_frame: bool = True, fx_id: str="fx_ray"):
        """
        Args:
            anim_graphic:
                Can be either callable or dictionary obj.
            wall_penetration_cnt:
                maximum number of walls that the ray can go through.
                Does not have to be a continuous array of walls.
        """
        super().__init__()
        self._anim_graphic = anim_graphic
        self.damage_range = damage_range
        self.penetration = penetration
        self.wall_penetration_cnt = wall_penetration_cnt
        self.max_range = max_range
        self.stack_anim_frame = stack_anim_frame
        self.fx_id = fx_id

    @property
    def anim_graphic(self):
        if callable(self._anim_graphic): # Dynamic graphic
            return self._anim_graphic()
        else:
            return self._anim_graphic

    @property
    def damage(self):
        return random.randint(*self.damage_range)

    def effects_on_path(self, action: actions.ReadItem, x: int, y: int):
        """effects applied to the tiles on the path."""
        pass

    def effects_on_collided_wall(self, action: actions.ReadItem, x: int, y: int):
        """effects applied to the tiles on the path."""
        pass

    def effects_on_consumer_tile(self, action: actions.ReadItem, x: int, y: int):
        """
        effects applied to the tile of the consumer.
        This function is called only if the ray's dx, dy is (0,0) meaning that the consumer shot the ray to itself. (towards descending direction)
        As default, this function does exactly the same as effects_on_path()
        """
        return self.effects_on_path(action, x, y)

    def effects_on_collided_entity(self, consumer: Actor, entity):
        """
        effects applied to the entity that the ray collided with.
        If the entity was an actor, effects_on_collided_actor() is called.
        """
        if isinstance(entity, Actor):
            self.effects_on_collided_actor(consumer=consumer, target=entity)
        else:
            pass

    def effects_on_collided_actor(self, consumer: Actor, target: Actor):
        """effects applied to the actor that the ray collided with."""
        pass

    def play_ray_fx(self, consumer:Actor):
        """Play sound fx when the ray is being casted AND consumer is player"""
        if consumer == self.engine.player and self.fx_id:
            self.engine.sound_manager.add_sound_queue(self.fx_id)

    def get_action(self, consumer, cancelled: bool=False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(i(f"{g(self.parent.name, '을')} 사용할 방향을 선택하세요. 바닥 방향으로 사용하려면 자신이 위치하고 있는 타일을 선택하세요.",
                                              f"Choose a direction to use {self.parent.name}. To aim downwards, select the tile that you are at."), color.help_msg)
        self.engine.message_log.add_message(i(f"방향키/마우스 이동:위치 선택 | 엔터/마우스 클릭:결정",
                                              f"Enter/LClick:Confirm"), color.help_msg)

        from input_handlers import RayRangedInputHandler
        self.engine.event_handler = RayRangedInputHandler(
            actor=consumer,
            max_range=self.max_range,
            callback=lambda xy: actions.ReadItem(consumer, self.parent, xy),
            item_cancel_callback=lambda x : self.get_action(consumer, x),
        )
        return None

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = None
        
        dx = action.target_xy[0]
        dy = action.target_xy[1]
        dest_x, dest_y = consumer.x + dx, consumer.y + dy
        path = []
        targets = []
        wall_penetration_cnt = self.wall_penetration_cnt # NOTE: You must NOT directly modify the self.wall_penetration_cnt since all readable shares one memory
        if self.parent.item_state.BUC == 1:
            wall_penetration_cnt = round(wall_penetration_cnt * 2)
        elif self.parent.item_state.BUC == -1:
            wall_penetration_cnt = round(wall_penetration_cnt / 2)

        self.play_ray_fx(consumer)

        while True:
            # ray is out of the map border
            if not self.engine.game_map.in_bounds(dest_x, dest_y):
                break
            # ray is blocked by a tile
            if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
                self.effects_on_collided_wall(action=action, x=dest_x, y=dest_y) # Function is called regardless of whether the beam can penetrate through walls or not
                if wall_penetration_cnt > 0:
                    wall_penetration_cnt -= 1
                    continue
                else:
                    break

            # check collision with entities
            collided = self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
            if collided:
                # collided with the reader
                if collided == consumer:
                    if dx == 0 and dy == 0:
                        self.effects_on_consumer_tile(action=action, x=consumer.x, y=consumer.y)
                    self.effects_on_collided_actor(consumer=consumer, target=consumer)
                    self.consume(consumer)
                    if not consumer.is_dead:
                        consumer.do_environmental_effects() # Apply environmental effects
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
            self.effects_on_path(action=action, x=loc[0], y=loc[1])

        # instantiate animation and render it
        ray_animation = Animation(engine=self.engine, frames=frames, stack_frames=self.stack_anim_frame) # sec_per_frames = default
        ray_animation.render()

        # effects on the entities
        for target in targets:
            if len(targets)>=1:
                self.effects_on_collided_entity(consumer=consumer, entity=target)

        self.consume(consumer)


class ScrollOfMagicMissileReadable(RayReadable):
    def effects_on_collided_actor(self, consumer: Actor, target: Actor):
        real_damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="magic")
        if self.parent.item_state.BUC == 1:
            real_damage *= 1.2
        elif self.parent.item_state.BUC == -1:
            real_damage *= 0.8
        real_damage = round(real_damage)
        # Log
        if target == self.engine.player:
            self.engine.message_log.add_message(i(f"마법 광선이 당신을 강타해 {real_damage} 데미지를 입혔다.",
                                                  f"A magic missile strikes you. You took {real_damage} damage."), fg=color.player_bad)
        else:
            self.engine.message_log.add_message(i(f"마법 광선이 {g(target.name, '을')} 강타해 {real_damage} 데미지를 입혔다.",
                                                  f"A magic missile strikes {target.name}. {target.name.capitalize()} took {real_damage} damage."),target=target, fg=color.enemy_unique)
        target.status.take_damage(amount=real_damage, attacked_from=consumer)


class ScrollOfDiggingReadable(RayReadable):
    def effects_on_consumer_tile(self, action: actions.ReadItem, x: int, y: int):
        consumer = action.entity
        if consumer.gamemap.tiles[x, y]["walkable"] and consumer.gamemap.tiles[x,y]["diggable"] and consumer.gamemap.tilemap[x,y] != TilemapOrder.MAP_BORDER.value:
            self.engine.message_log.add_message(i(f"굴착의 광선이 {g(consumer.gamemap.tiles[x, y]['tile_name'], '을')} 뚫고 지나갔다.",
                                                  f"A ray of digging goes through the {consumer.gamemap.tiles[x,y]['tile_name']}."),fg=color.player_neutral_important)
            consumer.gamemap.tiles[x, y] = consumer.gamemap.tileset["t_hole"]()
        return

    def effects_on_collided_wall(self, action: actions.ReadItem, x: int, y: int):
        consumer = action.entity
        dx = action.target_xy[0]
        dy = action.target_xy[1]
        if not consumer.gamemap.tiles[x,y]["walkable"] and consumer.gamemap.tiles[x,y]["diggable"] and consumer.gamemap.tilemap[x,y] != TilemapOrder.MAP_BORDER.value:
            self.engine.message_log.add_message(i(f"굴착의 광선이 {g(consumer.gamemap.tiles[x, y]['tile_name'], '을')} 뚫고 지나갔다.",
                                                  f"A ray of digging goes through the {consumer.gamemap.tiles[x, y]['tile_name']}."),fg=color.player_neutral_important)
            consumer.gamemap.tiles[x, y] = consumer.gamemap.tileset["t_floor"]()


class ScrollOfScorchingRayReadable(RayReadable):
    def effects_on_collided_actor(self, consumer: Actor, target: Actor):
        real_damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="fire")  # No direct state effect applied since fire entity is about to spawn
        if self.parent.item_state.BUC == 1:
            real_damage *= 1.2
        elif self.parent.item_state.BUC == -1:
            real_damage *= 0.8
        real_damage = round(real_damage)

        # Log
        if target == self.engine.player:
            self.engine.message_log.add_message(i(f"화염 광선이 당신을 꿰뚫으며 {real_damage} 데미지를 입혔다.",
                                                  f"A ray of scorching flame penetrates you. You took {real_damage} damage."),fg=color.player_bad)
        else:
            self.engine.message_log.add_message(i(f"화염 광선이 {g(target.name, '을')} 꿰뚫으며 {real_damage} 데미지를 입혔다.",
                                                  f"A ray of scorching flame penetrates {target.name}. {target.name.capitalize()} took {real_damage} damage."), target=target, fg=color.enemy_unique)
        target.actor_state.apply_burning([max(1,int(real_damage / 8)), 2, 0, 6])
        target.status.take_damage(amount=real_damage, attacked_from=consumer)
    
    def effects_on_path(self, action: actions.ReadItem, x: int, y: int):
        # Create fire
        import semiactor_factories
        semiactor_factories.fire.spawn(self.engine.game_map, x, y, 6)


class ScrollOfFreezingRayReadable(RayReadable):
    def effects_on_collided_actor(self, consumer: Actor, target: Actor):
        real_damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="cold")
        if self.parent.item_state.BUC == 1:
            real_damage *= 1.2
        elif self.parent.item_state.BUC == -1:
            real_damage *= 0.8
        real_damage = round(real_damage)

        # Log
        if target == self.engine.player:
            self.engine.message_log.add_message(i(f"얼음 광선이 당신을 꿰뚫으며 {real_damage} 데미지를 입혔다.",
                                                  f"A ray of freezing ice penetrates you. You took {real_damage} damage."), fg=color.player_bad)
        else:
            self.engine.message_log.add_message(i(f"얼음 광선이 {g(target.name, '을')} 꿰뚫으며 {real_damage} 데미지를 입혔다.",
                                                  f"A ray of freezing ice penetrates {target.name}. {target.name.capitalize()} took {real_damage} damage."),fg=color.enemy_unique, target=target)
        target.actor_state.apply_freezing([max(1,int(real_damage/8)), 5, 0.2, 0, 4])
        target.status.take_damage(amount=real_damage, attacked_from=consumer)

    def effects_on_path(self, action: actions.ReadItem, x: int, y: int):
        # Freeze water
        self.engine.game_map.tiles[x, y] = TileUtil.freeze(self.engine.game_map.tiles[x, y])


class ScrollOfLightningReadable(AutoTargetingHarmfulReadable):
    def __init__(self, maximum_range: int, fx_id, damage_range: Tuple[int,int]):
        super().__init__(maximum_range, fx_id)
        self.damage_range = damage_range

    @property
    def damage(self):
        return random.randint(*self.damage_range)

    def effects_on_target_actor(self, consumer:Actor, target: Actor):
        # Log
        if target == self.engine.player:
            self.engine.message_log.add_message(
                i(f"번개가 당신을 내리쳤다!",
                  f"A lightning strikes you!"), fg=color.player_bad
            )
        else:
            self.engine.message_log.add_message(
                i(f"번개가 {g(target.name, '을')} 내리쳤다!",
                  f"A lightning strikes {target.name}!"), target=target, fg=color.enemy_unique
            )

        target.status.take_damage(amount=0, attacked_from=consumer) # trigger target
        target.actor_state.apply_electrocution([self.damage, 0.5])
        target.actor_state.actor_electrocuted(source_actor=consumer)


class ScrollOfDestroyEquipmentReadable(Readable):
    def activate(self, action: actions.ReadItem) -> None:
        if action.entity == self.engine.player:
            self.engine.message_log.add_message(i(f"당신의 {g(self.parent.name, '으로')}부터 파괴적인 마법 에너지가 뿜어져 나왔다!",
                                                  f"Your {self.parent.name} emits a destructive magic energy!"),fg=color.player_neutral_important)
        equipments = [eq for eq in action.entity.equipments.equipments.values() if eq is not None]
        if equipments:
            destroy_item = random.choice(equipments)
            if destroy_item.item_state.BUC != 1 and not destroy_item.indestructible:
                destroy_item.remove_self()
                if action.entity == self.engine.player:
                    self.engine.sound_manager.add_sound_queue("fx_destroy_item")
                    self.engine.message_log.add_message(i(f"당신의 {g(destroy_item.name, '이')} 먼지가 되어 사라졌다!",
                                                          f"Your {destroy_item.name} crumbles to dust!"), fg=color.player_severe)
                else:
                    self.engine.message_log.add_message(i(f"{action.entity.name}의 {g(destroy_item.name, '이')} 먼지가 되어 사라졌다!",
                                                          f"{action.entity.name}'s {destroy_item.name} crumbles to dust!"), fg=color.player_severe)
            else:
                if action.entity == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신의 {g(destroy_item.name, '이')} 마법적 붕괴에 저항했다!",
                                                          f"Your {destroy_item} resists the power of magical destruction!"),fg=color.player_severe)
        self.consume(action.entity)


class ScrollOfHatredReadable(Readable):
    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        if consumer == self.engine.player:
            self.engine.message_log.add_message(i(f"던전 전체에서 당신을 향한 끔찍한 증오심이 느껴진다!",
                                                  f"You sense a dreadful amount of hatred towards you from the dungeon!"),fg=color.player_severe)
            self.engine.sound_manager.add_sound_queue("fx_hatred")

        for actor in consumer.gamemap.actors:
            if actor.ai:
                if actor.ai.check_if_enemy(consumer):
                    actor.status.take_damage(0, attacked_from=consumer)
                    actor.ai.path = actor.ai.get_path_to(consumer.x, consumer.y)
        self.consume(consumer)


class ScrollOfConflictReadable(Readable):
    def __init__(self, last_turn: int = 20):
        super().__init__()
        self.last_turn = last_turn

    def trigger_consumer(self, consumer: Actor) -> None:
        consumer.actor_state.apply_anger([0, self.last_turn])
        if consumer == self.engine.player:
            self.engine.message_log.add_message(i(f"당신은 참을 수 없는 분노를 느낀다!",
                                                  f"You feel an uncontrollable rage building inside you!"),
                                                fg=color.player_severe)

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        if consumer == self.engine.player:
            self.engine.sound_manager.add_sound_queue("fx_roar")
            self.engine.message_log.add_message(i(f"던전 곳곳에서 분노에 가득 찬 울부짖음이 들려온다!",
                                                  f"You hear an angry screams coming from the dungeon!"),fg=color.player_severe)

        if self.parent.item_state.BUC == -1: # If cursed, trigger only the consumer
            self.trigger_consumer(consumer)
        else:
            for actor in consumer.gamemap.actors:
                if actor == consumer and self.parent.item_state.BUC == 0: # If blessed, trigger all including the consumer.
                    self.trigger_consumer(consumer)
                else:
                    if actor.ai:
                        actor.ai.target = None # Reset target
                    actor.actor_state.apply_anger([0,self.last_turn])
        self.consume(consumer)


class ScrollOfSummoningReadable(Readable):
    """Spawn maximum of 8 monster onto nearby tiles."""
    def __init__(self, toughness: int = 0):
        super().__init__()
        self.toughness = max(0, toughness)

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        mon_cnt = 4
        if self.parent.item_state.BUC == -1: # If cursed, spawn 2 monster
            mon_cnt = 2
        elif self.parent.item_state.BUC == 1:
            mon_cnt = 8

        mon_list = spawn_monster_of_appr_diff_8way(gamemap=consumer.gamemap, center_x=consumer.x, center_y=consumer.y, spawn_cnt=mon_cnt, randomize=True)
        for m in mon_list:
            self.engine.message_log.add_message(i(f"{g(m.name, '이')} 소환되었다!",
                                                  f"{m.name} is summoned!"), fg=color.world)
        if mon_list:
            self.engine.sound_manager.add_sound_queue("fx_summon")
        self.consume(consumer)


from ability import Ability

class BookReadable(Readable):
    def __init__(
            self,
            ability: Optional[Ability]=None,
            read_msg: Optional[str]=None,
            int_req: int=10, # NOTE: in ReadItem, Intelligence 10 or higher is required to read something.
            comprehension_chance_per_int_bonus: float=0.2,
    ):
        """
        Args:
            ability:
                ability object.
                Reader will gain the ability when they complete the book.
            read_msg:
                message to print when player read and succeded to comprehend the book.
            int_req:
                the minimum intelligence requirement for one to comprehend the book.
            comprehension_chance_per_int_bonus:
                if the reader's intelligence surpass the minimum intelligence required to read,
                you gain this amount of chance to successfully read and comprehending the book.
        """
        super().__init__()
        self.ability = ability
        self.read_msg = read_msg
        self.int_req = int_req
        self.comprehension_chance_per_int_bonus = comprehension_chance_per_int_bonus

    def try_comprehend(self, reader: Actor) -> bool:
        """
        Return:
            Whether the reader was able to comprehend the book or not.
        """
        success_chance = (reader.status.changed_status["intelligence"] - self.int_req + 1) * self.comprehension_chance_per_int_bonus
        if self.parent.item_state.check_if_unidentified:
            success_chance -= 0.1
        if self.parent.item_state.BUC == 1:
            success_chance += 0.05
        elif self.parent.item_state.BUC == -1:
            success_chance -= 0.2 # Harder to understand cursed spellbooks
        if self.parent.item_state.burntness > 0:
            success_chance -= 0.1 * self.parent.item_state.burntness

        if random.random() <= success_chance:
            return True
        return False

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.ReadItem(consumer, self.parent)

    def activate(self, action: actions.ReadItem) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        reader = action.entity

        if self.try_comprehend(reader=reader):
            self.read(action)  # Identify when successful
            return None
        else:
            if reader.status.changed_status["intelligence"] > self.int_req:
                # failed by chance
                if reader == self.engine.player:
                    self.engine.message_log.add_message(i(f"당신은 {self.parent.name}의 내용을 이해하는 것에 실패했다.",
                                                          f"You fail to comprehend {self.parent.name}."), fg=color.player_failed)
                return None
            else:
                # failed or cursed.
                if reader == self.engine.player:
                    self.engine.message_log.add_message(i(f"{g(self.parent.name, '은')} 당신이 읽기엔 너무 어려웠다!",
                                                          f"{self.parent.name} was too difficult for you!"), fg=color.player_failed)
                reader.actor_state.apply_confusion([0, 5])
            return None

    def effects_when_read(self, action: actions.ReadItem) -> None:
        """Overwrite this function to give additional effects."""
        pass

    def read(self, action: actions.ReadItem) -> None:
        """Does not get removed from the inventory."""
        # fully identify used instance, and semi-identify the same item types.
        reader = action.entity
        if reader == self.engine.player and self.read_msg:
            self.engine.message_log.add_message(self.read_msg, fg=color.player_neutral_important)
        if self.ability:
            reader.ability_inventory.gain_ability(self.ability)
        self.parent.item_state.identify_self(identify_level=1)
        self.effects_when_read(action)

    def item_use_cancelled(self, actor: Actor) -> actions.Action:
        """
        Does nothing.
        """
        return actions.WaitAction(actor)


class SatanicBibleBookReadable(BookReadable):
    def effects_when_read(self, action: actions.ReadItem) -> None:
        reader = action.entity
        if reader.actor_state.has_soul:
            reader.actor_state.has_soul = False
            reader.status.gain_strength(1)
            reader.status.gain_dexterity(1)
            reader.status.gain_constitution(1)
            reader.status.gain_agility(1)
            reader.status.gain_intelligence(1)
            reader.status.gain_charm(1)
            if reader == self.engine.player:
                self.engine.sound_manager.add_sound_queue("fx_evil2")
                self.engine.message_log.add_message(i("당신은 무언가 중요한 것을 댓가로 더 강해진 듯한 기분이 들었다.",
                                                      f"You feel stronger in exchange for something important."), fg=color.player_neutral_important)
        else:
            if reader == self.engine.player:
                self.engine.message_log.add_message(i("당신은 책을 읽었지만 아무 일도 일어나지 않았다.",
                                                      f"You read the book but nothing happened."), fg=color.player_neutral_important)



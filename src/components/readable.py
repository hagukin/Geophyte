from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING, Tuple, List

import tiles
from animation import Animation
from components.base_component import BaseComponent
from exceptions import Impossible
from order import InventoryOrder
from korean import grammar as g
from tiles import TileUtil
from entity import Actor

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

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        # fully identify used instance, and semi-identify the same item types.
        self.parent.item_state.identify_self(identify_level=2)
        self.parent.parent.decrease_item_stack(self.parent, remove_count=1)

    def item_use_cancelled(self, actor: Actor) -> actions.Action:
        """
        Called when item usage is cancelled.
        Only the player should be able to call this function.
        """
        self.consume()
        self.engine.message_log.add_message(f"당신의 {g(self.parent.name, '이')} 먼지가 되어 사라졌다.", color.player_bad)
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

        self.engine.message_log.add_message("목표 지점을 선택하세요.", color.help_msg)

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
            raise Impossible("보이지 않는 지역을 선택할 수는 없습니다.")
        if not self.can_select_not_explored_tile and not self.engine.game_map.explored[action.target_xy]:
            raise Impossible("모험하지 않은 지역을 선택할 수는 없습니다.")

        if not target:
            self.effects_on_selected_tile_with_no_actor(consumer=consumer)
        else:
            self.effects_on_selected_tile_with_actor(consumer=consumer, target=target)

        self.consume()


class ScrollOfTeleportationReadable(SelectTileReadable):
    def __init__(self):
        super().__init__()
        self.can_select_not_visible_tile = True
        self.can_select_not_explored_tile = False

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.can_select_not_visible_tile and not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("보이지 않는 지역을 선택할 수는 없습니다.")
        if not self.can_select_not_explored_tile and not self.engine.game_map.explored[action.target_xy]:
            raise Impossible("모험하지 않은 지역을 선택할 수는 없습니다.")

        if self.parent.item_state.BUC == 1:
            stability = 0
        elif self.parent.item_state.BUC == 0:
            stability = 1
        else:
            stability = 2

        from actions import TeleportAction
        TeleportAction(entity=consumer, x=action.target_xy[0], y=action.target_xy[1], gamemap=self.engine.game_map,stability=stability).perform()
        self.consume()


class ScrollOfConfusionReadable(SelectTileReadable):
    def __init__(self, number_of_turns: int):
        super().__init__()
        self.can_select_not_visible_tile = False
        self.number_of_turns = number_of_turns
    
    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신은 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.", color.player_neutral)
        else:
            self.engine.message_log.add_message(f"{g(consumer.name, '은')} 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.",color.player_neutral, target=consumer)

    def effects_on_selected_tile_with_actor(self, consumer: Actor, target: Actor):
        if self.parent.item_state.BUC == -1:
            # Log
            new_target = consumer
            if new_target == self.engine.player:
                self.engine.message_log.add_message(f"당신은 굉장히 어지럽다.", color.player_not_good, )
            else:
                self.engine.message_log.add_message(f"{g(new_target.name, '이')} 휘청거리기 시작한다.", color.player_sense, target=target)

            new_target.actor_state.apply_confusion([0, self.number_of_turns])
        else:
            # Log
            if target == self.engine.player:
                self.engine.message_log.add_message(f"당신은 굉장히 어지럽다.", color.player_not_good,)
            else:
                self.engine.message_log.add_message(f"{g(target.name, '이')} 휘청거리기 시작한다.", color.player_sense, target=target)

            target.actor_state.apply_confusion([0,self.number_of_turns])


class ScrollOfTameReadable(SelectTileReadable):
    def __init__(self):
        super().__init__()
        self.can_select_not_visible_tile = False
    
    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"당신은 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.", color.player_neutral)
        else:
            self.engine.message_log.add_message(f"{g(consumer.name, '은')} 허공을 향해 주문서를 읽었고, 아무 일도 일어나지 않았다.",color.player_neutral, target=consumer)

    def effects_on_selected_tile_with_actor(self, consumer: Actor, target: Actor):
        if not target.ai or target == consumer:
            # Log
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"당신의 자신감이 차오른다.", color.player_buff)
            else:
                self.engine.message_log.add_message(f"{g(consumer.name, '은')} 자신감이 넘쳐 보인다.", color.player_sense, target=consumer)

            if consumer.status.experience:
                consumer.status.experience.gain_charm_exp(200)
        else:
            if self.parent.item_state.BUC == 1:
                tame_bonus = 5
            elif self.parent.item_state.BUC == -1:
                tame_bonus = -3
                target.take_damage(amount=0, attacked_from=consumer) # trigger
            else:
                tame_bonus = 0

            if target.ai.try_tame(consumer, tame_bonus=tame_bonus):
                # Log
                if consumer == self.engine.player:
                    self.engine.message_log.add_message(f"{g(target.name, '을')} 길들였다!", color.player_success, target=target)
                    if target.actor_state.can_talk:
                        self.engine.message_log.add_message(f"{g(target.name, '이')} 당신에게 충성을 표했다.", color.player_success, target=target)
                    else:
                        self.engine.message_log.add_message(f"{g(target.name, '이')} 당신에 대한 신뢰를 보였다.", color.player_success, target=target)
                else:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} 이제 {g(consumer.name, '을')} 주인으로 섬긴다!", color.enemy_unique, target=target)

                if consumer.status.experience:
                    consumer.status.experience.gain_charm_exp(100, exp_limit=1000)
            else:
                if consumer == self.engine.player:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} 당신의 정신적 지배에 저항했다!", color.player_failed, target=target)
                else:
                    self.engine.message_log.add_message(f"{g(target.name, '은')} {consumer.name}의 명령을 거부했다!", color.enemy_unique, target=target)


class SelectItemFromInventoryReadable(Readable):
    def get_action(self, consumer: Actor, cancelled: bool=False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("아이템을 선택하세요.", color.help_msg)

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
        self.consume()


class ScrollOfEnchantmentReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("마법 강화할 아이템을 선택하세요.", color.help_msg)

        from input_handlers import InventoryChooseItemAndCallbackHandler
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            inventory_component=consumer.inventory,
            show_only_types=(
                InventoryOrder.MELEE_WEAPON,
                InventoryOrder.THROWING_WEAPON,
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
            if self.parent.item_state.BUC == 1:
                if selected_item.equipable:
                    selected_item.equipable.upgrade_this(random.randint(1,2))
                self.engine.message_log.add_message(f"당신의 {g(selected_item.name, '이')} 황금색 빛을 내뿜었다!",color.player_success, target=consumer)
            else:
                if selected_item.equipable:
                    selected_item.equipable.upgrade_this(1)
                self.engine.message_log.add_message(f"당신의 {g(selected_item.name, '이')} 밝은 빛을 내뿜었다!", color.player_success, target=consumer)
            if selected_item.item_state.equipped_region:
                self.engine.message_log.add_message(f"당신의 {selected_item.name}에서 이전보다 더 강한 힘이 느껴진다.", color.player_success, target=consumer)
        else:
            if selected_item.equipable:
                selected_item.equipable.upgrade_this(1)
            self.engine.message_log.add_message(f"{consumer.name}의 {g(selected_item.name, '이')} 빛을 내뿜었다.", color.player_sense, target=consumer)


class ScrollOfIdentifyReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("감정할 아이템을 선택하세요.", color.help_msg)

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
            for i in items:
                i.item_state.identify_self(2)
                self.engine.message_log.add_message(f"당신은 {g(i.name, '을')} 감정했다.", color.player_success)

        if consumer.status.experience:
            consumer.status.experience.gain_intelligence_exp(20, exp_limit=2000)

        # Log TODO
        #TODO: identify multiple when blessed?
        #NOTE: Currently self-identification is possible


class ScrollOfRemoveCurseReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("저주를 해제할 아이템을 선택하세요.", color.help_msg)

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
                    self.engine.message_log.add_message(f"당신의 {g(selected_item.name, '로')}부터 사악한 기운이 사라졌다!", color.player_success, target=consumer)
                elif buc == -1 and not success:
                    self.engine.message_log.add_message(f"당신의 {g(selected_item.name, '로')}부터 뿜어져 나오는 사악한 기운이 너무 강력해, 저주를 해제할 수 없다!",color.player_failed, target=consumer)
                else:
                    self.engine.message_log.add_message(f"백색 빛이 당신의 {g(selected_item.name, '을')} 감쌌다.", color.player_sense, target=consumer)
            #NOTE: Currently self-uncursing is possible
        else:
            success = selected_item.item_state.change_buc(BUC=-1)
            # Log
            if consumer == self.engine.player:
                if buc != -1 and success:  # If item was not cursed before
                    self.engine.message_log.add_message(f"당신의 {g(selected_item.name, '로')}부터 사악한 기운이 뿜어져 나온다!",color.player_success, target=consumer)
                elif buc != -1 and not success:
                    self.engine.message_log.add_message(
                        f"당신의 {g(selected_item.name, '은')} 사악한 기운에 저항했다!",color.player_failed, target=consumer)
                else:
                    self.engine.message_log.add_message(f"검은 빛이 당신의 {g(selected_item.name, '을')} 감쌌다.",color.player_sense, target=consumer)

        if consumer.status.experience:
            consumer.status.experience.gain_intelligence_exp(10)


class ScrollOfMagicMappingReadable(Readable):
    """
    Unlike most items that receives input and call callback function,
    or items that receives no inputs,
    this readable will first apply the effect and after wait for an input. 
    When input is reveived, this will return 0 to callback and finish the whole process. (0 is just a trash value it doesn't matter what you pass)
    """
    def activate(self, consumer) -> None:
        self.engine.update_fov()
        self.consume()

    def get_action(self, consumer):
        if consumer == self.engine.player:
            if self.parent.item_state.BUC == 1:
                self.engine.message_log.add_message(f"당신의 머리 속에 이 층의 모든 비밀들이 전해졌다.", color.player_neutral_important,)
            elif self.parent.item_state.BUC == -1:
                self.engine.message_log.add_message(f"기괴한 기하학적 문양들이 당신의 머릿속을 가득 채운다!", color.player_bad, )
            else:
                self.engine.message_log.add_message( f"당신의 머리 속이 기하학적 정보들로 가득 차기 시작했다.", color.player_neutral_important,)

            for y in range(len(self.engine.game_map.visible[0])):
                for x in range(len(self.engine.game_map.visible)):
                    self.engine.game_map.visible[x, y] = True
            for y in range(len(self.engine.game_map.explored[0])):
                for x in range(len(self.engine.game_map.explored)):
                    self.engine.game_map.explored[x, y] = True

            from input_handlers import MagicMappingLookHandler
            self.engine.event_handler = MagicMappingLookHandler(
                callback=lambda trash_value: actions.ReadItem(consumer, self.parent),
            )#NOTE: Has no item_cancel_callback parameter, since the item already has been consumed.
        else:
            print("WARNING::AI read magic mapping")

        if self.parent.item_state.BUC == -1:
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"머리가 지끈거린다!", color.player_bad, )
            consumer.actor_state.apply_confusion([0, 15])
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
            f"{g(self.parent.name, '을')} 사용할 영역을 선택하세요.", color.help_msg
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
            raise Impossible("보이지 않는 지역을 선택할 수는 없습니다.")

        self.engine.message_log.add_message(f"허공에서 운석이 나타났다!", target=consumer, fg=color.world)

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
                        self.engine.message_log.add_message(f"당신은 운석에 맞아 {real_damage} 데미지를 받았다!",target=target, fg=color.player_bad)
                    else:
                        self.engine.message_log.add_message(f"{g(target.name, '이')} 운석에 맞아 {real_damage} 데미지를 받았다!", target=target, fg=color.enemy_unique)
                targets_hit = True

        if not targets_hit and self.engine.game_map.visible[target_xy[0], target_xy[1]]:# nothing was hit
            self.engine.message_log.add_message(f"운석이 바닥과 충돌했다.", fg=color.player_sense)
        self.consume()

        
class AutoTargetingHarmfulReadable(Readable):
    def __init__(self, maximum_range: int):
        super().__init__()
        self.maximum_range = maximum_range

    def effects_on_target_actor(self, consumer:Actor, target: Actor):
        pass

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0


        if self.parent.item_state.BUC == 1:
            targets = []

            if consumer == self.engine.player:
                for actor in self.engine.game_map.actors:
                    if actor != self.engine.player and self.parent.gamemap.visible[actor.x, actor.y]:
                        targets.append(actor)
            else:
                if consumer.ai:
                    for actor in self.engine.game_map.actors:
                        if actor != consumer and consumer.ai.vision[actor.x, actor.y]:
                            targets.append(actor)

            for target in set(targets):
                self.effects_on_target_actor(consumer=consumer, target=target)
        elif self.parent.item_state.BUC == -1:
            self.effects_on_target_actor(consumer=consumer, target=consumer)
        else:
            for actor in self.engine.game_map.actors:
                if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
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

        self.consume()


class RayReadable(Readable):
    def __init__(self, anim_graphic, damage_range: Tuple[int,int]=(0,0), penetration: bool=False, max_range: int=1000):
        """
        Args:
            anim_graphic:
                Can be either callable or dictionary obj.
        """
        super().__init__()
        self._anim_graphic = anim_graphic
        self.damage_range = damage_range
        self.penetration = penetration
        self.max_range = max_range

    @property
    def anim_graphic(self):
        if callable(self._anim_graphic): # Dynamic graphic
            return self._anim_graphic()
        else:
            return self._anim_graphic

    @property
    def damage(self):
        return random.randint(*self.damage_range)

    def effects_on_path(self, x: int, y: int):
        """effects applied to the tiles on the path."""
        pass

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

    def get_action(self, consumer, cancelled: bool=False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(f"{g(self.parent.name, '을')} 사용할 방향을 선택하세요.", color.help_msg)
        self.engine.message_log.add_message(f"방향키/마우스 이동:위치 선택 | 엔터/마우스 클릭:결정", color.help_msg)

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
                if collided == consumer:
                    self.effects_on_collided_actor(consumer=consumer, target=consumer)
                    self.consume()
                    return 0

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
        ray_animation = Animation(engine=self.engine, frames=frames, stack_frames=True) # sec_per_frames = default
        ray_animation.render()

        # effects on the entities
        for target in targets:
            if len(targets)>=1:
                self.effects_on_collided_entity(consumer=consumer, entity=target)

        self.consume()


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
            self.engine.message_log.add_message(f"마법 광선이 당신을 강타해 {real_damage} 데미지를 입혔다.", fg=color.player_bad)
        else:
            self.engine.message_log.add_message(f"마법 광선이 {g(target.name, '을')} 강타해 {real_damage} 데미지를 입혔다.",target=target, fg=color.enemy_unique)
        target.status.take_damage(amount=real_damage, attacked_from=consumer)


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
            self.engine.message_log.add_message(f"화염 광선이 당신을 꿰뚫으며 {real_damage} 데미지를 입혔다.",fg=color.player_bad)
        else:
            self.engine.message_log.add_message(f"화염 광선이 {g(target.name, '을')} 꿰뚫으며 {real_damage} 데미지를 입혔다.", target=target, fg=color.enemy_unique)
        target.actor_state.apply_burning([max(1,int(real_damage / 8)), 2, 0, 6])
        target.status.take_damage(amount=real_damage, attacked_from=consumer)
    
    def effects_on_path(self, x: int, y: int):
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
            self.engine.message_log.add_message(f"얼음 광선이 당신을 꿰뚫으며 {real_damage} 데미지를 입혔다.", fg=color.player_bad)
        else:
            self.engine.message_log.add_message(f"얼음 광선이 {g(target.name, '을')} 꿰뚫으며 {real_damage} 데미지를 입혔다.",fg=color.enemy_unique, target=target)
        target.actor_state.apply_freezing([max(1,int(real_damage/8)), 5, 0.2, 0, 4])
        target.status.take_damage(amount=real_damage, attacked_from=consumer)

    def effects_on_path(self, x: int, y: int):
        # Freeze water
        self.engine.game_map.tiles[x, y] = TileUtil.freeze(self.engine.game_map.tiles[x, y])


class ScrollOfThunderStormReadable(AutoTargetingHarmfulReadable):
    def __init__(self, maximum_range: int, damage_range: Tuple[int,int]):
        super().__init__(maximum_range)
        self.damage_range = damage_range

    @property
    def damage(self):
        return random.randint(*self.damage_range)

    def effects_on_target_actor(self, consumer:Actor, target: Actor):
        # Log
        if target == self.engine.player:
            self.engine.message_log.add_message(
                f"번개가 큰 천둥소리와 함께 당신을 내리쳤다!", fg=color.player_bad
            )
        else:
            self.engine.message_log.add_message(
                f"번개가 큰 천둥소리와 함께 {g(target.name, '을')} 내리쳤다!", target=target, fg=color.enemy_unique
            )

        # trigger target
        target.status.take_damage(amount=0, attacked_from=consumer)

        # damage
        target.actor_state.apply_electrocution([self.damage, 0.5])
        target.actor_state.actor_electrocuted(source_actor=consumer)



from ability import Ability

class BookReadable(Readable):
    def __init__(
            self,
            ability: Ability,
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
            if reader == self.engine.player and self.read_msg:
                self.engine.message_log.add_message(self.read_msg, fg=color.player_neutral_important)
            if self.ability:
                reader.ability_inventory.gain_ability(self.ability)
            self.consume()  # Identify when successful
            return None
        else:
            # failed or cursed.
            if reader == self.engine.player:
                self.engine.message_log.add_message(f"당신은 {self.parent.name}의 내용을 이해하는 것에 실패했다.", fg=color.player_failed)
            reader.actor_state.apply_confusion([0,5])
            return None

    def consume(self) -> None:
        """Does not get removed from the inventory."""
        # fully identify used instance, and semi-identify the same item types.
        self.parent.item_state.identify_self(identify_level=1)

    def item_use_cancelled(self, actor: Actor) -> actions.Action:
        """
        Does nothing.
        """
        return actions.WaitAction(actor)


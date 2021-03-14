from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from animation import Animation
from entity import Actor
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import AreaRangedAttackHandler, SingleRangedAttackHandler, RayRangedInputHandler, MagicMappingLookHandler, StorageSelectSingleEventHandler, InventoryChooseItemAndCallbackHandler
from order import InventoryOrder

import semiactor_factories
import actions
import color

if TYPE_CHECKING:
    from entity import Item

class Readable(BaseComponent):
    parent: Item
        
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
        self.parent.parent.remove_item(self.parent, remove_count=1)

    def item_use_cancelled(self, actor: Actor) -> actions.Action:
        """
        Called when item usage is cancelled.
        Only the player should be able to call this function.
        """
        self.consume()
        self.engine.message_log.add_message(f"Your {self.parent.name} crumbles into dust.", color.white)
        return actions.WaitAction(actor)


class SelectTileReadable(Readable):
    def __init__(self):
        pass
        
    def get_action(self, consumer: Actor, cancelled: bool=False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("Select a target location.", color.needs_target)
        self.engine.event_handler = SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ReadItem(consumer, self.parent, xy),
            revert_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        pass

    def effects_on_selected_tile_with_actor(self, consumer:Actor, target: Actor):
        pass

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            self.effects_on_selected_tile_with_no_actor(consumer=consumer)
        else:
            self.effects_on_selected_tile_with_actor(consumer=consumer, target=target)
        
        self.consume()


class ScrollOfConfusionReadable(SelectTileReadable):
    def __init__(self, number_of_turns: int):
        super().__init__()
        self.number_of_turns = number_of_turns
    
    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"You tried to confuse a thin air, and failed miserably.", color.gray)
        else:
            self.engine.message_log.add_message(f"{consumer.name} tried to confuse a thin air, and failed miserably.", color.gray)

    def effects_on_selected_tile_with_actor(self, consumer: Actor, target: Actor):
        # Log
        if consumer == self.engine.player and target == consumer:
            self.engine.message_log.add_message(f"You feel incredibly dizzy.", color.player_damaged,)
        elif target == consumer:
            self.engine.message_log.add_message(f"{consumer.name} starts to act weird.", color.white, target=target)
        else:
            self.engine.message_log.add_message(f"{target.name} starts to stagger.", color.status_effect_applied, target=target)

        target.actor_state.is_confused[1] = self.number_of_turns


class ScrollOfTameReadable(SelectTileReadable):
    
    def effects_on_selected_tile_with_no_actor(self, consumer: Actor):
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"You tried your best to tame a thin air, but failed.", color.gray)

    def effects_on_selected_tile_with_actor(self, consumer: Actor, target: Actor):
        if not target.ai or target == consumer:
            # Log
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"You feel much more confident in yourself.", color.stats_gained)
            else:
                self.engine.message_log.add_message(f"{consumer.name} looks more self-confident.", color.gray, target=consumer)
            
            # Apply
            target.status.gain_constitution(1)
        else:
            # Log
            if consumer == self.engine.player:
                self.engine.message_log.add_message(f"{target.name} is tamed!", color.status_effect_applied, target=target)
                if target.actor_state.can_talk:
                    self.engine.message_log.add_message(f"{target.name} pledges its loyalty to you.", color.status_effect_applied, target=target)
                else:
                    self.engine.message_log.add_message(f"{target.name} shows you its respect on you.", color.status_effect_applied, target=target)
            else:
                self.engine.message_log.add_message(f"{target.name} is now serving {consumer.name}!", color.white, target=target)

            # Apply
            target.ai.owner = consumer


class SelectItemFromInventoryReadable(Readable):
    def __init__(self):
        pass

    def get_action(self, consumer: Actor, cancelled: bool=False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("Choose an item to enchant.", color.needs_target)
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            self.engine,
            inventory_component=consumer.inventory,
            show_only=None, # If item_type filter is needed, you should override this entire function.
            callback=lambda selected_item : actions.ReadItem(consumer, self.parent, (0,0), selected_item),
            revert_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        raise NotImplementedError()

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        enchanted_item = action.item_selected

        self.effects_on_selected_item(consumer, enchanted_item)
        
        self.consume()


class ScrollOfEnchantmentReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("Choose an item to enchant.", color.needs_target)
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            self.engine,
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
            revert_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        selected_item.equipable.upgrade_this(1) #TODO: Add more powerful enchanting scrolls? blessed?
        
        # Log
        if consumer == self.engine.player:
            self.engine.message_log.add_message(f"Your {selected_item.name} emits a bright magical light!", color.status_effect_applied, target=consumer)
            if selected_item.item_state.is_equipped:
                self.engine.message_log.add_message(f"You feel your {selected_item.name} is now more powerful!", color.status_effect_applied, target=consumer)
        else:
            self.engine.message_log.add_message(f"{consumer.name}'s {selected_item.name} emits a bright magical light!", color.white, target=consumer)
            # TODO: auto-identify if the scroll is used in sight?


class ScrollOfIdentifyReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("Choose an item to identify.", color.needs_target)
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            self.engine,
            inventory_component=consumer.inventory,
            show_only_status=("unidentified-all", "semi-identified-all"), # NOTE: WARNING - If yoou pass only one parameter, additional comma is needed inside tuple to prevent passing the data in string form
            callback=lambda selected_item : actions.ReadItem(consumer, self.parent, (0,0), selected_item),
            revert_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        selected_item.item_state.identify_self(2)

        # Log TODO
        #TODO: identify multiple when blessed?
        #NOTE: Currently self-identification is possible


class ScrollOfRemoveCurseReadable(SelectItemFromInventoryReadable):
    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message("Choose an item to remove curse.", color.needs_target)
        self.engine.event_handler = InventoryChooseItemAndCallbackHandler(
            self.engine,
            inventory_component=consumer.inventory,
            show_only_status=("unidentified-all", "semi-identified-all", "full-identified-cursed",),
            callback=lambda selected_item : actions.ReadItem(consumer, self.parent, (0,0), selected_item),
            revert_callback=lambda x: self.get_action(consumer, x),
        )
        return None
    
    def effects_on_selected_item(self, consumer: Actor, selected_item: Item):
        temp = selected_item.item_state.BUC
        selected_item.item_state.uncurse_self() #TODO: uncurse multiple when blessed?

        # Log
        if temp <= -1: #If item was cursed before
            self.engine.message_log.add_message(f"The dark energy that were inside of {consumer.name}'s {selected_item.name} evaporates!", color.status_effect_applied, target=consumer)
        else:
            self.engine.message_log.add_message(f"A white light surrounds {consumer.name}'s {selected_item.name}.", color.status_effect_applied, target=consumer)
        #NOTE: Currently self-uncursing is possible


class ScrollOfMagicMappingReadable(Readable): #TODO: make parent class like other readables
    """
    Unlike most items that receives input and call callback function,
    or items that receives no inputs,
    this readable will first apply the effect and after wait for an input. 
    When input is reveived, this will return 0 to callback and finish the whole process. (0 is just a trash value it doesn't matter what you pass)
    """
    def __init__(self, tier:int=1):
        self.tier = tier

    def activate(self, consumer) -> None:
        self.engine.update_fov()
        self.consume()

    def get_action(self, consumer):
        if self.tier == 1:
            self.engine.message_log.add_message(f"For a brief moment, you sense everything on this level.", color.status_effect_applied,)
            for y in range(len(self.engine.game_map.visible[0])):
                for x in range(len(self.engine.game_map.visible)):
                    self.engine.game_map.visible[x, y] = True
            for y in range(len(self.engine.game_map.explored[0])):
                for x in range(len(self.engine.game_map.explored)):
                    self.engine.game_map.explored[x, y] = True
        elif self.tier == 2:
            self.engine.message_log.add_message( f"Your mind is filled with geometric informations.", color.status_effect_applied,)
            for y in range(len(self.engine.game_map.explored[0])):
                for x in range(len(self.engine.game_map.explored)):
                    self.engine.game_map.explored[x, y] = True
    
        self.engine.message_log.add_message("Press ESC to stop viewing the map.", color.white,)
        self.engine.event_handler = MagicMappingLookHandler(
            self.engine,
            callback=lambda trash_value: actions.ReadItem(consumer, self.parent),
        )#NOTE: Has no revert_callback parameter, since the item already has been consumed.
        return None


class ScrollOfMeteorStormReadable(Readable): #TODO: Make parent class like other readables
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor, cancelled: bool = False) -> Optional[actions.Action]:
        if cancelled:
            return self.item_use_cancelled(actor=consumer)

        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        self.engine.event_handler = AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ReadItem(consumer, self.parent, xy),
            revert_callback=lambda x: self.get_action(consumer, x),
        )
        return None

    def activate(self, action: actions.ReadItem) -> None:
        target_xy = action.target_xy
        consumer = action.entity

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        # Set fire on the given radius
        for dx in range(-self.radius, self.radius+1):
            for dy in range(-self.radius, self.radius+1):
                semiactor_factories.fire.spawn(self.engine.game_map, target_xy[0] + dx, target_xy[1] + dy, 6)

        targets_hit = False
        for target in self.engine.game_map.actors:
            if target.chebyshevDist(*target_xy) <= self.radius:
                # damage
                self.damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="physical")
                target.status.take_damage(amount=self.damage, attacked_from=consumer)

                # Log
                self.engine.message_log.add_message(f"The {target.name} gets slammed by a meteorite, taking {self.damage} damage!", target=target)

                targets_hit = True

        if not targets_hit:# nothing was hit
            self.engine.message_log.add_message(f"A meteorite falls and slams the ground!")
        self.consume()

        
class AutoTargetingReadable(Readable):
    def __init__(self, damage: int, maximum_range: int, tier: int=1):
        self.tier = tier
        self.damage = damage
        self.maximum_range = maximum_range

    def effects_on_target_actor(self, consumer:Actor, target: Actor):
        pass

    def activate(self, action: actions.ReadItem) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        if self.tier == 2: # tier 2: apply effect to one random actor nearby. 
            for actor in self.engine.game_map.actors:
                if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                    distance = consumer.distance(actor.x, actor.y)

                    if distance < closest_distance:
                        target = actor
                        closest_distance = distance

            if target:
                # apply effect
                self.effects_on_target_actor(consumer=consumer, target=target)
            else:
                # if there is no valid target, it will target the reader instead.
                self.effects_on_target_actor(consumer=consumer, target=consumer)
        elif self.tier == 1: # tier 1: apply effect to every nearby actor except for the reader. (Nothing will happen if there is no valid target)
            targets = []

            for actor in self.engine.game_map.actors:
                if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                    targets.append(actor)

            for target in set(targets):
                self.effects_on_target_actor(consumer=consumer, target=target)

        self.consume()


class RayReadable(Readable):
    def __init__(self, anim_graphic, damage: int=0, penetration: bool=False, max_range: int=1000):
        self.anim_graphic = anim_graphic
        self.damage = damage
        self.penetration = penetration
        self.max_range = max_range

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

        self.engine.message_log.add_message(
            "Select a direction.", color.needs_target
        )
        self.engine.event_handler = RayRangedInputHandler(
            self.engine,
            actor=consumer,
            max_range=self.max_range,
            callback=lambda xy: actions.ReadItem(consumer, self.parent, xy),
            revert_callback=lambda x: self.get_action(consumer, x),
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
            relative_x, relative_y = self.engine.camera.get_relative_coordinate(abs_x=loc[0], abs_y=loc[1])
            frames.append([(relative_x, relative_y, self.anim_graphic, None)])

            # effects on the paths
            self.effects_on_path(x=loc[0], y=loc[1])

        # instantiate animation and render it
        ray_animation = Animation(engine=self.engine, frames=frames, stack_frames=True) # sec_per_frames = default(0.1s)
        ray_animation.render()

        # effects on the entities
        for target in targets:
            if len(targets)>=1:
                self.effects_on_collided_entity(consumer=consumer, entity=target)

        self.consume()


class ScrollOfMagicMissileReadable(RayReadable):
    def effects_on_collided_actor(self, consumer: Actor, target: Actor):
        self.damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="magic")

        # Log
        self.engine.message_log.add_message(
        f"A magical beam strikes the {target.name}, for {self.damage} damage!", target=target
        )

        target.status.take_damage(amount=self.damage, attacked_from=consumer)


class ScrollOfPiercingFlameReadable(RayReadable):
    def effects_on_collided_actor(self, consumer: Actor, target: Actor):
        self.damage = target.status.calculate_dmg_reduction(damage=self.damage, damage_type="fire")

        # Log
        self.engine.message_log.add_message(
        f"A beam of flame pierces the {target.name}, for {self.damage} damage!", target=target
        )

        target.status.take_damage(amount=self.damage, attacked_from=consumer)
    
    def effects_on_path(self, x: int, y: int):
        # Create fire
        semiactor_factories.fire.spawn(self.engine.game_map, x, y, 6)


class ScrollOfThunderStormReadable(AutoTargetingReadable):
    def effects_on_target_actor(self, consumer:Actor, target: Actor):
        # Log
        self.engine.message_log.add_message(
            f"A lighting bolt strikes the {target.name} with a loud thunder!", target=target
        )

        # trigger target
        target.status.take_damage(amount=0, attacked_from=consumer)

        # damage
        target.actor_state.is_electrocuting = [self.damage, 0.5]
        target.actor_state.actor_electrocuted()

        
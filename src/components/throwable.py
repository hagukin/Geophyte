from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING
from animation import Animation
from components.base_component import BaseComponent
from korean import grammar as g
from language import interpret as i
from tiles import TileUtil
from entity import Actor, SemiActor, Entity
from order import InventoryOrder

import actions
import color
import random


class Throwable(BaseComponent):

    def __init__(self,
                 base_throw: int=0,
                 additional_throw: int=0,
                 penetration: bool=False,
                 break_chance: float=0,
                 air_friction: float=1,
                 sec_per_frame:Optional[float]=None, # Use default value (calculated in Animation.__init__)
                 trigger_if_thrown_at: bool = False,
                 identify_when_shattered: int = 0,
                 identify_when_collided_with_actor: int = 0,
                 identify_when_collided_with_entity: int = 0,
                 ):
        """
        Args:
            identify_when_shattered:
                0 - do nothing
                1 - semi identify
                2 - full identify
        """
        super().__init__(None)
        self.penetration = penetration
        self.break_chance = break_chance # 0~1
        self.air_friction = air_friction
        self.base_throw = base_throw
        self.additional_throw = additional_throw
        self.sec_per_frame = sec_per_frame
        self.trigger_if_thrown_at = trigger_if_thrown_at
        self.identify_when_shattered = identify_when_shattered
        self.identify_when_collided_with_actor = identify_when_collided_with_actor
        self.identify_when_collided_with_entity = identify_when_collided_with_entity

        #### Modified for each throw ####
        self.shattered = False # if True, item can be destroyed after being thrown (depending on the break_chance)
        self.shattered_x = None
        self.shattered_y = None
        self.collision_x = None # Set this value When collided with a monster, and when this throwable's penetrate == False. When collided with a wall, this value remains None.
        self.collision_y = None
        self.dx = None
        self.dy = None


    def reset_values(self) -> None:
        """Is called after activate() function finishes."""
        self.shattered = False
        self.shattered_x = None
        self.shattered_y = None
        self.collision_x = None
        self.collision_y = None
        self.dx = None
        self.dy = None

    def is_miss(self, thrower: Actor, target: Actor) -> bool:
        """return boolean indicating whether the attack is missed or not"""
        dexterity = thrower.status.changed_status["dexterity"]
        agility = target.status.changed_status["agility"]

        # Size bonus
        # increase chance of successful hits against bigger opponents, vice versa
        size_bonus = (target.actor_state.size - thrower.actor_state.size) * 0.15
        miss_constant = 10 # miss_constant: Constant. Adjust this value to handle in-game balance

        if random.random() * (1.3**dexterity + 1) * (1+size_bonus) * miss_constant / agility < 1:
            return True
        else:
            return False

    def crit_calculation(self, thrower: Actor, base_multiplier=1.5, always_critical=False) -> float:
        crit_chance = random.randint(0, 3000)
        # If critical is forced
        if always_critical:
            critical_hit = True
            crit_multiplier = base_multiplier + random.random()
            return crit_multiplier

        # else (on regular occasions)
        if crit_chance < min(thrower.status.changed_status["dexterity"] * 5 + thrower.status.changed_status["strength"], 1000):
            critical_hit = True
            crit_multiplier = base_multiplier + random.random()
        else:
            crit_multiplier = 1

        return crit_multiplier

    def damage_calculation(self, thrower: Actor, target: Actor, crit_multiplier):
        if self.parent:
            damage = self.base_throw + random.randint(0,self.additional_throw)

            temp = thrower.status.changed_status
            dexterity = temp["dexterity"]
            strength = temp["strength"]

            # Apply dexterity bonus
            dexterity_bonus = min(2, 1 + dexterity / 100)
            damage *= dexterity_bonus

            damage *= min(max(1, round(self.throw_distance(thrower) * 0.1)), 2)

            # Damage reduction
            damage = target.status.calculate_dmg_reduction(damage=damage, damage_type="physical", ignore_reduction=False)
                        
            # Crit
            damage *= crit_multiplier

            return round(damage)

    def break_calculation(self) -> None:
        """
        Calculate chance of this component's parent's destruction when the throw was successful.
        """
        if self.break_chance == 0:
            return None
        if random.random() <= self.break_chance:
            self.shattered = True
            if self.parent.item_type.value == InventoryOrder.POTION.value:
                self.engine.message_log.add_message(i(f"{g(self.parent.name, '이')} 깨졌다.",
                                                      f"{self.parent.name} is shattered."), fg=color.gray)
            else:
                self.engine.message_log.add_message(i(f"{g(self.parent.name, '이')} 파괴되었다.",
                                                      f"{self.parent.name} is destroyed."), fg=color.gray)

    def throw_distance(self, thrower: Actor):
        throw_dist_constant = 0.05

        if self.parent:
            return max(int(thrower.status.changed_status["dexterity"] * thrower.status.changed_status["strength"] * throw_dist_constant / max(0.1, self.parent.weight * self.air_friction)), 1)

    def get_action(self, thrower: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        self.engine.message_log.add_message(
            i("방향을 선택하세요.",
              f"Choose a direction."), color.help_msg
        )
        from input_handlers import RayRangedWithDistanceInputHandler
        self.engine.event_handler = RayRangedWithDistanceInputHandler(
            actor=thrower,
            max_range=self.throw_distance(thrower),
            callback=lambda xy, dist: actions.ThrowItem(thrower, self.parent, throw_range=dist, target_xy=xy),
        )
        return None

    def activate_logic(self, action: actions.ThrowItem) -> None:
        raise NotImplementedError()

    def activate(self, action: actions.ThrowItem) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        self.activate_logic(action)
        self.reset_values() # Must be called AFTER all functions are done


class NormalThrowable(Throwable):
    def effect_when_collided_with_entity(self, target: Entity, thrower: Actor):
        """
        When collided withg the entity.
        """
        if self.identify_when_collided_with_entity > 0 and self.engine.game_map.visible[target.x, target.y]:
            self.parent.item_state.identify_self(self.identify_when_collided_with_entity)


    def effect_when_collided_with_actor(self, target: Actor, thrower: Actor) -> None:
        """
        Can have additional effects when the throw was successful
        
        Target is always actor type since activate() will filter out other types of entities
        """
        self.effect_when_collided_with_entity(target, thrower)

        if self.identify_when_collided_with_actor > 0 and self.engine.game_map.visible[target.x, target.y]:
            self.parent.item_state.identify_self(self.identify_when_collided_with_actor)

        if self.trigger_if_thrown_at:
            if thrower != target:
                # Trigger target regardless of damage / lethality
                target.status.take_damage(amount=0, attacked_from=thrower)

        if self.shattered:
            self.effect_when_collided_with_actor_and_shattered(target=target, thrower=thrower)


    def effect_when_collided_with_actor_and_shattered(self, target: Actor, thrower: Actor) -> None:
        """Called when collided AND the object is shattered."""
        pass


    def collided_with_actor(self, collided, thrower):
        # Check dodged
        if self.is_miss(thrower=thrower, target=collided):
            if collided is self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 {g(self.parent.name, '을')} 피했다.",
                                                      f"You dodge {self.parent.name}."), color.player_atk_missed)
            else:
                self.engine.message_log.add_message(i(f"{g(collided.name, '이')} {g(self.parent.name, '을')} 피했다.",
                                                      f"{collided.name} dodges {self.parent.name}."), color.player_atk_missed, target=collided,)
        else:
            # set dmg
            crit_multiplier = self.crit_calculation(thrower=thrower)
            dmg = self.damage_calculation(thrower=thrower, target=collided, crit_multiplier=crit_multiplier)

            # log
            thrower_name = thrower.name
            collided_name = collided.name
            throw_fg = color.enemy_neutral

            if thrower == self.engine.player:
                thrower_name = i("당신", "you")
                throw_fg = color.player_atk
            if collided == self.engine.player:
                collided_name = i("당신", "you")
                throw_fg = color.player_melee_hit

            if dmg >= 0:
                if collided_name == "you" and thrower_name != "you":
                    self.engine.message_log.add_message(f"{thrower_name} throws {self.parent.name} at you and deal {dmg} damage.", target=thrower,fg=throw_fg)
                elif thrower_name == "you":
                    if collided_name == "you":
                        collided_name = "yourself"
                    self.engine.message_log.add_message(f"You throw {self.parent.name} at {collided_name} and deal {dmg} damage.",target=thrower,fg=throw_fg)
                else:
                    self.engine.message_log.add_message(i(f"{g(thrower_name, '이')} {g(self.parent.name, '을')} {collided_name}에게 던져 {dmg} 데미지를 입혔다.",
                                                          f"{thrower_name} throws {self.parent.name} at the {collided_name} and deals {dmg} damage."), target=thrower,fg=throw_fg)
                if dmg > 0:
                    collided.status.take_damage(amount=dmg, attacked_from=thrower) # Will not trigger the ai unless there is 1 or more damage.
            else:
                print(f"WARNING::Throwing dealt negative damage - thrower:{thrower_name}, dmg:{dmg}")

            # check destruction
            self.break_calculation()

            # apply special effects (if the target survived the initial damage)
            if not collided.actor_state.is_dead:
                self.effect_when_collided_with_actor(target=collided, thrower=thrower)


    def collided_with_semiactor(self, collided, thrower) -> bool:
        """Returns True if semiactor blocked the object, and the object dropped in front of the semiactor."""
        # check destruction
        self.break_calculation()

        if not self.shattered:
            # Open closed door if there is one
            if collided.entity_id[-11:] == "closed_door":
                if not self.shattered:
                    temp_x, temp_y = collided.x, collided.y
                    collided.remove_self()
                    import semiactor_factories
                    semiactor_factories.opened_door.spawn(self.engine.game_map, temp_x, temp_y, -1)
                # drop in front of the semiactor(NOTE: Not below the semiactor)
                return False
            else:
                return True


    def render_animation(self, path, thrower: Actor) -> Optional[List]:
        frames = []
        loc = None
        while len(path) > 0:
            loc = path.pop(0)

            # Create new graphic depending on the object that are being thrown
            throw_graphic = {"char":self.parent.char, "fg":self.parent.fg, "bg":self.parent.bg}

            # Using relative coordinates for animation rendering
            relative_x, relative_y = self.engine.camera.abs_to_rel(abs_x=loc[0], abs_y=loc[1])
            frames.append([(relative_x, relative_y, throw_graphic, None)])

        throw_animation = Animation(engine=self.engine, frames=frames, stack_frames=False, sec_per_frame=self.sec_per_frame, refresh_last_frame=False)
        throw_animation.render()
        if self.shattered:
            if self.parent.item_type.value == InventoryOrder.POTION.value:
                if thrower == self.engine.player:
                    self.engine.sound_manager.add_sound_queue("fx_shatter")
        if loc:
            return loc # Last location of the thrown item's path
        return None


    def drop_thrown_item(self, thrower, loc: Optional[List]=None):
        if not self.shattered:
            # If collided with actor, drop it on the actor's location
            if self.collision_x and self.collision_y:
                thrower.inventory.drop(item=self.parent, x=self.collision_x, y=self.collision_y, drop_count=None) # Drop all given count (usually 1)
            else:
                if loc: # if loc exists (if the object flied one or more tile)
                    thrower.inventory.drop(item=self.parent, x=loc[0], y=loc[1], drop_count=None) # Drop all given count (usually 1)
                else: # if loc doesn't exists (e.g. thrown against the wall)
                    thrower.inventory.drop(item=self.parent, x=thrower.x, y=thrower.y, drop_count=None) # Drop all given count (usually 1)
        else:# Destroyed
            self.parent.remove_self()


    def effects_when_shattered(self):
        """Effects when the item is broken. e.g. spawn fire when fire potion is broken
        NOTE: Think seperately from collided_with_entity or collided_with_actor_and_shattered functions."""
        if self.identify_when_shattered > 0 and self.engine.game_map.visible[self.shattered_x, self.shattered_y]:
            self.parent.item_state.identify_self(self.identify_when_shattered)

    def effects_when_contact_with_ground(self, thrower, loc) -> None:
        """When item reached its destination without colliding with anything and contacts the ground."""
        self.drop_thrown_item(thrower, loc)

    def activate_logic(self, action: actions.ThrowItem) -> None:
        thrower = action.entity
        target = None

        self.dx = action.target_xy[0]
        self.dy = action.target_xy[1]
        max_distance = self.throw_distance(thrower)
        if action.throw_range:
            if action.throw_range > max_distance:
                print("WARNING::ThrowItem.throw_range is too far for the actor's capabilities. Inputhandler might be the cause of it.")
            else:
                max_distance = action.throw_range

        dest_x, dest_y = thrower.x + self.dx, thrower.y + self.dy
        dist = 0
        path = []
        throw_over = False

        ### A. Main loop ###
        while not self.shattered:
            # 1. Collided with the map border
            if not self.engine.game_map.in_bounds(dest_x, dest_y):
                self.break_calculation()
                break
            # 2. Collided with a wall
            if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
                self.break_calculation()
                break
            # 3. Collided with an entity
            for collided in self.engine.game_map.get_all_blocking_entities_at_location(dest_x, dest_y):
                # 3-1. If collided with actor entity (beside thrower itself)
                if isinstance(collided, Actor):
                    self.collided_with_actor(collided=collided, thrower=thrower)
                # 3-2. If collided with semiactor entity, and the entity.block_movement is True
                if isinstance(collided, SemiActor):
                    if (self.collided_with_semiactor(collided=collided, thrower=thrower)):
                        self.collision_x = dest_x - self.dx
                        self.collision_y = dest_y - self.dy
                        break
                # Check penetration
                if self.penetration == False:
                    self.collision_x = dest_x
                    self.collision_y = dest_y
                    throw_over = True
                    break
            if throw_over:
                break

            # 4. Check range
            path.append((dest_x, dest_y))
            dest_x += self.dx
            dest_y += self.dy
            dist += 1
            if dist >= max_distance:
                break

        ### B. Render animation ###
        loc = self.render_animation(path, thrower=thrower)

        ### C. Item reached its destination ###
        self.effects_when_contact_with_ground(thrower, loc)
        
        ### D. Effects when shattered ###
        if self.shattered:
            self.shattered_x, self.shattered_y = dest_x, dest_y
            self.effects_when_shattered() # NOTE: Seperate from effects_when_collided_with_actor_and_shattered
            # throwable component is shared through the entire stack, so .shattered should be set back to False after the item was thrown
            # (So that the rest of the item stack can work properly)

        # Call is necessary
        self.reset_values()


class ShatterWhenContactGroundThrowable(NormalThrowable):
    """
    Items that COULD shatter when thrown at the ground.
    e.g. potions

    If you want to make specific throwing weapons that can break even if they just missed a target and landed on the ground such as toxic goo,
    inherit this class.
    """
    def effects_when_contact_with_ground(self, thrower, loc) -> None:
        # Check for breaking
        self.break_calculation() # NOTE: potion break guarenteed


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

class PotionQuaffAndThrowSameEffectThrowable(ShatterWhenContactGroundThrowable):
    """Potion that applies the same effect when quaffed and when thrown(collided) should use this general throwable component.
    If there is any difference between the two, you should override NormalThrowable class and make a new one."""
    def __init__(self,
                 base_throw: int=0,
                 additional_throw: int=0,
                 penetration: bool=False,
                 break_chance: float=1,
                 air_friction: int=1,
                 sec_per_frame:Optional[float]=None,
                 trigger_if_thrown_at: bool = True,
                 identify_when_shattered: int = 0,
                 identify_when_collided_with_actor: int = 0,
                 identify_when_collided_with_entity: int = 0
                 ):
        super().__init__(base_throw, additional_throw, penetration, break_chance, air_friction, sec_per_frame, trigger_if_thrown_at, identify_when_shattered, identify_when_collided_with_actor, identify_when_collided_with_entity)

    def effect_when_collided_with_actor_and_shattered(self, target: Actor, thrower: Actor) -> None:
        super().effect_when_collided_with_actor_and_shattered(target, thrower)
        if hasattr(self.parent, "quaffable"):
            self.parent.quaffable.apply_effect(apply_to=target)
        else:
            print(f"WARNING::{self.parent.entity_id} has no quaffable but is using potion throwable.")


class PotionOfFlameThrowable(PotionQuaffAndThrowSameEffectThrowable):
    """Additional freezing tile effect."""
    def effects_when_shattered(self):
        super().effects_when_shattered()
        import semiactor_factories
        from util import spawn_entity_8way
        tmp = semiactor_factories.fire.copy(self.engine.game_map, exact_copy=False, lifetime=self.parent.quaffable.fire_lifetime)
        tmp.rule.base_damage = int(self.parent.quaffable.base_dmg / 2)
        tmp.rule.add_damage = int(self.parent.quaffable.add_dmg / 2)
        spawn_entity_8way(entity=tmp, gamemap=self.engine.game_map, center_x=self.shattered_x-self.dx, center_y=self.shattered_y-self.dy, spawn_cnt=8, spawn_on_center=True)
        if self.engine.game_map.visible[self.shattered_x, self.shattered_y]:
            self.engine.message_log.add_message(i(f"{self.parent.name}이 깨진 자리에서 불꽃이 피어났다!",
                                                  f"Flames start to rise!"),color.player_sense)
            self.parent.item_state.identify_self(self.identify_when_shattered)


class PotionOfFrostThrowable(PotionQuaffAndThrowSameEffectThrowable):
    """Additional freezing tile effect."""
    def effects_when_shattered(self):
        super().effects_when_shattered()
        for dx in (1, 0, -1):
            for dy in (1, 0, -1):
                self.engine.game_map.tiles[self.shattered_x-self.dx+dx, self.shattered_y-self.dy+dy] = TileUtil.freeze(self.engine.game_map.tiles[self.shattered_x-self.dx+dx, self.shattered_y-self.dy+dy])


class PotionOfLiquifiedAntsThrowable(ShatterWhenContactGroundThrowable):
    def effects_when_shattered(self):
        super().effects_when_shattered()
        # Spawn 8 ants maximum surrounding the consumer.
        from actor_factories import ant
        from util import spawn_entity_8way
        spawn = ant
        spawn_cnt = random.randint(5,8)
        if self.parent.item_state.BUC == 1:
            spawn_cnt = 8
        actors = spawn_entity_8way(entity=spawn, gamemap=self.engine.game_map, center_x=self.shattered_x - self.dx, center_y=self.shattered_y - self.dy, spawn_cnt=spawn_cnt, spawn_on_center=True)
        for actor in actors:
            trigger_actor = self.engine.game_map.get_actor_at_location(x=self.collision_x, y=self.collision_y)
            actor.status.take_damage(amount=0, attacked_from=trigger_actor) # Trigger ants

        if self.engine.game_map.visible[self.shattered_x, self.shattered_y]:
            self.engine.message_log.add_message(i(f"{self.parent.name}이 깨진 자리에서 {g(spawn.name, '이')} 생겨났다!",
                                                  f"{spawn.name} spawns!."),color.player_sense)
            self.parent.item_state.identify_self(self.identify_when_shattered)


class ToxicGooThrowable(ShatterWhenContactGroundThrowable):
    def effect_when_collided_with_actor(self, target: Actor, thrower: Actor) -> None:
        super().effect_when_collided_with_actor(target, thrower)
        if target.actor_state.is_poisoned == [0,0,0,0]:
            # Log
            self.engine.message_log.add_message(i(f"{g(target.name, '은')} 독성 점액에 뒤덮였다.",
                                                  f"{target.name} is covered with toxic goo."), color.white, target=target)

            # Poison
            target.actor_state.apply_poisoning([1, 1, 0, 3])

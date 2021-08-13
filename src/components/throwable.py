from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING
from animation import Animation
from components.base_component import BaseComponent
from korean import grammar as g
from tiles import TileUtil
from entity import Actor, SemiActor, Entity

import actions
import color
import random


class Throwable(BaseComponent):

    def __init__(self, base_throw: int=0, additional_throw: int=0, penetration: bool=False, break_chance: float=0, air_friction: float=1, sec_per_frame:float=0.025, trigger_if_thrown_at: bool = False):
        super().__init__(None)
        self.penetration = penetration
        self.break_chance = break_chance # 0~1
        self.air_friction = air_friction
        self.base_throw = base_throw
        self.additional_throw = additional_throw
        self.sec_per_frame = sec_per_frame
        self.shattered = False # if True, item can be destroyed after being thrown (depending on the break_chance)
        self.trigger_if_thrown_at = trigger_if_thrown_at
        self.shattered_x = None
        self.shattered_y = None
        self.collision_x = None # Set this value When collided with a monster, and when this throwable's penetrate == False. When collided with a wall, this value remains None.
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

    def damage_calculation(self, target: Actor, crit_multiplier):
        if self.parent:
            damage = self.base_throw + random.randint(0,self.additional_throw)

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

    def throw_distance(self, thrower: Actor):
        throw_dist_constant = 0.05

        if self.parent:
            return max(int(thrower.status.changed_status["dexterity"] * thrower.status.changed_status["strength"] * throw_dist_constant / max(0.1, self.parent.weight * self.air_friction)), 1)

    def get_action(self, thrower: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        self.engine.message_log.add_message(
            "방향을 선택하세요.", color.help_msg
        )
        from input_handlers import RayRangedInputHandler
        self.engine.event_handler = RayRangedInputHandler(
            actor=thrower,
            max_range=self.throw_distance(thrower),
            callback=lambda xy: actions.ThrowItem(thrower, self.parent, xy),
        )
        return None

    def activate(self, action: actions.ThrowItem) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()


class NormalThrowable(Throwable):
    def effect_when_collided_with_entity(self, target: Entity, thrower: Actor):
        """
        When collided withg the entity.
        """
        pass

    def effect_when_collided_with_actor(self, target: Actor, thrower: Actor, trigger: bool=False) -> None:
        """
        Can have additional effects when the throw was successful
        
        Target is always actor type since activate() will filter out other types of entities
        
        Args:
            trigger:
                if True, target/collided actor will consider the throw as an attack.
        """
        self.effect_when_collided_with_entity(target, thrower)

        if trigger:
            # Trigger target regardless of damage / lethality
            target.status.take_damage(amount=0, attacked_from=thrower)

    def collided_with_thrower(self, thrower, target):
        # set dmg (NOTE: Self-firing is undodgeable)
        crit_multiplier = self.crit_calculation(thrower=thrower)
        dmg = self.damage_calculation(target=thrower, crit_multiplier=crit_multiplier)

        if dmg > 0:
            self.engine.message_log.add_message(f"{g(thrower.name, '이')} {g(self.parent.name, '을')} 자신에게 던져 {dmg} 데미지를 입혔다!", target=thrower,)
        else:
            self.engine.message_log.add_message(f"{g(thrower.name, '이')} {g(self.parent.name, '을')} 자신에게 던졌다!", target=thrower,)
        thrower.status.take_damage(amount=self.damage) # cannot trigger itself

        # apply special effects (if the thrower survived the initial damage)
        if not target.actor_state.is_dead:
            self.effect_when_collided_with_actor(target=thrower)

        # check destruction
        self.break_calculation()
        
        # actual destruction / item dropping
        if not self.shattered:
            thrower.inventory.throw(item=self.parent, x=thrower.x, y=thrower.y, show_msg=False)
        else:
            from order import InventoryOrder
            if self.parent.item_type == InventoryOrder.POTION:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 깨졌다.", fg=color.gray, target=thrower)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 파괴되었다.", fg=color.gray, target=thrower)
            self.parent.parent.decrease_item_stack(self.parent, remove_count=1)

    def collided_with_actor(self, collided, thrower):
        # Check dodged
        if self.is_miss(thrower=thrower, target=collided):
            if collided is self.engine.player:
                self.engine.message_log.add_message(f"당신은 {g(self.parent.name, '을')} 피했다.", color.player_atk_missed)
            else:
                self.engine.message_log.add_message(f"{g(collided.name, '이')} {g(self.parent.name, '을')} 피했다.", color.player_atk_missed, target=collided,)
        else:
            # set dmg
            crit_multiplier = self.crit_calculation(thrower=thrower)
            dmg = self.damage_calculation(target=collided, crit_multiplier=crit_multiplier)

            # log
            if dmg > 0:
                self.engine.message_log.add_message(f"{g(thrower.name, '이')} {g(self.parent.name, '을')} {collided.name}에게 던져 {dmg} 데미지를 입혔다.", target=thrower,)
                collided.status.take_damage(amount=dmg, attacked_from=thrower)

            # apply special effects (if the target survived the initial damage)
            if not collided.actor_state.is_dead:
                self.effect_when_collided_with_actor(target=collided, thrower=thrower, trigger=self.trigger_if_thrown_at)

            # check destruction
            self.break_calculation()

    def collided_with_semiactor(self, collided, thrower) -> bool:
        """Returns True if semiactor blocked the object, and the object dropped in front of the semiactor."""
        # check destruction
        self.break_calculation()

        if not self.shattered:
            # Open closed door if there is one
            if collided.entity_id == "closed_door":
                if not self.shattered:
                    temp_x, temp_y = collided.x, collided.y
                    collided.remove_self()
                    import semiactor_factories
                    semiactor_factories.opened_door.spawn(self.engine.game_map, temp_x, temp_y, -1)
                # drop in front of the semiactor(NOTE: Not below the semiactor)
                return False
            else:
                return True

    def render_animation(self, path) -> Optional[List]:
        frames = []
        loc = None
        while len(path) > 0:
            loc = path.pop(0)

            # Create new graphic depending on the object that are being thrown
            throw_graphic = {"char":self.parent.char, "fg":self.parent.fg, "bg":self.parent.bg}

            # Using relative coordinates for animation rendering
            relative_x, relative_y = self.engine.camera.abs_to_rel(abs_x=loc[0], abs_y=loc[1])
            frames.append([(relative_x, relative_y, throw_graphic, None)])

        throw_animation = Animation(engine=self.engine, frames=frames, stack_frames=False, sec_per_frame=self.sec_per_frame, refresh_last_frame=False) # TODO : air resistance의 값에 따라 프레임당 소요시간 변경??
        throw_animation.render()
        if loc:
            return loc # Last location of the thrown item's path
        return None

    def drop_thrown_item(self, thrower, loc: Optional[List]=None):
        if not self.shattered:
            # If collided with actor, drop it on the actor's location
            if self.collision_x and self.collision_y:
                thrower.inventory.throw(item=self.parent, x=self.collision_x, y=self.collision_y, show_msg=False)
            else:
                if loc: # if loc exists (if the object flied one or more tile)
                    thrower.inventory.throw(item=self.parent, x=loc[0], y=loc[1], show_msg=False)
                else: # if loc doesn't exists (e.g. thrown against the wall)
                    thrower.inventory.throw(item=self.parent, x=thrower.x, y=thrower.y, show_msg=False)
        else:# Destroyed
            from order import InventoryOrder
            if self.parent.item_type == InventoryOrder.POTION:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 깨졌다.", fg=color.gray, target=thrower)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 파괴되었다.", fg=color.gray, target=thrower)
            self.parent.parent.decrease_item_stack(self.parent, remove_count=1)

    def effects_when_shattered(self):
        """Effects when the item is broken. e.g. spawn fire when fire potion is broken
        NOTE: Think seperately from collided_with_entity functions."""
        pass

    def activate(self, action: actions.ThrowItem) -> None:
        thrower = action.entity
        target = None

        self.dx = action.target_xy[0]
        self.dy = action.target_xy[1]
        dest_x, dest_y = thrower.x + self.dx, thrower.y + self.dy
        dist = 0
        path = []

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
                # 3-1. If collided with the thrower itself #NOTE TODO: Further debugging required
                if collided == thrower:
                    self.collided_with_thrower(target=target, thrower=thrower)
                    return None
                # 3-2. If collided with actor entity (beside thrower itself)
                if isinstance(collided, Actor):
                    self.collided_with_actor(collided=collided, thrower=thrower)
                # 3-3. If collided with semiactor entity, and the entity.block_movement is True
                if isinstance(collided, SemiActor):
                    if (self.collided_with_semiactor(collided=collided, thrower=thrower)):
                        self.collision_x = dest_x - self.dx
                        self.collision_y = dest_y - self.dy
                        break
                # Check penetration
                if self.penetration == False:
                    self.collision_x = dest_x
                    self.collision_y = dest_y
                    break
            # 4. Check range
            path.append((dest_x, dest_y))
            dest_x += self.dx
            dest_y += self.dy
            dist += 1
            if dist >= self.throw_distance(thrower=thrower):
                break

        ### B. Render animation ###
        loc = self.render_animation(path)

        ### C. Drop Item ###
        self.drop_thrown_item(thrower, loc)
        
        ### D. Effects when shattered ###
        if self.shattered:
            self.shattered_x, self.shattered_y = dest_x, dest_y
            self.effects_when_shattered()
            # throwable component is shared through the entire stack, so .shattered should be set back to False after the item was thrown
            # (So that the rest of the item stack can work properly)
            self.shattered = False



###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

class PotionQuaffAndThrowSameEffectThrowable(NormalThrowable):
    """Potion that applies the same effect when quaffed and when thrown(collided) should use this general throwable component.
    If there is any difference between the two, you should override NormalThrowable class and make a new one."""
    def __init__(self, base_throw: int=4, additional_throw: int=1, penetration: bool=False, break_chance: float=1, air_friction: int=1, sec_per_frame:float=0.025, trigger_if_thrown_at: bool = True):
        super().__init__(base_throw, additional_throw, penetration, break_chance, air_friction, sec_per_frame, trigger_if_thrown_at)

    def effect_when_collided_with_actor(self, target: Actor, thrower: Actor, trigger: bool) -> None:
        super().effect_when_collided_with_actor(target, thrower, trigger)
        if hasattr(self.parent, "quaffable"):
            self.parent.quaffable.apply_effect(apply_to=target)
        else:
            print(f"WARNING::{self.parent.entity_id} has no quaffable but is using potion throwable.")


class PotionOfFlameThrowable(NormalThrowable):
    """Additional freezing tile effect."""
    def effects_when_shattered(self):
        import semiactor_factories
        from util import spawn_entity_8way
        tmp = semiactor_factories.fire.copy(self.engine.game_map, lifetime=self.parent.quaffable.fire_lifetime)
        tmp.rule.base_damage = int(self.parent.quaffable.base_dmg / 2)
        tmp.rule.add_damage = int(self.parent.quaffable.add_dmg / 2)
        spawn_entity_8way(entity=tmp, gamemap=self.engine.game_map, center_x=self.shattered_x-self.dx, center_y=self.shattered_y-self.dy, spawn_cnt=8, spawn_on_center=True)


class PotionOfFrostThrowable(PotionQuaffAndThrowSameEffectThrowable):
    """Additional freezing tile effect."""
    def effects_when_shattered(self):
        for dx in (1, 0, -1):
            for dy in (1, 0, -1):
                self.engine.game_map.tiles[self.shattered_x-self.dx+dx, self.shattered_y-self.dy+dy] = TileUtil.freeze(self.engine.game_map.tiles[self.shattered_x-self.dx+dx, self.shattered_y-self.dy+dy])


class PotionOfLiquifiedAntsThrowable(NormalThrowable):
    def effects_when_shattered(self):
        # Spawn 8 ants maximum surrounding the consumer.
        from actor_factories import ant
        from util import spawn_entity_8way
        spawn = ant
        spawn_entity_8way(entity=spawn, gamemap=self.engine.game_map, center_x=self.shattered_x - self.dx, center_y=self.shattered_y - self.dy, spawn_cnt=random.randint(5,8), spawn_on_center=True)

        if self.engine.game_map.visible[self.shattered_x, self.shattered_y]:
            self.engine.message_log.add_message(f"{self.parent.name}이 깨진 자리에서 {spawn.name}들이 생겨났다!",color.player_sense)
            self.parent.item_state.identify_self(identify_level=1)
            self.engine.message_log.add_message(f"당신은 {self.parent.name}의 존재를 알게 되었다.",
                                                color.player_neutral_important)


class ToxicGooThrowable(NormalThrowable):
    def __init__(self, base_throw: int=4, additional_throw: int=1, penetration: bool=False, break_chance: float=1, air_friction: int=1, sec_per_frame:float=0.025, trigger_if_thrown_at: bool = True):
        super().__init__(base_throw, additional_throw, penetration, break_chance, air_friction, sec_per_frame, trigger_if_thrown_at)
    
    def effect_when_collided_with_actor(self, target: Actor, thrower: Actor, trigger: bool) -> None:
        super().effect_when_collided_with_actor(target, thrower, trigger)
        if target.actor_state.is_poisoned == [0,0,0,0]:
            # Log
            self.engine.message_log.add_message(f"{g(target.name, '은')} 독성 점액에 뒤덮였다.", color.white, target=target)

            # Poison
            target.actor_state.apply_poisoning([1, 1, 0, 3])

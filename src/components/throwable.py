from __future__ import annotations

from typing import Optional
from animation import Animation
from components.base_component import BaseComponent
from entity import Actor, SemiActor
from input_handlers import RayRangedInputHandler
from korean import grammar as g

import semiactor_factories
import actions
import color
import random


class Throwable(BaseComponent):

    def __init__(self, base_throw: int=0, additional_throw: int=0, penetration: bool=False, break_chance: float=0, air_friction: int=1, sec_per_frame:float=0.025):
        self.parent = None # parent is intialized later
        self.penetration = penetration
        self.break_chance = break_chance # 0~1
        self.air_friction = air_friction
        self.base_throw = base_throw
        self.additional_throw = additional_throw
        self.sec_per_frame = sec_per_frame
        self.shattered = False # if True, item can be destroyed after being thrown (depending on the break_chance)

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

    def break_calculation(self):
        """
        Calculate chance of this component's parent's destruction when the throw was successful.
        """
        # indestrutible object
        if self.break_chance == 0:
            return None

        if random.random() <= self.break_chance:
            # Destroy object (The actual destruction of object is handled somewhere else)
            self.shattered = True
                
    def throw_distance(self, thrower: Actor):
        throw_dist_constant = 0.05

        if self.parent:
            return max(int(thrower.status.changed_status["dexterity"] * thrower.status.changed_status["strength"] * throw_dist_constant / max(0.1, self.parent.weight * self.air_friction)), 1)

    def get_action(self, thrower: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        self.engine.message_log.add_message(
            "방향을 선택하세요.", color.needs_target
        )
        self.engine.event_handler = RayRangedInputHandler(
            self.engine,
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

    def effect_when_collided_with_actor(self, target: Actor) -> None:
        """
        Can have additional effects when the throw was successful
        
        Target is always actor type since activate() will filter out other types of entities
        """
        pass

    def activate(self, action: actions.ThrowItem) -> None:
        thrower = action.entity
        target = None
        
        dx = action.target_xy[0]
        dy = action.target_xy[1]
        dest_x, dest_y = thrower.x + dx, thrower.y + dy

        dist = 0

        collision_x = None # Set this value When collided with a monster, and when this throwable's penetrate == False. When collided with a wall, this value remains None.
        collision_y = None

        path = []
        targets = []

        ### A. Main loop ###
        while not self.shattered:

            # 1. Collided with the map border
            if not self.engine.game_map.in_bounds(dest_x, dest_y):
                # Destination is out of bounds.
                self.break_calculation()
                break

            # 2. Collided with a wall
            if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
                # Destination is blocked by a tile.
                self.break_calculation()
                break

            # 3. Collided with an entity
            collided = self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)

            if collided:
                # 3-1. If collided with the thrower itself #NOTE TODO: Further debugging required
                if collided == thrower:
                    # set dmg (NOTE: Self-firing is undodgeable)
                    crit_multiplier = self.crit_calculation(thrower=thrower)
                    dmg = self.damage_calculation(target=thrower, crit_multiplier=crit_multiplier)

                    if dmg > 0:
                        self.engine.message_log.add_message(f"{g(thrower.name, '이')} {g(self.parent.name, '을')} 자신에게 던져 {dmg} 데미지를 입혔다!", target=thrower,)
                    else:
                        self.engine.message_log.add_message(f"{g(thrower.name, '이')} {g(self.parent.name, '을')} 자신에게 던졌다!", target=thrower,)
                    thrower.status.take_damage(amount=self.damage) # cannot trigger itself

                    # apply special effects (if the thrower survived the initial damage)
                    if not collided.actor_state.is_dead:
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
                        self.parent.parent.remove_item(self.parent, remove_count=1)

                    return 0

                # 3-2. If collided with actor entity (beside thrower itself)
                if isinstance(collided, Actor):
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
                            self.effect_when_collided_with_actor(target=collided)

                        # check destruction
                        self.break_calculation()
                
                # 3-3. If collided with semiactor entity, and the entity.block_movement is True
                if isinstance(collided, SemiActor):
                    # check destruction
                    self.break_calculation()

                    if not self.shattered:
                        # Open closed door if there is one
                        if collided.entity_id == "closed_door":
                            if not self.shattered:
                                temp_x, temp_y = collided.x, collided.y
                                collided.remove_self()
                                semiactor_factories.opened_door.spawn(self.engine.game_map, temp_x, temp_y, -1)
                        # drop in front of the semiactor(NOTE: Not below the semiactor)
                        else:
                            collision_x = dest_x - dx
                            collision_y = dest_y - dy
                            break

                # Check penetration
                if self.penetration == False:
                    collision_x = dest_x
                    collision_y = dest_y
                    break

            # 4. Check range
            path.append((dest_x, dest_y))
            dest_x += dx
            dest_y += dy
            
            dist += 1
            if dist >= self.throw_distance(thrower=thrower):
                break

        ### B. Render animation ###
        frames = []
        while len(path) > 0:
            loc = path.pop(0)

            # Create new graphic depending on the object that are being thrown
            throw_graphic = {"char":self.parent.char, "fg":self.parent.fg, "bg":self.parent.bg}

            # Using relative coordinates for animation rendering
            relative_x, relative_y = self.engine.camera.get_relative_coordinate(abs_x=loc[0], abs_y=loc[1])
            frames.append([(relative_x, relative_y, throw_graphic, None)])

        throw_animation = Animation(engine=self.engine, frames=frames, stack_frames=False, sec_per_frame=self.sec_per_frame, refresh_last_frame=False) # TODO : air resistance의 값에 따라 프레임당 소요시간 변경??
        throw_animation.render()

        ### C. Drop Item ###
        if not self.shattered:
            # If collided with actor, drop it on the actor's location
            if collision_x and collision_y:
                thrower.inventory.throw(item=self.parent, x=collision_x, y=collision_y, show_msg=False)
            else:
                try: # if loc exists (if the object flied one or more tile)
                    thrower.inventory.throw(item=self.parent, x=loc[0], y=loc[1], show_msg=False)
                except: # if loc doesn't exists (e.g. thrown against the wall)
                    thrower.inventory.throw(item=self.parent, x=thrower.x, y=thrower.y, show_msg=False)
        else:# Destroyed
            from order import InventoryOrder
            if self.parent.item_type == InventoryOrder.POTION:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 깨졌다.", fg=color.gray, target=thrower)
            else:
                self.engine.message_log.add_message(f"{g(self.parent.name, '이')} 파괴되었다.", fg=color.gray, target=thrower)
            self.parent.parent.remove_item(self.parent, remove_count=1)

            # throwable component is shared through the entire stack, so .shattered should be set back to False after the item was thrown
            # (So that the rest of the item stack can work properly)
            self.shattered = False


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

class PotionOfParalysisThrowable(NormalThrowable):
    
    def effect_when_collided_with_actor(self, target: Actor):
        if target.actor_state.is_paralyzing == [0,0]: # When the target wasn't paralyzed before

            # Log
            if target == self.engine.player:
                self.engine.message_log.add_message(f"당신은 갑자기 몸을 움직일 수가 없게 되었다!",color.player_damaged,)
            else:
                if self.engine.game_map.visible[target.x, target.y]:
                    self.engine.message_log.add_message(f"{g(target.name, '이')} 갑자기 모든 움직임을 멈추었다.", color.white, target=target)

            # Paralyze
            target.actor_state.is_paralyzing = [0, self.parent.quaffable.turn]
        else: # When the target was paralyzed before

            # Log
            if target == self.engine.player:
                self.engine.message_log.add_message(f"당신의 몸이 더 뻣뻣해졌다!",color.player_damaged,)

            # If paralyzation is permanent, (is_paralyzing[0] is set to negative) prevent overwriting the turn left
            target.actor_state.is_paralyzing = [min(target.actor_state.is_paralyzing[0], 0), max(target.actor_state.is_paralyzing[1], self.parent.quaffable.turn)]
            

class AcidGooThrowable(NormalThrowable):
    
    def effect_when_collided_with_actor(self, target: Actor):
        if target.actor_state.is_melting == [0,0,0,0]:
            # Log
            self.engine.message_log.add_message(f"{g(target.name, '은')} 산성 점액에 뒤덮였다.", color.white, target=target)

            # Poison
            target.actor_state.is_melting = [4, 1, 0, 4]

from __future__ import annotations
from typing import List, Optional
from tcod.map import compute_fov
from entity import Entity, Actor, Item
from util import get_distance
from korean import grammar as g
from actions import Action

import anim_graphics
import color
import util
import copy

class RadiusAction(Action):
    """
    Handles action that occurs within certain radius.
    """
    def __init__(self, entity: Entity, affect_items: bool, affect_actors: bool, radius: int=1):
        super().__init__(entity)
        self.tiles = []
        self.target_actors = []
        self.target_items = []
        self.radius = radius
        self.affect_items = affect_items
        self.affect_actors = affect_actors

    def get_items(self, x: int, y: int) -> Optional[List[Item]]:
        """
        Return all items at the given location.
        """
        return self.engine.game_map.get_all_items_at_location(x, y)

    def get_actor(self, x: int, y: int) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(x, y)

    def get_tiles(self, radius: int) -> None:
        self.tiles = util.calc_circle(self.engine, self.entity.x, self.entity.y, radius, fat_circles=True)

    def get_target_actors(self) -> None:
        for xy in self.tiles:
            target = self.get_actor(x=xy[0], y=xy[1])
            if target:
                self.target_actors.append(target)

    def get_target_items(self) -> None:
        for xy in self.tiles:
            target = self.get_items(xy[0], xy[1])
            if target:
                self.target_items += target
    
    def actor_in_radius_action(self, actor: Actor):
        raise NotImplementedError()
    
    def item_in_radius_action(self, item: Item):
        raise NotImplementedError()

    def tile_in_radius_action(self, x, y):
        pass

    def perform(self):
        self.get_tiles(self.radius, penetrate_wall=False, only_in_sight=False)

        if self.affect_actors:
            self.get_target_actors()
            for actor in self.target_actors:
                self.actor_in_radius_action(actor)
        if self.affect_items:
            self.get_target_items()
            for item in self.target_items:
                self.item_in_radius_action(item)
    
        for tile in self.tiles:
            self.tile_in_radius_action(tile[0], tile[1])


class ExplodeAction(RadiusAction):
    def __init__(
        self, 
        entity: Entity, 
        affect_items: bool, 
        affect_actors: bool,
        radius: int=1,
        graphic_function: dict = anim_graphics.explosion,
        explosion_speed: int=1,
        expl_dmg: int=0,
        dmg_reduction_by_dist: int=1,
        growing_expl_anim: bool = True,
        expl_anim_frame_len: float = None, # if None, the game chooses the optimal value
        cause_fire: int = 0,
        ):
        """
        Args:
            growing_expl_anim:
                whether the explosion animation starts from 1x1 cube and continue to grow,
                or the animation keeps its static shape.
            cause_fire:
                integer. turns of fire's lifetime that are being spawned in the given radius.
                0 means there will be no fire.
            explosion_speed:
                distance explosion travel per traversal.
                (explosion will travel as much as possible for single turn.)
        """
        super().__init__(entity, affect_items, affect_actors, radius)
        self.explosion_speed = explosion_speed
        self.graphic_function = graphic_function
        self.expl_dmg = expl_dmg
        self.dmg_reduction_by_dist = dmg_reduction_by_dist
        self.growing_expl_anim = growing_expl_anim
        if expl_anim_frame_len:
            self.expl_anim_frame_len = expl_anim_frame_len
        else:
            self.expl_anim_frame_len = 0.25 / radius
        self.cause_fire = cause_fire

    def get_tiles(self, radius: int, penetrate_wall: bool, only_in_sight: bool) -> None:
        # Overriden
        self.tiles = util.calc_explosion(self.engine, self.entity.x, self.entity.y, fat_circles=True, radius=radius, penetrate_wall=penetrate_wall, only_in_sight=only_in_sight)

    def real_dmg(self, dist: int) -> int:
        """
        Calculate damage falloff by distance and return the damage.
        NOTE: damage reduction by the actor has not been applied
        """
        return max(0, self.expl_dmg - self.dmg_reduction_by_dist * dist)

    def actor_in_radius_action(self, actor: Actor):
        distance = get_distance(self.entity.x, self.entity.y, actor.x, actor.y)
        dmg = actor.status.calculate_dmg_reduction(self.real_dmg(dist=distance), "explosion")
        if actor == self.engine.player:
            self.engine.message_log.add_message(f"당신은 폭발로부터 {dmg} 데미지를 받았다.", color.player_bad)
        else:
            self.engine.message_log.add_message(f"{g(actor.name, '이')} 폭발로부터 {dmg} 데미지를 받았다.", color.yellow, target=actor)
        actor.status.take_damage(dmg)

    def item_in_radius_action(self, item: Item):
        item.collided_with_fire()

    def tile_in_radius_action(self, x, y):
        from semiactor_factories import fire
        if self.cause_fire > 0:
            fire.spawn(self.entity.gamemap, x, y, self.cause_fire)

        pass #NOTE: Can do additional things here

    def animation(self):
        from animation import Animation
        # Animation
        frames = []
        curr_radius = 0
        while curr_radius <= self.radius:
            frame = []
            self.get_tiles(radius=curr_radius, penetrate_wall=False, only_in_sight=True)
            path = self.tiles
            while len(path):
                loc = path.pop(0)

                # Using relative coordinates for rendering animations
                relative_x, relative_y = self.engine.camera.abs_to_rel(abs_x=loc[0], abs_y=loc[1])
                frame.append((relative_x, relative_y, self.graphic_function(), None))

            if frame:
                frames.append(frame)
            
            curr_radius += 1

        # instantiate animation and render it
        ray_animation = Animation(engine=self.engine, frames=frames, stack_frames=True, sec_per_frame=self.expl_anim_frame_len)
        ray_animation.render()

    def perform(self):
        self.animation()
        super().perform()


class AcidExplodeAction(ExplodeAction):
    def __init__(
        self, 
        entity: Entity, 
        affect_items: bool, 
        affect_actors: bool,
        radius: int=1,
        graphic_function: dict = anim_graphics.acid_explosion,
        explosion_speed: int=1,
        expl_dmg: int=0,
        dmg_reduction_by_dist: int=1,
        growing_expl_anim: bool = True,
        expl_anim_frame_len: float = None, # if None, the game chooses the optimal value
        cause_fire: int = 0,
        acid: List(int, int, int, int) = [8, 2, 0, 6]
    ):
        super().__init__(
            entity, 
            affect_items, 
            affect_actors, 
            radius, 
            graphic_function, 
            explosion_speed, 
            expl_dmg, 
            dmg_reduction_by_dist, 
            growing_expl_anim, 
            expl_anim_frame_len, 
            cause_fire
            )
        self.acid = acid

    def actor_in_radius_action(self, actor: Actor):
        super().actor_in_radius_action(actor)
        actor.actor_state.apply_melting(self.acid)



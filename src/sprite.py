from typing import Tuple, Optional, TYPE_CHECKING
import pygame
import copy

class GameSprite():
    """A general sprite object used for every tile-based graphics in the game.
    This includes every entities, tiles, and visual objects.
    NOTE: a tile object could have multiple sprites.
     e.g. burnt sprite, dark sprite, bright sprite, etc.
     an Actor can only have one Skin at a time, but can have multiple different sprites.
     e.g. walking sprite, idle sprite, death sprite etc."""
    engine = None  # initialized during engine.adjustments_before_game

    def __init__(self,
                 sprite_category: str,
                 sprite_id: str,
                 is_animating: bool,
                 frame_len: int = 1,
                 easing: str = "linear", #TODO
                 ):
        """
        Args:
            sprite_category:
                General id of this sprite object.
                e.g. actors/large_cat, actors/dwarf_lord, tiles/dense_grass, etc.
            sprite_id:
                Specific id of this sprite object. Each sprites should have different ids.
                e.g. "shroud/light_default" etc.
            frame_len:
                total count of frames of this sprite.
                Set to 1 if its static and has no animation.
                NOTE: a length starts counting from 1.
                Thus, a static sprite has length of 1.
                NOTE: a image file should ALWAYS contain their frame number after their name.
                This rule also applies to static sprite images.
                e.g. floating_eye_dead1.png
            easing:
                animation easing.
                default is set to linear.
                Can have one of the following:
                    "linear"
                    TODO
        Vars:
            is_animating:
                Whether this sprite is CURRENTLY being animated or not.
                Even sprites with multiple images can have this value as false if they are currently not animating(moving).
        """
        self.sprite_category = sprite_category
        self.sprite_id = sprite_id
        self.is_animating = is_animating
        self.frame_len = frame_len
        self.tick = 0.0 # indicates current animation status
        self.images = []
        for n in range(1,frame_len+1):# Auto-adding sprites
            try:
                self.images.append(pygame.image.load(f"./resources/sprites/{sprite_category}/{sprite_id}/{str(n)}.png"))
            except FileNotFoundError:
                print(f"ERROR::Cannot find ./resources/sprites/{sprite_category}/{sprite_id}/{str(n)}.png")

    @property
    def curr_frame(self):
        tmp = int((self.frame_len) * self.tick)
        if tmp > self.frame_len - 1:
            print("ERROR::SPRITE.CURR_FRAME >= SPRITE.FRAME_LEN")
            return self.frame_len - 1
        return tmp

    @property
    def curr_img(self):
        return self.images[self.curr_frame]

    @property
    def screen(self):
        return GameSprite.engine.screen

    def __deepcopy__(self, memo):
        # deepcopy rest
        new_obj = GameSprite(self.sprite_category, self.sprite_id, self.is_animating)
        for name, attr in self.__dict__.items():
            if name == "images":
                new_images = list()
                for img in self.images:
                    new_images.append(img.copy())
                new_obj.__dict__[name] = new_images
            elif name == "engine":
                new_obj.__dict__[name] = copy.copy(GameSprite.engine)
            else:
                new_obj.__dict__[name] = copy.deepcopy(attr)

        return new_obj

    def set_tick(self, tick: float) -> None:
        self.tick = tick

    def update(self, speed) -> None:
        """Update tick, and update this sprite"""
        if self.is_animating:
            self.tick += speed
            if self.tick > 1:
                self.tick -= 1
        try:
            self.image = self.images[self.curr_frame]
        except:
            pass
        return None

    def render(self, screen: pygame.Surface, xy: Tuple[int,int]) -> None:
        """Render curr_frame sprite to engine.screen.
        NOTE: Scaling is not applied."""
        self.screen.blit(source=self.curr_img, dest=(xy[0], xy[1]))

    def render_frame(self, xy: Tuple[int,int], frame: int) -> None:
        if frame >= self.frame_len:
            raise Exception("ERROR::Tried to render sprite with invalid frame number")
        self.screen.blit(source=self.images[frame], dest=xy)


class TileSprite(GameSprite):
    def __init__(self,
                 sprite_category: str,
                 sprite_id: str,
                 is_animating: bool,
                 frame_len: int = 1,
                 sprite_zoom_ratio: float = 1,
                 easing: str = "linear",
                 ):
        super().__init__(sprite_category, sprite_id, is_animating, frame_len, easing)


class ActorSprite(GameSprite):
    def __init__(self,
                 sprite_category: str,
                 sprite_id: str,
                 is_animating: bool,
                 frame_len: int = 1,
                 sprite_zoom_ratio: float = 1,
                 easing: str = "linear",
                 ):
        super().__init__(sprite_category, sprite_id, is_animating, frame_len, easing)

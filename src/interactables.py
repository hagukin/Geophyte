from __future__ import annotations
from typing import Tuple, Dict
from pygame.sprite import Sprite
import pygame

class MouseInteractable(Sprite):
    """ A sprite object that is interactable with mouse. """

    def __init__(self,
        center: Tuple[int, int],
        images: Dict,
        custom_rect: pygame.rect.Rect = None,
        mouse_down_return: str = None,
        mouse_up_return: str = None
        ):
        """
        Args:
            center:
                x, y coordinates of this object on the screen.
            images:
                a dictionary that has a pygame Surfaces which are used for this sprite object.
                the input must have images["default"] as a key. 
                NOTE: images["default"] can be set to None if the object is invisible.
                Or it can be set to transparent box if the object is invisible, but interactable.
                e.g. images["default"] has a representative image for this object.
                NOTE: All images inside self.images dictionary must have same center position.

                NOTE: "default" for default image, "mouse_on" for images when mouse cursor is on
        Vars:
            custom_rect:
                pygame.Rect object.
                custom event area for this interactable object.
                Any other event area will be ignored.


        NOTE: Each images can have different event area.
        You can get the event area of a image(Surface) by image.get_rect() method.
        pygame.Surface.get_rect() -> returns pygame.Rect object
        """
        super().__init__()
        self.center = center
        self.mouse_on = False
        self.images = images
        self.custom_rect = custom_rect
        self.mouse_down_return = mouse_down_return
        self.mouse_up_return = mouse_up_return

    @property
    def curr_rect(self) -> pygame.Rect:
        if self.custom_rect:
            return self.custom_rect
        if self.mouse_on and self.images["mouse_on"]:
            return self.images["mouse_on"].get_rect(center=self.center)
        return self.images["default"].get_rect(center=self.center)

    @property
    def curr_img(self) -> pygame.surface.Surface:
        if self.mouse_on and self.images["mouse_on"]:
            return self.images["mouse_on"]
        return self.images["default"]

    def update_mouse_status(self, mouse_pos) -> None:
        """
        Returns whether the given mouse position collides with this object's current position.
        """
        if self.curr_rect.collidepoint(mouse_pos):
            self.mouse_on = True
            return
        self.mouse_on = False

    def render(self, screen, mouse_pos) -> None:
        """Render this object onto another surface(screen)."""
        self.update_mouse_status(mouse_pos)
        screen.blit(self.curr_img, self.curr_rect)


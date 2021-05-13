from typing import List
import time

import pygame.display


class Animation:
    """
    In-game animation object.

    frames: 
        "frames" is a list of frame objects.
        Frames consists of [(frame object for frame 1), (frame object for frame 2), ... ]

        A single frame object is consisted with graphical informations regarding the specific period of the animation.
        A frame object consists of [(graphic object 1 for this frame), (graphic object 2 for this frame), ...]

        A single graphical object is consisted with multiple data that is directly related to a single graphic of the animation.
        A graphical object consists of (visual object, display length)

        e.g. frames = [ [(visual_factories.v_magic_missile(x=2, y=3, randomize=True), None), ... ]
        > This "frames" object will display a "magical_ray" graphic on the given location for 2 frames.
        > Since the length(second) for per frame is not given, each frame will be shown for 0.2 second. (This is the default value)
    """

    def __init__(self, engine, frames: List, stack_frames: bool=False, sec_per_frame: float=0.05, refresh_last_frame: bool=True):
        """
        Args:
            stack_frames:
                Boolean. If True, every frame stacks on top of one another. (Animation will not refresh after each frame)
            sec_per_frame:
                The default value for how long each frame should be rendered on screen.
                However, this can be set for each frame indivisually, by passing values to the graphical objects.
            refresh_last_frame:
                Boolean. If False, the animation object will not refresh the screen after rendering the final frame of the animation.
                If you want to transition from animation to game map smoothly without any "blinking", you should set this True.
                e.g. Throwing animations have this value set to False
        """
        self.engine = engine
        self.total_frames = len(frames)
        self.frames = frames
        self.stack_frames = stack_frames
        self.sec_per_frame = sec_per_frame
        self.refresh_last_frame = refresh_last_frame
        self.current_frame_num = 0
        self.current_graphic_num = 0

    def current_graphic(self):
        """
        returns a tuple that consists of multiple informations regarding the graphics of the current frame.
        (
            visual object,
            frame length(seconds),
            boolean value whether this is the last graphic of current frame
        )
        """
        frame = self.frames[self.current_frame_num]

        is_last_graphic = False
        if self.current_graphic_num == len(frame) - 1:
            is_last_graphic = True #If this is the last graphic of current frame, return True.

        if frame[self.current_graphic_num][1]:
            anim_second = frame[self.current_graphic_num][1] # If the graphic object has its own specific time value, use it as this frame's render duration.
        else:
            anim_second = self.sec_per_frame # If not, use the default value as this frame's render duration.

        return(frame[self.current_graphic_num][0], anim_second, is_last_graphic)

    def render(self, only_in_camera: bool=True, only_in_visible: bool=True) -> None:
        """
        This method renders the animation onto screen.
        Args:
            only_in_camera:
                if True, only render if the animation is in camera's area.
            only_in_visible:
                if True, only render if animation is in visible area.
        """
        while True:
            # Break the loop after last frame
            if self.current_frame_num == self.total_frames:
                break

            visual_obj, anim_second, is_last_graphic = self.current_graphic()
            if (only_in_camera and (0 > visual_obj.x or visual_obj.x > self.engine.camera.width or 0 > visual_obj.y or visual_obj.y > self.engine.camera.height))\
                or (only_in_visible and not self.engine.game_map.visible[visual_obj.x, visual_obj.y]):# Do not display
                pass
            else:
                self.engine.screen.blit(source=pygame.transform.scale(visual_obj.skin.curr_sprite.curr_img, (self.engine.camera.tile_size, self.engine.camera.tile_size)),
                                        dest=(self.engine.camera.abs_display_cor(visual_obj.x, visual_obj.y)))

            if is_last_graphic:
                # Increase current frame number by 1, and set the current graphic number to 0.
                self.current_frame_num += 1
                self.current_graphic_num = 0

                # Update Screen
                pygame.display.update()

                # Wait for time given for this frame (frame duration)
                time.sleep(anim_second)

                # Check if this is the last frame of the entire animation
                if self.current_frame_num == self.total_frames:
                    if self.refresh_last_frame:
                        self.engine.refresh_screen()
                        break
                    else:
                        break
                else:
                    # If stack_frames is True, continue rendering the next frame without refreshing the screen
                    if self.stack_frames:
                        pass
                    else:
                        self.engine.refresh_screen()
            else: self.current_graphic_num += 1


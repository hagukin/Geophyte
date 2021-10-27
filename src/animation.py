from typing import List
from game import Game
import time

class Animation:
    """
    In-game animation object.

    frames: 
        "frames" is a list of frame objects.
        Frames consists of [(frame object for frame 1), (frame object for frame 2), ... ]

        A single frame object is consisted with graphical informations regarding the specific period of the animation.
        A frame object consists of [(graphic object 1 for this frame), (graphic object 2 for this frame), ...]

        A single graphical object is consisted with multiple data that is directly related to a single graphic of the animation.
        A graphical object consists of (x position, y position, graphic type, display length)
        
        e.g. frames = [ [(1, 4, magical_ray, None), (2, 4, magical_ray, None)], [(1, 5, magical_ray, None), (2, 5, magical_ray, None)] ] 
        > This "frames" object will display a "magical_ray" graphic on the given location for 2 frames.
        > Since the length(second) for per frame is not given, each frame will be shown for 0.2 second. (This is the default value)
    """

    def __init__(self, engine, frames: List, stack_frames: bool=False, sec_per_frame: float=None, refresh_last_frame: bool=False, render_if_in_sight: bool=True):
        """
        Args:
            stack_frames:
                Boolean. If True, every frame stacks on top of one another. (Animation will not refresh after each frame)
            sec_per_frame:
                The default value for how long each frame should be rendered on screen.
                However, this can be set for each frame indivisually, by passing values to the graphical objects.
            refresh_last_frame:
                Boolean. If False, the animation object will not refresh the screen after rendering the final frame of the animation.
                If you want to transition from animation to game map smoothly without any "blinking", you should set this False.
                e.g. Throwing animations have this value set to False
        """
        self.total_frames = len(frames)
        self.frames = frames
        self.stack_frames = stack_frames
        self.sec_per_frame = sec_per_frame
        if sec_per_frame is None:
            if self.total_frames == 0:
                self.sec_per_frame = 0
            else:
                self.sec_per_frame = min(0.05, 0.25 / self.total_frames) # Default length: Each animation will end within one second.
        self.refresh_last_frame = refresh_last_frame
        self.current_frame_num = 0
        self.current_graphic_num = 0
        self.render_if_in_sight = render_if_in_sight

    @property
    def engine(self):
        return Game.engine

    @property
    def current_graphic(self):
        """
        returns a tuple that consists of multiple informations regarding the graphics of the current frame.
        (
            animation x location, 
            animation y location, 
            animation graphic object, 
            boolean value whether this is the last graphic of current frame
        )
        """
        frame = self.frames[self.current_frame_num]
        
        is_last_graphic = False
        if self.current_graphic_num == len(frame) - 1:
            is_last_graphic = True #If this is the last graphic of current frame, return True.
        
        anim_x = frame[self.current_graphic_num][0]
        anim_y = frame[self.current_graphic_num][1]
        anim_graphic = frame[self.current_graphic_num][2]

        if frame[self.current_graphic_num][3]:
            anim_second = frame[self.current_graphic_num][3] # If the graphic object has its own specific time value, use it as this frame's render duration.
        else:
            anim_second = self.sec_per_frame # If not, use the default value as this frame's render duration.
        return(anim_x, anim_y, anim_graphic, anim_second, is_last_graphic)

    def render(self) -> None:
        """
        This method renders the animation onto screen.
        """
        while True:
            # Break the loop after last frame
            if self.current_frame_num == self.total_frames:
                break

            graphic = self.current_graphic
            if 0 <= graphic[0] <= self.engine.camera.width and 0 <= graphic[1] <= self.engine.camera.height: # Clamp inside camera screen
                should_render = True
                if self.render_if_in_sight:
                    abs_x, abs_y = self.engine.camera.rel_to_abs(graphic[0], graphic[1])
                    if not self.engine.game_map.visible[abs_x, abs_y]:
                        should_render = False
                if should_render:
                    self.engine.console.print(x=graphic[0], y=graphic[1], string=graphic[2]["char"], fg=graphic[2]["fg"], bg=graphic[2]["bg"])

            if graphic[4]:
                # Increase current frame number by 1, and set the current graphic number to 0.
                self.current_frame_num += 1
                self.current_graphic_num = 0

                # Actual rendering
                self.engine.context.present(self.engine.console)

                # Wait for time given for this frame (frame duration)
                time.sleep(graphic[3])

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
            else:
                self.current_graphic_num += 1


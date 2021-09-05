from render import render_img
from util import center_print, draw_horizontal_line

import color
import tcod
import time
import random


class CreditInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the credit screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_ESCAPE: # Quit Game
            return "escape"
        return None

class Credit():
    @staticmethod
    def render_credit_animation(console, x, y, frame):
        """
        Render animations on the credit screen.
        """
        return #DEBUG

        # Get animation graphic
        with open(f"resources\\c{frame}.txt", "r") as f:
            graphic = f.read()
        flame_color = (255, random.randint(100,255), 0)

        width = tcod.console_get_width(console)
        height = tcod.console_get_height(console)
        anim_x = int(width / 2) - 9
        anim_y = height - 18
        console.print(anim_x - 2, anim_y - 2, string=graphic, fg=flame_color)

    @staticmethod
    def render_credit_gui(console: tcod.Console):
        """
        Renders GUI for the credit screen.
        """
        y = 1
        console.clear(fg=color.black, bg=color.black)
        draw_horizontal_line(console, y=y-1, thickness=3, title="Developed By", fg=color.black, bg=color.credit_dev)
        center_print(console, string="Haguk Kim / Gamesmith", y=y+5, fg=color.credit_dev)

        draw_horizontal_line(console, y=y+9, thickness=3, title="Soundtrack By", fg=color.black, bg=color.credit_sound)
        center_print(console, string="Maxim Tsukanov / X3nus", y=y + 15, fg=color.credit_sound)

        draw_horizontal_line(console, y=y+19, thickness=3, title="Special thanks to", fg=color.black, bg=color.credit_special)
        center_print(console, string="Kyle Benesch / HexDecimal", y=y+25, fg=color.credit_special)
        center_print(console, string="Joao F. Henriques / Jotaf", y=y+26, fg=color.credit_special)
        center_print(console, string="Tyler Standridge / TStand90", y=y+27, fg=color.credit_special)
        center_print(console, string="hukseol", y=y+28, fg=color.credit_special)
        center_print(console, string="Habin Cho / chb09876", y=y+29, fg=color.credit_special)

        draw_horizontal_line(console, y=y+33, thickness=3, title="License", bg=color.credit_license)
        center_print(console, string="MIT-style license:", y=y+37, fg=color.white)
        center_print(console, string="White Rabbit font by Matthew Welch", y=y+38, fg=color.credit_license)
        center_print(console, string="OFL license:", y=y+40, fg=color.white)
        center_print(console, string="Nanumfont", y=y+41, fg=color.credit_license)

        draw_horizontal_line(console, y=y + 45, thickness=1, title="FX By", bg=color.credit_fx)
        center_print(console, string="mensageirocs | dersuperanton", y=y + 47, fg=color.credit_fx)



    @staticmethod
    def get_credit_action(sec_per_frame):
        """
        Get input from the player using creditInputHandler, and return the coresspondent action in a string form.
        """
        # Set Input Handler
        credit_input_handler = CreditInputHandler()
        start_time = time.time()
        is_time_over = False

        # Get input
        while True:
            end_time = time.time()
            if end_time - start_time >= sec_per_frame:
                #print(end_time - start_time) #NOTE: time consumed for each loop
                is_time_over = True
                return None

            for event in tcod.event.wait(timeout=0.01):#NOTE: increasing the timeout value might cause each loop to consume longer time.
                credit_action = credit_input_handler.dispatch(event)

                if credit_action:
                    return credit_action

            if is_time_over:
                return None

    @staticmethod
    def render_credit(console, context, anim_x:int, anim_y:int, anim_frame: int) -> None:
        """
        Render credit screen.
        """
        console.clear(fg=color.black, bg=color.black)
        render_img(console=console, dest_x = 5, dest_y = 5, img=tcod.image_load("resources\\credit_img.png"))
        Credit.render_credit_gui(console=console)
        Credit.render_credit_animation(console=console, x=anim_x, y=anim_y, frame=anim_frame)
        context.present(console, keep_aspect=True)

    @staticmethod
    def credit_event_handler(console, context):
        """
        Core function that handles most of the things related to the credit screen.
        credit screen loop is handled here.
        """
        credit_animation_x = int(tcod.console_get_width(console) / 2) - 41
        credit_animation_y = 15

        sec_per_frame = 0.2
        max_frame = 8

        # Render credit for the first time
        animation_frame = 1
        Credit.render_credit(console, context, credit_animation_x, credit_animation_y, animation_frame)

        # credit screen loop
        while True:
            # Get Input from credit + timeoout when this animation frame is overs next animation
            credit_action = Credit.get_credit_action(sec_per_frame=sec_per_frame)

            # Render credit GUI
            Credit.render_credit_gui(console=console)

            # Add frame
            if animation_frame >= max_frame:
                animation_frame = 1
            else:
                animation_frame += 1

            Credit.render_credit_animation(console=console, x=credit_animation_x, y=credit_animation_y, frame=animation_frame)

            # Present to console
            context.present(console, keep_aspect=True)

            # Get input from credit screen
            if credit_action == "escape":
                return None

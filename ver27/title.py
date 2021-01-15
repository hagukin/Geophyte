import tcod

import time
import color

import random

from loader.initialization import init_game_variables
from loader.data_loader import load_game

class TitleInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_n: # New Game
            return "new_game"
        elif event.sym == tcod.event.K_l: # Load Game
            return "load_game"
        elif event.sym == tcod.event.K_q: # Quit Game
            return "quit_game"
        return None


def render_title_animation(console, context, x, y, frame):
    """
    Render animations for the title screen.
    """
    # Title Logo Color changes every loop
    num = random.randint(0,1)
    if num == 0:
        text_color = color.white
    else:
        text_color = color.red

    # Get title graphic
    with open("sources\\geophyte_title.txt", "r") as f:
        title = f.read()
    
    # render
    console.print(x, y, string=title, fg=text_color)

    # Get animation graphic
    if frame == 1:
        with open("sources\\f1.txt", "r") as f:
            graphic = f.read()
    elif frame == 2:
        with open("sources\\f2.txt", "r") as f:
            graphic = f.read()
    elif frame == 3:
        with open("sources\\f3.txt", "r") as f:
            graphic = f.read()
    elif frame == 4:
        with open("sources\\f4.txt", "r") as f:
            graphic = f.read()

    # render
    console.print(x, y + 15, string=graphic, fg=color.white)
    

def render_title_gui(console, context, x, y):
    """
    Renders GUI for the title screen.
    """
    # render
    console.print(x, y, string="N - New Game\n\nL - Load Game\n\nQ - Quit Game", fg=color.white)


def get_title_action(sec_per_frame):
    """
    Get input from the player using TitleInputHandler, and return the coresspondent action in a string form.
    """
    # Set Input Handler
    title_input_handler = TitleInputHandler()

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
            title_action = title_input_handler.dispatch(event)

            if title_action:
                return title_action

        if is_time_over:
            return None


def title_event_handler(console, context, cfg):
    """
    Core function that handles most of the things related to the title screen.
    Title screen loop is handled here.
    """
    # Set variables
    title_gui_x = 5
    title_gui_y = 50

    title_animation_x = 28
    title_animation_y = 10

    sec_per_frame = 1
    prev_frame = time.time()

    max_frame = 4

    # Render Title Screen for the first time
    render_title_gui(console=console, context=context, x=title_gui_x, y=title_gui_y)
    animation_frame = 1
    render_title_animation(console=console, context=context, x=title_animation_x, y=title_animation_y, frame=animation_frame)


    # Present to console
    context.present(console, keep_aspect=True)

    # Title screen loop
    while True:
        # Get Input from title + timeoout when this animation frame is overs next animation
        title_action = get_title_action(sec_per_frame=sec_per_frame)
    
        # Render Title GUI
        render_title_gui(console=console, context=context, x=title_gui_x, y=title_gui_y)
        time_increment = time.time()

        # Add frame
        if animation_frame >= max_frame:
            animation_frame = 1
        else:
            animation_frame += 1

        render_title_animation(console=console, context=context, x=title_animation_x, y=title_animation_y, frame=animation_frame)

        # Present to console
        context.present(console, keep_aspect=True)

        # Get input from title screen
        if title_action == "new_game":
            player, engine = init_game_variables(cfg)
            engine.message_log.add_message(f"Hello {player.name}, welcome to Geophyte!", color.welcome_text)
            return player, engine
        elif title_action == "load_game":
            try:
                player, engine = load_game()
                engine.message_log.add_message(f"Welcome back to Geophyte, {player.name}!", color.welcome_text)
                return player, engine
            except:
                console.print(5, 5, string="Couldn't find any save data available.", fg=color.red)
                context.present(console, keep_aspect=True)
                continue


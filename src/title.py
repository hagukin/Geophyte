from loader.initialization import init_game_variables
from loader.data_loader import load_game
from render import render_img
from loader.data_loader import quit_game

import color
import tcod
import time
import random
import option
import credits


class TitleInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_n: # New Game
            return "new_game"
        elif event.sym == tcod.event.K_l: # Load Game
            return "load_game"
        elif event.sym == tcod.event.K_o: # Option
            return "option"
        elif event.sym == tcod.event.K_c: # Credits
            return "credits"
        elif event.sym == tcod.event.K_q: # Quit Game
            return "quit_game"
        return None


def render_title_animation(console, x, y, frame):
    """
    Render animations for the title screen.
    """
    # Title Logo Color changes every loop
    # num = random.randint(0,1)
    # if num == 0:
    #     text_color = color.white
    # else:
    #     text_color = color.red

    text_color = color.logo_c1

    # Get title graphic
    with open("resources\\geophyte_title.txt", "r") as f:
        title = f.read()
    
    # render
    console.print(x, y, string=title, fg=text_color)

    # Get animation graphic
    g2frame = (3,4,5,6,7,8,1,2) #differs the frame to make more non-synchronized feeleing
    with open(f"resources\\f{frame}.txt", "r") as f:
        graphic1 = f.read()
    with open(f"resources\\f{g2frame[frame-1]}.txt", "r") as f:
        graphic2 = f.read()
    torch = " \' \n\\-/\n\\#/\n # \n # \n # \n # \n # \n # \n # \n # \n # "
    
    flame_color = (255, random.randint(100,255), 0)

    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    anim_x = int(width / 2) - 9
    anim_y = height - 18
    console.print(anim_x - 2, anim_y - 2, string=graphic1, fg=flame_color)
    console.print(anim_x - 2, anim_y, string=torch, fg=color.brown)
    console.print(anim_x + 18, anim_y - 2, string=graphic2, fg=flame_color)
    console.print(anim_x + 18, anim_y, string=torch, fg=color.brown)


def render_title_gui(console):
    """
    Renders GUI for the title screen.
    """
    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    x = int(width / 2) - 8
    y = height - 17
    # render
    from util import draw_thick_frame
    #draw_thick_frame(console, x, y, width=17, height=9, fg=color.title_gui_frame)
    console.print(x+2, y+1, string="N - New Game\n\nL - Load Game\n\nO - Options\n\nC - Credits\n\nQ - Quit Game\n", fg=color.white)

    # Copyright Note, version mark
    console.print(width - 32, height - 4, string="Copyright (C) 2020 by Haguk Kim", fg=color.white)
    console.print(width - 24, height - 2, string="Geophyte Pre-Alpha v1.0", fg=color.white)


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


def render_title(console, context, anim_x:int, anim_y:int, anim_frame: int) -> None:
    """
    Render title screen.
    """
    console.clear(fg=color.black, bg=color.black)
    render_img(console=console, dest_x = 5, dest_y = 5, img=tcod.image_load("resources\\title_img.png"))
    render_title_gui(console=console)
    render_title_animation(console=console, x=anim_x, y=anim_y, frame=anim_frame)
    context.present(console, keep_aspect=True)


def title_event_handler(console, context, cfg):
    """
    Core function that handles most of the things related to the title screen.
    Title screen loop is handled here.
    """
    title_animation_x = int(tcod.console_get_width(console) / 2) - 41
    title_animation_y = 15

    sec_per_frame = 0.2
    max_frame = 8

    # Render title for the first time
    animation_frame = 1
    render_title(console, context, title_animation_x, title_animation_y, animation_frame)

    # Title screen loop
    while True:
        # Get Input from title + timeoout when this animation frame is overs next animation
        title_action = get_title_action(sec_per_frame=sec_per_frame)
    
        # Render Title GUI
        render_title_gui(console=console)

        # Add frame
        if animation_frame >= max_frame:
            animation_frame = 1
        else:
            animation_frame += 1

        render_title_animation(console=console, x=title_animation_x, y=title_animation_y, frame=animation_frame)

        # Present to console
        context.present(console, keep_aspect=True)

        # Get input from title screen
        if title_action == "new_game":
            player, engine = init_game_variables(cfg)
            engine.message_log.add_message(f"{player.name}님, 지오파이트의 세계에 오신 것을 환영합니다!", color.welcome_text)
            return player, engine
        elif title_action == "load_game":
            try:
                player, engine = load_game()
                engine.message_log.add_message(f"{player.name}님, 지오파이트의 세계에 돌아오신 것을 환영합니다!", color.welcome_text)
                return player, engine
            except:
                console.print(5, 5, string="세이브 파일을 찾지 못했습니다.", fg=color.red)
                context.present(console, keep_aspect=True)
                continue
        elif title_action == "option":
            option.option_event_handler(console=console, context=context, game_started=False)
            render_title(console, context, title_animation_x, title_animation_y, animation_frame)
        elif title_action == "credits":
            credits.credit_event_handler(console=console, context=context)
            render_title(console, context, title_animation_x, title_animation_y, animation_frame)
        elif title_action == "quit_game":
            quit_game()


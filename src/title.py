from base.initialization import init_game_variables
from base.data_loader import load_game
from render import render_img
from base.data_loader import quit_game, delete_saved_game
from game import Game
from language import interpret as i

import color
import tcod
import time
import random
import chargen
from option import Option
from credits import Credit
from sound import SoundManager
from exceptions import DiffLangException, DiffVerException


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

class Title():
    g2frame = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 1, 2)

    @staticmethod
    def render_logo(console, x, y):
        # render title
        logo_color = color.logo_c1
        with open("resources\\geophyte_title.txt", "r") as f:
            title = f.read()
        console.print(x, y, string=title, fg=logo_color)

    @staticmethod
    def render_title_animation(console, frame):
        """
        Render animations for the title screen.
        """
        # Title Logo Color changes every loop
        # num = random.randint(0,1)
        # if num == 0:
        #     text_color = color.white
        # else:
        #     text_color = color.red

        # Get animation graphic
        with open(f"resources\\a{frame}.txt", "r") as f:
            graphic1 = f.read()
        with open(f"resources\\a{frame}.txt", "r") as f: #g2frame[frame-1]
            graphic2 = f.read()
        torch = " \' \n\\\-//\n\\###/\n ### \n  #  \n  #  \n  #  \n  #  \n  #"

        width = tcod.console_get_width(console)
        height = tcod.console_get_height(console)
        anim_x = int(width / 2) - 9
        anim_y = height - 22
        console.print(anim_x - 11, anim_y - 1, string=graphic1, fg=(255, random.randint(100,180), 0))
        console.print(anim_x - 6, anim_y + 8, string=torch, fg=color.brown)
        console.print(anim_x + 16, anim_y - 1, string=graphic2, fg=(255, random.randint(100,180), 0))
        console.print(anim_x + 20, anim_y + 8, string=torch, fg=color.brown)


    @staticmethod
    def render_title_gui(console):
        """
        Renders GUI for the title screen.
        """
        width = tcod.console_get_width(console)
        height = tcod.console_get_height(console)
        x = int(width / 2) - 8
        y = height - 17
        # render
        console.print(x+2, y+1, string="(n) New Game\n\n(l) Load Game\n\n(o) Options\n\n(c) Credits\n\n(q) Quit Game\n", fg=color.white)

        # Copyright Note, version mark
        txt1 = "Copyright (C) 2020-2022 by Haguk Kim"
        txt2 = "Geophyte "+Game.version+f" ({Game.language})"
        console.print(width - len(txt1) - 1, height - 4, string=txt1, fg=color.white)
        console.print(width - len(txt2) - 1, height - 2, string=txt2, fg=color.white)

    @staticmethod
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

    @staticmethod
    def render_title(console, context, anim_x:int, anim_y:int, anim_frame: int) -> None:
        """
        Render title screen.
        """
        console.clear(fg=color.black, bg=color.black)
        render_img(console=console, dest_x=8, dest_y=0, img=tcod.image_load("resources\\title_img.png"))
        Title.render_title_animation(console=console,frame=anim_frame)
        Title.render_logo(console, x=anim_x, y=anim_y)
        Title.render_title_gui(console=console)
        context.present(console, keep_aspect=True)

    @staticmethod
    def title_sound(sound_manager: SoundManager) -> None:
        sound_manager.change_bgm("bgm_title_screen", force_change=False, show_warning=False)

    @staticmethod
    def title_event_handler(console, context, sound_manager: SoundManager):
        """
        Core function that handles most of the things related to the title screen.
        Title screen loop is handled here.
        """
        logo_x = int(tcod.console_get_width(console) / 2) - 41
        logo_y = 8
        sec_per_frame = 0.1
        max_frame = 15
        animation_frame = 1

        # Title screen loop
        while True:
            Title.title_sound(sound_manager)
            console.clear()
            # Get Input from title + timeoout when this animation frame is overs next animation
            title_action = Title.get_title_action(sec_per_frame=sec_per_frame)
            Title.render_title(console, context, logo_x, logo_y, animation_frame)

            # Add frame
            if animation_frame >= max_frame:
                animation_frame = 1
            else:
                animation_frame += 1
            context.present(console, keep_aspect=True)

            # Load config
            from configuration import get_game_config
            cfg = get_game_config()

            # Get input from title screen
            if title_action == "new_game":
                chara_gen = chargen.CharGen()
                player = chara_gen.chargen_event_handler(console=console, context=context, cfg=cfg,sound_manager=sound_manager)
                if not player:
                    continue # Exit chargen, go back to title
                engine = init_game_variables(player, cfg, console, context)
                engine.message_log.add_message(
                    i(f"{engine.player.name}님, 지오파이트의 세계에 오신 것을 환영합니다!",
                      f"{engine.player.name}, Welcome to the world of Geophyte!"), color.welcome_text)
                sound_manager.remove_bgm()
                sound_manager.remove_bgs()
                delete_saved_game()
                return engine
            elif title_action == "load_game":
                langstr = "(알 수 없음)"
                verstr = "(알 수 없음)"
                try:
                    engine = load_game()

                    # Language check
                    try:
                        if engine.LANGUAGE != cfg['lang']:
                            langstr = engine.LANGUAGE
                            raise DiffLangException
                    except DiffLangException:
                        console.print(1, 1, string=i(f"다른 언어로 플레이한 세이브 파일은 열 수 없습니다. 현재:{cfg['lang']} 세이브파일:{langstr}",
                                                     f"Your current language doesn't match with savefile's. Current:{cfg['lang']} Savefile:{langstr}"),
                                      fg=color.red)
                        sound_manager.add_sound_queue("fx_ui_warning")
                        context.present(console, keep_aspect=True)
                        continue

                    # Version check
                    try:
                        if engine.VERSION != Game.version:
                            verstr = engine.VERSION
                            raise DiffVerException
                    except DiffVerException:
                        console.print(1, 1, string=i(f"다른 버전의 게임에서 플레이한 세이브 파일은 열 수 없습니다. 현재:{Game.version} 세이브파일:{verstr}",
                                                     f"Your current game version doesn't match with savefile's. Current:{Game.version} Savefile:{verstr}"),
                                      fg=color.red)
                        sound_manager.add_sound_queue("fx_ui_warning")
                        context.present(console, keep_aspect=True)
                        continue

                    engine.message_log.add_message(
                        i(f"{engine.player.name}님, 지오파이트의 세계에 돌아오신 것을 환영합니다!",
                          f"{engine.player.name}, Welcome back to the world of Geophyte!"),
                          color.welcome_text)
                    return engine
                except FileNotFoundError:
                    console.print(1, 1, string=i("세이브 파일을 찾지 못했습니다.",
                                                 "Failed to find a valid game data."), fg=color.red)
                    sound_manager.add_sound_queue("fx_ui_warning")
                    context.present(console, keep_aspect=True)
                    continue
                except Exception:
                    console.print(1, 1, string=i(f"세이브 파일이 훼손되어 로드할 수 없습니다.",
                                                 f"Savefile corrupted, failed to load."),
                                  fg=color.red)
                    sound_manager.add_sound_queue("fx_ui_warning")
                    context.present(console, keep_aspect=True)
                    continue

            elif title_action == "option":
                Option.option_event_handler(console=console, context=context, game_started=False, sound_manager=sound_manager)
                Title.render_title(console, context, logo_x, logo_y, animation_frame)
            elif title_action == "credits":
                Credit.credit_event_handler(console=console, context=context)
                Title.render_title(console, context, logo_x, logo_y, animation_frame)
            elif title_action == "quit_game":
                quit_game()


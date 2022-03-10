#!usr/bin/env python
#coding=utf-8

import os
import sys
import traceback
import tcod
import color
import json
import threading
from exceptions import RestartException
from game import Game
from option import Option
from configuration import get_game_config
from title import Title
from sound import SoundManager

global sound_queue # Contains sound that are going to be played once
global bgm
global bgs

f = open("./config/config.json", "r")
debug = json.load(f)["debugmode"]
f.close()

class SystemLog(object):
    def __init__(self, origin_stdout):
        self.terminal = origin_stdout
        if debug:
            import datetime
            date = str(datetime.datetime.now())
            log = "======================" + date + "======================\n"
            open("log\\syslog.dat", 'w').write(log) # delete old data
    def write(self, message):
        if debug:
            open("log\\syslog.dat", 'a+').write(message)
        self.terminal.write(message)
    def flush(self):
        pass
tmp = sys.stdout
sys.stdout = SystemLog(tmp)


def track_error(is_sys_error:bool) -> None:
    # Print error to stderr then print the error to the message log
    traceback.print_exc()  # stdout is SystemLog
    if not is_sys_error and debug:
        if Game.engine:
            Game.engine.message_log.add_message(traceback.format_exc(), color.error)

    file = "log\\error_log.txt"
    if is_sys_error:
        file = "log\\system_error_log.txt"
    with open(file, 'a+') as f:
        import datetime
        date = str(datetime.datetime.now())
        log = "======================" + date + "======================\n"
        log += traceback.format_exc()
        f.write(log)
    if get_game_config()["report_issue_automatically"]:
        try:
            raise NotImplementedError()
        except Exception as e:
            print(f"ERROR::Issue report failed. - {e}")


def main() -> None:
    sound_manager = SoundManager()
    sound_thread = threading.Thread(target=sound_manager.update, args=()) # SoundManager.update will sleep for every 1/60 second.
    sound_thread.daemon = True # is Daemon thread. will stop when main thread dies.
    sound_thread.start()

    # Prevent save data exploits
    from base.exit import GameExit
    GameExit.unexpected_exit = True

    # Get Configuration
    cfg = get_game_config()

    # Toggle Fullscreen
    if cfg["fullscreen"]:
        set_screen = tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP
    else:
        set_screen = tcod.context.SDL_WINDOW_ALLOW_HIGHDPI

    with tcod.context.new(
        columns=cfg["screen_width"],
        rows=cfg["screen_height"],
        tileset=tcod.tileset.load_truetype_font(
        path=cfg["tileset_path"],
        tile_width=cfg["tile_width"],
        tile_height=cfg["tile_height"]
        ),
        title="Geophyte "+Game.version,
        sdl_window_flags=set_screen,
        vsync=False,
    ) as context:
        root_console = tcod.Console(cfg["screen_width"], cfg["screen_height"], order="F")

        try:
            # System loop
            while True:
                ## Initialization
                # must set language before title loop
                Game.language = cfg['lang']
                Option.update_lang()

                # title Screen Loop
                Game.engine = Title.title_event_handler(console=root_console, context=context, sound_manager=sound_manager)
                Game.engine.update_config()

                # initialize book data if there is None. Else load the book data
                from base.data_loader import load_book
                load_book()
                # initialize engine
                engine = Game.engine
                engine.console = root_console
                engine.context = context
                engine.sound_manager = sound_manager
                engine.initialize_pixel()
                sound_manager.play_bgm_for_biome(engine.game_map.biome)
                sound_manager.play_bgs_for_biome(engine.game_map.biome)

                ## Main Game Loop
                while True:
                    try:
                        if engine.player_path or engine.player_dir:
                            cx, cy = engine.player.x, engine.player.y
                            turn_pass = engine.do_player_queue_actions()
                            if cx == engine.player.x and cy == engine.player.y:
                                engine.player_path.clear()
                            engine.player_dir = None
                            engine.handle_world(turn_pass=turn_pass)

                            # Render game
                            root_console.clear()
                            engine.event_handler.on_render(console=root_console) #refreshing graphics for the root console
                            context.present(root_console, keep_aspect=True)
                        else:
                            for event in tcod.event.wait(timeout=None):# set to None = wait indefinitly for any events
                                context.convert_event(event)
                                turn_pass = engine.event_handler.handle_events(event)# returns True if player does any action that costs a in-game turn
                                engine.handle_world(turn_pass=turn_pass)

                                # Render game
                                root_console.clear()
                                engine.event_handler.on_render(console=root_console) #refreshing graphics for the root console
                                context.present(root_console, keep_aspect=True)

                            ### WRITE DEBUG FUNCTIONS HERE ###
                    except RestartException:
                        break
                    except Exception:
                        track_error(is_sys_error=False)
        except Exception as e:
            track_error(is_sys_error=True)
            sys.exit()

if __name__ == "__main__":
    # Set this to True when testing performance
    # NOTE : make sure you click the X button when exiting the program (do not stop the program itself)
    performance_debug = False

    if performance_debug:

        import cProfile
        import pstats
        from pstats import SortKey

        cProfile.run('main()', "output.dat")
        
        with open("output_time.txt", "w") as f:
            p = pstats.Stats("output.dat", stream=f)
            p.sort_stats("time").print_stats()
        
        with open("output_calls.txt", "w") as f:
            p = pstats.Stats("output.dat", stream=f)
            p.sort_stats("calls").print_stats()
    else:
        while True:
            main()
    
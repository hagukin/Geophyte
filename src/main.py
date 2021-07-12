#!/usr/bin/env python3
import traceback
import tcod
import color
from tcod.context import RENDERER_SDL2
from configuration import get_game_config
from title import Title

def main() -> None:
    # Get Configuration
    cfg = get_game_config()

    # Toggle Fullscreen
    if cfg["fullscreen"]:
        set_screen = tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP
    else:
        set_screen = None

    with tcod.context.new(
        columns=cfg["screen_width"],
        rows=cfg["screen_height"],
        tileset=tcod.tileset.load_truetype_font(
            path=cfg["tileset_path"], 
            tile_width=cfg["tile_width"], 
            tile_height=cfg["tile_height"]
        ),
        title="Geophyte",
        sdl_window_flags=set_screen,
        vsync=False,
    ) as context:
        root_console = tcod.Console(cfg["screen_width"], cfg["screen_height"], order="F")

        # Title Screen Loop
        player, engine = Title.title_event_handler(console=root_console, context=context, cfg=cfg)

        # Main Game Loop
        while True:
            try:
                if engine.player_path or engine.player_dir:
                    turn_pass = engine.do_player_queue_actions()
                    engine.game_map.sort_entities() # rearranging entities to prevent rendering issues
                    engine.handle_world(turn_pass=turn_pass)

                    # Render game
                    root_console.clear()
                    engine.event_handler.on_render(console=root_console) #refreshing graphics for the root console
                    context.present(root_console, keep_aspect=True)
                else:
                    for event in tcod.event.wait(timeout=None):# set to None = wait indefinitly for any events
                        context.convert_event(event)
                        turn_pass = engine.event_handler.handle_events(event)# returns True if player does any action that costs a in-game turn
                        engine.game_map.sort_entities()
                        engine.handle_world(turn_pass=turn_pass)

                        # Render game
                        root_console.clear()
                        engine.event_handler.on_render(console=root_console) #refreshing graphics for the root console
                        context.present(root_console, keep_aspect=True)
                
                ### WRITE DEBUG FUNCTIONS HERE ###
                # print("Hi")

            except Exception:
                # Print error to stderr then print the error to the message log
                traceback.print_exc()
                engine.message_log.add_message(traceback.format_exc(), color.error)


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
    
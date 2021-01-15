#!/usr/bin/env python3
import traceback
import title
import tcod
import color

from loader.initialization import get_game_config

def main() -> None:
    # Get Configuration
    cfg = get_game_config()

    # Toggle Fullscreen
    if cfg["fullscreen"]:
        set_screen = tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP
    else:
        set_screen = None

    with tcod.context.new_terminal(
        columns=cfg["screen_width"],
        rows=cfg["screen_height"],
        tileset=tcod.tileset.load_tilesheet(cfg["tileset_path"], 16, 16, tcod.tileset.CHARMAP_CP437),
        title="Geophyte",
        sdl_window_flags=set_screen,
        vsync=False,
    ) as context:
        root_console = tcod.Console(cfg["screen_width"], cfg["screen_height"], order="F")

        # Title Screen Loop
        player, engine = title.title_event_handler(console=root_console, context=context, cfg=cfg)
        
        # Final adjustments before starting the game loop
        engine.console = root_console
        engine.context = context
        engine.game_map.sort_entities()
        engine.update_fov()
        engine.update_enemy_fov(is_initialization=True)
        engine.update_entity_in_sight(is_initialization=True)

        # Main Game Loop
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console) #refreshing graphics for the root console
            context.present(root_console, keep_aspect=True)

            try:
                if engine.player_path or engine.player_dir:
                    turn_pass = engine.do_player_queue_actions()
                    engine.game_map.sort_entities() # rearranging entities to prevent rendering issues
                    engine.handle_world(turn_pass=turn_pass)
                else:
                    for event in tcod.event.wait(timeout=None):# set to None = wait indefinitly for any events
                        context.convert_event(event)
                        turn_pass = engine.event_handler.handle_events(event)# returns True if player does any action that costs a in-game turn
                        engine.game_map.sort_entities()
                        engine.handle_world(turn_pass=turn_pass)

                ### WRITE DEBUG FUNCTIONS HERE ###
                # print("DEBUG")

            # Handle exceptions in game
            except Exception:
                # Print error to stderr
                traceback.print_exc()

                # Then print the error to the message log
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
        main()
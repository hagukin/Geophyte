#!/usr/bin/env python3
import traceback
import title
import pygame
import color
from configuration import get_game_config

def main() -> None:
    game_on = True
    while game_on: #TODO reboot game after cfg change
        # Get Configuration
        cfg = get_game_config()

        # init pygame
        pygame.init()
        clock = pygame.time.Clock()
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h

        if cfg["fullscreen"]:
            screen = pygame.display.set_mode((cfg["screen_width"], cfg["screen_height"]), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((cfg["screen_width"], cfg["screen_height"]))
        pygame.display.set_caption('Geophyte')
        pygame.display.update()

        # Title Screen Loop
        player, engine = title.title_event_handler(screen, cfg=cfg)
        
        # Final adjustments before starting the game loop
        engine.adjustments_before_game()
        engine.adjustments_before_new_map(update_player_fov=True)

        # Main Game Loop
        while True:
            try:
                if engine.player_path or engine.player_dir:
                    turn_pass = engine.do_player_queue_actions()
                    engine.game_map.sort_entities() # rearranging entities to prevent rendering issues
                    engine.handle_world(turn_pass=turn_pass)
                else:
                    for event in pygame.event.get():# set to None = wait indefinitly for any events
                        pressed = pygame.key.get_pressed()
                        turn_pass = engine.event_handler.handle_event(engine.event_handler.dispatch_event(event, pressed)) # returns True if player does any action that costs a in-game turn
                        engine.game_map.sort_entities()
                        engine.handle_world(turn_pass=turn_pass)

                screen.fill((40, 40, 20))
                engine.event_handler.on_render(mouse_pos=pygame.mouse.get_pos())
                pygame.display.update()

                ### WRITE DEBUG FUNCTIONS HERE ###

            except Exception:
                # Print error to stderr then print the error to the message log
                traceback.print_exc()
                engine.message_log.add_message(traceback.format_exc(), color.error)

            pygame.display.flip()
            clock.tick(20) #framerate


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

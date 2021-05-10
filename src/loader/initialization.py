import actor_factories
import camera
import pygame

from engine import Engine
from message_log import MessageLog
from game_gui import GameGui
from configuration import get_game_config

def init_game_variables(screen, cfg):
    """
    Initialize game variables.(using the config data)
    """
    # Set Player TODO: Character Building
    player = actor_factories.player
    # NOTE: player.initialize_actor() is called from procgen.generate_entities()

    # Generate Engine
    engine = Engine(player=None, screen=screen)

    # Save Config to engine
    engine.config = cfg

    # Set item manager
    engine.initialize_item_manager()

    # Generate Map
    engine.depth = 1
    engine.world[1] = engine.generate_new_dungeon(screen, depth=1) #TODO
    engine.game_map = engine.world[1]
    engine.camera = camera.Camera(engine, width=cfg["camera_width"], height=cfg["camera_height"],
                                  display_x=cfg["camera_display_x"], display_y=cfg["camera_display_y"])

    engine.fonts = {
        "default":pygame.font.Font(engine.config["fonts"]["default"], 16)
    }
    engine.player = player.spawn(engine.game_map, 5, 5) ###DEBUG
    engine.message_log = MessageLog(engine, font_size=16)
    engine.game_gui = GameGui(engine)

    return player, engine

def update_game_variables(engine: Engine):
    """
    Re-read the config JSON file.
    TODO: Function currently under construction
    """
    engine.config = get_game_config()

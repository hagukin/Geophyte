import copy
import actor_factories
import camera

from engine import Engine
from configuration import get_game_config

def init_game_variables(cfg):
    """
    Initialize game variables.(using the config data)
    """
    # Set Player TODO: Character Building
    player = copy.deepcopy(actor_factories.player)
    # NOTE: player.initialize_actor() is called from procgen.generate_entities()

    # Generate Engine
    engine = Engine(player=player)

    # Save Config to engine
    engine.config = cfg

    # Set item manager
    engine.initialize_item_manager()

    # Generate Map
    engine.depth = 1
    engine.world[1] = engine.generate_new_dungeon()
    engine.game_map = engine.world[1]
    engine.player.parent = engine.world[engine.depth]

    # Generate Camea
    engine.camera = camera.Camera(engine, width=cfg["camera_width"], height=cfg["camera_height"], display_x=cfg["camera_xpos"], display_y=cfg["camera_ypos"])

    return player, engine

def update_game_variables(engine: Engine):
    """
    Re-read the config JSON file.
    TODO: Function currently under construction
    """
    engine.config = get_game_config()

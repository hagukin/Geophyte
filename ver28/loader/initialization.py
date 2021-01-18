import tcod
import copy

from engine import Engine
import actor_factories
import camera
from procgen import generate_dungeon


def get_game_config():

    screen_width = 100
    screen_height = 60
    fullscreen = False

    camera_width = 70
    camera_height = 45
    camera_xpos = 1 # top-left (0,0)
    camera_ypos = 1

    tileset_path = "sources\\Cheepicus-8x8x2.png"

    world_depth = 25 # Total dungeon depth TODO: Unused value

    game_config = {
        "screen_width" : screen_width,
        "screen_height" : screen_height,
        "fullscreen" : fullscreen,
        "camera_width" : camera_width,
        "camera_height" : camera_height,
        "camera_xpos" : camera_xpos,
        "camera_ypos" : camera_ypos,
        "tileset_path" : tileset_path,
        "world_depth" : world_depth,
    }

    return game_config

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
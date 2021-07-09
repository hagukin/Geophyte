import copy
from world import World
import actor_factories
import camera
import random

from engine import Engine
from tcod import Console
from tcod.context import Context
from configuration import get_game_config

def init_game_variables(cfg, console: Console, context: Context):
    """
    Initialize game variables.(using the config data)
    """
    # Seed
    seed = random.random() #TODO: Let player enter whatever seed they want

    # Set Player TODO: Character Building
    player = copy.deepcopy(actor_factories.player)
    ##DEBUG
    print(id(player))
    # NOTE: player.initialize_actor() is called from procgen.generate_entities()

    # Generate Engine
    engine = Engine(player=player)
    engine.world = World(engine, seed, max_depth=999)
    engine.console = console
    engine.context = context

    # Save Config to engine
    engine.config = cfg

    # Set item manager
    engine.initialize_item_manager()
    
    # Generate Map
    engine.depth = 1
    engine.world.set_map(engine.generate_new_dungeon(console, context, 1, False), 1)
    engine.change_gamemap_depth(1)
    engine.change_entity_depth(engine.player, 1, engine.game_map.ascend_loc[0], engine.game_map.ascend_loc[1])
    engine.player.parent = engine.world.get_map(engine.depth)
    engine.game_map.adjustments_before_new_map(update_player_fov=True)

    # Initialize player (give initial items, skils, etc)
    engine.player.initialize_actor()

    # Generate Camea
    engine.camera = camera.Camera(engine, width=cfg["camera_width"], height=cfg["camera_height"], display_x=cfg["camera_xpos"], display_y=cfg["camera_ypos"])

    return player, engine

def update_game_variables(engine: Engine):
    """
    Re-read the config JSON file.
    TODO: Function currently under construction
    """
    engine.config = get_game_config()

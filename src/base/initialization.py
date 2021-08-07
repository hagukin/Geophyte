import copy

from game_map import GameMap
from world import World
import actor_factories
import camera
import random
import color

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
    engine.world = World(seed, max_depth=999)
    engine.console = console
    engine.context = context

    # Save Config to engine
    engine.config = cfg

    # Set item manager
    engine.initialize_item_manager()
    
    # Set current depth
    engine.depth = 1

    # Set GameMap.engine. All in-game access to engine object is handled using this class variable.
    from game import Game
    Game.engine = engine

    # Generate camera
    engine.camera = camera.Camera(engine, width=cfg["camera_width"], height=cfg["camera_height"],
                                  display_x=cfg["camera_xpos"], display_y=cfg["camera_ypos"])

    from render import randomized_screen_paint

    randomized_screen_paint(console, context, color.black, diversity=0)
    console.print(int(console.width/2) - 4, int(console.height/2), "던전 초기화 중", fg=color.procgen_fg, bg=color.procgen_bg)
    console.print(int(console.width / 2) - 12, int(console.height / 2)+2, "이 작업은 약간의 시간이 걸릴 수 있습니다.", fg=color.procgen_fg, bg=color.procgen_bg)
    context.present(console=console, keep_aspect=True)
    engine.world.set_map(engine.generate_new_dungeon(console, context, 1, False), 1)
    engine.change_gamemap_depth(1)
    engine.change_entity_depth(engine.player, 1, engine.game_map.ascend_loc[0], engine.game_map.ascend_loc[1])
    engine.player.gamemap = engine.world.get_map(engine.depth)

    # Initialize player (give initial items, skils, etc)
    engine.player.initialize_actor()

    # Give player a complete encyclopedia TODO: delete?
    from base.data_loader import save_actor_book
    save_actor_book(get_all_monsters=True)


    engine.game_map.adjustments_before_new_map(update_player_fov=True)
    return engine

def update_game_variables(engine: Engine):
    """
    Re-read the config JSON file.
    TODO: Function currently under construction
    """
    engine.config = get_game_config()

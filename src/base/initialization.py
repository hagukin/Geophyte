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
from language import interpret as i

def init_game_variables(player, cfg, console: Console, context: Context):
    """
    Initialize game variables.(using the config data)
    """
    from game import Game

    # Generate Engine
    engine = Engine(player=player, language=Game.language, version=Game.version)
    engine.world = World(max_depth=999)
    engine.console = console
    engine.context = context

    # Save Config to engine
    engine._config = cfg

    # Set item manager
    engine.initialize_item_manager()
    
    # Set current depth
    engine.depth = 1

    # Set Game.engine. All in-game access to engine object is handled using this class variable.
    Game.engine = engine

    # Generate camera
    engine.camera = camera.Camera(engine, width=cfg["camera_width"], height=cfg["camera_height"],
                                  display_x=cfg["camera_xpos"], display_y=cfg["camera_ypos"])

    from render import randomized_screen_paint

    randomized_screen_paint(console, context, color.black, diversity=0)
    tmp1 = i("던전 초기화 중",
             "Creating a new dungeon")
    console.print(int(console.width/2) - int(len(tmp1)/2), int(console.height/2), tmp1, fg=color.procgen_fg, bg=color.procgen_bg)
    tmp2 = i("이 작업은 약간의 시간이 걸릴 수 있습니다.",
             "This may take a while.")
    console.print(int(console.width / 2) - int(len(tmp2)/2), int(console.height / 2)+2, tmp2, fg=color.procgen_fg, bg=color.procgen_bg)
    context.present(console=console, keep_aspect=True)


    engine.depth = 1
    engine.world.save_map_to_memory(engine.generate_new_dungeon(console, context, engine.depth, False), engine.depth)
    engine.game_map = engine.world.get_map(depth=engine.depth) # Has to manually set player gamemap so that

    # Normally setting up gamemap is handled in entity.copy(gamemap=gamemap), but this is the only exception.
    engine.player.gamemap = engine.game_map

    # You should not directly use .append
    # but this is an exception.
    engine.player.gamemap.entities.append(engine.player)

    engine.player.initialize_self() # Initialize player (give initial items, skils, etc)
    engine.game_map.adjustments_before_new_map()
    engine.change_entity_depth(entity=engine.player, depth=engine.depth, xpos=engine.game_map.ascend_loc[0], ypos=engine.game_map.ascend_loc[1])
    engine.world.save_world()

    # Give player a complete encyclopedia
    # from base.data_loader import save_actor_book
    # save_actor_book(get_all_monsters=True)

    return engine

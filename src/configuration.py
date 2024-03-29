import json
from exceptions import ConfigException

def get_game_config():
    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)
    return game_config


def alter_resolution(tile_width: int, tile_height: int) -> None:
    """
    Alter the game's pixels per tiles number by directly modifying config.json file.
    """
    if tile_width > 20 or tile_height > 20 or tile_width < 10 or tile_height < 10:
        raise ConfigException()

    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)
    
    game_config["tile_width"] = tile_width
    game_config["tile_height"] = tile_height

    with open("./config/config.json", "w") as cfg:
        json.dump(game_config, cfg, indent=4)

    from game import Game
    if Game.engine:
        Game.engine.update_config()


def toggle_fullscreen() -> None:
    """
    Toggle on/off fullscreen by directly modifying config.json file.
    """
    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)
        
    game_config["fullscreen"] = not game_config["fullscreen"]

    with open("./config/config.json", "w") as cfg:
        json.dump(game_config, cfg, indent=4)

    from game import Game
    if Game.engine:
        Game.engine.update_config()


def change_master_volume(percent: int) -> None:
    """Increase / Decrease master volume"""
    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)

    game_config["master_volume"] = max(min(game_config["master_volume"] + percent, 100),0)

    with open("./config/config.json", "w") as cfg:
        json.dump(game_config, cfg, indent=4)

    from game import Game
    if Game.engine:
        Game.engine.update_config()


def toggle_animation(using: bool) -> None:
    """Toggle ingame animation effects"""
    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)

    game_config["render_animation"] = using

    with open("./config/config.json", "w") as cfg:
        json.dump(game_config, cfg, indent=4)

    from game import Game
    if Game.engine:
        Game.engine.update_config()


def toggle_mouse_enemy_ignore(using: bool) -> None:
    """Toggle ingame animation effects"""
    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)

    game_config["ignore_enemy_spotted_during_mouse_movement"] = using

    with open("./config/config.json", "w") as cfg:
        json.dump(game_config, cfg, indent=4)

    from game import Game
    if Game.engine:
        Game.engine.update_config()

def change_language() -> None:
    """Change in-game language"""
    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)

    # TODO: Find a better way to enumerate through the list of supported languages
    support = ("KR", "EN")
    for i in range(0,len(support)):
        if game_config["lang"] == support[i]:
            game_config["lang"] = support[(i+1)%len(support)]
            break

    with open("./config/config.json", "w") as cfg:
        json.dump(game_config, cfg, indent=4)

    from game import Game
    Game.update_language(game_config["lang"])
    if Game.engine:
        Game.engine.update_config()
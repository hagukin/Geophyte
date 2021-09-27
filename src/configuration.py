import json
from exceptions import ConfigException
from game import Game

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

    if Game.engine:
        Game.engine.update_config()


def change_master_volume(percent: int) -> None:
    """Increase / Decrease master volume"""
    with open("./config/config.json", "r") as cfg:
        game_config = json.load(cfg)

    game_config["master_volume"] = max(min(game_config["master_volume"] + percent, 100),0)

    with open("./config/config.json", "w") as cfg:
        json.dump(game_config, cfg, indent=4)

    if Game.engine:
        Game.engine.update_config()
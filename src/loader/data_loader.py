import os
import sys
import shelve

def save_game(player, engine):
    with shelve.open("savefiles\\save_file", "n") as save_file:
        # prevent pickle lib error(cannot serialize c objects)
        temp_console = engine.console
        temp_context = engine.context
        engine.console = None
        engine.context = None

        #Player
        save_file["player_index"] = engine.game_map.entities.index(player)

        # Engine
        save_file["engine"] = engine
        engine.console = temp_console
        engine.context = temp_context


def load_game(cfg):
    # Check if file exists (os.getcwd() = current folder directory)
    if not os.path.isfile(os.getcwd()+"\\savefiles\\save_file.dat"):
        raise FileNotFoundError

    with shelve.open(os.getcwd()+"\\savefiles\\save_file", "r") as savefile:
        player_index = savefile["player_index"]
        engine = savefile["engine"]

        # Save Config to engine
        engine.config = cfg

    return engine.game_map.entities[player_index], engine


def quit_game():
    sys.exit()
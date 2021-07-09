import os
import sys
import shelve

def save_game(player, engine):
    with shelve.open(os.getcwd()+"\\saves\\save_file", "n") as save_file:
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


def load_game():
    # Check if file exists (os.getcwd() = current folder directory)
    if not os.path.isfile(os.getcwd()+"\\saves\\save_file.dat"):
        raise FileNotFoundError

    with shelve.open(os.getcwd()+"\\saves\\save_file", "r") as savefile:
        player_index = savefile["player_index"]
        engine = savefile["engine"]

    return engine.game_map.entities[player_index], engine


def quit_game():
    sys.exit()
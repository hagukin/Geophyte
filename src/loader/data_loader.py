import os
import sys
import shelve
import copy

def save_game(player, engine):
    with shelve.open(os.getcwd()+"\\saves\\save_file", "n") as save_file:
        # prevent pickle lib error(cannot serialize c objects)
        from game import Game

        temp_console = copy.copy(Game.engine.console)
        temp_context = copy.copy(Game.engine.context)
        Game.engine.console = None
        Game.engine.context = None

        # Player
        save_file["player_index"] = engine.game_map.entities.index(player) # Save the index number of a player instead of the entire object to reduce savefile size.

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
        engine.player = engine.game_map.entities[player_index]
    return engine


def quit_game():
    sys.exit()
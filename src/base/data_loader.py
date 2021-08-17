import os
import sys
import shelve
import copy


def save_game(player, engine):
    # Serialize all cached gamemaps
    engine.world.save_world()

    with shelve.open(os.getcwd()+"\\storage\\data\\game", "n") as gamedata:
        # prevent pickle lib error(cannot serialize c objects)
        from game import Game

        temp_console = Game.engine.console
        temp_context = Game.engine.context
        Game.engine.console = None
        Game.engine.context = None

        # Player
        gamedata["player_index"] = engine.game_map.entities.index(player) # Save the index number of a player instead of the entire object to reduce savefile size.

        # Engine
        gamedata["engine"] = engine
        engine.console = temp_console
        engine.context = temp_context


def load_game():
    # Check if file exists (os.getcwd() = current folder directory)
    if not os.path.isfile(os.getcwd()+"\\storage\\data\\game.dat"):
        raise FileNotFoundError

    with shelve.open(os.getcwd()+"\\storage\\data\\game", "r") as savefile:
        player_index = savefile["player_index"]
        engine = savefile["engine"]
        engine.player = engine.game_map.entities[player_index]
    return engine


def quit_game():
    sys.exit()


def save_actor_book(get_all_monsters: bool=False):
    with shelve.open(os.getcwd() + "\\storage\\book\\book", "n") as f:
        if get_all_monsters:
            # reset and init dictionary
            from book import monchar
            temp = {}
            for c in monchar:
                temp[str(c)] = {
                    "a":None,"b":None,"c":None,"d":None,"e":None,"f":None,"g":None,"h":None,"i":None,"j":None,"k":None,"l":None,"m":None,"n":None,"o":None,"p":None,"q":None,"r":None,"s":None,"t":None,"u":None,"v":None,"w":None,"x":None,"y":None,"z":None,
                    "A":None,"B":None,"C":None,"D":None,"E":None,"F":None,"G":None,"H":None,"I":None,"J":None,"K":None,"L":None,"M":None,"N":None,"O":None,"P":None,"Q":None,"R":None,"S":None,"T":None,"U":None,"V":None,"W":None,"X":None,"Y":None,"Z":None
                }

            # Insert data
            from actor_factories import ActorDB
            for monllist in ActorDB.monster_difficulty.values():
                if monllist:
                    for m in monllist:
                        for key, val in temp[m.char].items():
                            if val == None:
                                temp[m.char][key] = m.entity_id
                                break

            f["actors"] = temp


def load_book():
    # Check if file exists (os.getcwd() = current folder directory)
    if not os.path.isfile(os.getcwd() + "\\storage\\book\\book.dat"):
        raise FileNotFoundError

    import book
    with shelve.open(os.getcwd() + "\\storage\\book\\book", "r") as b:
        book.actor_db = b["actors"]
    return book.actor_db


def delete_saved_game() -> None:
    # Check if file exists (os.getcwd() = current folder directory)
    import os
    if not os.path.isfile(os.getcwd()+"\\storage\\data\\game.dat"):
        print("ERROR::Savefile not found. - delete_saved_game()")
        return None

    import os
    try:
        os.remove(os.getcwd()+"\\storage\\data\\game.dat")
        os.remove(os.getcwd() + "\\storage\\data\\game.bak")
        os.remove(os.getcwd() + "\\storage\\data\\game.dir")
    except Exception as e:
        print(f"WARNING::{e}")
    return None
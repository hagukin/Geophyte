import atexit

class GameExit:
    unexpected_exit: bool = True

def on_exit():
    if GameExit.unexpected_exit:
        on_unexpected_exit()

def on_unexpected_exit():
    # Check if file exists (os.getcwd() = current folder directory)
    import os
    if not os.path.isfile(os.getcwd() + "\\storage\\data\\game.dat"):
        print("ERROR::Savefile not found. - on_unexpected_exit()")
        return None

    import os
    try:
        os.remove(os.getcwd() + "\\storage\\data\\game.dat")
        os.remove(os.getcwd() + "\\storage\\data\\game.bak")
        os.remove(os.getcwd() + "\\storage\\data\\game.dir")
    except Exception as e:
        print(f"WARNING::{e}")
    return None

atexit.register(on_exit)
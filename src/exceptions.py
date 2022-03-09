class Impossible(Exception):
    """
    Exception raised when an action is impossible to be performed.
    The reason is given as the exception message.
    """

class ConfigException(Exception):
    """
    EXception raised when user tried to modify the config file but failed.
    """

class DiffLangException(Exception):
    """
    Exception raised when trying to load a gamefile that has a different language.
    """

class DiffVerException(Exception):
    """
    Exception when the game's version does not match with a savefile.
    """
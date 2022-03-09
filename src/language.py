from game import Game
def interpret(kr: str="", en: str="") -> str:
    """
    NOTE: When importing this function, it is recommended to not call it as 'i'.
    It could cause a nasty errors if used in for i in ... loop since the variable has the same name.
    """
    if Game.language == "KR":
        return kr
    else:
        return en
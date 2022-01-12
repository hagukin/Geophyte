from game import Game
def interpret(kr: str="", en: str="") -> str:
    if Game.language == "KR":
        return kr
    else:
        return en
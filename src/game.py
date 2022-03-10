from __future__ import annotations

class Game():
    engine = None
    version = "Alpha v2.2.1"
    from configuration import get_game_config
    language = get_game_config()['lang']

    @staticmethod
    def update_language(lang: str="EN") -> None:
        """Update all in-game language."""
        Game.language = lang

        from language import reimport_all
        reimport_all()
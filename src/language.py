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

def reimport_all() -> None:
    """
    When the language setting is changed after game has been booted up,
    you should reimport every entities from the factory to update their names/desc into translated ones.

    NOTE:
        It is important that you should seperate ~_factories.py files and class declaration files.
        For example, If reload the ais.py file which is NOT a factory type file but a class declaration file,
        you'll have a pickle/shelve related error since the ai classes are redeclared and the pickle lib will get confused.
        So it is extremely important to use 'interpret()' function only in the instance scope, NOT in the class declaration scope.
        For the same reason, you should NEVER have a class declaration inside of ~_factories.py file since they will cause an error
        when reimported.

        e.g.
        < Best thing to do >
        rabbit = Actor( ... , name = interpret("토끼", "rabbit"), ... )

        < Will not work and will cause an error >
        RabbitActor( ... )
            def __init__( ... , name = interpret("토끼", "rabbit"), ... ):
                self.name = name
                ...

        < Will work but is not recommended >
        RabbitActor( ... )
            def __init__( ... ):
                self.name = interpret("토끼", "rabbit")
                ...
    """
    try:
        import importlib
        import item_factories
        import actor_factories
        import terrain_factories
        import biome_factories
        import chest_factories
        import ability_factories
        import components.rule_factories
        importlib.reload(item_factories)
        importlib.reload(actor_factories)
        importlib.reload(terrain_factories)
        importlib.reload(biome_factories)
        importlib.reload(chest_factories)
        importlib.reload(ability_factories)
        importlib.reload(components.rule_factories)
    except Exception as e:
        print(f"ERROR::{e} - language.reimport_all()")
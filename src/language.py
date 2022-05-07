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
        import components.rule_factories
        import ability_factories
        import item_factories
        import actor_factories
        import semiactor_factories
        import chest_factories
        import terrain_factories
        import biome_factories

        # NOTE:
        # The order of reload() call is extremely important since one might reference other,
        # which could result in storing the objects with previously selected language.
        # e.g. Terrain object can store actors or semiactors during its declaration as their "actor_to_spawn" or "door_types" variables.
        # Thus, actors and semiactors should get reimported beforehand.
        # e.g.2. actor can store items or abilities, so you should reimported them beforehand.
        # WARNING:
        # If a object that contains translatable string references each other this could cause an translation issue so you should avoid mutual reference.
        # One way to get around this problem is by using an object's id instead of the object reference itself.
        # Currently there is no known case of mutual reference.
        # Reference map (20220508):
        #   Rule:
        #       None
        #   Ability:
        #       None
        #   Item:
        #       Ability
        #   Actor:
        #       Ability
        #       Item
        #   SemiActor:
        #       Rule
        #   Chest:
        #       None
        #   Terrain:
        #       Item
        #       Actor
        #       SemiActor
        #   Biome:
        #       Terrain

        importlib.reload(components.rule_factories)
        importlib.reload(ability_factories)
        importlib.reload(item_factories)
        importlib.reload(actor_factories)
        importlib.reload(semiactor_factories)
        importlib.reload(chest_factories)
        importlib.reload(terrain_factories)
        importlib.reload(biome_factories)
    except Exception as e:
        print(f"ERROR::{e} - language.reimport_all()")
from enum import auto, Enum

class RenderOrder(Enum):
    #CORPSE = auto() # corpses now has the same rendering order as items.
    LOWEST = auto()
    SEMIACTOR = auto()
    ITEM = auto()
    SEMIACTOR_OBJ = auto() # e.g. chests
    ACTOR = auto()
    PLAYER = auto()

class TilemapOrder(Enum):
    VOID = auto()
    MAP_BORDER = auto()
    ROOM_WALL = auto()
    ROOM_INNER = auto()
    TUNNEL = auto()
    DOOR_CONVEX = auto()
    DOOR = auto()
    GRASS_CORE = auto()
    GRASS = auto()
    WATER_CORE = auto()
    WATER = auto()
    PIT_CORE = auto()
    PIT = auto()
    HOLE_CORE = auto()
    HOLE = auto()
    ASCEND_STAIR = auto()
    DESCEND_STAIR = auto()
    TRAP = auto()
    PLANT = auto()
    CHEST = auto()


class InventoryOrder(Enum):
    CASH = auto()
    MELEE_WEAPON = auto()
    THROWING_WEAPON = auto()
    ARMOR = auto()
    AMULET = auto()
    RING = auto()
    POTION = auto()
    SCROLL = auto()
    SKILLBOOK = auto()
    SPELLBOOK = auto()
    WAND = auto()
    FOOD = auto()
    CORPSE = auto()
    TOOL = auto()
    GEM = auto()
    MISC = auto()


class EquipableOrder(Enum):
    BLADE = auto()
    CLUB = auto()
    SHIELD = auto()
    LIGHT_ARMOR = auto()
    HEAVY_ARMOR = auto() # including robes, capes
    AMULET = auto()
    MISC = auto()


class AbilityOrder(Enum):
    """
    SKILL - Non-magics
    SPELL - Magics
    """
    PASSIVE_SKILL = auto()
    REGULAR_SKILL = auto()
    PASSIVE_SPELL = auto()
    REGULAR_SPELL = auto()
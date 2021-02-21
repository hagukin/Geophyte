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
    ASCEND_STAIR = auto()
    DESCEND_STAIR = auto()
    TRAP = auto()
    CHEST = auto()

class InventoryOrder(Enum):
    MELEE_WEAPON = auto()
    THROWING_WEAPON = auto()
    ARMOR = auto()
    AMULET = auto()
    RING = auto()
    POTION = auto()
    SCROLL = auto()
    WAND = auto()
    FOOD = auto()
    CORPSE = auto()
    TOOL = auto()
    MISC = auto()

class AbilityOrder(Enum):
    """
    SKILL - 비 마법 능력
    SPELL - 마법 능력
    """
    PASSIVE_SKILL = auto()
    REGULAR_SKILL = auto()
    PASSIVE_SPELL = auto()
    REGULAR_SPELL = auto()
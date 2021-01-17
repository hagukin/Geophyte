from components import readable, quaffable, equipable, throwable
from components.item_state import ItemState
from entity import Item
import anim_graphics

from order import InventoryOrder

item_lists = []
item_rarity = []
item_identified = {} #key: item.entity_id, value: item.item_state.is_identified

#########################################################################
################################ POTIONS ################################
#########################################################################

### Potion of healing
potion_of_healing = Item(
    char="!",
    fg=(127, 0, 255),
    name="Potion of healing",
    entity_id="potion_of_healing",
    entity_desc="Potion of healing desc",
    rarity=60, #DEBUG
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(break_chance=1),
    readable=None,
    quaffable=quaffable.PotionOfHealingQuaffable(amount=10),
)
item_lists.append(potion_of_healing)
item_rarity.append(potion_of_healing.rarity)
item_identified[potion_of_healing.entity_id] = potion_of_healing.item_state.is_identified


### Potion of paralysis
potion_of_paralysis = Item(
    char="!",
    fg=(255, 0, 255),
    name="Potion of paralysis",
    entity_id="potion_of_paralysis",
    entity_desc="Potion of paralysis desc",
    rarity=6,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionOfParalysisThrowable(break_chance=1, penetration=True),
    readable=None,
    quaffable=quaffable.PotionOfParalysisQuaffable(turn=10),
)
item_lists.append(potion_of_paralysis)
item_rarity.append(potion_of_paralysis.rarity)
item_identified[potion_of_paralysis.entity_id] = potion_of_paralysis.item_state.is_identified

#########################################################################
################################ SCROLLS ################################
#########################################################################

### Scroll of Confusion
scroll_of_confusion = Item(
    char="≈",
    fg=(207, 63, 255),
    name="Scroll of confusion",
    entity_id="scroll_of_confusion",
    entity_desc="Scroll of confusion desc",
    rarity=4,
    weight=0.1,
    price=200,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfConfusionReadable(number_of_turns=15),
    quaffable=None,
)
item_lists.append(scroll_of_confusion)
item_rarity.append(scroll_of_confusion.rarity)
item_identified[scroll_of_confusion.entity_id] = scroll_of_confusion.item_state.is_identified


### Scroll of Meteor Storm
scroll_of_meteor_storm = Item(
    char="≈",
    fg=(255, 100, 0),
    name="Scroll of meteor storm",
    entity_id="scroll_of_meteor_storm",
    entity_desc="Scroll of meteor storm desc",
    rarity=4,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfMeteorStormReadable(damage=12, radius=1),
    quaffable=None,
)
item_lists.append(scroll_of_meteor_storm)
item_rarity.append(scroll_of_meteor_storm.rarity)
item_identified[scroll_of_meteor_storm.entity_id] = scroll_of_meteor_storm.item_state.is_identified


### Scroll of Thunderstorm
scroll_of_thunderstorm = Item(
    char="≈",
    fg=(255, 255, 0),
    name="Scroll of thunderstom",
    entity_id="scroll_of_thunderstorm",
    entity_desc="Scroll of thunderstorm desc",
    rarity=3,
    weight=0.1,
    price=400,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfThunderStormReadable(damage=20, maximum_range=5, tier=1),
    quaffable=None,
)
item_lists.append(scroll_of_thunderstorm)
item_rarity.append(scroll_of_thunderstorm.rarity)
item_identified[scroll_of_thunderstorm.entity_id] = scroll_of_thunderstorm.item_state.is_identified


### Scroll of Lightning
scroll_of_lightning = Item(
    char="≈",
    fg=(255, 252, 99),
    name="Scroll of lightning",
    entity_id="scroll_of_lightning",
    entity_desc="Scroll of lightning desc",
    rarity=6,
    weight=0.1,
    price=200,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfThunderStormReadable(damage=20, maximum_range=5, tier=2),
    quaffable=None,
)
item_lists.append(scroll_of_lightning)
item_rarity.append(scroll_of_lightning.rarity)
item_identified[scroll_of_lightning.entity_id] = scroll_of_lightning.item_state.is_identified


### Scroll of magic missile
scroll_of_magic_missile = Item(
    char="≈",
    fg=(100, 50, 255),
    name="Scroll of magic missile",
    entity_id="scroll_of_magic_missile",
    entity_desc="Scroll of magic missile desc",
    rarity=4,
    weight=0.1,
    price=250,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfMagicMissileReadable(anim_graphic=anim_graphics.magic_missile, damage=20, penetration=False),
    quaffable=None,
)
item_lists.append(scroll_of_magic_missile)
item_rarity.append(scroll_of_magic_missile.rarity)
item_identified[scroll_of_magic_missile.entity_id] = scroll_of_magic_missile.item_state.is_identified


### Scroll of magic mapping
scroll_of_magic_mapping = Item(
    char="≈",
    fg=(255, 90, 90),
    name="Scroll of magic mapping",
    entity_id="scroll_of_magic_mapping",
    entity_desc="Scroll of magic mapping desc",
    rarity=99,#DEBUG
    weight=0.1,
    price=250,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfMagicMappingReadable(tier=1),
    quaffable=None,
)
item_lists.append(scroll_of_magic_mapping)
item_rarity.append(scroll_of_magic_mapping.rarity)
item_identified[scroll_of_magic_mapping.entity_id] = scroll_of_magic_mapping.item_state.is_identified


### Scroll of piercing flame
scroll_of_piercing_flame = Item(
    char="≈",
    fg=(255, 0, 30),
    name="Scroll of piercing flame",
    entity_id="scroll_of_piercing_flame",
    entity_desc="Scroll of piercing flame desc",
    rarity=4,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfPiercingFlameReadable(anim_graphic=anim_graphics.piercing_flame, damage=20, penetration=True),
    quaffable=None,
)
item_lists.append(scroll_of_piercing_flame)
item_rarity.append(scroll_of_piercing_flame.rarity)
item_identified[scroll_of_piercing_flame.entity_id] = scroll_of_piercing_flame.item_state.is_identified


### Scroll of tame
scroll_of_tame = Item(
    char="≈",
    fg=(255, 0, 200),
    name="Scroll of tame",
    entity_id="scroll_of_tame",
    entity_desc="Scroll of tame desc",
    rarity=4,
    weight=0.1,
    price=400,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfTame(),
    quaffable=None,
)
item_lists.append(scroll_of_tame)
item_rarity.append(scroll_of_tame.rarity)
item_identified[scroll_of_tame.entity_id] = scroll_of_tame.item_state.is_identified


### Scroll of enchantment
scroll_of_enchantment = Item(
    char="≈",
    fg=(191, 255, 0),
    name="Scroll of enchantment",
    entity_id="scroll_of_enchantment",
    entity_desc="Scroll of enchantment desc",
    rarity=4,
    weight=0.1,
    price=400,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfEnchantmentReadable(),
    quaffable=None,
)
item_lists.append(scroll_of_enchantment)
item_rarity.append(scroll_of_enchantment.rarity)
item_identified[scroll_of_enchantment.entity_id] = scroll_of_enchantment.item_state.is_identified


### Scroll of identify
scroll_of_identify = Item(
    char="≈",
    fg=(255, 255, 200),
    name="Scroll of identify",
    entity_id="scroll_of_identify",
    entity_desc="Scroll of identify desc",
    rarity=4,
    weight=0.1,
    price=50,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfIdentifyReadable(),
    quaffable=None,
)
item_lists.append(scroll_of_identify)
item_rarity.append(scroll_of_identify.rarity)
item_identified[scroll_of_identify.entity_id] = scroll_of_identify.item_state.is_identified


### Scroll of Remove Curse
scroll_of_remove_curse = Item(
    char="≈",
    fg=(255, 255, 200),
    name="Scroll of remove curse",
    entity_id="scroll_of_remove_curse",
    entity_desc="Scroll of remove curse desc",
    rarity=4,
    weight=0.1,
    price=150,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfRemoveCurseReadable(),
    quaffable=None,
)
item_lists.append(scroll_of_remove_curse)
item_rarity.append(scroll_of_remove_curse.rarity)
item_identified[scroll_of_remove_curse.entity_id] = scroll_of_remove_curse.item_state.is_identified


#########################################################################
################################ ARMORS #################################
#########################################################################

### Leather Armor
leather_armor = Item(
    char="[",
    fg=(255, 100, 50),
    name="Leather armor",
    entity_id="leather_armor",
    entity_desc="Leather armor desc",
    rarity=3,
    weight=4.5,
    price=300,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(),
    spawnable=True,
    flammable=1,##DEBUG
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.LeatherArmorEquipable()
)
item_lists.append(leather_armor)
item_rarity.append(leather_armor.rarity)
item_identified[leather_armor.entity_id] = 1


#########################################################################
############################### WEAPONS #################################
#########################################################################

### Shortsword
shortsword = Item(
    char=")",
    fg=(215, 219, 171),
    name="Shortsword",
    entity_id="shortsword",
    entity_desc="Shortsword desc",
    rarity=3,
    weight=1.5,
    price=250,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(),
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=15),
    equipable=equipable.ShortswordEquipable()
)
item_lists.append(shortsword)
item_rarity.append(shortsword.rarity)
item_identified[shortsword.entity_id] = 1 #NOTE: All weapons are semi-identified from the beginning


#########################################################################
############################### EDIBLES #################################
#########################################################################

### Corpses
corpse = Item(
    char="%",
    fg = (191, 0, 0),
    name="Corpse",# Name automatically changes later
    entity_id="corpse",
    entity_desc="corpse desc",
    rarity=0,
    weight=0,# Weight initialized when the actor dies
    price=2,
    item_type=InventoryOrder.FOOD,
    item_state=ItemState(
    ),
    spawnable=False,
    flammable=0.2,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    edible=None # Edible initialized when the actor is generated (status.py)
)
item_lists.append(corpse)
item_rarity.append(corpse.rarity) # All items should be appended regardless of its rarity
item_identified[corpse.entity_id] = 1 #NOTE: All corpses are semi-identified from the beginning


#########################################################################
################################# MISCS #################################
#########################################################################

### Toxic Goo
toxic_goo = Item(
    char="*",
    fg = (44, 23, 61),
    name="Toxic Goo",
    entity_id="toxic_goo",
    entity_desc="toxic goo desc",
    rarity=0,
    weight=0.1,
    price=0,
    item_type=InventoryOrder.MISC,
    item_state=ItemState(
    ),
    spawnable=False,
    flammable=0,
    droppable=True,
    stackable=True,
    throwable=throwable.ToxicGooThrowable(base_throw=1, additional_throw=1, break_chance=1, air_friction=2),
    edible=None
)
item_lists.append(toxic_goo)
item_rarity.append(toxic_goo.rarity)
item_identified[toxic_goo.entity_id] = 1

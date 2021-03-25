from components import readable, quaffable, equipable, throwable
from components.item_state import ItemState
from entity import Item
import anim_graphics
import components.edible as edible

from order import InventoryOrder

temp_items_lists = []
item_rarity = []


#########################################################################
################################ POTIONS ################################
#########################################################################

### Potion of healing
potion_of_healing = Item(
    should_randomize=True,
    char="!",
    fg=(127, 0, 255),
    name="회복의 물약",
    entity_id="potion_of_healing",
    entity_desc="Potion of healing desc",
    rarity=60, #DEBUG
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(break_chance=1),
    readable=None,
    quaffable=quaffable.PotionOfHealingQuaffable(amount=10),
)
temp_items_lists.append(potion_of_healing)
item_rarity.append(potion_of_healing.rarity)


### Potion of paralysis
potion_of_paralysis = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="마비 물약",
    entity_id="potion_of_paralysis",
    entity_desc="Potion of paralysis desc",
    rarity=6,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionOfParalysisThrowable(break_chance=1, penetration=True),
    readable=None,
    quaffable=quaffable.PotionOfParalysisQuaffable(turn=10),
)
temp_items_lists.append(potion_of_paralysis)
item_rarity.append(potion_of_paralysis.rarity)


### Potion of mosnter detection
potion_of_monster_detection = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="생명체 탐지의 물약",
    entity_id="potion_of_monster_detection",
    entity_desc="Potion of telepathy desc",
    rarity=6,
    weight=0.2,
    price=80,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(break_chance=1),
    readable=None,
    quaffable=quaffable.PotionOfMonsterDetectionQuaffable(turn=20),
)
temp_items_lists.append(potion_of_monster_detection)
item_rarity.append(potion_of_monster_detection.rarity)


#########################################################################
################################ SCROLLS ################################
#########################################################################

### Scroll of Confusion
scroll_of_confusion = Item(
    should_randomize=True,
    char="~",
    fg=(207, 63, 255),
    name="혼란의 주문서",
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
temp_items_lists.append(scroll_of_confusion)
item_rarity.append(scroll_of_confusion.rarity)


### Scroll of Meteor Storm
scroll_of_meteor_storm = Item(
    should_randomize=True,
    char="~",
    fg=(255, 100, 0),
    name="운석 폭풍의 주문서",
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
temp_items_lists.append(scroll_of_meteor_storm)
item_rarity.append(scroll_of_meteor_storm.rarity)


### Scroll of Thunderstorm
scroll_of_thunderstorm = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 0),
    name="천둥 폭풍의 주문서",
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
temp_items_lists.append(scroll_of_thunderstorm)
item_rarity.append(scroll_of_thunderstorm.rarity)


### Scroll of Lightning
scroll_of_lightning = Item(
    should_randomize=True,
    char="~",
    fg=(255, 252, 99),
    name="번개의 주문서",
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
temp_items_lists.append(scroll_of_lightning)
item_rarity.append(scroll_of_lightning.rarity)


### Scroll of magic missile
scroll_of_magic_missile = Item(
    should_randomize=True,
    char="~",
    fg=(100, 50, 255),
    name="마법 광선의 주문서",
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
temp_items_lists.append(scroll_of_magic_missile)
item_rarity.append(scroll_of_magic_missile.rarity)


### Scroll of magic mapping
scroll_of_magic_mapping = Item(
    should_randomize=True,
    char="~",
    fg=(255, 90, 90),
    name="마법 지도의 주문서",
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
temp_items_lists.append(scroll_of_magic_mapping)
item_rarity.append(scroll_of_magic_mapping.rarity)


### Scroll of piercing flame
scroll_of_piercing_flame = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 30),
    name="작열하는 창의 주문서",
    entity_id="scroll_of_piercing_flame",
    entity_desc="Scroll of piercing flame desc",
    rarity=4,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfPiercingFlameReadable(anim_graphic=anim_graphics.piercing_flame, damage=20, penetration=True),
    quaffable=None,
)
temp_items_lists.append(scroll_of_piercing_flame)
item_rarity.append(scroll_of_piercing_flame.rarity)


### Scroll of tame
scroll_of_tame = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 200),
    name="복종의 주문서",
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
    readable=readable.ScrollOfTameReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_tame)
item_rarity.append(scroll_of_tame.rarity)


### Scroll of enchantment
scroll_of_enchantment = Item(
    should_randomize=True,
    char="~",
    fg=(191, 255, 0),
    name="마법 강화의 주문서",
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
temp_items_lists.append(scroll_of_enchantment)
item_rarity.append(scroll_of_enchantment.rarity)


### Scroll of identify
scroll_of_identify = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name="감정의 주문서",
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
temp_items_lists.append(scroll_of_identify)
item_rarity.append(scroll_of_identify.rarity)


### Scroll of Remove Curse
scroll_of_remove_curse = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name="저주 해제의 주문서",
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
temp_items_lists.append(scroll_of_remove_curse)
item_rarity.append(scroll_of_remove_curse.rarity)


#########################################################################
################################ ARMORS #################################
#########################################################################

### Leather Armor
leather_armor = Item(
    char="[",
    fg=(255, 100, 50),
    name="가죽 갑옷",
    entity_id="leather_armor",
    entity_desc="Leather armor desc",
    rarity=3,
    weight=4.5,
    price=300,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=1,##DEBUG
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.LeatherArmorEquipable()
)
temp_items_lists.append(leather_armor)
item_rarity.append(leather_armor.rarity)


#########################################################################
############################### WEAPONS #################################
#########################################################################

### Shortsword
shortsword = Item(
    char=")",
    fg=(215, 219, 171),
    name="숏소드",
    entity_id="shortsword",
    entity_desc="Shortsword desc",
    rarity=3,
    weight=1.5,
    price=250,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.4,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=15),
    equipable=equipable.ShortswordEquipable(),
    lockpickable=(1,1),
)
temp_items_lists.append(shortsword)
item_rarity.append(shortsword.rarity)


#########################################################################
############################### AMULETS #################################
#########################################################################

### Amulet of Kugah
amulet_of_kugah = Item(
    indestructible=True,
    char="⊕",
    fg = (255, 72, 0),
    name="쿠가의 아뮬렛",
    entity_id="amulet_of_kugah",
    entity_desc="amulet of kugah desc",
    rarity=0,
    weight=0.2,
    price=0,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=2),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=15),
    equipable=equipable.AmuletOfKugahEquipable(),
    edible=None
)
temp_items_lists.append(amulet_of_kugah)
item_rarity.append(amulet_of_kugah.rarity)



#########################################################################
############################### EDIBLES #################################
#########################################################################

### Corpses
corpse = Item(
    char="%",
    fg = (191, 0, 0),
    name="시체",# Name automatically changes later
    entity_id="corpse",
    entity_desc="corpse desc",
    rarity=0,
    weight=0,# Weight initialized when the actor dies
    price=2,
    item_type=InventoryOrder.FOOD,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0.2,
    corrodible=0.2,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    edible=None # Edible initialized when the actor is generated (status.py)
)
temp_items_lists.append(corpse)
item_rarity.append(corpse.rarity) # All items should be appended regardless of its rarity


#########################################################################
################################# MISCS #################################
#########################################################################

### toxic Goo
toxic_goo = Item(
    char="*",
    fg = (44, 23, 61),
    name="독성 점액",
    entity_id="toxic_goo",
    entity_desc="toxic goo desc",
    rarity=0,
    weight=0.1,
    price=0,
    item_type=InventoryOrder.MISC,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.ToxicGooThrowable(base_throw=1, additional_throw=1, break_chance=1, air_friction=1),
    edible=edible.BlackJellyEdible()
)
temp_items_lists.append(toxic_goo)
item_rarity.append(toxic_goo.rarity)

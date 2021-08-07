from components import readable, quaffable, equipable, throwable
from components.item_state import ItemState
from entity import Item
import color
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
    rarity=60,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(break_chance=1),
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
    rarity=20,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(break_chance=1, trigger_if_thrown_at=True),
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
    rarity=10,
    weight=0.2,
    price=150,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(break_chance=1),
    readable=None,
    quaffable=quaffable.PotionOfMonsterDetectionQuaffable(turn=50),
)
temp_items_lists.append(potion_of_monster_detection)
item_rarity.append(potion_of_monster_detection.rarity)


### Potion of flame
potion_of_flame = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="화염의 물약",
    entity_id="potion_of_flame",
    entity_desc="Potion of flame desc",
    rarity=20,
    weight=0.2,
    price=80,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionOfFlameThrowable(break_chance=1, trigger_if_thrown_at=True),
    readable=None,
    quaffable=quaffable.PotionOfFlameQuaffable(base_dmg=10, add_dmg=2, turn=8, fire_lifetime=8),
)
temp_items_lists.append(potion_of_flame)
item_rarity.append(potion_of_flame.rarity)


### Potion of acid
potion_of_acid = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="강산성 물약",
    entity_id="potion_of_acid",
    entity_desc="Potion of acid desc",
    rarity=20,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(break_chance=1, trigger_if_thrown_at=True),
    readable=None,
    quaffable=quaffable.PotionOfAcidQuaffable(turn=15),
)
temp_items_lists.append(potion_of_acid)
item_rarity.append(potion_of_acid.rarity)


### Potion of frost
potion_of_frost = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="냉기의 물약",
    entity_id="potion_of_frost",
    entity_desc="Potion of frost desc",
    rarity=20,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionOfFrostThrowable(break_chance=1, trigger_if_thrown_at=True),
    readable=None,
    quaffable=quaffable.PotionOfFrostQuaffable(turn=7),
)
temp_items_lists.append(potion_of_frost)
item_rarity.append(potion_of_frost.rarity)


### Potion of poison
potion_of_poison = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="맹독의 물약",
    entity_id="potion_of_poison",
    entity_desc="Potion of poison desc",
    rarity=20,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(break_chance=1, trigger_if_thrown_at=True),
    readable=None,
    quaffable=quaffable.PotionOfPoisonQuaffable(turn=16),
)
temp_items_lists.append(potion_of_poison)
item_rarity.append(potion_of_poison.rarity)


### Potion of levitation
potion_of_levitation = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="공중 부양의 물약",
    entity_id="potion_of_levitation",
    entity_desc="",
    rarity=30,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(break_chance=1, trigger_if_thrown_at=True),
    readable=None,
    quaffable=quaffable.PotionOfLevitationQuaffable(turn=50),
)
temp_items_lists.append(potion_of_levitation)
item_rarity.append(potion_of_levitation.rarity)


### Potion of liquified ants
potion_of_liquified_ants = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="액화 개미 물약",
    entity_id="potion_of_liquified_ants",
    entity_desc="",
    rarity=20,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionOfLiquifiedAntsThrowable(break_chance=1, trigger_if_thrown_at=True),
    readable=None,
    quaffable=quaffable.PotionOfLiquifiedAntsQuaffable(turn=5),
)
temp_items_lists.append(potion_of_liquified_ants)
item_rarity.append(potion_of_liquified_ants.rarity)


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
    rarity=30,
    weight=0.1,
    price=200,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    corrodible=0.3,
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
    rarity=20,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    corrodible=0.3,
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
    rarity=10,
    weight=0.1,
    price=400,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    corrodible=0.3,
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
    rarity=20,
    weight=0.1,
    price=200,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    corrodible=0.3,
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
    rarity=40,
    weight=0.1,
    price=250,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    corrodible=0.3,
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
    rarity=40,
    weight=0.1,
    price=250,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    corrodible=0.3,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfMagicMappingReadable(tier=1),
    quaffable=None,
)
temp_items_lists.append(scroll_of_magic_mapping)
item_rarity.append(scroll_of_magic_mapping.rarity)


### Scroll of scorching ray
scroll_of_scorching_ray = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 30),
    name="맹렬한 화염 광선의 주문서",
    entity_id="scroll_of_scorching_ray",
    entity_desc="Scroll of scorching ray desc",
    rarity=20,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0.3,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfScorchingRayReadable(anim_graphic=anim_graphics.scorching_ray, damage=20, penetration=True),
    quaffable=None,
)
temp_items_lists.append(scroll_of_scorching_ray)
item_rarity.append(scroll_of_scorching_ray.rarity)


### Scroll of piercing flame
scroll_of_freezing_ray = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 30),
    name="얼어붙는 빙결 광선의 주문서",
    entity_id="scroll_of_freezing_ray",
    entity_desc="Scroll of freezing ray desc",
    rarity=20,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.5,
    corrodible=0.3,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfFreezingRayReadable(anim_graphic=anim_graphics.freezing_ray, damage=10, effect_dmg=6, penetration=True),
    quaffable=None,
)
temp_items_lists.append(scroll_of_freezing_ray)
item_rarity.append(scroll_of_freezing_ray.rarity)


### Scroll of tame
scroll_of_tame = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 200),
    name="복종의 주문서",
    entity_id="scroll_of_tame",
    entity_desc="Scroll of tame desc",
    rarity=10,
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
    rarity=40,
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
    rarity=60,
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
    rarity=40,
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

### Rags
rags = Item(
    char="[",
    fg=(231, 255, 173),
    name="천쪼가리",
    entity_id="rags",
    entity_desc="rags desc",
    rarity=5,
    weight=0.3,
    price=1,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=1,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=40),
    equipable=equipable.RagsEquipable()
)
temp_items_lists.append(rags)
item_rarity.append(rags.rarity)


### Leather Armor
leather_armor = Item(
    char="[",
    fg=(255, 100, 50),
    name="가죽 갑옷",
    entity_id="leather_armor",
    entity_desc="Leather armor desc",
    rarity=5,
    weight=4.5,
    price=300,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0.08,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.LeatherArmorEquipable()
)
temp_items_lists.append(leather_armor)
item_rarity.append(leather_armor.rarity)


### Merchant robe
merchant_robe = Item(
    char="[",
    fg=(120, 60, 250),
    name="상인의 로브",
    entity_id="merchant_robe",
    entity_desc="Merchant Robe desc",
    rarity=0,
    weight=3.3,
    price=410,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=25),
    equipable=equipable.MerchantRobeEquipable()
)
temp_items_lists.append(merchant_robe)
item_rarity.append(merchant_robe.rarity)


### Silk Dress
silk_dress = Item(
    char="[",
    fg=(255, 222, 251),
    name="실크 드레스",
    entity_id="silk_dress",
    entity_desc="Silk dress desc",
    rarity=1,
    weight=0.8,
    price=5,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0.9,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=25),
    equipable=equipable.SilkDressEquipable()
)
temp_items_lists.append(silk_dress)
item_rarity.append(silk_dress.rarity)


#########################################################################
######################### MELEE WEAPONS #################################
#########################################################################

### Iron Dagger
iron_dagger = Item(
    char=")",
    fg=(255, 145, 0),
    name="철제 단검",
    entity_id="iron_dagger",
    entity_desc="Irondagger desc",
    rarity=10,
    weight=0.4,
    price=8,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.5,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=6, additional_throw=3, penetration=True, air_friction=1),
    equipable=equipable.IronDaggerEquipable(),
    lockpickable=(1,0.1),
)
temp_items_lists.append(iron_dagger)
item_rarity.append(iron_dagger.rarity)

### Shortsword
shortsword = Item(
    char=")",
    fg=(215, 219, 171),
    name="숏소드",
    entity_id="shortsword",
    entity_desc="Shortsword desc",
    rarity=9,
    weight=1.5,
    price=25,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.4,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=15),
    equipable=equipable.ShortswordEquipable(),
    lockpickable=(1,0.1),
)
temp_items_lists.append(shortsword)
item_rarity.append(shortsword.rarity)


### Longsword
longsword = Item(
    char=")",
    fg=(152, 227, 226),
    name="롱소드",
    entity_id="longsword",
    entity_desc="longsword desc",
    rarity=5,
    weight=1.8,
    price=75,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.4,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=20),
    equipable=equipable.LongswordEquipable(),
    lockpickable=(0.8,0.1),
)
temp_items_lists.append(longsword)
item_rarity.append(longsword.rarity)


### Giant Wood Club
giant_wood_club = Item(
    char=")",
    fg=(97, 53, 0),
    name="통나무 곤봉",
    entity_id="giant_wood_club",
    entity_desc="giant_wood_club desc",
    rarity=1,
    weight=284,
    price=5,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.2,
    corrodible=0,
    spawnable=False,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=20),
    equipable=equipable.GiantWoodClubEquipable(),
    lockpickable=(0,0),
)
temp_items_lists.append(giant_wood_club)
item_rarity.append(giant_wood_club.rarity)


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
################################# GEMS ##################################
#########################################################################

### Diamond
diamond = Item(
    should_randomize=True,
    char="*",
    fg = (255, 255, 255),
    name="다이아몬드",
    entity_id="diamond",
    entity_desc="diamond desc",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(diamond)
item_rarity.append(diamond.rarity)


### Ruby
ruby = Item(
    should_randomize=True,
    char="*",
    fg = (255, 0, 38),
    name="루비",
    entity_id="ruby",
    entity_desc="ruby desc",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(diamond)
item_rarity.append(diamond.rarity)


### Emerald
emerald = Item(
    should_randomize=True,
    char="*",
    fg = (21, 207, 0),
    name="에메랄드",
    entity_id="emerald",
    entity_desc="emerald desc",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(emerald)
item_rarity.append(emerald.rarity)


### Sapphire
sapphire = Item(
    should_randomize=True,
    char="*",
    fg = (0, 162, 255),
    name="사파이어",
    entity_id="sapphire",
    entity_desc="sapphire desc",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(sapphire)
item_rarity.append(sapphire.rarity)


### Worthless piece of white glass
worthless_piece_of_white_glass = Item(
    should_randomize=True,
    char="*",
    fg = (255, 255, 255),
    name="하얀색 싸구려 유리 조각",
    entity_id="worthless_piece_of_white_glass",
    entity_desc="worthless piece of white glass desc",
    rarity=2,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(worthless_piece_of_white_glass)
item_rarity.append(worthless_piece_of_white_glass.rarity)


### Worthless piece of red glass
worthless_piece_of_red_glass = Item(
    should_randomize=True,
    char="*",
    fg = (255, 0, 38),
    name="빨간색 싸구려 유리 조각",
    entity_id="worthless_piece_of_red_glass",
    entity_desc="worthless piece of red glass desc",
    rarity=2,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(worthless_piece_of_red_glass)
item_rarity.append(worthless_piece_of_red_glass.rarity)


### Worthless piece of green glass
worthless_piece_of_green_glass = Item(
    should_randomize=True,
    char="*",
    fg = (21, 207, 0),
    name="초록색 싸구려 유리 조각",
    entity_id="worthless_piece_of_green_glass",
    entity_desc="worthless piece of green glass desc",
    rarity=1,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(worthless_piece_of_green_glass)
item_rarity.append(worthless_piece_of_green_glass.rarity)


### Worthless piece of blue glass
worthless_piece_of_blue_glass = Item(
    should_randomize=True,
    char="*",
    fg = (0, 162, 255),
    name="파랑색 싸구려 유리 조각",
    entity_id="worthless_piece_of_blue_glass",
    entity_desc="worthless_piece_of_blue_glass desc",
    rarity=1,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(worthless_piece_of_blue_glass)
item_rarity.append(worthless_piece_of_blue_glass.rarity)



#########################################################################
################################# MISCS #################################
#########################################################################

### toxic Goo
toxic_goo = Item(
    char="•",# Unicode bullet
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
    change_stack_count_when_dropped=(1,1),
    stackable=False,
    throwable=throwable.ToxicGooThrowable(base_throw=1, additional_throw=1, break_chance=1, air_friction=1, trigger_if_thrown_at=True),
    edible=edible.BlackJellyEdible()
)
temp_items_lists.append(toxic_goo)
item_rarity.append(toxic_goo.rarity)


#########################################################################
################################# CASH ##################################
#########################################################################

### Shine
shine = Item(
    char="$",
    fg = color.gold,
    name="샤인",
    entity_id="shine",
    entity_desc="shine desc",
    rarity=0,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.CASH,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    counter_at_front=True,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=1, break_chance=0, air_friction=1),
    edible=None
)
temp_items_lists.append(shine)
item_rarity.append(shine.rarity)

shines = lambda amount: Item(
    char="$",
    fg = color.gold,
    name="샤인",
    entity_id="shine",
    entity_desc="shine desc",
    rarity=0,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.CASH,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    counter_at_front=True,
    stack_count=amount,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=1, break_chance=0, air_friction=1),
    edible=None
)
from components import readable, quaffable, equipable, throwable, usable
from components.item_state import ItemState
from entity import Item
from language import interpret as t
import color
import anim_graphics
import components.edible as edible
import ability_factories

from order import InventoryOrder, EquipableOrder

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
    name=t("회복의 물약", "potion of healing"),
    entity_id="potion_of_healing",
    entity_desc=("회복의 물약은 유기체의 손상된 조직을 빠른 속도로 치유한다. "
                 "흥미롭게도 회복의 물약의 구체적인 작동 원리는 밝혀지지 않은 채 조제법 만이 전해져 내려오고 있는데, "
                 "대다수의 포션술사들은 회복의 물약이 몇 백여년 간 대대로 연구된 끝에 만들어진 포션학의 결정체일 것이라고 추측한다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
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
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # handles in quaffable
    ), # Handle in quaffable. Only identified when actor is healed.
    readable=None,
    quaffable=quaffable.PotionOfHealingQuaffable(heal_range=(70,100)),
)
temp_items_lists.append(potion_of_healing)
item_rarity.append(potion_of_healing.rarity)


### Potion of mana
potion_of_mana = Item(
    should_randomize=True,
    char="!",
    fg=(127, 0, 255),
    name=t("마나 회복의 물약", "potion of mana"),
    entity_id="potion_of_mana",
    entity_desc=("마나 회복의 물약은 음용자의 마나를 회복시킨다. "
                 "물약 속에는 다량의 마법 에너지들이 농축되어 있으며, 때문에 마나 회복의 물약을 만들기 위해서는 살아있는 생명체의 마나를 뽑아내는 과정이 필요하다. "
                 "일부 포션술사들은 이같은 제조법을 '반인륜적이다'라고 비판하고 있으며, 때문에 기존의 제조법을 대체할 새로운 방법이 연구중에 있다."
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
    rarity=40,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0
    ), # Handle in quaffable. Only identified when actor is healed.
    readable=None,
    quaffable=quaffable.PotionOfManaQuaffable(gain_range=(50,100)),
)
temp_items_lists.append(potion_of_mana)
item_rarity.append(potion_of_mana.rarity)


### Potion of paralysis
potion_of_paralysis = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name=t("마비 물약", "potion of paralysis"),
    entity_id="potion_of_paralysis",
    entity_desc=("마비 물약은 생명체를 일시적으로 마비시킬 수 있는 위험한 포션이다. "
                 "주로 사냥꾼들이 위험한 야수들을 사냥할 때 사용하곤 한다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
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
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # Handles in quaffable
    ), # Handle in quaffable
    readable=None,
    quaffable=quaffable.PotionOfParalysisQuaffable(turn=10),
)
temp_items_lists.append(potion_of_paralysis)
item_rarity.append(potion_of_paralysis.rarity)


### Potion of sleep
potion_of_sleep = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name=t("수면 물약", "potion of sleep"),
    entity_id="potion_of_sleep",
    entity_desc=("수면 물약은 생명체를 순식간에 깊은 잠에 빠지게 만든다. "
                 "생명체는 통상적인 수면보다 깊게 잠들게 되지만, 외부로부터의 충격을 받으면 잠에서 깰 수 있다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
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
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=1
    ), # Handle in quaffable
    readable=None,
    quaffable=quaffable.PotionOfSleepQuaffable(turn=20),
)
temp_items_lists.append(potion_of_sleep)
item_rarity.append(potion_of_sleep.rarity)


### Potion of mosnter detection
potion_of_monster_detection = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name=t("생명체 탐지의 물약", "potion of monster detection"),
    entity_id="potion_of_monster_detection",
    entity_desc=("모든 생명체는 약간이지만 다른 생명체의 마력을 감지할 수 있는데, 우리가 간혹 '인기척이 느껴진다'는 기분을 받는 것도 이 때문이다. "
                 "생명체 탐지의 물약은 이 감각을 극도로 증폭시켜 복용자가 일시적으로 주변의 다른 생명체들을 감지할 수 있도록 만든다."
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
    rarity=20,
    weight=0.2,
    price=150,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0
        ),
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
    name=t("화염의 물약", "potion of flame"),
    entity_id="potion_of_flame",
    entity_desc=("화염의 물약은 대기와 반응해 불꽃을 일으킨다. "
                 "과거 화염 물약을 연료로 사용하려는 시도가 있었지만, 수많은 인명피해가 발생하고 나서 이러한 시도는 금지되었다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
    rarity=40,
    weight=0.2,
    price=80,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionOfFlameThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=1,
        identify_when_collided_with_entity=1,
        identify_when_collided_with_actor=1, # handle in quaffable
    ),
    readable=None,
    quaffable=quaffable.PotionOfFlameQuaffable(base_dmg=10, add_dmg=2, turn=6, fire_lifetime=10),
)
temp_items_lists.append(potion_of_flame)
item_rarity.append(potion_of_flame.rarity)


### Potion of acid
potion_of_acid = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name=t("강산성 물약", "potion of acid"),
    entity_id="potion_of_acid",
    entity_desc=("강산성 물약은 산성을 띄는 화합물들에 마법적 변이를 가해 만든 물약으로, 이를 다룰 때는 극도로 주의를 기울여야 한다."
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
    rarity=40,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # handles in quaffable
    ),
    readable=None,
    quaffable=quaffable.PotionOfAcidQuaffable(turn=8),
)
temp_items_lists.append(potion_of_acid)
item_rarity.append(potion_of_acid.rarity)


### Potion of frost
potion_of_frost = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name=t("냉기의 물약", "potion of frost"),
    entity_id="potion_of_frost",
    entity_desc=("냉기의 물약은 대기와 반응하면 순식간에 얼어붙는 성질을 지녔다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
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
    throwable=throwable.PotionOfFrostThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # handles in quaffable
    ),
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
    name=t("맹독의 물약", "potion of poison"),
    entity_id="potion_of_poison",
    entity_desc=("맹독의 물약은 다양한 독성 화합물들에 마법적 변이를 가해 만든 물약으로, 대부분의 생명체들에게 치명적인 효과를 줄 수 있다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
    rarity=35,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # handles in quaffable
    ),
    readable=None,
    quaffable=quaffable.PotionOfPoisonQuaffable(turn=8),
)
temp_items_lists.append(potion_of_poison)
item_rarity.append(potion_of_poison.rarity)


### Potion of levitation
potion_of_levitation = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name=t("공중 부양의 물약", "potion of levitation"),
    entity_id="potion_of_levitation",
    entity_desc=("공중 부양의 물약은 음용자를 일시적으로 지상에서 다섯 뼘 정도 떠오르게 만든다. "),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
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
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # handles in quaffable
    ),
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
    name=t("액화 개미 물약", "potion of liquified ants"),
    entity_id="potion_of_liquified_ants",
    entity_desc=("액화 개미의 물약은 말 그대로 개미들에 마법적 변이를 가해 액체 형태로 만든 물약으로, "
                 "물약은 대기와 반응하여 다시 고체 형태의 개미들로 되돌아온다."
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
    rarity=40,
    weight=0.2,
    price=100,
    item_type=InventoryOrder.POTION,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.PotionOfLiquifiedAntsThrowable(
        base_throw=0,
        additional_throw=0,
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=1,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0,
    ),
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
    name=t("혼란의 주문서", "scroll of confusion"),
    entity_id="scroll_of_confusion",
    entity_desc=("혼란의 주문서를 읽은 사용자는 한 차례 자신이 원하는 생명체를 선택해 그 생명체의 사고를 방해해 혼란스럽게 만들 수 있다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    ),
    rarity=43,
    weight=0.1,
    price=200,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
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
    name=t("운석 폭풍의 주문서", "scroll of meteor storm"),
    entity_id="scroll_of_meteor_storm",
    entity_desc=("운석 폭풍의 주문서를 읽은 사용자는 한 차례 자신이 원하는 공간에 거대한 운석을 소환할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=30,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfMeteorStormReadable(damage_range=(50,85), radius=1),
    quaffable=None,
)
temp_items_lists.append(scroll_of_meteor_storm)
item_rarity.append(scroll_of_meteor_storm.rarity)


### Scroll of Lightning
scroll_of_lightning = Item(
    should_randomize=True,
    char="~",
    fg=(255, 252, 99),
    name=t("번개의 주문서", "scroll of lightning"),
    entity_id="scroll_of_lightning",
    entity_desc=("번개의 주문서를 읽으면 읽은 사용자의 주변에 강력한 방전 현상이 발생해 주위 생명체에 강력한 번개를 내리친다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=40,
    weight=0.1,
    price=200,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfLightningReadable(damage_range=(38, 45), fx_id="fx_lightning", maximum_range=20),
    quaffable=None,
)
temp_items_lists.append(scroll_of_lightning)
item_rarity.append(scroll_of_lightning.rarity)


### Scroll of magic missile
scroll_of_magic_missile = Item(
    should_randomize=True,
    char="~",
    fg=(100, 50, 255),
    name=t("마법 광선의 주문서", "scroll of magic missile"),
    entity_id="scroll_of_magic_missile",
    entity_desc=("마법 광선의 주문서를 읽은 사용자는 강력한 마법 에너지가 내재된 광선을 발사할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=55,
    weight=0.1,
    price=250,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfMagicMissileReadable(anim_graphic=anim_graphics.magic_missile, damage_range=(45, 65), penetration=True),
    quaffable=None,
)
temp_items_lists.append(scroll_of_magic_missile)
item_rarity.append(scroll_of_magic_missile.rarity)


### Scroll of digging
scroll_of_digging = Item(
    should_randomize=True,
    char="~",
    fg=(100, 50, 255),
    name=t("굴착의 주문서", "scroll of digging"),
    entity_id="scroll_of_digging",
    entity_desc=("굴착의 주문서를 읽은 사용자는 대부분의 지형을 파괴시킬 수 있는 광선을 발사할 수 있게 된다. "
                 "이 광선은 대부분의 생명체에게는 아무런 피해를 주지 않는 것으로 알려져 있다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=30,
    weight=0.1,
    price=250,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfDiggingReadable(anim_graphic=anim_graphics.digging_ray, penetration=True, wall_penetration_cnt=3),
    quaffable=None,
)
temp_items_lists.append(scroll_of_digging)
item_rarity.append(scroll_of_digging.rarity)


### Scroll of magic mapping
scroll_of_magic_mapping = Item(
    should_randomize=True,
    char="~",
    fg=(255, 90, 90),
    name=t("마법 지도의 주문서", "scroll of magic mapping"),
    entity_id="scroll_of_magic_mapping",
    entity_desc=("마법 지도의 주문서를 읽은 사용자는 주위의 공간적 정보들을 일시적으로 인식할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=50,
    weight=0.1,
    price=250,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfMagicMappingReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_magic_mapping)
item_rarity.append(scroll_of_magic_mapping.rarity)


### Scroll of scorching ray
scroll_of_scorching_ray = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 30),
    name=t("맹렬한 화염 광선의 주문서", "scroll of scorching ray"),
    entity_id="scroll_of_scorching_ray",
    entity_desc=("맹렬한 화염 광선의 주문서를 읽은 사용자는 주위 것들을 태워버리는 강렬한 화염으로 이루어진 광선을 발사할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=35,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfScorchingRayReadable(anim_graphic=anim_graphics.scorching_ray, damage_range=(20,50), penetration=True),
    quaffable=None,
)
temp_items_lists.append(scroll_of_scorching_ray)
item_rarity.append(scroll_of_scorching_ray.rarity)


### Scroll of piercing flame
scroll_of_freezing_ray = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 30),
    name=t("얼어붙는 빙결 광선의 주문서", "scroll of freezing ray"),
    entity_id="scroll_of_freezing_ray",
    entity_desc=("얼어붙는 빙결 광선의 주문서를 읽은 사용자는 주위 것들을 얼려버리는 차가운 냉기로 이루어진 광선을 발사할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=35,
    weight=0.1,
    price=300,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfFreezingRayReadable(anim_graphic=anim_graphics.freezing_ray, damage_range=(18,66), penetration=True),
    quaffable=None,
)
temp_items_lists.append(scroll_of_freezing_ray)
item_rarity.append(scroll_of_freezing_ray.rarity)


### Scroll of tame
scroll_of_tame = Item(
    should_randomize=True,
    char="~",
    fg=(255, 0, 200),
    name=t("복종의 주문서", "scroll of tame"),
    entity_id="scroll_of_tame",
    entity_desc=("복종의 주문서를 읽은 사용자는 다른 생명체를 복종시킬 수 있는 강력한 고위 주문을 한 차례 사용할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=25,
    weight=0.1,
    price=400,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
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
    name=t("마법 강화의 주문서", "scroll of enchantment"),
    entity_id="scroll_of_enchantment",
    entity_desc=("마법 강화의 주문서를 읽은 사용자는 보유 중인 도구에 마법 에너지를 부여해 도구의 성능을 강화할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=75,
    weight=0.1,
    price=400,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
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
    name=t("감정의 주문서", "scroll of identify"),
    entity_id="scroll_of_identify",
    entity_desc=("감정의 주문서를 읽은 사용자는 원하는 물품의 성질에 대해 더 자세하게 이해할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=95,
    weight=0.1,
    price=50,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfIdentifyReadable(),
    quaffable=None,
    initial_BUC={1:1,0:15,-1:1} # rarely blessed
)
temp_items_lists.append(scroll_of_identify)
item_rarity.append(scroll_of_identify.rarity)


### Scroll of Remove Curse
scroll_of_remove_curse = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name=t("저주 해제의 주문서", "scroll of remove curse"),
    entity_id="scroll_of_remove_curse",
    entity_desc=("저주 해제의 주문서를 읽은 사용자는 물건에 걸린 저주를 제거할 수 있는 강력한 고위 마법을 한 차례 사용할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=60,
    weight=0.1,
    price=150,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfRemoveCurseReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_remove_curse)
item_rarity.append(scroll_of_remove_curse.rarity)


### Scroll of Teleportation
scroll_of_teleportation = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name=t("순간 이동의 주문서", "scroll of teleportation"),
    entity_id="scroll_of_teleportation",
    entity_desc=("순간 이동의 주문서를 읽은 사용자는 물리적으로 떨어진 공간으로 순간 이동을 할 수 있는 고위 마법을 한 차례 사용할 수 있게 된다. "
                 "불안정한 이동을 하는 경우가 잦다고 한다. "
                 ),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=65,
    weight=0.1,
    price=175,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfTeleportationReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_teleportation)
item_rarity.append(scroll_of_teleportation.rarity)


### Scroll of Destroy Equipment
scroll_of_destroy_equipment = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name=t("장착품 파괴의 주문서", "scroll of destroy equipment"),
    entity_id="scroll_of_destroy_equipment",
    entity_desc=("장착품 파괴의 주문서는 사용자가 장비한 임의의 장착품 하나에 강력한 마법 에너지를 투사해 마법적으로 붕괴시킨다."),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=50,
    weight=0.1,
    price=175,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfDestroyEquipmentReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_destroy_equipment)
item_rarity.append(scroll_of_destroy_equipment.rarity)


### Scroll of Hatred
scroll_of_hatred = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name=t("증오의 주문서", "scroll of hatred"),
    entity_id="scroll_of_hatred",
    entity_desc=("증오의 주문서는 주변의 생명체들에게 사용자를 향한 강한 증오감을 심어준다."),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=45,
    weight=0.1,
    price=150,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfHatredReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_hatred)
item_rarity.append(scroll_of_hatred.rarity)


### Scroll of Conflict
scroll_of_conflict = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name=t("불화의 주문서", "scroll of conflict"),
    entity_id="scroll_of_conflict",
    entity_desc=("불화의 주문서는 자신을 포함한 주변 생명체들에게 걷잡을 수 없는 분노를 느끼게 만들어 서로 간의 불화를 발생시킨다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=55,
    weight=0.1,
    price=150,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfConflictReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_conflict)
item_rarity.append(scroll_of_conflict.rarity)


### Scroll of Summoning
scroll_of_summoning = Item(
    should_randomize=True,
    char="~",
    fg=(255, 255, 200),
    name=t("소환의 주문서", "scroll of summoning"),
    entity_id="scroll_of_summoning",
    entity_desc=("소환의 주문서는 무작위의 생명체를 주변에 소환시킨다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "
                    "같은 종류의 주문서를 사용하더라도 주문서가 저주받았다면 전혀 다른 결과를 가져올 수도 있다. "),
    rarity=40,
    weight=0.1,
    price=150,
    item_type=InventoryOrder.SCROLL,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.1,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.ScrollOfSummoningReadable(),
    quaffable=None,
)
temp_items_lists.append(scroll_of_summoning)
item_rarity.append(scroll_of_summoning.rarity)


#########################################################################
############################# SKILLBOOKS ################################
#########################################################################

### steal skillbook
steal_skillbook = Item(
    should_randomize=False, # NOTE: Skillbook names are not randomized.
    char="=",
    fg=(255, 255, 200),
    name=t("'대도둑 레오파드의 소매치기 특강'이라고 적힌 책",
           "A book called 'Tips and tricks for thieves written by the Great Theif Leopard'"),
    entity_id="steal_skillbook",
    entity_desc=("표지에 큼지막한 글씨로 저자의 이름이 적혀있다. "),
    rarity=2,
    weight=0.67,
    price=320,
    item_type=InventoryOrder.SKILLBOOK,
    item_state=ItemState(is_identified=1), # Skillbooks are identified
    spawnable=True,
    flammable=0.3,
    corrodible=0.08,
    droppable=True,
    stackable=False,
    cursable=False, # Skillbooks are not cursable
    blessable=False, # Skillbooks are not blessable
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.BookReadable(
        ability=ability_factories.steal,
        int_req=11,
        read_msg=t("책에는 어떻게 하면 들키지 않고 소매치기를 할 수 있는지에 대한 내용들이 적혀있다.",
                   "The book explains a variety of ways to steal things without getting caught."),
        comprehension_chance_per_int_bonus=1, # Guarenteed
    ),
    quaffable=None,
)
temp_items_lists.append(steal_skillbook)
item_rarity.append(steal_skillbook.rarity)


### satanic bible
# Technically not a skillbook
satanic_bible = Item(
    should_randomize=False,
    char="=",
    fg=(161, 0, 0),
    name=t("악마의 성서", "satanic bible"),
    entity_id="satanic_bible",
    entity_desc=t("알 수 없는 언어가 빼곡히 적혀있다. 중간중간 의미를 알 수 없는 삽화들이 그려져 있다. 책 표지는 파충류의 비늘과도 유사한 무언가로 만들어져 있다.",
                  "The book contains unrecognizable glyphs and odd pictures. The cover of the book is made of something that resembles a scale of a snake."),
    rarity=0,
    weight=0.66,
    price=13,
    item_type=InventoryOrder.SKILLBOOK,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.SatanicBibleBookReadable(
        ability=None,
        int_req=17,
        comprehension_chance_per_int_bonus=0.5,
    ),
    quaffable=None,
    initial_BUC={1:0,0:0,-1:1},
    uncursable=False,
    blessable=False,
)
temp_items_lists.append(satanic_bible)
item_rarity.append(satanic_bible.rarity)


#########################################################################
############################# SPELLBOOKS ################################
#########################################################################

### lightning bolt spellbook
lightning_bolt_spellbook = Item(
    should_randomize=True,
    char="=",
    fg=(255, 255, 200),
    name=t("뇌격 마법서", "spellbook of lightning bolt"),
    entity_id="lightning_bolt_spellbook",
    item_type_desc=("마법서는 단순한 책들과는 격을 달리 하는 물건이다. "
                    "이들은 막대한 마법 에너지를 사용해 제작되며, 그 내용도 쉽게 이해하기 어려운 경우가 많다."),
    rarity=8,
    weight=0.85,
    price=480,
    item_type=InventoryOrder.SPELLBOOK,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.08,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.BookReadable(
        ability=ability_factories.lightning_bolt,
        int_req=17,
        comprehension_chance_per_int_bonus=0.1,
    ),
    quaffable=None,
)
temp_items_lists.append(lightning_bolt_spellbook)
item_rarity.append(lightning_bolt_spellbook.rarity)


### Soul bolt spellbook
soul_bolt_spellbook = Item(
    should_randomize=True,
    char="=",
    fg=(255, 255, 200),
    name=t("소울 볼트 마법서", "spellbook of soul bolt"),
    entity_id="soul_bolt_spellbook",
    item_type_desc=("마법서는 단순한 책들과는 격을 달리 하는 물건이다. "
                    "이들은 막대한 마법 에너지를 사용해 제작되며, 그 내용도 쉽게 이해하기 어려운 경우가 많다."),
    rarity=10,
    weight=0.85,
    price=480,
    item_type=InventoryOrder.SPELLBOOK,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.08,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.BookReadable(
        ability=ability_factories.soul_bolt,
        int_req=15,
        comprehension_chance_per_int_bonus=0.1,
    ),
    quaffable=None,
)
temp_items_lists.append(soul_bolt_spellbook)
item_rarity.append(soul_bolt_spellbook.rarity)


### Cure wound spellbook
cure_wound_spellbook = Item(
    should_randomize=True,
    char="=",
    fg=(255, 255, 200),
    name=t("상처 치유 마법서", "spellbook of cure wound"),
    entity_id="cure_wound_spellbook",
    item_type_desc=("마법서는 단순한 책들과는 격을 달리 하는 물건이다. "
                    "이들은 막대한 마법 에너지를 사용해 제작되며, 그 내용도 쉽게 이해하기 어려운 경우가 많다."),
    rarity=7,
    weight=0.85,
    price=480,
    item_type=InventoryOrder.SPELLBOOK,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.08,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.BookReadable(
        ability=ability_factories.cure_wound,
        int_req=16,
        comprehension_chance_per_int_bonus=0.2,
    ),
    quaffable=None,
)
temp_items_lists.append(cure_wound_spellbook)
item_rarity.append(cure_wound_spellbook.rarity)


### Mesmerize spellbook
mesmerize_spellbook = Item(
    should_randomize=True,
    char="=",
    fg=(255, 255, 200),
    name=t("매혹 마법서", "spellbook of mesmerization"),
    entity_id="mesmerize_spellbook",
    item_type_desc=("마법서는 단순한 책들과는 격을 달리 하는 물건이다. "
                    "이들은 막대한 마법 에너지를 사용해 제작되며, 그 내용도 쉽게 이해하기 어려운 경우가 많다."),
    rarity=8,
    weight=0.85,
    price=480,
    item_type=InventoryOrder.SPELLBOOK,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.08,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.BookReadable(
        ability=ability_factories.mesmerize,
        int_req=15,
        comprehension_chance_per_int_bonus=0.3,
    ),
    quaffable=None,
)
temp_items_lists.append(mesmerize_spellbook)
item_rarity.append(mesmerize_spellbook.rarity)


### Teleport spellbook
teleport_spellbook = Item(
    should_randomize=True,
    char="=",
    fg=(255, 255, 200),
    name=t("순간이동 마법서", "spellbook of teleportation"),
    entity_id="teleport_spellbook",
    item_type_desc=("마법서는 단순한 책들과는 격을 달리 하는 물건이다. "
                    "이들은 막대한 마법 에너지를 사용해 제작되며, 그 내용도 쉽게 이해하기 어려운 경우가 많다."),
    rarity=10,
    weight=0.85,
    price=480,
    item_type=InventoryOrder.SPELLBOOK,
    item_state=ItemState(),
    spawnable=True,
    flammable=0.3,
    corrodible=0.08,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=20),
    readable=readable.BookReadable(
        ability=ability_factories.teleport,
        int_req=18,
        comprehension_chance_per_int_bonus=0.1,
    ),
    quaffable=None,
)
temp_items_lists.append(teleport_spellbook)
item_rarity.append(teleport_spellbook.rarity)


#########################################################################
################################ ARMORS #################################
#########################################################################


####################### TORSO ################################
### Rags
rags = Item(
    char="[",
    fg=(231, 255, 173),
    name=t("천쪼가리", "rags"),
    entity_id="rags",
    entity_desc=("다 헤져가는 천 쪼가리이다. "),
    rarity=7,
    weight=0.3,
    price=1,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=1,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=40),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 6),
        possible_regions=("leg", "torso",),
        str_requirement=4,
        protection=1,
        charm=-1,
        protection_mag=1,
    )
)
temp_items_lists.append(rags)
item_rarity.append(rags.rarity)


### Leather Armor
leather_armor = Item(
    char="[",
    fg=(255, 100, 50),
    name=t("가죽 갑옷", "leather armor"),
    entity_id="leather_armor",
    entity_desc=("질긴 가죽을 덧대 만든 갑옷이다. "),
    rarity=5,
    weight=4.5,
    price=300,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0.08,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 5),
        possible_regions=("torso",),
        str_requirement=11,
        protection=6,
        protection_mag=1.8,
    )
)
temp_items_lists.append(leather_armor)
item_rarity.append(leather_armor.rarity)


### Iron Chain mail
iron_chain_mail = Item(
    char="[",
    fg=(94, 255, 0),
    name=t("철제 사슬 갑옷", "iron chain mail"),
    entity_id="iron_chain_mail",
    entity_desc=("철로 만든 사슬들을 엮어 만든 갑옷이다. "),
    rarity=3,
    weight=17.9,
    price=10,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 5),
        possible_regions=("torso",),
        str_requirement=15,
        protection=8,
        protection_mag=2.8,
    )
)
temp_items_lists.append(iron_chain_mail)
item_rarity.append(iron_chain_mail.rarity)


### Iron Scale Armor
iron_scale_armor = Item(
    char="[",
    fg=(166, 255, 254),
    name=t("철제 비늘 갑옷", "iron scale armor"),
    entity_id="iron_scale_armor",
    entity_desc=("작은 철판들을 가죽에 덧대 만든 갑옷이다. "),
    rarity=3,
    weight=16.9,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 5),
        possible_regions=("torso",),
        str_requirement=15,
        protection=9,
        protection_mag=2.5,
    )
)
temp_items_lists.append(iron_scale_armor)
item_rarity.append(iron_scale_armor.rarity)


### Iron Plate armor
iron_plate_armor = Item(
    char="[",
    fg=(255, 100, 50),
    name=t("철제 판금 갑옷", "iron plate armor"),
    entity_id="iron_plate_armor",
    entity_desc=("철판들을 이어붙여 만든 갑옷이다. "),
    rarity=3,
    weight=18.5,
    price=10,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 5),
        possible_regions=("torso",),
        str_requirement=17,
        protection=10,
        protection_mag=2.4,
    )
)
temp_items_lists.append(iron_plate_armor)
item_rarity.append(iron_plate_armor.rarity)


### Merchant robe
merchant_robe = Item(
    char="[",
    fg=(120, 60, 250),
    name=t("상인의 로브", "merchant robe"),
    entity_id="merchant_robe",
    entity_desc="던전에서 장사하는 상인들이 착용하는 로브로, 상인 길드 로고가 그려진 작은 금속 단추가 달려 있다.",
    rarity=0,
    weight=3.3,
    price=410,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=25),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("torso",),
        str_requirement=6,
        protection=4,
        fire_resistance=0.1,
        cold_resistance=0.1,
        shock_resistance=0.1,
        acid_resistance=0.1,
        poison_resistance=0.1,
        protection_mag=2,
    )
)
temp_items_lists.append(merchant_robe)
item_rarity.append(merchant_robe.rarity)


### Silk Dress
silk_dress = Item(
    char="[",
    fg=(255, 222, 251),
    name=t("실크 드레스", "silk dress"),
    entity_id="silk_dress",
    entity_desc="실크로 만들어진 드레스이다. ",
    rarity=1,
    weight=0.8,
    price=5,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0.9,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=25),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("torso",),
        protection=1,
        magic_resistance=0.1,
        sleep_resistance=0.6,
        protection_mag=1,
        sleep_resistance_mag=0.08,
    )
)
temp_items_lists.append(silk_dress)
item_rarity.append(silk_dress.rarity)


### Primeval Tortoise shell
primeval_tortoise_shell = Item(
    char="[",
    fg=(37, 171, 0),
    name=t("태고의 거북 등껍질", "primeval tortoise shell"),
    entity_id="primeval_tortoise_shell",
    entity_desc="태고의 거북의 등껍질 조각이다. 방어구로 착용할 수 있을 것 같아 보인다.",
    rarity=0,
    weight=10.3,
    price=50,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=25),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(4, 4),
        possible_regions=("torso",),
        str_requirement=14,
        protection=8,
        protection_mag=1,
        fire_resistance_mag=0.1,
        fire_resistance=0.4,
    )
)
temp_items_lists.append(primeval_tortoise_shell)
item_rarity.append(primeval_tortoise_shell.rarity)



################################## HEAD ######################################
### Iron Headpiece
iron_headpiece = Item(
    char="[",
    fg=(201, 168, 0),
    name=t("철제 전투모", "iron headpiece"),
    entity_id="iron_headpiece",
    entity_desc=("머리 윗 부분을 보호해주는 철제 전투모이다. 가죽 끈을 턱에 둘러 머리에 고정시킬 수 있다. "),
    rarity=9,
    weight=3.2,
    price=8,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 5),
        possible_regions=("head",),
        str_requirement=10,
        protection=5,
        protection_mag=1.6,
    )
)
temp_items_lists.append(iron_headpiece)
item_rarity.append(iron_headpiece.rarity)


### Iron Helmet
iron_helmet = Item(
    char="[",
    fg=(0, 201, 70),
    name=t("철제 투구", "iron helmet"),
    entity_id="iron_helmet",
    entity_desc=("철로 만들어진 투구이다. 얼굴 부분을 제외한 모든 부분이 철판으로 둘러쌓여 있다. "),
    rarity=7,
    weight=4.3,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("head",),
        str_requirement=12,
        protection=7,
        protection_mag=1.8,
    )
)
temp_items_lists.append(iron_helmet)
item_rarity.append(iron_helmet.rarity)


### Spiked Iron Helmet
iron_armet = Item(
    char="[",
    fg=(10, 104, 255),
    name=t("철제 아멧", "iron armet"),
    entity_id="iron_armet",
    entity_desc=("머리 전체를 보호하는 투구이다. 얼굴 부분에 철로 만들어진 바이저가 부착되어 있다. "),
    rarity=5,
    weight=5,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("head",),
        str_requirement=15,
        protection=8,
        protection_mag=2,
    )
)
temp_items_lists.append(iron_armet)
item_rarity.append(iron_armet.rarity)


### Horned Helmet
horned_helmet = Item(
    char="[",
    fg=(166, 255, 254),
    name=t("뿔 달린 투구", "horned helmet"),
    entity_id="horned_helmet",
    entity_desc=("머리를 보호하는 투구이다. 머리 양쪽에 철로 만들어진 뿔 한 쌍이 달려 있다. "),
    rarity=5,
    weight=3.8,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.01,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("head",),
        str_requirement=8,
        protection=6,
        charm=1,
        protection_mag=1.4,
    )
)
temp_items_lists.append(horned_helmet)
item_rarity.append(horned_helmet.rarity)




################################## PANTS ######################################
### Leather Pants
leather_pants = Item(
    char="[",
    fg=(255, 61, 71),
    name=t("가죽 바지", "leather pants"),
    entity_id="leather_pants",
    entity_desc=("질긴 가죽으로 만들어진 바지이다. "),
    rarity=9,
    weight=1.2,
    price=10,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.05,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("leg",),
        str_requirement=7,
        protection=4,
        protection_mag=1.8,
    )
)
temp_items_lists.append(leather_pants)
item_rarity.append(leather_pants.rarity)


### Leather Armored Pants
leather_armored_pants = Item(
    char="[",
    fg=(120, 214, 175),
    name=t("가죽 장갑 하의", "leather armored pants"),
    entity_id="leather_armored_pants",
    entity_desc=("가죽에 철판을 덧대 만든 하의이다. "),
    rarity=7,
    weight=3.8,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.03,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("leg",),
        str_requirement=10,
        protection=6,
        protection_mag=1.5,
    )
)
temp_items_lists.append(leather_armored_pants)
item_rarity.append(leather_armored_pants.rarity)


### Iron Armored Pants
iron_armored_pants = Item(
    char="[",
    fg=(159, 224, 90),
    name=t("철제 장갑 하의", "iron armored pants"),
    entity_id="iron_armored_pants",
    entity_desc=("철판으로 만들어진 하의이다. "),
    rarity=5,
    weight=8.5,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("leg",),
        str_requirement=15,
        protection=8,
        protection_mag=2,
    )
)
temp_items_lists.append(iron_armored_pants)
item_rarity.append(iron_armored_pants.rarity)



################################## BOOTS ######################################
### Leather boots
leather_boots = Item(
    char="[",
    fg=(17, 168, 45),
    name=t("가죽 부츠", "leather boots"),
    entity_id="leather_boots",
    entity_desc=("발목까지 올라오는 가죽 부츠이다. "
                 "일부 지형지물로부터 사용자를 보호할 수 있다. "),
    rarity=8,
    weight=1.54,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("feet",),
        str_requirement=7,
        protection=3,
        protection_mag=1.4,
    )
)
temp_items_lists.append(leather_boots)
item_rarity.append(leather_boots.rarity)


### Boots of haste
boots_of_haste = Item(
    char="[",
    fg=(0, 255, 76),
    name=t("신속의 부츠", "boots of haste"),
    entity_id="boots_of_haste",
    entity_desc=(""),
    rarity=1,
    weight=1.54,
    price=6830,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("feet",),
        str_requirement=7,
        protection=3,
        protection_mag=1.4,
        agility=3,
        agility_mag=0.5,
    ),
    cursable=False,
    is_artifact=True,
    initial_upgrades={0:0},
)
temp_items_lists.append(boots_of_haste)
item_rarity.append(boots_of_haste.rarity)


### Iron boots
iron_boots = Item(
    char="[",
    fg=(17, 113, 168),
    name=t("철제 부츠", "iron boots"),
    entity_id="iron_boots",
    entity_desc=("발목까지 올라오는 철제 부츠이다. "
                 "일부 지형지물로부터 사용자를 보호할 수 있다. "),
    rarity=5,
    weight=8.3,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("feet",),
        str_requirement=11,
        protection=6,
        protection_mag=1.5,
    )
)
temp_items_lists.append(iron_boots)
item_rarity.append(iron_boots.rarity)


############################################ GAUNTLETS/GLOVES ###############################################
### Iron Gauntlet
iron_gauntlet = Item(
    char="[",
    fg=(255, 221, 143),
    name=t("철제 건틀릿", "iron gauntlet"),
    entity_id="iron_gauntlet",
    entity_desc=("손과 팔 부분을 보호하는 건틀릿이다. "),
    rarity=6,
    weight=1.8,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("fist",),
        str_requirement=11,
        protection=7,
        protection_mag=1.5,
    )
)
temp_items_lists.append(iron_gauntlet)
item_rarity.append(iron_gauntlet.rarity)


### Leather Glove
leather_glove = Item(
    char="[",
    fg=(168, 111, 50),
    name=t("가죽 장갑", "leather glove"),
    entity_id="leather_glove",
    entity_desc=("가죽으로 된 장갑이다. 사냥꾼들이 즐겨 착용한다. "),
    rarity=8,
    weight=0.38,
    price=9,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.05,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 5),
        possible_regions=("fist",),
        str_requirement=7,
        protection=3,
        protection_mag=1,
    )
)
temp_items_lists.append(leather_glove)
item_rarity.append(leather_glove.rarity)


### Mitten
mitten = Item(
    char="[",
    fg=(240, 240, 240),
    name=t("벙어리 장갑", "mitten"),
    entity_id="mitten",
    entity_desc=("두꺼운 털로 만들어진 벙어리 장갑이다. 사용자를 추위로부터 보호해주지만 물건을 다루기가 약간 더 불편해진다."),
    rarity=3,
    weight=0.36,
    price=15,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0.1,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 5),
        possible_regions=("fist",),
        str_requirement=2,
        protection=2,
        protection_mag=1,
        dexterity=-1,
        cold_resistance=0.1,
        cold_resistance_mag=0.1,
    )
)
temp_items_lists.append(mitten)
item_rarity.append(mitten.rarity)


### Gauntlet of strength
gauntlet_of_strength = Item(
    char="[",
    fg=(255, 0, 81),
    name=t("힘의 건틀릿", "gauntlet of strength"),
    entity_id="gauntlet_of_strength",
    entity_desc=(""),
    rarity=1,
    weight=1.8,
    price=7700,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.HEAVY_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("fist",),
        str_requirement=11,
        protection=7,
        protection_mag=1.5,
        strength=3,
        strength_mag=0.5,
    ),
    cursable=False,
    is_artifact=True,
    initial_upgrades={0:0},
)
temp_items_lists.append(gauntlet_of_strength)
item_rarity.append(gauntlet_of_strength.rarity)



############################################ CLOAKS ###############################################

### Red cloak
red_cloak = Item(
    char="[",
    fg=(138, 0, 0),
    name=t("적색 망토", "red cloak"),
    entity_id="red_cloak",
    entity_desc="적색 천으로 만들어진 망토이다. 천 표면이 알 수 없는 무언가로 코팅되어 있다.",
    rarity=3,
    weight=2.4,
    price=230,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0,
    corrodible=0.04,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("cloak",),
        protection=2,
        fire_resistance=0.2,
        protection_mag=1,
        fire_resistance_mag=0.05,
    )
)
temp_items_lists.append(red_cloak)
item_rarity.append(red_cloak.rarity)


### Blue cloak
blue_cloak = Item(
    char="[",
    fg=(0, 98, 255),
    name=t("청색 망토", "blue cloak"),
    entity_id="blue_cloak",
    entity_desc="청색 천으로 만들어진 망토이다. 천 표면이 알 수 없는 무언가로 코팅되어 있다.",
    rarity=3,
    weight=2.4,
    price=230,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0.02,
    corrodible=0.02,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("cloak",),
        protection=2,
        cold_resistance=0.2,
        protection_mag=1,
        cold_resistance_mag=0.05,
    )
)
temp_items_lists.append(blue_cloak)
item_rarity.append(blue_cloak.rarity)


### Green cloak
green_cloak = Item(
    char="[",
    fg=(0, 98, 255),
    name=t("녹색 망토", "green cloak"),
    entity_id="green_cloak",
    entity_desc="녹색 천으로 만들어진 망토이다. 천 표면이 알 수 없는 무언가로 코팅되어 있다.",
    rarity=3,
    weight=2.4,
    price=230,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=True,
    flammable=0.05,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("cloak",),
        protection=2,
        acid_resistance=0.2,
        protection_mag=1,
        acid_resistance_mag=0.05,
    )
)
temp_items_lists.append(green_cloak)
item_rarity.append(green_cloak.rarity)


### Elven cloak
elven_cloak = Item(
    char="[",
    fg=(126, 255, 20),
    name=t("엘프제 망토", "elven cloak"),
    entity_id="elven_cloak",
    entity_desc="엘프들이 흔히 입는 가벼운 망토이다. 엘프를 상징하는 문양이 정교한 자수로 새겨져 있다.",
    rarity=3,
    weight=0.7,
    price=70,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("cloak",),
        protection=2,
        protection_mag=1,
    )
)
temp_items_lists.append(elven_cloak)
item_rarity.append(elven_cloak.rarity)


### Hooded cloak
hooded_cloak = Item(
    char="[",
    fg=(237, 255, 253),
    name=t("후드가 달린 망토", "hooded cloak"),
    entity_id="hooded_cloak",
    entity_desc="머리에 쓸 수 있는 후드가 달린 망토이다.",
    rarity=7,
    weight=3.8,
    price=20,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    spawnable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        equip_size=(3, 4),
        possible_regions=("cloak",),
        protection=2,
        protection_mag=1,
    )
)
temp_items_lists.append(hooded_cloak)
item_rarity.append(hooded_cloak.rarity)


### Cloak of Protection
cloak_of_protection = Item(
    char="[",
    fg=(0, 255, 166),
    name=t("보호의 망토", "cloak of protection"),
    entity_id="cloak_of_protection",
    entity_desc=("아주 오래 전, 고룡의 비늘에서부터 섬유를 추출하는 방법을 찾아낸 의류 장인이 있었다. "
                 "이 섬유는 비늘 형태일 때보다도 훨씬 더 튼튼했다고 전해지며, 현존하는 어떠한 섬유도 이에 버금가는 내구성을 가지고 있지 않은 것으로 알려져 있다. "
                 "그는 이러한 기술이 사람들에게 보급된다면 인간이 드래곤들을 무분별하게 사냥하기 시작할 것을 우려해, 그 기술을 아무에게도 전수하지 않은 채 세상을 떠났다. "
                 "그가 이 섬유를 사용해 처음이자 마지막으로 만들었던 것이 바로 '보호의 망토'인데, 그동안 '보호의 망토'임을 자칭하는 수많은 가품들이 등장했지만 아직까지 진품의 행방은 밝혀지지 않았다. "),
    rarity=1,
    weight=2.2,
    price=9830,
    item_type=InventoryOrder.ARMOR,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.LIGHT_ARMOR,
        upgrade=0,
        possible_regions=("cloak",),
        equip_size=(3, 5),
        fire_resistance=1,
        poison_resistance=1,
        acid_resistance=1,
        shock_resistance=1,
        cold_resistance=1,
        protection=8,
        protection_mag=1.1,
    ),
    is_artifact=True,
    cursable=False,
    initial_BUC={1:1,0:0,-1:0},
    initial_upgrades={0:0},
)
temp_items_lists.append(cloak_of_protection)
item_rarity.append(cloak_of_protection.rarity)


#########################################################################
######################### MELEE WEAPONS #################################
#########################################################################

###### BLADES
### Wooden Dagger
wooden_dagger = Item(
    char=")",
    fg=(128, 84, 38),
    name=t("나무 단검", "wooden dagger"),
    entity_id="wooden_dagger",
    entity_desc="주로 병사들의 훈련에 사용되는 나무 단검이다. ",
    rarity=16,
    weight=0.14,
    price=3,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.3,
    corrodible=0.06,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=3, additional_throw=2, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(2, 5),
        str_requirement=8,
        base_melee=3,
        additional_melee=2,
        base_melee_mag=1,
        additional_melee_mag=1,
    ),
    lockpickable=(0.5,0.5),
)
temp_items_lists.append(wooden_dagger)
item_rarity.append(wooden_dagger.rarity)


### Iron Dagger
iron_dagger = Item(
    char=")",
    fg=(255, 145, 0),
    name=t("철제 단검", "iron dagger"),
    entity_id="iron_dagger",
    entity_desc="다양한 용도로 사용이 가능한 철제 단검이다. ",
    rarity=18,
    weight=0.4,
    price=8,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.05,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=7, additional_throw=5, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 5),
        str_requirement=10,
        base_melee=7,
        additional_melee=7,
        base_melee_mag=2,
        additional_melee_mag=1.4,
    ),
    lockpickable=(0.9,0.1),
)
temp_items_lists.append(iron_dagger)
item_rarity.append(iron_dagger.rarity)


### Brass Dagger
brass_dagger = Item(
    char=")",
    fg=(204, 184, 35),
    name=t("황동 단검", "brass dagger"),
    entity_id="brass_dagger",
    entity_desc="다양한 용도로 사용이 가능한 황동 단검이다. ",
    rarity=10,
    weight=0.6,
    price=12,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.03,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=5, additional_throw=9, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 5),
        str_requirement=10,
        base_melee=8,
        additional_melee=8,
        base_melee_mag=2,
        additional_melee_mag=1.6,
    ),
    lockpickable=(0.9,0.1),
)
temp_items_lists.append(brass_dagger)
item_rarity.append(brass_dagger.rarity)


### Elven Dagger
elven_dagger = Item(
    char=")",
    fg=(84, 255, 41),
    name=t("엘프제 단검", "elven dagger"),
    entity_id="elven_dagger",
    entity_desc="엘프들에 의해 단조된 단검이다. 검날에 엘프 고유의 문양이 새겨져 있다. ",
    rarity=6,
    weight=0.38,
    price=15,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.02,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=6, additional_throw=9, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 5),
        str_requirement=10,
        base_melee=9,
        additional_melee=5,
        base_melee_mag=1.5,
        additional_melee_mag=1.6,
    ),
    lockpickable=(0.9,0.1),
)
temp_items_lists.append(elven_dagger)
item_rarity.append(elven_dagger.rarity)


### Scalpel
scalpel = Item(
    char=")",
    fg=(255, 77, 77),
    name=t("스칼펠", "scalpel"),
    entity_id="scalpel",
    entity_desc=("주로 외과 수술을 할 때 사용되는 날카로운 의료용 나이프이다. "
                 "적에게 출혈을 동반한 치명적인 상처를 입힐 수 있다."),
    rarity=3,
    weight=0.19,
    price=50,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=6, additional_throw=1, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 5),
        str_requirement=10,
        base_melee=8,
        additional_melee=5,
        melee_effects=(("bleed_target", 0.3),),
        melee_effects_var=((4, 1, 3),),
        base_melee_mag=1.2,
        additional_melee_mag=2.5,
    ),
    lockpickable=(0.5,0.5),
)
temp_items_lists.append(scalpel)
item_rarity.append(scalpel.rarity)


### Shortsword
shortsword = Item(
    char=")",
    fg=(215, 219, 171),
    name=t("숏소드", "shortsword"),
    entity_id="shortsword",
    entity_desc="단검보다는 크지만 장검보다는 작은 팔뚝 정도 크기의 검이다. ",
    rarity=12,
    weight=1.5,
    price=25,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.03,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=10, additional_throw=8, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=13,
        base_melee=12,
        additional_melee=12,
        base_melee_mag=2.2,
        additional_melee_mag=1.6
    ),
    lockpickable=(0.6,0.1),
)
temp_items_lists.append(shortsword)
item_rarity.append(shortsword.rarity)


### Elven sword
elven_sword = Item(
    char=")",
    fg=(0, 255, 166),
    name=t("엘프제 검", "elven sword"),
    entity_id="elven_sword",
    entity_desc="긴 손잡이와 휘어있는 검날이 달려있는 엘프제 무기이다.",
    rarity=4,
    weight=1.35,
    price=32,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.02,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=10, additional_throw=8, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=12,
        base_melee=11,
        additional_melee=15,
        base_melee_mag=1.4,
        additional_melee_mag=3
    ),
    lockpickable=(0.3,0.1),
)
temp_items_lists.append(elven_sword)
item_rarity.append(elven_sword.rarity)


### Longsword
longsword = Item(
    char=")",
    fg=(152, 227, 226),
    name=t("롱소드", "longsword"),
    entity_id="longsword",
    entity_desc="양쪽 모두에 날이 달려있는 긴 검이다. 기사들이 즐겨 사용하는 무기이다. ",
    rarity=7,
    weight=1.8,
    price=75,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.03,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=12, additional_throw=10, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=17,
        base_melee=15,
        additional_melee=15,
        base_melee_mag=2,
        additional_melee_mag=1.8,
    ),
    lockpickable=(0.3,0.2),
)
temp_items_lists.append(longsword)
item_rarity.append(longsword.rarity)


### Sunbringer
sunbringer = Item(
    char=")",
    fg=(255, 34, 0),
    name=t("선브링거", "sunbringer"),
    entity_id="sunbringer",
    entity_desc=("태양을 집어삼킨 검이라고도 불리우는 선브링거는 알 수 없는 재질의 금속으로 만들어진 고대의 롱소드이다. "
                 "선브링거는 소유자가 검을 휘두를 때 강력한 불꽃을 방출하며, 선브링거라는 이름은 붉게 빛나는 검신의 모습을 보고 붙여졌다."
                 "검의 소유자는 선브링거로부터 뿜어져 나오는 불꽃을 비롯한 대부분의 열기에 강한 저항을 가지게 된다."
                 ),
    rarity=1,
    weight=1.8,
    price=8200,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=18, additional_throw=10, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=17,
        base_melee=20,
        additional_melee=15,
        base_melee_mag=2.1,
        additional_melee_mag=2,
        melee_effects=(("burn_target", 0.8),),
        melee_effects_var=((10, 2, 0, 4),),
        fire_resistance=0.9,
    ),
    lockpickable=(0.8,0),
    is_artifact=True,
    initial_BUC={1:1,0:0,-1:0},
    initial_upgrades={0:0},
    cursable=False,
)
temp_items_lists.append(sunbringer)
item_rarity.append(sunbringer.rarity)



###### BLADES - MISC
swordstick = Item(
    char=")",
    fg=(196, 255, 202),
    name=t("소드 스틱", "swordstick"),
    entity_id="swordstick",
    entity_desc="화려한 보석들로 치장된 지팡이 형태의 칼이다. 손잡이 부분을 당겨 긴 날이 달린 검을 뽑을 수 있다. ",
    rarity=6,
    weight=0.62,
    price=350,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=11, additional_throw=2, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 4),
        str_requirement=12,
        base_melee=13,
        additional_melee=2,
        base_melee_mag=2.3,
        additional_melee_mag=2,
    ),
    lockpickable=(0.2,0.5),
)
temp_items_lists.append(swordstick)
item_rarity.append(swordstick.rarity)



###### AXES
# Axe
axe = Item(
    char=")",
    fg=(112, 105, 255),
    name=t("도끼", "axe"),
    entity_id="axe",
    entity_desc="쇠로 만든 도끼날이 달린 평범한 도끼이다. ",
    rarity=12,
    weight=3,
    price=5,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.01,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=8, additional_throw=17, penetration=False, air_friction=1),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(4, 6),
        str_requirement=15,
        base_melee=8,
        additional_melee=15,
        base_melee_mag=1.5,
        additional_melee_mag=3,
    ),
    lockpickable=(0.5,0.05),
)
temp_items_lists.append(axe)
item_rarity.append(axe.rarity)


tomahawk = Item(
    char=")",
    fg=(120, 66, 245),
    name=t("토마호크", "tomahawk"),
    entity_id="tomahawk",
    entity_desc="던지기 쉽게 짧은 손잡이가 달려있는 도끼이다. ",
    rarity=9,
    weight=0.35,
    price=120,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=6, additional_throw=12, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 5),
        str_requirement=13,
        base_melee=6,
        additional_melee=14,
        base_melee_mag=1.4,
        additional_melee_mag=3,
    ),
    lockpickable=(0.2,0.1),
)
temp_items_lists.append(tomahawk)
item_rarity.append(tomahawk.rarity)


# Battle Axe
battle_axe = Item(
    char=")",
    fg=(214, 51, 111),
    name=t("전투 도끼", "battle axe"),
    entity_id="battle_axe",
    entity_desc="다용도 도구로써의 기능을 포기하고 오로지 전투만을 위해 만들어진 도끼이다. 도끼날이 양면에 달려 있다.",
    rarity=5,
    weight=3.1,
    price=200,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=12, additional_throw=17, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(4, 6),
        str_requirement=19,
        base_melee=10,
        additional_melee=26,
        base_melee_mag=2,
        additional_melee_mag=3.3,
    ),
    lockpickable=(0.5,0.01),
)
temp_items_lists.append(battle_axe)
item_rarity.append(battle_axe.rarity)


# Stonefury
stonefury = Item(
    char=")",
    fg=(214, 51, 111),
    name=t("스톤퓨리", "stonefury"),
    entity_id="stonefury",
    entity_desc=("스톤퓨리는 알 수 없는 암석으로 만들어진 도끼날을 갖고 있으며 과거 바이킹들에 의해 만들어졌다고 알려져 있다. "
                 "이 무기는 사용자에게 강력한 분노를 불러일으키며, 공격받은 대상에게까지도 막심한 분노를 유발하는 것으로 알려져 있다. "
                 "이러한 특성 때문에 스톤퓨리는 늘상 피비릿내나는 역사의 중심에 있었으며, 바이킹이 내전으로 멸망하게 된 것도 이 무기의 탄생 때문이라고 보는 학자들도 존재한다. "),
    rarity=1,
    weight=2.8,
    price=8500,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=12, additional_throw=17, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.BLADE,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(4, 6),
        str_requirement=19,
        base_melee=12,
        additional_melee=30,
        base_melee_mag=2,
        additional_melee_mag=2.5,
        alter_actor_state={"is_angry":list((0,-1))},# using list()
        melee_effects=(("anger_target", 0.5),),
        melee_effects_var=((0,5),),
    ),
    lockpickable=(0.9, 0),
    is_artifact=True,
    initial_BUC={1: 1, 0: 0, -1: 0},
    initial_upgrades={0: 0},
    cursable=False,
)
temp_items_lists.append(stonefury)
item_rarity.append(stonefury.rarity)


###### CLUBS
### Forging hammer
forging_hammer = Item(
    char=")",
    fg=(92, 28, 28),
    name=t("단조용 망치", "forging hammer"),
    entity_id="forging_hammer",
    entity_desc="대장간에서 쇠를 내리칠 때 쓰이는 단조용 망치이다. 망치 머리의 끝부분이 둥그런 형태를 하고 있다.",
    rarity=2,
    weight=0.58,
    price=20,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.03,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=10, additional_throw=9, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.CLUB,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 4),
        str_requirement=13,
        base_melee=5,
        additional_melee=12,
        base_melee_mag=1,
        additional_melee_mag=1.8,
    ),
    lockpickable=(0.2,0.01),
)
temp_items_lists.append(forging_hammer)
item_rarity.append(forging_hammer.rarity)


### Quarterstaff
quarterstaff = Item(
    char=")",
    fg=(0, 207, 24),
    name=t("육척봉", "quarterstaff"),
    entity_id="quarterstaff",
    entity_desc="양쪽 끝에 강철을 덧댄 봉 형태의 무기이다. ",
    rarity=4,
    weight=1.98,
    price=15,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.01,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=10, additional_throw=9, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.CLUB,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=14,
        base_melee=13,
        additional_melee=4,
        base_melee_mag=1.9,
        additional_melee_mag=1.8,
    ),
    lockpickable=(0.01,0.2),
)
temp_items_lists.append(quarterstaff)
item_rarity.append(quarterstaff.rarity)


### Giant Wood Club
giant_wood_club = Item(
    char=")",
    fg=(97, 53, 0),
    name=t("통나무 곤봉", "giant wood club"),
    entity_id="giant_wood_club",
    entity_desc="성인 남성 정도 크기의 거대한 나무 곤봉이다. ",
    rarity=0,
    weight=80,
    price=5,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.2,
    corrodible=0,
    spawnable=False,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.CLUB,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(5,7),
        str_requirement=20,
        base_melee=16,
        additional_melee=10,
        base_melee_mag=2,
        additional_melee_mag=2
    ),
    lockpickable=(0,0),
)
temp_items_lists.append(giant_wood_club)
item_rarity.append(giant_wood_club.rarity)


# Morning star
morning_star = Item(
    char=")",
    fg=(255, 0, 247),
    name=t("철퇴", "morning star"),
    entity_id="morning_star",
    entity_desc=("곤봉 끝에 가시달린 철 덩어리가 쇠사슬로 연결되어 있는 무기이다. "
                 "다소 다루기가 어렵지만 제대로 맞추기만 한다면 어마어마한 위력을 자랑하는 무기이다. "),
    rarity=8,
    weight=2.9,
    price=25,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=8, additional_throw=2, penetration=False, air_friction=100),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.CLUB,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(4, 6),
        str_requirement=15,
        base_melee=1,
        additional_melee=30,
        base_melee_mag=1,
        additional_melee_mag=2.5,
    ),
    lockpickable=(0.05,0.05),
)
temp_items_lists.append(morning_star)
item_rarity.append(morning_star.rarity)


###### POLEARMS
### Spear
spear = Item(
    char=")",
    fg=(0, 47, 255),
    name=t("창", "spear"),
    entity_id="spear",
    entity_desc=("뾰족한 머리가 달려있는 대표적인 장병 무기이다. "
                 "기동성은 다소 떨어지지만 출혈을 동반한 자상을 입힐 수 있다. "),
    rarity=8,
    weight=4.8,
    price=25,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.01,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=5, additional_throw=15, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.POLEARM,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=14,
        base_melee=16,
        additional_melee=3,
        agility=-2,
        base_melee_mag=1.9,
        additional_melee_mag=1,
        melee_effects=(("bleed_target", 0.2),),
        melee_effects_var=((3, 0, 3),),
    ),
    lockpickable=(0.1,0.5),
)
temp_items_lists.append(spear)
item_rarity.append(spear.rarity)


### Halberd
halberd = Item(
    char=")",
    fg=(0, 47, 255),
    name=t("할버드", "halberd"),
    entity_id="halberd",
    entity_desc=("도끼 형태의 날과 창 형태의 뾰족한 머리가 모두 달려있는 장병 무기이다. "
                 "기동성은 다소 떨어지지만 출혈을 동반한 자상을 입힐 수 있다. "),
    rarity=5,
    weight=6.8,
    price=80,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.01,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=5, additional_throw=15, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.POLEARM,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=14,
        base_melee=20,
        additional_melee=5,
        agility=-2,
        base_melee_mag=2,
        additional_melee_mag=1.8,
        melee_effects=(("bleed_target", 0.1),),
        melee_effects_var=((2, 0, 4),),
    ),
    lockpickable=(0.1,0.5),
)
temp_items_lists.append(halberd)
item_rarity.append(halberd.rarity)


### Heartpiercer
heartpiercer = Item(
    char=")",
    fg=(0, 47, 255),
    name=t("하트피어써", "heartpiercer"),
    entity_id="heartpiercer",
    entity_desc=("'심장을 꿰뚫는 자'라는 뜻의 이름을 가진 하트피어써는 세 개의 창끝이 달린 삼지창 형태를 하고 있는 무기이다. "
                 "하트피어써는 특수한 합금으로 만들어졌는데, 이 합금을 주조하기 위해선 각종 금속들 뿐만 아니라 여러 괴물들의 혈액 또한 필요로 하는 것으로 알려져 있다. "
                 "이러한 특성 때문에 하트피어써는 생명체의 피를 갈망하며 주변 생명체들의 기운을 빨아들이는데, 이는 하트피어써의 사용자도 예외가 아니다. "
                 "그럼에도 이러한 특성이 부여하는 강력한 출혈 효과 때문에 하트피어써는 수많은 전사들과 무기 수집가들에게 선망의 대상이 되어왔다."),
    rarity=1,
    weight=5.5,
    price=8666,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=5, additional_throw=35, penetration=True),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.POLEARM,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 6),
        str_requirement=20,
        base_melee=28,
        additional_melee=5,
        constitution=-2,
        base_melee_mag=2,
        additional_melee_mag=1.5,
        melee_effects=(("bleed_target", 0.25),),
        melee_effects_var=((5, 0, 4),),
    ),
    lockpickable=(0.2,0),
    is_artifact=True,
    initial_BUC={1: 0, 0: 0, -1: 1},
    initial_upgrades={0: 0},
)
temp_items_lists.append(heartpiercer)
item_rarity.append(heartpiercer.rarity)


###### SHIELDS
### Wooden Shield
wooden_shield = Item(
    char=")",
    fg=(252, 186, 3),
    name=t("나무 방패", "wooden shield"),
    entity_id="wooden_shield",
    entity_desc="나무를 덧대 만든 방패이다. ",
    rarity=10,
    weight=3.2,
    price=5,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.2,
    corrodible=0.04,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=5, penetration=False, air_friction=55),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.SHIELD,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3,5),
        str_requirement=11,
        base_melee=1,
        additional_melee=3,
        protection=5,
        shock_resistance=0.5,
        cold_resistance=0.3,
        protection_mag=2.1,
        base_melee_mag=0.5,
    ),
    lockpickable=(0.05,0.01),
)
temp_items_lists.append(wooden_shield)
item_rarity.append(wooden_shield.rarity)


### Silver Shield
silver_shield = Item(
    char=")",
    fg=(189, 189, 189),
    name=t("은 방패", "silver shield"),
    entity_id="silver_shield",
    entity_desc="은으로 만들어진 방패이다. 마법 공격으로부터의 저항성이 뛰어나다. ",
    rarity=3,
    weight=2.7,
    price=650,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=3, additional_throw=3, penetration=False, air_friction=55),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.SHIELD,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3, 5),
        str_requirement=13,
        base_melee=3,
        additional_melee=3,
        protection=7,
        magic_resistance=0.2,
        protection_mag=2.2,
        base_melee_mag=1,
    ),
    lockpickable=(0.1,0.01),
)
temp_items_lists.append(silver_shield)
item_rarity.append(silver_shield.rarity)


### Platinum Shield
platinum_shield = Item(
    char=")",
    fg=(255, 255, 255),
    name=t("백금 방패", "platinum shield"),
    entity_id="platinum_shield",
    entity_desc="백금으로 만들어진 방패이다. 대부분의 속성 피해로부터 어느 정도 내성을 제공한다. ",
    rarity=2,
    weight=2.9,
    price=1250,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=3, additional_throw=5, penetration=False, air_friction=55),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.SHIELD,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3,5),
        str_requirement=15,
        base_melee=3,
        additional_melee=5,
        protection=7,
        fire_resistance=0.3,
        cold_resistance=0.3,
        shock_resistance=0.3,
        poison_resistance=0.3,
        acid_resistance=0.3,
        magic_resistance=0.1,
        protection_mag=2.1,
        base_melee_mag=1.1,
    ),
    lockpickable=(0.1,0.01),
)
temp_items_lists.append(platinum_shield)
item_rarity.append(platinum_shield.rarity)


### Iron Shield
iron_shield = Item(
    char=")",
    fg=(252, 186, 3),
    name=t("철제 방패", "iron shield"),
    entity_id="iron_shield",
    entity_desc="철판으로 만들어진 믿음직한 방패이다. ",
    rarity=5,
    weight=3.5,
    price=5,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.2,
    corrodible=0.02,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=2, additional_throw=2, penetration=False, air_friction=55),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.SHIELD,
        upgrade=0,
        possible_regions=("main hand", "off hand"),
        equip_size=(3,5),
        str_requirement=15,
        base_melee=2,
        additional_melee=2,
        protection=8,
        fire_resistance=0.4,
        protection_mag=1.9,
        base_melee_mag=1,
    ),
    lockpickable=(0.1,0.01),
)
temp_items_lists.append(iron_shield)
item_rarity.append(iron_shield.rarity)



#########################################################################
############################### AMULETS #################################
#########################################################################

### Amulet of Kugah
amulet_of_kugah = Item(
    indestructible=True,
    should_initialize=False,
    should_randomize=False,
    char="♀",
    fg = (255, 72, 0),
    name=t("쿠가의 아뮬렛", "amulet of Kugah"),
    entity_id="amulet_of_kugah",
    entity_desc="창조신 쿠가가 힘을 되찾기 위해 필요한 아뮬렛이다.",
    rarity=0,
    weight=0.2,
    price=0,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=2),
    tradable=False,
    spawnable=False,
    cursable=False,
    blessable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
    ),
    edible=None,
    initial_BUC={1:1, 0:0, -1:0},
    initial_upgrades={0:1},
    is_artifact=True,
)
temp_items_lists.append(amulet_of_kugah)
item_rarity.append(amulet_of_kugah.rarity)


### Amulet of Brilliance
amulet_of_brilliance = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("지적 각성의 아뮬렛", "amulet of brilliance"),
    entity_id="amulet_of_brilliance",
    entity_desc=(""),
    rarity=1,
    weight=0.2,
    price=6503,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        intelligence=3,
        intelligence_mag=0.5,
    ),
    edible=None,
    cursable=False,
    is_artifact=True,
    initial_upgrades={0:0},
)
temp_items_lists.append(amulet_of_brilliance)
item_rarity.append(amulet_of_brilliance.rarity)


### Amulet of Sensitivity
amulet_of_sensitivity = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("감각 향상의 아뮬렛", "amulet of sensitivity"),
    entity_id="amulet_of_sensitivity",
    entity_desc="착용자의 감각기관을 예민하게 만드는 것으로 알려진 아뮬렛이다. ",
    rarity=5,
    weight=0.2,
    price=320,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        eyesight=40,
        hearing=40,
        eyesight_mag=10,
        hearing_mag=10,
    ),
    edible=None
)
temp_items_lists.append(amulet_of_sensitivity)
item_rarity.append(amulet_of_sensitivity.rarity)


### Amulet of Telepathy
amulet_of_telepathy = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("텔레파시의 아뮬렛", "amulet of telepathy"),
    entity_id="amulet_of_telepathy",
    entity_desc="착용자에게 텔레파시의 능력을 부여한다고 알려진 아뮬렛이다. ",
    rarity=5,
    weight=0.2,
    price=320,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        alter_actor_state={"has_telepathy":True},
    ),
    edible=None
)
temp_items_lists.append(amulet_of_telepathy)
item_rarity.append(amulet_of_telepathy.rarity)


### Amulet of Underwater Breathing
amulet_of_underwater_breathing = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("수중 호흡의 아뮬렛", "amulet of underwater breathing"),
    entity_id="amulet_of_underwater_breathing",
    entity_desc="착용자에게 물 속에서 호흡할 수 있는 능력을 부여한다고 알려진 아뮬렛이다. ",
    rarity=5,
    weight=0.2,
    price=320,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        alter_actor_state={"can_breathe_underwater":True},
    ),
    edible=None
)
temp_items_lists.append(amulet_of_underwater_breathing)
item_rarity.append(amulet_of_underwater_breathing.rarity)


### Amulet of monastic silence
amulet_of_monastic_silence = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("묵언 수행의 아뮬렛", "amulet of monastic silence"),
    entity_id="amulet_of_monastic_silence",
    entity_desc="착용자는 말을 하는 능력을 잃게 되지만, 보다 더 빠르게 행동할 수 있게 된다. ",
    rarity=5,
    weight=0.2,
    price=320,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        alter_actor_state={"can_talk":False},
        agility=1,
    ),
    edible=None
)
temp_items_lists.append(amulet_of_monastic_silence)
item_rarity.append(amulet_of_monastic_silence.rarity)


### Amulet of Charisma
amulet_of_charisma = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("카리스마의 아뮬렛", "amulet of charisma"),
    entity_id="amulet_of_charisma",
    entity_desc="착용자를 한 층 더 카리스마 넘치게 만들어주는 것으로 알려진 아뮬렛이다. ",
    rarity=1,
    weight=0.2,
    price=320,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        charm=3,
        charm_mag=0.5,
    ),
    edible=None,
    cursable=False,
    is_artifact=True,
    initial_upgrades={0: 0},
)
temp_items_lists.append(amulet_of_charisma)
item_rarity.append(amulet_of_charisma.rarity)


### Amulet of immunity loss
amulet_of_immunity_loss = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("면역력 저하의 아뮬렛", "amulet of immunity loss"),
    entity_id="amulet_of_immunity_loss",
    entity_desc="착용자의 신체적 면역력을 낮추는 효과를 지닌 아뮬렛이다. ",
    rarity=5,
    weight=0.2,
    price=320,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        alter_actor_state={"heal_wounds":False},
        poison_resistance=0,
        constitution=-2,
        constitution_mag=-1,
    ),
    edible=None,
    initial_BUC={1:0,0:1,-1:10},
)
temp_items_lists.append(amulet_of_immunity_loss)
item_rarity.append(amulet_of_immunity_loss.rarity)


### Amulet of magic aversion
amulet_of_magic_aversion = Item(
    should_randomize=True,
    char="♀",
    fg = (255, 72, 0),
    name=t("반마법의 아뮬렛", "amulet of magic aversion"),
    entity_id="amulet_of_magic_aversion",
    entity_desc="착용자와 마법과의 상호작용을 방해하는 아뮬렛이다. ",
    rarity=5,
    weight=0.2,
    price=320,
    item_type=InventoryOrder.AMULET,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        alter_actor_state={"regain_mana":False},
        intelligence=-5,
        intelligence_mag=-1,
        magic_resistance=0.5,
        magic_resistance_mag=0.1,
    ),
    edible=None,
    initial_BUC={1:0,0:1,-1:10},
)
temp_items_lists.append(amulet_of_magic_aversion)
item_rarity.append(amulet_of_magic_aversion.rarity)


#########################################################################
############################### RINGS ###################################
#########################################################################


### Ring of inner peace
ring_of_inner_peace = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("내적 평화의 반지", "ring of inner piece"),
    entity_id="ring_of_inner_peace",
    entity_desc=("착용자에게 마음의 평화를 가져다주는 반지이다. "
                 "착용자는 쉽게 분노하지 않게 된다. "),
    rarity=6,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        alter_actor_state={"has_inner_peace":True},
    ),
    edible=None
)
temp_items_lists.append(ring_of_inner_peace)
item_rarity.append(ring_of_inner_peace.rarity)


### Ring of water
ring_of_water = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("물의 반지", "ring of water"),
    entity_id="ring_of_water",
    entity_desc=("착용자에게 물의 기운을 부여하는 반지이다. "
                 "착용자는 물 속에서 빠르게 이동을 할 수 있게 되고, 화염과 산에 저항을 가지게 되지만, 냉기에 다소 취약해진다."),
    rarity=6,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        alter_actor_state={"can_swim":True},
        fire_resistance=0.5,
        acid_resistance=0.5,
        cold_resistance=-0.5, # negative
    ),
    edible=None
)
temp_items_lists.append(ring_of_water)
item_rarity.append(ring_of_water.rarity)


### Ring of earth
ring_of_earth = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("땅의 반지", "ring of earth"),
    entity_id="ring_of_earth",
    entity_desc=("착용자에게 땅의 기운을 부여하는 반지이다. "
                 "착용자는 전격과 독, 그리고 냉기에 저항을 가지게 된다."),
    rarity=6,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        alter_actor_state={"can_move_on_surface":True},
        shock_resistance=0.5,
        poison_resistance=0.5,
        cold_resistance=0.5,
    ),
    edible=None
)
temp_items_lists.append(ring_of_earth)
item_rarity.append(ring_of_earth.rarity)


### Ring of sky
ring_of_sky = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("하늘의 반지", "ring of sky"),
    entity_id="ring_of_sky",
    entity_desc=("착용자에게 하늘의 기운을 부여하는 반지이다. "
                 "착용자는 하늘을 날 수 있게 된다. "),
    rarity=6,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        alter_actor_state={"can_fly":True},
    ),
    edible=None
)
temp_items_lists.append(ring_of_sky)
item_rarity.append(ring_of_sky.rarity)


### Ring of Dexterity
ring_of_dexterity = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("재주의 반지", "ring of dexterity"),
    entity_id="ring_of_dexterity",
    entity_desc=("착용자에게 재주를 부여한다고 알려진 반지이다. "),
    rarity=1,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        dexterity=3,
        dexterity_mag=0.5,
    ),
    edible=None,
    cursable=False,
    is_artifact=True,
    initial_upgrades={0:0},
)
temp_items_lists.append(ring_of_dexterity)
item_rarity.append(ring_of_dexterity.rarity)


### Ring of Constitution
ring_of_constitution = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("활력의 반지", "ring of constitution"),
    entity_id="ring_of_constitution",
    entity_desc=("착용자에게 활력을 부여한다고 알려진 반지이다. "),
    rarity=1,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        constitution=3,
        constitution_mag=0.5,
    ),
    edible=None,
    cursable=False,
    is_artifact=True,
    initial_upgrades={0:0},
)
temp_items_lists.append(ring_of_constitution)
item_rarity.append(ring_of_constitution.rarity)


### Ring of Insomnia
ring_of_insomnia = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("불면증의 반지", "ring of insomnia"),
    entity_id="ring_of_insomnia",
    entity_desc=("착용자가 잠을 잘 수 없게 만든다고 알려진 반지이다. "),
    rarity=6,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        alter_actor_state={"can_sleep":False}, # Cant sleep with its own will
        sleep_resistance=1,
    ),
    edible=None,
    initial_BUC={1:1,0:1,-1:8},
)
temp_items_lists.append(ring_of_insomnia)
item_rarity.append(ring_of_insomnia.rarity)


### Ring of Martial artist
ring_of_martial_artist = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("무술가의 반지", "ring of martial artist"),
    entity_id="ring_of_martial_artist",
    entity_desc=("착용자가 다양한 무술 기술들을 사용할 수 있게 만들어준다고 알려진 반지이다. "),
    rarity=6,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        base_melee=5,
        additional_melee=5,
    ),
    edible=None
)
temp_items_lists.append(ring_of_martial_artist)
item_rarity.append(ring_of_martial_artist.rarity)


### Ring of Blindness
ring_of_blindness = Item(
    should_randomize=True,
    char="◦",
    fg = (255, 72, 0),
    name=t("실명의 반지", "ring of blindness"),
    entity_id="ring_of_blindness",
    entity_desc=("착용자의 시력을 악화시킨다고 알려진 반지이다. "),
    rarity=6,
    weight=0.2,
    price=400,
    item_type=InventoryOrder.RING,
    item_state=ItemState(is_identified=0),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.RING,
        upgrade=0,
        possible_regions=("left ring","right ring",),
        eyesight=-50,
    ),
    initial_BUC={1:0,0:1,-1:10},
    edible=None
)
temp_items_lists.append(ring_of_blindness)
item_rarity.append(ring_of_blindness.rarity)


#########################################################################
############################### EDIBLES #################################
#########################################################################

### Corpses
corpse = Item(
    char="%",
    fg = (191, 0, 0),
    name=t("시체", "corpse"),# Name automatically changes later
    entity_id="corpse",
    entity_desc="",
    rarity=0,
    weight=0,# Weight initialized when the actor dies
    price=2,
    item_type=InventoryOrder.FOOD,
    item_state=ItemState(is_identified=1),
    tradable=False,
    spawnable=False,
    flammable=0.2,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    edible=None # Edible initialized when the actor is generated (status.py)
)
temp_items_lists.append(corpse)
item_rarity.append(corpse.rarity) # All items should be appended regardless of its rarity


### Ration
ration = Item(
    char="%",
    fg = (255, 0, 247),
    name=t("비상식량", "ration"),
    entity_id="ration",
    entity_desc=("여러 종류의 가공육들과 비스켓, 약간의 물이 들어있는 비상식량이다. "
                 "쉽게 상하지 않아 던전을 탐험하는 모험가들이 자주 휴대하고 다닌다. "),
    rarity=40,
    weight=2.3,
    price=150,
    item_type=InventoryOrder.FOOD,
    item_state=ItemState(is_identified=1),
    tradable=True,
    spawnable=True,
    flammable=0.1,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(),
    edible=edible.RationEdible(nutrition=500)
)
temp_items_lists.append(ration)
item_rarity.append(ration.rarity)


### Lintol
lintol = Item(
    char="%",
    fg = (255, 99, 224),
    name=t("린톨", "lintol"),
    entity_id="lintol",
    entity_desc=("뾰족하고 얇은 잎사귀를 가진 허브의 한 종류이다. 린톨은 예로부터 해열제로 널리 사용되어왔다. "),
    rarity=5,
    weight=0.005,
    price=30,
    item_type=InventoryOrder.FOOD,
    item_state=ItemState(is_identified=1),
    tradable=True,
    spawnable=True,
    flammable=0.5,
    corrodible=0,
    droppable=True,
    stackable=False,
    cursable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    edible=edible.LintolEdible(nutrition=5)
)
temp_items_lists.append(lintol)
item_rarity.append(lintol.rarity)


### Fillapoty
fillapoty = Item(
    char="%",
    fg = (255, 99, 224),
    name=t("필라포티", "fillapoty"),
    entity_id="fillapoty",
    entity_desc=("넓은 잎사귀를 가진 허브의 한 종류이다. 필라포티의 잎을 가르면 나오는 즙은 해독 작용을 하는 것으로 알려져 있다. "),
    rarity=5,
    weight=0.005,
    price=30,
    item_type=InventoryOrder.FOOD,
    item_state=ItemState(is_identified=1),
    tradable=True,
    spawnable=True,
    flammable=0.5,
    corrodible=0,
    droppable=True,
    stackable=False,
    cursable=False,
    throwable=throwable.NormalThrowable(air_friction=100),
    edible=edible.FillapotyEdible(nutrition=5)
)
temp_items_lists.append(fillapoty)
item_rarity.append(fillapoty.rarity)


### Kettoniss
kettoniss = Item(
    char="%",
    fg = (255, 123, 0),
    name=t("케토니스", "kettoniss"),
    entity_id="kettoniss",
    entity_desc=("둥근 잎사귀를 가진 허브의 한 종류이다. 케토니스를 달인 차는 추위에 효과적이라고 알려져 있다. "),
    rarity=5,
    weight=0.005,
    price=30,
    item_type=InventoryOrder.FOOD,
    item_state=ItemState(is_identified=1),
    tradable=True,
    spawnable=True,
    flammable=0.5,
    corrodible=0,
    droppable=True,
    stackable=False,
    cursable=False,
    throwable=throwable.NormalThrowable(),
    edible=edible.KettonissEdible(nutrition=5)
)
temp_items_lists.append(kettoniss)
item_rarity.append(kettoniss.rarity)


#########################################################################
################################# GEMS ##################################
#########################################################################

### Diamond
diamond = Item(
    should_randomize=True,
    char="*",
    fg = (255, 255, 255),
    name=t("다이아몬드", "diamond"),
    entity_id="diamond",
    entity_desc="하얀 빛의 아름다운 보석이다. 상당한 고가에 거래된다.",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
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
    name=t("루비", "ruby"),
    entity_id="ruby",
    entity_desc="붉은 빛의 아름다운 보석이다. 상당한 고가에 거래된다.",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=1),
    equipable=None,
    edible=None
)
temp_items_lists.append(ruby)
item_rarity.append(ruby.rarity)


### Emerald
emerald = Item(
    should_randomize=True,
    char="*",
    fg = (21, 207, 0),
    name=t("에메랄드", "emerald"),
    entity_id="emerald",
    entity_desc="푸른 빛의 아름다운 보석이다. 상당한 고가에 거래된다.",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
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
    name=t("사파이어", "sapphire"),
    entity_id="sapphire",
    entity_desc="녹색 빛의 아름다운 보석이다. 상당한 고가에 거래된다.",
    rarity=1,
    weight=0.01,
    price=3000,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
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
    name=t("싸구려 유리 조각", "worthless piece white glass"),
    entity_id="worthless_piece_of_white_glass",
    entity_desc="아무런 가치도 없는 깨진 유리 조각이다.",
    rarity=3,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
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
    name=t("싸구려 유리 조각", "worthless piece red glass"),
    entity_id="worthless_piece_of_red_glass",
    entity_desc="아무런 가치도 없는 깨진 유리 조각이다.",
    rarity=3,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
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
    name=t("싸구려 유리 조각", "worthless piece green glass"),
    entity_id="worthless_piece_of_green_glass",
    entity_desc="아무런 가치도 없는 깨진 유리 조각이다.",
    rarity=3,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
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
    name=t("싸구려 유리 조각", "worthless piece blue glass"),
    entity_id="worthless_piece_of_blue_glass",
    entity_desc="아무런 가치도 없는 깨진 유리 조각이다.",
    rarity=3,
    weight=0.01,
    price=1,
    item_type=InventoryOrder.GEM,
    item_state=ItemState(is_identified=0),
    spawnable=True,
    cursable=False,
    blessable=False,
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
################################# TOOLS #################################
#########################################################################

### rustproof wax
rustproof_wax = Item(
    char="(",
    fg = (255, 255, 255),
    name=t("부식 방지의 왁스", "rustproof wax"),
    entity_id="rustproof_wax",
    entity_desc="갑옷 등에 발라 부식을 다소 방지할 수 있는 왁스이다.",
    rarity=20,
    weight=0.07,
    price=120,
    item_type=InventoryOrder.TOOL,
    item_state=ItemState(is_identified=1),
    tradable=True,
    spawnable=True,
    flammable=0.7,
    corrodible=0,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    usable=usable.RustproofWaxUsable(should_consume=True, corrodible_modifier=0.5),
    edible=None
)
temp_items_lists.append(rustproof_wax)
item_rarity.append(rustproof_wax.rarity)


### fireproof wax
fireproof_wax = Item(
    char="(",
    fg = (255, 255, 0),
    name=t("그을림 방지의 왁스", "fireproof wax"),
    entity_id="fireproof_wax",
    entity_desc="갑옷 등에 발라 불이 붙거나 그을리는 것을 다소 방지할 수 있는 왁스이다.",
    rarity=20,
    weight=0.07,
    price=120,
    item_type=InventoryOrder.TOOL,
    item_state=ItemState(is_identified=1),
    tradable=True,
    spawnable=True,
    flammable=0,
    corrodible=0.7,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(penetration=False, air_friction=15),
    usable=usable.FireproofWaxUsable(should_consume=True, flammable_modifier=0.5),
    edible=None
)
temp_items_lists.append(fireproof_wax)
item_rarity.append(fireproof_wax.rarity)


#########################################################################
################################# MISCS #################################
#########################################################################

### toxic Goo
toxic_goo = Item(
    char="*",
    fg = (61, 0, 82),
    name=t("독성 점액", "toxic goo"),
    entity_id="toxic_goo",
    entity_desc="검은 덩어리의 몸에서 떨어져 나온 검정색 점액질 물체이다.",
    rarity=0,
    weight=0.1,
    price=0,
    item_type=InventoryOrder.MISC,
    item_state=ItemState(is_identified=1),
    tradable=False,
    spawnable=False,
    cursable=False,
    blessable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    # change_stack_count_when_dropped=(1,1),
    # stackable=False, # Old codes -> no longer needed
    stackable=True,
    throwable=throwable.ToxicGooThrowable(
        base_throw=1,
        additional_throw=1,
        break_chance=1,
        air_friction=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0
    ),
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
    name=t("샤인", "shine"),
    entity_id="shine",
    entity_desc="물건을 사고 팔 때 사용되는 화폐이다.",
    rarity=0,
    weight=0.001,
    price=1,
    item_type=InventoryOrder.CASH,
    item_state=ItemState(is_identified=2),
    tradable=False,
    cursable=False,
    blessable=False,
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
    name=t("샤인", "shine"),
    entity_id="shine",
    entity_desc="물건을 사고 팔 때 사용되는 화폐이다.",
    rarity=0,
    weight=0.001,
    price=1,
    item_type=InventoryOrder.CASH,
    item_state=ItemState(is_identified=2),
    tradable=False,
    spawnable=False,
    cursable=False,
    blessable=False,
    flammable=0,
    corrodible=0,
    droppable=True,
    stackable=True,
    counter_at_front=True,
    stack_count=amount,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=1, break_chance=0, air_friction=1),
    edible=None
)
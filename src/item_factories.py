from components import readable, quaffable, equipable, throwable
from components.item_state import ItemState
from entity import Item
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
    name="회복의 물약",
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
        break_chance=1,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0
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
    name="마나 회복의 물약",
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
    name="마비 물약",
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
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0
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
    name="수면 물약",
    entity_id="potion_of_paralysis",
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
    name="생명체 탐지의 물약",
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
    name="화염의 물약",
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
    name="강산성 물약",
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
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # Handle in quaffable
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
    name="냉기의 물약",
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
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # Handle in quaffable
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
    name="맹독의 물약",
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
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # Handle in quaffable
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
    name="공중 부양의 물약",
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
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # handle in quaffable
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
    name="액화 개미 물약",
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
    name="혼란의 주문서",
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
    name="운석 폭풍의 주문서",
    entity_id="scroll_of_meteor_storm",
    entity_desc=("운석 폭풍의 주문서를 읽은 사용자는 한 차례 자신이 원하는 공간에 거대한 운석을 소환할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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
    name="번개의 주문서",
    entity_id="scroll_of_lightning",
    entity_desc=("번개의 주문서를 읽으면 읽은 사용자의 주변에 강력한 방전 현상이 발생해 주위 생명체에 강력한 번개를 내리친다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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
    readable=readable.ScrollOfLightningReadable(damage_range=(38, 45), maximum_range=20),
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
    entity_desc=("마법 광선의 주문서를 읽은 사용자는 강력한 마법 에너지가 내재된 광선을 발사할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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


### Scroll of magic mapping
scroll_of_magic_mapping = Item(
    should_randomize=True,
    char="~",
    fg=(255, 90, 90),
    name="마법 지도의 주문서",
    entity_id="scroll_of_magic_mapping",
    entity_desc=("마법 지도의 주문서를 읽은 사용자는 주위의 공간적 정보들을 일시적으로 인식할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
    rarity=65,
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
    name="맹렬한 화염 광선의 주문서",
    entity_id="scroll_of_scorching_ray",
    entity_desc=("맹렬한 화염 광선의 주문서를 읽은 사용자는 주위 것들을 태워버리는 강렬한 화염으로 이루어진 광선을 발사할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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
    name="얼어붙는 빙결 광선의 주문서",
    entity_id="scroll_of_freezing_ray",
    entity_desc=("얼어붙는 빙결 광선의 주문서를 읽은 사용자는 주위 것들을 얼려버리는 차가운 냉기로 이루어진 광선을 발사할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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
    name="복종의 주문서",
    entity_id="scroll_of_tame",
    entity_desc=("복종의 주문서를 읽은 사용자는 다른 생명체를 복종시킬 수 있는 강력한 고위 주문을 한 차례 사용할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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
    name="마법 강화의 주문서",
    entity_id="scroll_of_enchantment",
    entity_desc=("마법 강화의 주문서를 읽은 사용자는 보유 중인 도구에 마법 에너지를 부여해 도구의 성능을 강화할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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
    name="감정의 주문서",
    entity_id="scroll_of_identify",
    entity_desc=("감정의 주문서를 읽은 사용자는 원하는 물품의 성질에 대해 더 자세하게 이해할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
    rarity=85,
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
    name="저주 해제의 주문서",
    entity_id="scroll_of_remove_curse",
    entity_desc=("저주 해제의 주문서를 읽은 사용자는 물건에 걸린 저주를 제거할 수 있는 강력한 고위 마법을 한 차례 사용할 수 있게 된다. "),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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
    name="순간 이동의 주문서",
    entity_id="scroll_of_teleportation",
    entity_desc=("순간 이동의 주문서를 읽은 사용자는 물리적으로 떨어진 공간으로 순간 이동을 할 수 있는 고위 마법을 한 차례 사용할 수 있게 된다. "
                 "불안정한 이동을 하는 경우가 잦다고 한다. "
                 ),
    item_type_desc=("주문서들은 마법을 사용할 줄 모르거나 내재하고 있는 마력이 부족하더라도 마법을 사용할 수 있게 해주는 유용한 도구이다. "),
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


#########################################################################
############################# SKILLBOOKS ################################
#########################################################################

### steal skillbook
steal_skillbook = Item(
    should_randomize=False, # NOTE: Skillbook names are not randomized.
    char="=",
    fg=(255, 255, 200),
    name="'대도둑 레오파드의 소매치기 특강'이라고 적힌 책",
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
        read_msg="책에는 어떻게 하면 들키지 않고 소매치기를 할 수 있는지에 대한 내용들이 적혀있다.",
        comprehension_chance_per_int_bonus=1, # Guarenteed
    ),
    quaffable=None,
)
temp_items_lists.append(steal_skillbook)
item_rarity.append(steal_skillbook.rarity)


#########################################################################
############################# SPELLBOOKS ################################
#########################################################################

### lightning bolt spellbook
lightning_bolt_spellbook = Item(
    should_randomize=True,
    char="=",
    fg=(255, 255, 200),
    name="뇌격 마법서",
    entity_id="lightning_bolt_spellbook",
    item_type_desc=("마법서는 단순한 책들과는 격을 달리 하는 물건이다. "
                    "이들은 막대한 마법 에너지를 사용해 제작되며, 그 내용도 쉽게 이해하기 어려운 경우가 많다."),
    rarity=3,
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
        int_req=14,
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
    name="소울 볼트 마법서",
    entity_id="soul_bolt_spellbook",
    item_type_desc=("마법서는 단순한 책들과는 격을 달리 하는 물건이다. "
                    "이들은 막대한 마법 에너지를 사용해 제작되며, 그 내용도 쉽게 이해하기 어려운 경우가 많다."),
    rarity=4,
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
        int_req=14,
        comprehension_chance_per_int_bonus=0.1,
    ),
    quaffable=None,
)
temp_items_lists.append(soul_bolt_spellbook)
item_rarity.append(soul_bolt_spellbook.rarity)


#########################################################################
################################ ARMORS #################################
#########################################################################


####################### TORSO ################################
### Rags
rags = Item(
    char="[",
    fg=(231, 255, 173),
    name="천쪼가리",
    entity_id="rags",
    entity_desc=("다 헤져가는 천 쪼가리이다. "),
    rarity=5,
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
    name="가죽 갑옷",
    entity_id="leather_armor",
    entity_desc=("질긴 가죽을 덧대 만든 갑옷이다. "),
    rarity=10,
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
        protection_mag=1.6,
    )
)
temp_items_lists.append(leather_armor)
item_rarity.append(leather_armor.rarity)


### Iron Chain mail
iron_chain_mail = Item(
    char="[",
    fg=(94, 255, 0),
    name="철제 사슬 갑옷",
    entity_id="iron_chain_mail",
    entity_desc=("철로 만든 사슬들을 엮어 만든 갑옷이다. "),
    rarity=8,
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
        protection_mag=1.8,
    )
)
temp_items_lists.append(iron_chain_mail)
item_rarity.append(iron_chain_mail.rarity)


### Iron Scale Armor
iron_scale_armor = Item(
    char="[",
    fg=(166, 255, 254),
    name="철제 비늘 갑옷",
    entity_id="iron_scale_armor",
    entity_desc=("작은 철판들을 가죽에 덧대 만든 갑옷이다. "),
    rarity=8,
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
        protection_mag=1.5,
    )
)
temp_items_lists.append(iron_scale_armor)
item_rarity.append(iron_scale_armor.rarity)


### Iron Plate armor
iron_plate_armor = Item(
    char="[",
    fg=(255, 100, 50),
    name="철제 판금 갑옷",
    entity_id="iron_plate_armor",
    entity_desc=("철판들을 이어붙여 만든 갑옷이다. "),
    rarity=5,
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
        protection_mag=1.8,
    )
)
temp_items_lists.append(iron_plate_armor)
item_rarity.append(iron_plate_armor.rarity)


### Merchant robe
merchant_robe = Item(
    char="[",
    fg=(120, 60, 250),
    name="상인의 로브",
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
        fire_resistance=0.3,
        cold_resistance=0.3,
        shock_resistance=0.3,
        acid_resistance=0.3,
        poison_resistance=0.3,
        protection_mag=2,
    )
)
temp_items_lists.append(merchant_robe)
item_rarity.append(merchant_robe.rarity)


### Silk Dress
silk_dress = Item(
    char="[",
    fg=(255, 222, 251),
    name="실크 드레스",
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



################################## HEAD ######################################
### Iron Headpiece
iron_headpiece = Item(
    char="[",
    fg=(201, 168, 0),
    name="철제 전투모",
    entity_id="iron_headpiece",
    entity_desc=("머리 윗 부분을 보호해주는 철제 전투모이다. 가죽 끈을 턱에 둘러 머리에 고정시킬 수 있다. "),
    rarity=12,
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
    name="철제 투구",
    entity_id="iron_helmet",
    entity_desc=("철로 만들어진 투구이다. 얼굴 부분을 제외한 모든 부분이 철판으로 둘러쌓여 있다. "),
    rarity=10,
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
    name="철제 아멧",
    entity_id="iron_armet",
    entity_desc=("머리 전체를 보호하는 투구이다. 얼굴 부분에 철로 만들어진 바이저가 부착되어 있다. "),
    rarity=8,
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
        protection_mag=1.8,
    )
)
temp_items_lists.append(iron_armet)
item_rarity.append(iron_armet.rarity)


### Horned Helmet
horned_helmet = Item(
    char="[",
    fg=(166, 255, 254),
    name="뿔 달린 투구",
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
    name="가죽 바지",
    entity_id="leather_pants",
    entity_desc=("질긴 가죽으로 만들어진 바지이다. "),
    rarity=12,
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
        protection_mag=1.4,
    )
)
temp_items_lists.append(leather_pants)
item_rarity.append(leather_pants.rarity)


### Leather Armored Pants
leather_armored_pants = Item(
    char="[",
    fg=(120, 214, 175),
    name="가죽 장갑 하의",
    entity_id="leather_armored_pants",
    entity_desc=("가죽에 철판을 덧대 만든 하의이다. "),
    rarity=10,
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
        protection_mag=1.4,
    )
)
temp_items_lists.append(leather_armored_pants)
item_rarity.append(leather_armored_pants.rarity)


### Iron Armored Pants
iron_armored_pants = Item(
    char="[",
    fg=(159, 224, 90),
    name="철제 장갑 하의",
    entity_id="iron_armored_pants",
    entity_desc=("철판으로 만들어진 하의이다. "),
    rarity=7,
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
        protection_mag=1.66,
    )
)
temp_items_lists.append(iron_armored_pants)
item_rarity.append(iron_armored_pants.rarity)



################################## BOOTS ######################################
### Leather boots
leather_boots = Item(
    char="[",
    fg=(17, 168, 45),
    name="가죽 부츠",
    entity_id="leather_boots",
    entity_desc=("발목까지 올라오는 가죽 부츠이다. "),
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


### Iron boots
iron_boots = Item(
    char="[",
    fg=(17, 113, 168),
    name="철제 부츠",
    entity_id="iron_boots",
    entity_desc=("발목까지 올라오는 철제 부츠이다. "),
    rarity=8,
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
        protection_mag=1.38,
    )
)
temp_items_lists.append(iron_boots)
item_rarity.append(iron_boots.rarity)


#########################################################################
######################### MELEE WEAPONS #################################
#########################################################################

###### BLADES
### Wooden Dagger
wooden_dagger = Item(
    char=")",
    fg=(128, 84, 38),
    name="나무 단검",
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
    name="철제 단검",
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
        additional_melee=5,
        base_melee_mag=1.3,
        additional_melee_mag=1.4,
    ),
    lockpickable=(0.9,0.1),
)
temp_items_lists.append(iron_dagger)
item_rarity.append(iron_dagger.rarity)


### Scalpel
scalpel = Item(
    char=")",
    fg=(255, 77, 77),
    name="스칼펠",
    entity_id="scalpel",
    entity_desc="주로 외과 수술을 할 때 사용되는 날카로운 의료용 나이프이다. ",
    rarity=5,
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
        base_melee=6,
        additional_melee=1,
        melee_effects=(("bleed_target", 0.2),),
        melee_effects_var=((3, 0, 3),),
        base_melee_mag=1.2,
        additional_melee_mag=2.5,
    ),
    lockpickable=(1,0.3),
)
temp_items_lists.append(scalpel)
item_rarity.append(scalpel.rarity)


### Shortsword
shortsword = Item(
    char=")",
    fg=(215, 219, 171),
    name="숏소드",
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
        base_melee=10,
        additional_melee=8,
        base_melee_mag=1.4,
        additional_melee_mag=1.6
    ),
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
        base_melee=12,
        additional_melee=10,
        base_melee_mag=1.9,
        additional_melee_mag=1.8,
    ),
    lockpickable=(0.8,0.1),
)
temp_items_lists.append(longsword)
item_rarity.append(longsword.rarity)


### Sunbringer
sunbringer = Item(
    char=")",
    fg=(255, 34, 0),
    name="선브링거",
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
        base_melee=18,
        additional_melee=10,
        base_melee_mag=2.1,
        additional_melee_mag=2,
        melee_effects=(("burn_target", 0.8),),
        melee_effects_var=((10, 2, 0, 4),),
        fire_resistance=0.9,
    ),
    lockpickable=(0.8,0),
    is_artifact=True,
)
temp_items_lists.append(sunbringer)
item_rarity.append(sunbringer.rarity)



###### BLADES - MISC
swordstick = Item(
    char=")",
    fg=(196, 255, 202),
    name="소드 스틱",
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
        base_melee=11,
        additional_melee=2,
        charm=3,
        intelligence=1,
        base_melee_mag=1.5,
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
    name="도끼",
    entity_id="axe",
    entity_desc="나무를 벨 때 사용하는 도끼이다. ",
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
        additional_melee=17,
        base_melee_mag=1.3,
        additional_melee_mag=2.1,
    ),
    lockpickable=(0.8,0.05),
)
temp_items_lists.append(axe)
item_rarity.append(axe.rarity)


tomahawk = Item(
    char=")",
    fg=(120, 66, 245),
    name="토마호크",
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
        additional_melee=12,
        base_melee_mag=1.2,
        additional_melee_mag=1.9,
    ),
    lockpickable=(0.8,0.1),
)
temp_items_lists.append(tomahawk)
item_rarity.append(tomahawk.rarity)


# Battle Axe
battle_axe = Item(
    char=")",
    fg=(214, 51, 111),
    name="전투 도끼",
    entity_id="battle_axe",
    entity_desc="오로지 전투만을 위해 만들어진 도끼이다. 도끼날이 양면에 달려 있다.",
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
        base_melee=12,
        additional_melee=17,
        base_melee_mag=2,
        additional_melee_mag=2.5,
    ),
    lockpickable=(0.8,0),
)
temp_items_lists.append(battle_axe)
item_rarity.append(battle_axe.rarity)


###### CLUBS
### Forging hammer
forging_hammer = Item(
    char=")",
    fg=(92, 28, 28),
    name="단조용 망치",
    entity_id="forging_hammer",
    entity_desc="대장간에서 쇠를 내리칠 때 쓰이는 단조용 망치이다. 망치 머리의 끝부분이 둥그런 형태를 하고 있다.",
    rarity=3,
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
        base_melee=10,
        additional_melee=9,
        base_melee_mag=1.9,
        additional_melee_mag=1.8,
    ),
    lockpickable=(0.8,0),
)
temp_items_lists.append(forging_hammer)
item_rarity.append(forging_hammer.rarity)


### Giant Wood Club
giant_wood_club = Item(
    char=")",
    fg=(97, 53, 0),
    name="통나무 곤봉",
    entity_id="giant_wood_club",
    entity_desc="성인 남성 정도 크기의 거대한 나무 곤봉이다. ",
    rarity=2,
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
        base_melee=6,
        additional_melee=10,
        base_melee_mag=2,
        additional_melee_mag=2
    ),
    lockpickable=(0,0),
)
temp_items_lists.append(giant_wood_club)
item_rarity.append(giant_wood_club.rarity)


###### SHIELDS
### Wooden Shield
wooden_shield = Item(
    char=")",
    fg=(252, 186, 3),
    name="나무 방패",
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
    lockpickable=(0.05,0),
)
temp_items_lists.append(wooden_shield)
item_rarity.append(wooden_shield.rarity)


### Silver Shield
silver_shield = Item(
    char=")",
    fg=(189, 189, 189),
    name="은 방패",
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
    lockpickable=(0.1,0),
)
temp_items_lists.append(silver_shield)
item_rarity.append(silver_shield.rarity)


### Platinum Shield
platinum_shield = Item(
    char=")",
    fg=(255, 255, 255),
    name="백금 방패",
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
    lockpickable=(0.1,0),
)
temp_items_lists.append(platinum_shield)
item_rarity.append(platinum_shield.rarity)


### Iron Shield
iron_shield = Item(
    char=")",
    fg=(252, 186, 3),
    name="철제 방패",
    entity_id="iron_shield",
    entity_desc="철판으로 만들어진 믿음직한 방패이다. ",
    rarity=8,
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
    lockpickable=(0.1,0),
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
    char="⊕",
    fg = (255, 72, 0),
    name="쿠가의 아뮬렛",
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
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=15),
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
    char="⊕",
    fg = (255, 72, 0),
    name="지적 각성의 아뮬렛",
    entity_id="amulet_of_brilliance",
    entity_desc="착용자에게 지적인 영감을 부여한다고 알려진 아뮬렛이다. ",
    rarity=3,
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
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=15),
    equipable=equipable.Equipable(
        equipable_type=EquipableOrder.AMULET,
        upgrade=0,
        possible_regions=("amulet",),
        intelligence=4,
    ),
    edible=None
)
temp_items_lists.append(amulet_of_brilliance)
item_rarity.append(amulet_of_brilliance.rarity)


#########################################################################
############################### EDIBLES #################################
#########################################################################

### Corpses
corpse = Item(
    char="%",
    fg = (191, 0, 0),
    name="시체",# Name automatically changes later
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
    name="루비",
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
    name="에메랄드",
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
    name="사파이어",
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
    name="싸구려 유리 조각",
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
    name="싸구려 유리 조각",
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
    name="싸구려 유리 조각",
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
    name="싸구려 유리 조각",
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
################################# MISCS #################################
#########################################################################

### toxic Goo
toxic_goo = Item(
    char="*",
    fg = (61, 0, 82),
    name="독성 점액",
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
    name="샤인",
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
    name="샤인",
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
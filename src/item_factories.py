from components import readable, quaffable, equipable, throwable
from components.item_state import ItemState
from entity import Item
import color
import anim_graphics
import components.edible as edible
import ability_factories

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


### Potion of paralysis
potion_of_paralysis = Item(
    should_randomize=True,
    char="!",
    fg=(255, 0, 255),
    name="마비 물약",
    entity_id="potion_of_paralysis",
    entity_desc=("마비의 물약은 생명체를 일시적으로 마비시킬 수 있는 위험한 포션이다. "
                 "주로 사냥꾼들이 위험한 야수들을 사냥할 때 사용하곤 한다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
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
    throwable=throwable.PotionOfFlameThrowable(
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=1,
        identify_when_collided_with_entity=1,
        identify_when_collided_with_actor=1, # handle in quaffable
    ),
    readable=None,
    quaffable=quaffable.PotionOfFlameQuaffable(base_dmg=5, add_dmg=2, turn=10, fire_lifetime=10),
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
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0, # Handle in quaffable
    ),
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
    entity_desc=("냉기의 물약은 대기와 반응하면 순식간에 얼어붙는 성질을 지녔다. "
                 ),
    item_type_desc=("예로부터 물약은 인간, 비인간을 막론하고 다양한 지적 생명체들에게 널리 연구되어왔다. "
                    "때문에 지금은 그 종류도 굉장히 다양한데, 이 중 일부는 생명체에게 치명적인 효과를 부여하기도 한다. "
                    "대부분의 물약들은 신체에 빠르게 흡수되며 극도로 높은 반응성을 띄기 때문에 주로 유리병에 담아 보관한다."
                    ),
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
    throwable=throwable.PotionQuaffAndThrowSameEffectThrowable(
        break_chance=1,
        trigger_if_thrown_at=True,
        identify_when_shattered=0,
        identify_when_collided_with_entity=0,
        identify_when_collided_with_actor=0,
    ),
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
    rarity=30,
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
    rarity=12,
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
    rarity=20,
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
    readable=readable.ScrollOfThunderStormReadable(damage_range=(38,45), maximum_range=20),
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
    rarity=40,
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
    rarity=40,
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
    rarity=20,
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
    rarity=20,
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
    rarity=10,
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
    rarity=40,
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
    rarity=60,
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
    initial_BUC={1:1,0:10,-1:1} # rarely blessed
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
    rarity=40,
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
    rarity=2,
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



#########################################################################
################################ ARMORS #################################
#########################################################################

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
    equipable=equipable.SilkDressEquipable()
)
temp_items_lists.append(silk_dress)
item_rarity.append(silk_dress.rarity)


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
    rarity=8,
    weight=0.14,
    price=3,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.3,
    corrodible=0.06,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=3, additional_throw=2, penetration=True, air_friction=1),
    equipable=equipable.WoodenDaggerEquipable(),
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
    rarity=9,
    weight=0.4,
    price=8,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.05,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=6, additional_throw=3, penetration=True, air_friction=1),
    equipable=equipable.IronDaggerEquipable(),
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
    rarity=2,
    weight=0.19,
    price=50,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=6, additional_throw=1, penetration=True, air_friction=1),
    equipable=equipable.ScalpelEquipable(),
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
    rarity=5,
    weight=1.5,
    price=25,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.03,
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
    entity_desc="양쪽 모두에 날이 달려있는 긴 검이다. 기사들이 즐겨 사용하는 무기이다. ",
    rarity=3,
    weight=1.8,
    price=75,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.03,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=20),
    equipable=equipable.LongswordEquipable(),
    lockpickable=(0.8,0.1),
)
temp_items_lists.append(longsword)
item_rarity.append(longsword.rarity)


###### BLADES - MISC
swordstick = Item(
    char=")",
    fg=(196, 255, 202),
    name="소드 스틱",
    entity_id="swordstick",
    entity_desc="화려한 보석들로 치장된 지팡이 형태의 칼이다. 손잡이 부분을 당겨 긴 날이 달린 검을 뽑을 수 있다. ",
    rarity=3,
    weight=0.62,
    price=350,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=1, penetration=False, air_friction=3),
    equipable=equipable.SwordstickEquipable(),
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
    rarity=9,
    weight=3,
    price=5,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.01,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=2, additional_throw=2, penetration=False, air_friction=1),
    equipable=equipable.AxeEquipable(),
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
    rarity=3,
    weight=0.35,
    price=120,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0.01,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=6, additional_throw=8, penetration=False, air_friction=0.2),
    equipable=equipable.TomahawkEquipable(),
    lockpickable=(0.8,0.1),
)
temp_items_lists.append(tomahawk)
item_rarity.append(tomahawk.rarity)


###### CLUBS
### Giant Wood Club
giant_wood_club = Item(
    char=")",
    fg=(97, 53, 0),
    name="통나무 곤봉",
    entity_id="giant_wood_club",
    entity_desc="성인 남성 정도 크기의 거대한 나무 곤봉이다. ",
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


###### SHIELDS
### Wooden Shield
wooden_shield = Item(
    char=")",
    fg=(252, 186, 3),
    name="나무 방패",
    entity_id="wooden_shield",
    entity_desc="나무를 덧대 만든 방패이다. ",
    rarity=5,
    weight=3.2,
    price=5,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0.2,
    corrodible=0.04,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=55),
    equipable=equipable.WoodenShieldEquipable(),
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
    rarity=1,
    weight=2.7,
    price=650,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=55),
    equipable=equipable.SilverShieldEquipable(),
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
    rarity=1,
    weight=2.9,
    price=1250,
    item_type=InventoryOrder.MELEE_WEAPON,
    item_state=ItemState(is_identified=1),
    flammable=0,
    corrodible=0,
    spawnable=True,
    droppable=True,
    stackable=False,
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=55),
    equipable=equipable.PlatinumShieldEquipable(),
    lockpickable=(0.1,0),
)
temp_items_lists.append(platinum_shield)
item_rarity.append(platinum_shield.rarity)


### Iron Shield
iron_shield = Item(
    char=")",
    fg=(252, 186, 3),
    name="강철 방패",
    entity_id="iron_shield",
    entity_desc="강철로 만들어진 믿음직한 방패이다. ",
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
    throwable=throwable.NormalThrowable(base_throw=0, additional_throw=0, penetration=False, air_friction=55),
    equipable=equipable.IronShieldEquipable(),
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
    equipable=equipable.AmuletOfKugahEquipable(),
    edible=None,
    initial_BUC={1:1, 0:0, -1:0},
    initial_upgrades={0:1}
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
    throwable=throwable.NormalThrowable(base_throw=1, additional_throw=2, penetration=False, air_friction=15),
    equipable=equipable.AmuletOfBrillianceEquipable(),
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
temp_items_lists.append(diamond)
item_rarity.append(diamond.rarity)


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
    rarity=2,
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
    rarity=2,
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
    rarity=1,
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
    rarity=1,
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
    char="•",# Unicode bullet
    fg = (44, 23, 61),
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
    change_stack_count_when_dropped=(1,1),
    stackable=False,
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
    item_state=ItemState(is_identified=1),
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
    item_state=ItemState(is_identified=1),
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
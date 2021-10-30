import random

import ai_factories
import item_factories
import ability_factories
import components.edible as edible
from components.status import Status
from components.inventory import Inventory
from components.ability_inventory import AbilityInventory
from components.equipments import Equipments
from components.actor_state import ActorState
from entity import Actor
from order import RenderOrder, InventoryOrder
from typing import Optional
from components.ai import BaseAI

### NOTE: Rarity can have value between 0 and 10 ###
class ActorDB:
    monster_difficulty = { # Includes both surface and underwater
        0: [],
        1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
        11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [],
        21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [],
    }

    monster_rarity_for_each_difficulty = {
        0: [],
        1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
        11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [],
        21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [],
    }

    surface_monster_difficulty = {}
    underwater_monster_difficulty = {} # Underwater monsters are also stored in monster_difficulty dictionary.
    # k, v = difficulty, actor
    
    def get_actor_by_id(entity_id: str) -> Optional[Actor]:
        for monslist in ActorDB.monster_difficulty.values():
            for mon in monslist:
                if mon.entity_id == entity_id:
                    return mon
        print(f"WARNING::Can't find {entity_id} from ActorDB.")
        return None


### DEBUG
DEBUG = Actor(
    char="?",
    fg=(63, 127, 63),
    name="DEBUG",
    entity_id="DEBUG",
    entity_desc="DEBUG",
    rarity=0,
    weight = 70,
    spawnable=False,
    edible=edible.RawMeatEdible(nutrition=300),
    ai_cls=None,
    status=Status(
        hp=30,
        mp=0,
        strength=6,
        dexterity=2,
        agility=15,
        intelligence=1,
        constitution=4,
        charm=1,
        difficulty=0,
        base_melee=3,
        additional_melee=1,
        protection=3,
        eyesight=6,
        ),
    actor_state=ActorState(
        size=4,
        heal_wounds=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=10),
    equipments=Equipments(),
)
#ActorDB.monster_difficulty[DEBUG.status.difficulty].append(DEBUG)


####################################################
################## @ - Humanoids  ##################
####################################################

### Player
player = Actor(
    char="@",
    fg=(0, 255, 0),
    name="모험가",
    entity_id="player",
    actor_type_desc=("당신은 쿠가의 아뮬렛을 가져오라는 임무를 받고 끝이 보이지 않는 던전으로 발을 들였다. "),
    rarity=0,
    weight=70,
    spawnable=False,
    growthable=True,
    edible=edible.RawMeatEdible(nutrition=400),
    render_order=RenderOrder.PLAYER,
    ai_cls=None,
    status=Status(
        hp=180, #180
        mp=50, #50
        strength=15, # can be changed during CharGen
        dexterity=15,
        agility=15,
        intelligence=15,
        constitution=15,
        charm=15,
        difficulty=0,
        base_melee=10, #10
        additional_melee=10,
        protection=10,
        eyesight=20,
        hearing=15,
        ),
    actor_state=ActorState(
        hunger=1199,
        heal_wounds=True,
        regain_mana=True,
        size=4,
        can_talk=True,
        # has_telepathy=True, #DEBUG
        # has_right_arm=True,  #DEBUG
    ),
    inventory=Inventory(capacity=52, is_fireproof=False, is_acidproof=False, is_waterproof=False),
    ability_inventory=AbilityInventory(capacity=26),
    equipments=Equipments(),
    # initial_items=
    # (
    #     {"item": item_factories.iron_dagger, "chance": 1, "count": (1, 1), "BUC": {1:0,0:1,-1:0}, "upgrade": {1:1}},
    #     {"item": item_factories.ration, "chance": 1, "count": (1, 1), "BUC": {1:0,0:1,-1:0}, "upgrade": None},
    # ),
#     initial_equipments=(
#         {"item":item_factories.longsword, "chance":1, "count":(1,1), "BUC":None, "upgrade": {0:1}},
# {"item":item_factories.iron_plate_armor, "chance":1, "count":(1,1), "BUC":None, "upgrade": {0:1}},
# {"item":item_factories.iron_armored_pants, "chance":1, "count":(1,1), "BUC":None, "upgrade": {0:1}},
# {"item":item_factories.iron_helmet, "chance":1, "count":(1,1), "BUC":None, "upgrade": {0:1}},
# {"item":item_factories.iron_gauntlet, "chance":1, "count":(1,1), "BUC":None, "upgrade": {0:1}},
# {"item":item_factories.elven_cloak, "chance":1, "count":(1,1), "BUC":None, "upgrade": {0:1}},
#     ),
    # initial_abilities=
    # (
    #     (ability_factories.cure_wound, 1),
    #     (ability_factories.mesmerize, 1),
    #     (ability_factories.teleport, 1),
    # )
)


### Shopkeeper
shopkeeper = Actor(
    char="@",
    fg=(214, 181, 49),
    name="상인",
    entity_id="shopkeeper",
    entity_desc=("던전 속에서 장사를 하기 위해서는 많은 것들이 필요하다. "
    "고객을 사로잡는 화려한 언변, 값어치있는 물건을 알아보는 눈썰미, 물건을 감정하기 위한 폭 넓은 지식. "
    "그러나 무엇보다 중요한 건, 바로 상점을 지킬 힘이다. "),
    actor_quote=("저 아래 괴물 소굴에서 장사하는 놈들은 둘 중에 하나야. 미쳤거나, 아니면 완전히 정신이 나갔거나. "),
    rarity=0,
    weight = 75,
    swappable=False, # Cannot swap
    spawnable=False,
    edible=edible.RawMeatEdible(nutrition=300),
    ai_cls=ai_factories.Shopkeeper_Ai(),
    status=Status(
        hp=650,
        mp=450,
        strength=28,
        dexterity=25,
        agility=30,
        intelligence=26,
        constitution=29,
        charm=25,
        difficulty=30,
        base_melee=33,
        additional_melee=20,
        protection=35,
        eyesight=80,
        hearing=30,
        fire_resistance=0.5,
        poison_resistance=0.5,
        cold_resistance=0.5,
        acid_resistance=0.5,
        psychic_resistance=0.9,
        sleep_resistance=0.9,
        shock_resistance=0.5,
        magic_resistance=0.9,
        ),
    actor_state=ActorState(
        heal_wounds=True,
        regain_mana=True,
        size=4,
        sexuality="male",
        can_swim=True,
        can_breathe_underwater=True,
        has_telepathy=True, # Shopkeeper has telepathy
        can_think=True,
        can_talk=True,
        has_inner_peace=True,
    ),
    inventory=Inventory(capacity=52, is_fireproof=True),
    ability_inventory=AbilityInventory(capacity=10),
    equipments=Equipments(),
    initial_items=(
        {"item":item_factories.shine, "chance":1, "count":(2000,3500), "BUC":None, "upgrade":None},
        ),
    initial_equipments=(
        {"item":item_factories.merchant_robe, "chance":1, "count":(1,1), "BUC": None, "upgrade":None},
    ),
    initial_abilities=None,
)
ActorDB.monster_difficulty[shopkeeper.status.difficulty].append(shopkeeper)


####################################################
###################### a - ants  ###################
####################################################

### ant
ant = Actor(
    char="a",
    fg=(51, 13, 0),
    name="개미",
    entity_id="ant",
    entity_desc=("던전에서 뿜어나오는 어두운 기운은 동물은 물론 곤충들까지 거대하고 흉측한 괴수로 변이시켰다. "
    "그렇지만 개중에는 어두운 기운의 영향을 덜 받은 개체들도 있기 마련이다. "
    "비교적 던전의 기운을 덜 받은 이 개미들은 기껏해야 사람 손가락 남짓한 크기로, 대체로 별 위협이 되지 않는다. "),
    actor_quote=("우리 엄마는 저보고 항상 개미같이 열심히 일하는 사람이 되라고 말했어요. "),
    rarity=15,
    weight = 0.07,
    spawnable=True,
    edible=edible.InsectEdible(nutrition=10),
    ai_cls=BaseAI(
        alignment=(("hostile",),(1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat", "insect",),
    ),
    status=Status(
        hp=28,
        mp=0,
        strength=4,
        dexterity=6,
        agility=10,
        intelligence=4,
        constitution=6,
        charm=3,
        difficulty=2,
        base_melee=3,
        additional_melee=4,
        protection=6,
        eyesight=8,
        hearing=9,
        acid_resistance=0.2,
        ),
    actor_state=ActorState(
        size=2,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_think=True,
        can_talk=False,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[ant.status.difficulty].append(ant)


### fire ant
fire_ant = Actor(
    char="a",
    fg=(255, 0, 0),
    name="불개미",
    entity_id="fire_ant",
    entity_desc=("던전의 불개미들은 만지면 따끔한 수준의 지상의 불개미들과는 차원이 다른 존재이다. "
    "성인 남성 주먹 정도의 크기인 이들은, 전신에 두른 약한 화염으로 자신을 방어한다. "
    "이들이 턱에서 쏘는 작은 불꽃은 인간에게 크게 위협적이지는 않지만, "
    "책이나 주문서를 가지고 다니는 마법사들에게는 큰 골칫거리로 여겨진다. "),
    actor_quote=("썅, 빌어먹을 불개미녀석들, 이번에는 400샤인짜리 주문서를 태워먹었다고. "),
    rarity=30,
    weight=0.1,
    spawnable=True,
    edible=edible.FireAntEdible(nutrition=40),
    ai_cls=BaseAI(
        alignment=(("hostile",),(1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat", "insect",),
    ),
    status=Status(
        hp=36,
        mp=0,
        strength=5,
        dexterity=8,
        agility=10,
        intelligence=4,
        constitution=7,
        charm=5,
        difficulty=4,
        base_melee=5,
        additional_melee=7,
        protection=9,
        hearing=7,
        eyesight=15,
        fire_resistance=1,
        melee_effects_var=((3,1,0,4),),
        melee_effects=(("burn_target", 0.2),),
        ),
    actor_state=ActorState(
        size=2,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_think=True,
        can_talk=False,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[fire_ant.status.difficulty].append(fire_ant)


### volt ant
volt_ant = Actor(
    char="a",
    fg=(99, 255, 193),
    name="스파크 개미",
    entity_id="volt_ant",
    entity_desc=("스파크 개미들은 몸에 두른 전류를 통해 적으로부터 자신을 보호한다. "
    "스파크 개미는 시큼텁텁한 맛이 나는 것으로 알려져 있으며, 일부 모험가들 사이에서는 별미로 꼽힌다. "),
    actor_quote=("이놈들을 잔뜩 잡아서 안주로 팔면 대박이 날 거야. "),
    rarity=30,
    weight=0.1,
    spawnable=True,
    edible=edible.VoltAntEdible(nutrition=40),
    ai_cls=BaseAI(
        alignment=(("hostile",),(1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat", "insect",),
    ),
    status=Status(
        hp=36,
        mp=0,
        strength=5,
        dexterity=8,
        agility=10,
        intelligence=4,
        constitution=7,
        charm=5,
        difficulty=4,
        base_melee=5,
        additional_melee=7,
        protection=9,
        hearing=7,
        eyesight=15,
        shock_resistance=1,
        melee_effects_var=((5, 0.5),),
        melee_effects=(("electrocute_target", 0.8),),
        ),
    actor_state=ActorState(
        size=2,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_think=True,
        can_talk=False,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[volt_ant.status.difficulty].append(volt_ant)


####################################################
#################  b- bats / birds  ################
####################################################

### Bat
bat = Actor(
    char="b",
    fg=(94, 0, 122),
    name="박쥐",
    entity_id="bat",
    entity_desc=("박쥐는 조류가 아님에도, 공중에서 자유자재로 날아다닐 수 있는 비행능력을 보유하고 있다. "
    "특유의 혐오감을 주는 외형 때문에 이들은 오랜 시간 인간들에게 박해받아왔고, 때문에 인간의 발길이 비교적 적은 던전 속에서 살아가는 박쥐들의 수가 점점 늘어나고 있다. "),
    actor_quote=("동굴에 사는 쬐끄만 박쥐들은 오래 보면 귀엽기라도 하단 말이야. 근데 던전에 사는 놈들은 몇 번을 봐도 적응이 안된단 말이지. "),
    rarity=30,
    weight=3,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=70, cook_bonus=10),
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral",),(3,1)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("insect", "fruit"),
    ),
    status=Status(
        hp=56,
        mp=0,
        strength=5,
        dexterity=8,
        agility=19,
        intelligence=3,
        constitution=8,
        charm=1,
        difficulty=5,
        base_melee=2,
        additional_melee=6,
        protection=7,
        hearing=25,
        eyesight=20,
        psychic_resistance=0.2,
        ),
    actor_state=ActorState(
        size=2,
        is_flying=True,
        can_fly=True,
        can_talk=False,
        has_left_arm=False,
        has_right_arm=False,
        has_wing=True,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_move_on_surface=False,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[bat.status.difficulty].append(bat)


####################################################
#####################  c- cats  ####################
####################################################

### Kitten
kitten = Actor(
    char="c",
    fg=(222, 208, 169),
    name="새끼고양이",
    entity_id="kitten",
    entity_desc=("던전 속에서 새끼고양이는 둘 중 하나로 취급된다. "
    "작고 귀여운 동물, "
    "혹은 영양가 넘치는 자그마한 고깃덩어리. "),
    actor_quote=("얼마 전 옆집 고양이가 새끼를 낳았다던데, 그 집 식구들이 요즘 기운이 넘쳐보이는 건 기분 탓인가? "),
    rarity=10,
    weight=3.3,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=100, cook_bonus=30),
    ai_cls=BaseAI(
        alignment=(("hostile","neutral"),(1,1)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("insect", ),
    ),
    status=Status(
        hp=32,
        mp=10,
        strength=6,
        dexterity=11,
        agility=12,
        intelligence=6,
        constitution=10,
        charm=15,
        difficulty=3,
        base_melee=6,
        additional_melee=10,
        protection=8,
        hearing=20,
        eyesight=20,
        ),
    actor_state=ActorState(
        size=2,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=False,# NOTE: baby cats cannot swim
        can_talk=False,
    ),
    inventory=Inventory(capacity=2),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[kitten.status.difficulty].append(kitten)


### Cat
cat = Actor(
    char="c",
    fg=(217, 184, 91),
    name="고양이",
    entity_id="cat",
    entity_desc=("고양이들은 게으르지만 맹수의 본능을 지닌 민첩한 사냥꾼들이다. "
    "이들은 잡식성이고 시력이 좋기 때문에 많은 모험가들에게 애완동물로 사랑받는다. "
    "고양이들이 사람의 꿈을 조종하는 영적인 능력을 지녔다고 주장하는 학자들도 있지만, 명확히 밝혀진 것은 없다. "),
    actor_quote=("그 녀석하고 눈이 마주친 날이면 난 항상 악몽을 꿔. 그런데도 왜일까, 녀석만 보면 자꾸 먹이를 주게 돼. "),
    rarity=40,
    weight=6.5,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=120, cook_bonus=50),
    ai_cls=BaseAI(
        alignment=(("hostile","neutral"),(3,1)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("insect", "meat"),
    ),
    status=Status(
        hp=55,
        mp=15,
        strength=12,
        dexterity=12,
        agility=15,
        intelligence=10,
        constitution=11,
        charm=13,
        difficulty=6,
        base_melee=10,
        additional_melee=13,
        protection=12,
        hearing=22,
        eyesight=20,
        ),
    actor_state=ActorState(
        size=3,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
    ),
    inventory=Inventory(capacity=8),
    ability_inventory=AbilityInventory(capacity=4),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[cat.status.difficulty].append(cat)


### Large Cat
large_cat = Actor(
    char="c",
    fg=(230, 169, 0),
    name="큰 고양이",
    entity_id="large_cat",
    entity_desc=("던전의 기운을 받은 고양이들은 지상의 맹수에 가까운 크기로 자라기도 한다. " 
        "이들은 결코 맹수는 아니지만, 무방비한 모험가에게는 충분한 위협이 될 수 있다. "),
    actor_quote=("내 흉터가 고양이 때문에 생겼다는 건 죽어도 비밀이다, 알겠지? "),
    rarity=35,
    weight=18.5,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=150, cook_bonus=60),
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (7, 1)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=65,
        mp=25,
        strength=15,
        dexterity=19,
        agility=19,
        intelligence=10,
        constitution=14,
        charm=13,
        difficulty=9,
        base_melee=13,
        additional_melee=13,
        protection=13,
        hearing=23,
        eyesight=22,
        ),
    actor_state=ActorState(
        size=4,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=8),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[large_cat.status.difficulty].append(large_cat)


####################################################
####################  d - dogs  ####################
####################################################


### puppy
puppy = Actor(
    char="d",
    fg=(196, 220, 255),
    name="강아지",
    entity_id="puppy",
    actor_type_desc=("인간 최고의 친구라는 이명은 던전 안에서도 예외가 아니다. "
        "이들은 한 번 충성을 바친 주인에게는 무슨 일이 있어도 복종하며, 자신의 목숨을 바치는 데에도 망설임이 없다. "),
    entity_desc=("강아지들은 호기심이 넘치는 존재들이다. "
        "이들은 성체에 비해 한참 뒤떨어지는 신체능력을 가졌지만, 넘치는 에너지 만큼은 성체를 압도한다. "),
    actor_quote=("포션술사는 절대 강아지를 길러선 안돼. 집이 언제 불바다가 될 지 모르거든. "),
    rarity=10,
    weight=5.7,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=110, cook_bonus=12),
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 1)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=32,
        mp=0,
        strength=7,
        dexterity=10,
        agility=11,
        intelligence=7,
        constitution=10,
        charm=15,
        difficulty=3,
        base_melee=5,
        additional_melee=3,
        protection=8,
        hearing=20,
        eyesight=18,
        ),
    actor_state=ActorState(
        size=3,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
    ),
    inventory=Inventory(capacity=3),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[puppy.status.difficulty].append(puppy)


### Dog
dog = Actor(
    char="d",
    fg=(105, 165, 255),
    name="개",
    entity_id="dog",
    actor_type_desc=("인간 최고의 친구라는 이명은 던전 안에서도 예외가 아니다. "
        "이들은 한 번 충성을 바친 주인에게는 무슨 일이 있어도 복종하며, 자신의 목숨을 바치는 데에도 망설임이 없다. "),
    actor_quote=("가족이 날 버려도 너만은 함께 해주는구나, 토비. "),
    rarity=35,
    weight=38.5,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=160, cook_bonus=50),
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (3, 1)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=60,
        mp=10,
        strength=13,
        dexterity=11,
        agility=12,
        intelligence=11,
        constitution=13,
        charm=13,
        difficulty=6,
        base_melee=12,
        additional_melee=8,
        protection=13,
        hearing=25,
        eyesight=18,
        ),
    actor_state=ActorState(
        size=3,
        can_swim=True,
        can_talk=False,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=15),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[dog.status.difficulty].append(dog)


### Large Dog
large_dog = Actor(
    char="d",
    fg=(0, 102, 255),
    name="큰 개",
    entity_id="large_dog",
    actor_type_desc=("인간 최고의 친구라는 이명은 던전 안에서도 예외가 아니다. "
        "...적으로 마주치지만 않는다면. "),
    actor_quote=("사냥꾼의 가장 강력한 무기는 단검도, 활도 아니야. 그건 바로 녀석의 사냥개지. "),
    rarity=35,
    weight=55.3,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=200, cook_bonus=30),
    ai_cls=BaseAI(
        alignment=(("hostile", ), (1, )),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=68,
        mp=10,
        strength=17,
        dexterity=17,
        agility=16,
        intelligence=11,
        constitution=14,
        charm=15,
        difficulty=9,
        base_melee=15,
        additional_melee=8,
        protection=14,
        hearing=25,
        eyesight=21,
        ),
    actor_state=ActorState(
        size=4,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
    ),
    inventory=Inventory(capacity=25),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[large_dog.status.difficulty].append(large_dog)


### Cerberus
cerberus = Actor(
    char="d",
    fg=(227, 45, 0),
    name="케르베로스",
    entity_id="cerberus",
    entity_desc=("머리가 세 개 달린 커다란 개의 형상을 하고 있는 케르베로스는 예로부터 많은 사람들에게 공포의 대상으로 여겨졌다. "
        "이들은 일반적인 개들보다 뛰어난 신체 능력을 가지고 있으며, 세 개의 머리에서 약한 화염을 내뿜을 수 있다. "
        "세 개의 머리는 각각 별도의 자아를 지니고 있으나, 몸의 지배권 또한 세 개로 나누어져 있는지는 밝혀지지 않았다. "),
    rarity=18,
    weight=165,
    spawnable=True,
    edible=edible.CerberusEdible(nutrition=350, cook_bonus=85),
    ai_cls=BaseAI(
        alignment=(("hostile", ), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        hostile_type=('@',),
        use_ability=False,
    ),
    status=Status(
        hp=75,
        mp=66,
        strength=18,
        dexterity=18,
        agility=15,
        intelligence=15,
        constitution=18,
        charm=18,
        difficulty=10,
        base_melee=23,
        additional_melee=10,
        protection=18,
        hearing=14,
        eyesight=23,
        melee_effects_var=((3, 2, 0, 6),),
        melee_effects=(("burn_target", 0.3),),
        ),
    actor_state=ActorState(
        size=4,
        has_head=3, # 3 heads
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
    ),
    inventory=Inventory(capacity=33),
    ability_inventory=AbilityInventory(capacity=8),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[large_dog.status.difficulty].append(cerberus)


####################################################
################  e - eyes & brains  ###############
####################################################

### floating eye
floating_eye = Actor(
    char="e",
    fg=(255, 255, 255),
    name="떠다니는 눈",
    entity_id="floating_eye",
    entity_desc=("던전 안의 많은 생명체들 중에서도 가장 기원을 알 수 없는 존재가 바로 '떠다니는 눈' 들이다. "
        "이들은 눈을 마주치는 것으로 생명체를 마비시킬 수 있는 강력한 힘을 가졌지만 "
        "다행히 이들은 호전적이지 않으며, 또 물리적으로는 아무런 위협이 되지 못한다. "),
    actor_quote=("녀석의 눈을 바라봤을 때, 마치 몸의 지배권을 빼앗기는 느낌이었어. 내가 녀석이 되고 녀석이 내가 되는 듯한 느낌이었지. "),
    rarity=15,
    weight=255.8,
    spawnable=True,
    edible=edible.FloatingEyeEdible(nutrition=120),#cannot be cooked
    ai_cls=ai_factories.Floating_Eye_Ai(),
    status=Status(
        hp=68,
        mp=30,
        strength=5,
        dexterity=2,
        agility=5,
        intelligence=7,
        constitution=13,
        charm=7,
        difficulty=4,
        base_melee=0,
        additional_melee=0,
        protection=10,
        hearing=1,
        eyesight=35,
        sleep_resistance=1,
        ),
    actor_state=ActorState(
        size=3,
        sexuality="None",
        has_head=0,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_talk=False,
        can_breathe_underwater=True,  # Don't Breathe
        can_fly=True,
        is_flying=True,
        has_telepathy=True,
        has_inner_peace=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[floating_eye.status.difficulty].append(floating_eye)


####################################################
########### f - fish & sharks & whales  ############
####################################################

### Piranha
piranha = Actor(
    char="f",
    fg=(0, 255, 0),
    name="피라냐",
    entity_id="piranha",
    entity_desc=("포악한 성격과 게걸스러운 식성으로 악명높은 피라냐는, 수영하기를 좋아하는 모험가들에게는 상당히 골치아픈 존재이다."
                 "이들은 날카로운 이빨로 먹이를 인정사정없이 물어뜯으며, 작은 몸집에 걸맞는 재빠른 움직임을 보여주기 때문에 많은 주의가 필요하다."),
    actor_quote=("백상아리도 피라냐 떼 앞에서는 맛있는 고깃덩어리에 지나지 않지."),
    rarity=30,
    weight=5.4,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=50, cook_bonus=50),
    ai_cls=BaseAI(
        alignment=(("hostile", ), (1, )),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=30,
        mp=0,
        strength=8,
        dexterity=13,
        agility=18,
        intelligence=5,
        constitution=6,
        charm=7,
        difficulty=6,
        base_melee=5,
        additional_melee=10,
        protection=5,
        hearing=3,
        eyesight=5,
        melee_effects_var=((1, 0, 3),),
        melee_effects=(("bleed_target", 0.5),),
        ),
    actor_state=ActorState(
        size=2,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
        can_move_on_surface=False,
        can_breathe_air=False,
        can_breathe_underwater=True,
        live_underwater=True,
    ),
    inventory=Inventory(capacity=3),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[piranha.status.difficulty].append(piranha)


### Eel
eel = Actor(
    char="f",
    fg=(0, 234, 255),
    name="뱀장어",
    entity_id="eel",
    entity_desc=("던전 속의 뱀장어들은 평범한 뱀장어들보다 두 배 가량 거대한 크기를 자랑한다. "
                 "이들은 날카로운 비늘과 지느러미로 상대를 공격하며 때로는 마치 뱀처럼 먹이를 칭칭 감아 집어삼키기도 한다. "
                 "뱀장어의 고기는 어류 중에서도 특히 영양분이 풍부한 것으로 알려져 있다. "),
    rarity=30,
    weight=13.2,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=330, cook_bonus=150),
    ai_cls=BaseAI(
        alignment=(("hostile", ), (1, )),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=65,
        mp=0,
        strength=13,
        dexterity=15,
        agility=19,
        intelligence=7,
        constitution=6,
        charm=7,
        difficulty=9,
        base_melee=7,
        additional_melee=15,
        protection=8,
        hearing=3,
        eyesight=5,
        ),
    actor_state=ActorState(
        size=3,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
        can_move_on_surface=False,
        can_breathe_air=False,
        can_breathe_underwater=True,
        live_underwater=True,
    ),
    inventory=Inventory(capacity=3),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[eel.status.difficulty].append(eel)


### Electric eel
electric_eel = Actor(
    char="f",
    fg=(0, 255, 208),
    name="전기뱀장어",
    entity_id="electric_eel",
    entity_desc=("'소리없는 죽음'이라는 별명으로도 불리는 전기뱀장어들은, 상대에게 소리없는 강력한 전격 피해를 가하는 것으로 알려져 있다. "
                 "이들은 외형적으로 평범한 뱀장어와 큰 차이가 없기 때문에 뱀장어를 사냥하려다 되려 이들에게 사망하는 경우가 종종 발생한다. "),
    actor_quote=("뱀장어 구이를 좋아하던 옆집 녀석의 이야기를 듣고 나서부터 난 평생 고등어만 먹기로 다짐했지."),
    rarity=10,
    weight=13.5,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=50, cook_bonus=50),
    ai_cls=BaseAI(
        alignment=(("hostile", ), (1, )),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=65,
        mp=0,
        strength=13,
        dexterity=15,
        agility=19,
        intelligence=7,
        constitution=6,
        charm=7,
        difficulty=12,
        base_melee=7,
        additional_melee=15,
        protection=8,
        hearing=3,
        eyesight=5,
        melee_effects_var=((20, 0.9),),
        melee_effects=(("electrocute_target", 1),),
        ),
    actor_state=ActorState(
        size=3,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
        can_move_on_surface=False,
        can_breathe_air=False,
        can_breathe_underwater=True,
        live_underwater=True,
    ),
    inventory=Inventory(capacity=3),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[electric_eel.status.difficulty].append(electric_eel)


####################################################
############### i = flying insects  ################
####################################################

### fly
fly = Actor(
    char="i",
    fg=(171, 63, 63),
    name="파리",
    entity_id="fly",
    entity_desc=("\'던전의 청소부\' 라는 이명으로도 불리는 이 파리들은, 지상의 파리보다 몇 십 배는 더 큰 덩치에 걸맞는 왕성한 식욕을 보여준다. "
        "이들은 던전 속 썩어가는 거대한 시체들을 모조리 먹어치우며, 그 시체에 알을 낳고 번식한다. "),
    actor_quote=("파리들이 다 죽으면 던전이 시체더미가 된다고는 하지만, 그 징그럽게 생긴 날개를 보고서도 놈을 죽이지 않을 놈이 몇이나 있을까? "),
    rarity=40,
    weight=0.07,
    spawnable=True,
    edible=edible.InsectEdible(nutrition=12, cook_bonus=2),
    ai_cls=BaseAI(
        alignment=(("hostile", ), (1, )),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("meat", "insect", "fruit", "vegetable", "food"),
    ),
    status=Status(
        hp=8,
        mp=0,
        strength=3,
        dexterity=8,
        agility=14,
        intelligence=3,
        constitution=8,
        charm=1,
        difficulty=2,
        base_melee=2,
        additional_melee=5,
        protection=5,
        hearing=6,
        eyesight=20,
        poison_resistance=0.2,
        cold_resistance=0.1,
        ),
    actor_state=ActorState(
        size=2,
        has_left_arm=False,
        has_right_arm=False,
        has_wing=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=False,
        can_fly=True,
        is_flying=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[fly.status.difficulty].append(fly)


### giant wasp
giant_wasp = Actor(
    char="i",
    fg=(250, 250, 0),
    name="거대 말벌",
    entity_id="giant_wasp",
    entity_desc=("성인 남성 손가락 만한 이들의 독침은, 독 없이 그 자체만으로도 치명상을 입히기 충분하다. "
        "거대 말벌들은 곡예에 가까운 비행 능력을 보여주며, 쏜살같은 속도로 목표물에게 날아들어 독침을 찔러넣는다. "
        "독침을 찔러 넣을 때는 눈, 생식기 등 급소를 노리는 것으로 알려져 있으며, 때문에 이들을 상대할 때는 갑옷을 입었다고 하더라도 큰 주의가 필요하다. "),
    actor_quote=("독이 묻은 단검을 떠올려 봐. 꽤 살벌하지? 그런데 그 단검이 날아다니면서 너를 쫓아와 네 고간을 찌른다고 생각해봐. 대체 이보다 끔찍한 게 어디 있겠어? "),
    rarity=35,
    weight=1.5,
    spawnable=True,
    edible=edible.GiantWaspEdible(nutrition=30),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        hostile_id=('fly',),
        attracted_eat_type=("insect",),
    ),
    status=Status(
        hp=45,
        mp=0,
        strength=11,
        dexterity=10,
        agility=17,
        intelligence=6,
        constitution=9,
        charm=6,
        difficulty=7,
        base_melee=6,
        additional_melee=7,
        protection=11,
        hearing=7,
        eyesight=20,
        poison_resistance=0.4,
        melee_effects_var=((1, 1, 0, 4),),
        melee_effects=(("poison_target", 0.8),),
        ),
    actor_state=ActorState(
        size=3,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_fly=True,
        is_flying=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[giant_wasp.status.difficulty].append(giant_wasp)


####################################################
############### j - jellies / slimes  ##############
####################################################

### black jelly
black_jelly = Actor(
    char="j",
    fg=(10, 20, 10),
    name="검정 덩어리",
    entity_id="black_jelly",
    entity_desc=("점액질로 이루어진 이 생명체들은 딱히 이렇다 할 외형적 특징을 가지고 있지 않아 \"덩어리\"라는 이름으로 불린다. "
                "이들 중 검정색을 띄고 있는 개체들은 독성 점액질로 이루어져 있는데, 이들은 신체 내에서 독성 가스를 압축한 뒤 터뜨려 자신의 점액질 일부를 적에게 발사하는 형식으로 적을 공격한다고 알려져 있다. "
                "독성 점액질은 본체에서 분리되고 얼마 지나지 않아 썩어 사라지며, 본체 또한 많은 부분이 절단되면 순식간에 썩어 사라지는 특징을 보인다. "),
    actor_quote=("이 놈들만큼 비료로 쓰기 좋은 게 또 없어. 당나귀 똥처럼 냄새도 안나지, 썩기는 또 순식간에 잘 썩지. 거기에 이놈들 살덩이는 잘라도 잘라도 계속 다시 자라나서 비료값 걱정도 할 필요 없다니깐? "),
    rarity=33,
    weight=187,
    spawnable=True,
    edible=edible.BlackJellyEdible(nutrition=50),
    ai_cls=ai_factories.Black_Jelly_Ai(),
    status=Status(
        hp=45,
        mp=0,
        strength=10,
        dexterity=11,
        agility=10,
        intelligence=4,
        constitution=18,
        charm=5,
        difficulty=6,
        base_melee=7,
        additional_melee=3,
        protection=10,
        eyesight=15,
        poison_resistance=1,
        psychic_resistance=1,
        sleep_resistance=1,
        melee_effects_var=((2, 1, 0, 3),),
        melee_effects=(("poison_target", 0.15),),
        ),
    actor_state=ActorState(
        size=3,
        sexuality="None",
        has_head=0,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=False,
        has_torso=False,
        has_blood=False,
        has_soul=False,
        can_breathe_underwater=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
    initial_items=None, # no longer has toxic goo.
    initial_drop_on_death=({"item":item_factories.toxic_goo, "chance":0.9, "count":(1,5), "BUC": {-1:0,0:1,1:0}, "upgrade":None},),
)
ActorDB.monster_difficulty[black_jelly.status.difficulty].append(black_jelly)



####################################################
################# l - Elves  #######################
####################################################

### Elf herbalist
elf_herbalist = Actor(
    char="l",
    fg=(255, 128, 247),
    name="엘프 약초술사",
    entity_id="elf_herbalist",
    actor_type_desc=("엘프들은 예로부터 자연과 동화되어 사는 삶을 중요시해왔다. "
        "이들은 자기애가 넘치며, 인간을 비롯한 다른 종족들을 하대하는 경향이 있다. "
        "엘프 사회 내에서는 종족간의 다양성을 지향하는 온건파와 다른 종족들을 멸시하고 공격하는 강경파가 대립하고 있다. "),
    entity_desc=("엘프 종족은 직업을 불문하고 약초술에 굉장히 능통한 모습을 보이는데, 개중에는 약초술만을 전문적으로 다루는 약초술사들도 존재한다. "
                 "이들은 허브와 다양한 식물들을 배합해 강력한 포션을 만들어내며, 이러한 포션들을 사용해 전투에도 종종 참여하곤 한다. "),
    actor_quote=("약초 따오는건 우리 마누라도 기가 막히게 잘하지. 얼굴도 좀 닮았으면 좋으련만."),
    rarity=35,
    weight=57,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=105),
    ai_cls=ai_factories.Elf_Herbalist_Ai(),
    status=Status(
        hp=65,
        mp=65,
        strength=13,
        dexterity=19,
        agility=16,
        intelligence=17,
        constitution=18,
        charm=22,
        difficulty=9,
        base_melee=6,
        additional_melee=14,
        protection=10,
        hearing=20,
        eyesight=20,
    ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
        regain_mana=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.potion_of_poison, "chance": 0.5, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.potion_of_acid, "chance": 0.5, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.potion_of_paralysis, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.fillapoty, "chance": 0.3, "count": (1, 2), "BUC": None, "upgrade": None},
        {"item": item_factories.kettoniss, "chance": 0.3, "count": (1, 2), "BUC": None, "upgrade": None},
        {"item": item_factories.lintol, "chance": 0.3, "count": (1, 2), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item": item_factories.elven_cloak, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_dagger, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
    ),
)
ActorDB.monster_difficulty[elf_herbalist.status.difficulty].append(elf_herbalist)


### Elf assasin
elf_assasin = Actor(
    char="l",
    fg=(161, 0, 0),
    name="엘프 암살자",
    entity_id="elf_assasin",
    actor_type_desc=("엘프들은 예로부터 자연과 동화되어 사는 삶을 중요시해왔다. "
                     "이들은 자기애가 넘치며, 인간을 비롯한 다른 종족들을 하대하는 경향이 있다. "
                     "엘프 사회 내에서는 종족간의 다양성을 지향하는 온건파와 다른 종족들을 멸시하고 공격하는 강경파가 대립하고 있다. "),
    entity_desc=("엘프 암살자들은 날렵한 모습을 보여주며, 근거리, 원거리 할 것 없이 지능적으로 적과 전투한다. "
                 "이들은 엘프제 무기를 주로 사용하며, 특히 엘프제 단검을 애용하는 것으로 알려져 있다. "
                 "이들은 어려서부터 단검 투척술을 배운다고 전해지며, 이들이 던지는 단검은 위협적이므로 많은 주의가 필요하다. "),
    rarity=35,
    weight=71,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=135),
    ai_cls=ai_factories.Elf_Fighter_Ai(),
    status=Status(
        hp=68,
        mp=40,
        strength=16,
        dexterity=18,
        agility=18,
        intelligence=16,
        constitution=14,
        charm=18,
        difficulty=11,
        base_melee=12,
        additional_melee=4,
        protection=13,
        hearing=15,
        eyesight=20,
    ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
        regain_mana=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.fillapoty, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.kettoniss, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.lintol, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_dagger, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_dagger, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_dagger, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_dagger, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_dagger, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item": item_factories.elven_cloak, "chance": 0.8, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.leather_boots, "chance": 0.3, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_sword, "chance": 1, "count": (1, 1), "BUC": None, "upgrade": None},
    ),
)
ActorDB.monster_difficulty[elf_assasin.status.difficulty].append(elf_assasin)


### Elf fighter
elf_fighter = Actor(
    char="l",
    fg=(255, 48, 48),
    name="엘프 전사",
    entity_id="elf_fighter",
    actor_type_desc=("엘프들은 예로부터 자연과 동화되어 사는 삶을 중요시해왔다. "
                     "이들은 자기애가 넘치며, 인간을 비롯한 다른 종족들을 하대하는 경향이 있다. "
                     "엘프 사회 내에서는 종족간의 다양성을 지향하는 온건파와 다른 종족들을 멸시하고 공격하는 강경파가 대립하고 있다. "),
    entity_desc=("엘프 전사들은 엘프 고유의 발달된 감각기관을 이용하여 적의 공격을 능숙하게 피하고 치명적인 일격을 가한다. "
                 "이들은 엘프제 무기를 주로 사용하며, 특히 엘프제 검과 나무 방패를 애용하는 것으로 알려져 있다. "),
    rarity=45,
    weight=71,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=135),
    ai_cls=BaseAI(
        alignment=(("hostile",), (5,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@', 'O', 'F', 'I'),
    ),
    status=Status(
        hp=70,
        mp=35,
        strength=16,
        dexterity=18,
        agility=17,
        intelligence=16,
        constitution=14,
        charm=18,
        difficulty=11,
        base_melee=7,
        additional_melee=10,
        protection=14,
        hearing=15,
        eyesight=20,
    ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
        regain_mana=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.fillapoty, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.kettoniss, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.lintol, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item": item_factories.elven_cloak, "chance": 1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.leather_boots, "chance": 0.5, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.leather_armor, "chance": 0.5, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.elven_sword, "chance": 1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.wooden_shield, "chance": 0.5, "count": (1, 1), "BUC": None, "upgrade": None},
    ),
)
ActorDB.monster_difficulty[elf_fighter.status.difficulty].append(elf_fighter)


####################################################
#################### n - nymphs  ###################
####################################################

### nymph
nymph = Actor(
    char="n",
    fg=(63, 245, 39),
    name="님프",
    entity_id="nymph",
    entity_desc=("아름다운 님프와 인간 남성이 사랑에 빠지는 일은 현실에서도 종종 일어나곤 한다. "
        "그러나 그 결말은 신화 속 이야기처럼 아름답지 않다. "
        "님프의 아름다움에 홀린 남성들은 가진 것을 모두 내어주고, 종국에는 파멸에 이른다. "
        "아름다운 외모에 속아 방심한다면 당신은 이들에게 목숨까지 내어주게 될 지도 모른다. "),
    actor_quote=("전 가끔 녀석들이 흉측했으면 좋았겠다는 생각을 합니다. 목을 벨 때 일말의 동정심도 들지 않게 말이죠. "),
    rarity=20, #20
    weight=53,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=200),
    ai_cls=ai_factories.Nymph_Ai(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=True,
        hostile_type=('@',),
        attracted_own_type=(InventoryOrder.GEM, InventoryOrder.CASH, InventoryOrder.AMULET, )
    ),
    status=Status(
        hp=68,
        mp=45,
        strength=12,
        dexterity=22,
        agility=19,
        intelligence=16,
        constitution=18,
        charm=27,
        difficulty=10,
        base_melee=8,
        additional_melee=10,
        protection=13,
        hearing=19,
        eyesight=26,
        ),
    actor_state=ActorState(
        size=4,
        sexuality="female",
        can_swim=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_talk=True,
    ),
    inventory=Inventory(capacity=3),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item":item_factories.scroll_of_teleportation, "chance":1, "count":(2,2), "BUC": None, "upgrade":None},
    ),
    initial_equipments=(
        {"item":item_factories.silk_dress, "chance":1, "count":(1,1), "BUC": None, "upgrade":None},
    ),
    initial_abilities=((ability_factories.steal, 1),)
)
ActorDB.monster_difficulty[nymph.status.difficulty].append(nymph)


####################################################
#################### o - spheres ###################
####################################################
sphere_of_acid = Actor(
    char="o",
    fg=(123, 255, 0),
    name="산성 구체",
    entity_id="sphere_of_acid",
    entity_desc=("산성 구체는 이름 그대로 산성을 띄는 가스들이 뭉친 구체이다. "
        "인간을 비롯한 일부 생명체에게만 반응하는 것을 보아 이들은 분명 인지 능력을 가지고는 있지만, "
        "특별한 생체 기관 없이 어떻게 주변을 인식하는지는 아직 밝혀지지 않았다. "
        "이들은 생명체 주변으로 다가가 자신을 폭발하는데, 당연하게도 스스로도 폭발로 인해 소멸한다. "
        "학자들 사이에선 스스로를 폭발시키는 이러한 행위가 공격이나 자기 보호의 수단이 아니라, 일종의 본능과도 같은 행위라는 의견이 지배적이다. "),
    actor_quote=("폭발의 열기로 머리카락이 타버렸어. 그래도 목숨은 건졌구나 싶었는데 눈, 코, 귀가 차례대로 녹아내리기 시작하더군. 걔는 자길 죽여달라고 애원했지. 내가 해줄 수 있는 거라고는... "),
    rarity=25,
    weight=0.8,
    spawnable=True,
    edible=None,
    ai_cls=ai_factories.Sphere_Of_Acid_Ai(),
    status=Status(
        hp=20,
        mp=0,
        strength=2,
        dexterity=1,
        agility=15,
        intelligence=3,
        constitution=2,
        charm=6,
        difficulty=7,
        base_melee=0,
        additional_melee=0,
        protection=1,
        eyesight=15,
        cold_resistance=0.6,
        poison_resistance=1,
        acid_resistance=1,
        psychic_resistance=1,
        sleep_resistance=1,
        ),
    actor_state=ActorState(
        size=3,
        has_head=0,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=False,
        has_torso=False,
        has_blood=False,
        has_soul=False,
        can_fly=True,
        is_flying=True,
        need_breathe=False,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[sphere_of_acid.status.difficulty].append(sphere_of_acid)


####################################################
############# s - spiders & scorpions  #############
####################################################

### jumping spider
jumping_spider = Actor(
    char="s",
    fg=(127, 235, 224),
    name="깡충거미",
    entity_id="jumping_spider",
    entity_desc=("손톱 정도 크기의 이 자그마한 거미들은 자신보다 덩치 큰 생명체들의 몸에 붙어 벼룩이나 빈대, 구더기 등을 잡아먹으며 살아간다. "
        "예로부터 몇몇 모험가들은 옷에 붙어있는 자그마한 벌레들을 잡기 위해 옷 속에 깡충거미를 집어넣기도 했다고 전해지며, "
        "그 중 일부는 이들을 물약 병 같은 곳에 담아 애지중지 기르기도 했다고 전해진다. "),
    actor_quote=("딜런이 죽던 날은 내 생애 최악의 날이었어. 그 날 무심코 자켓 위에 앉지만 않았어도... "),
    rarity=30,
    weight=0.01,
    spawnable=True,
    edible=edible.InsectEdible(nutrition=5),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_id=("maggot",),
        attracted_eat_type=("insect",),
    ),
    status=Status(
        hp=12,
        mp=0,
        strength=1,
        dexterity=3,
        agility=9,
        intelligence=1,
        constitution=1,
        charm=3,
        difficulty=1,
        base_melee=1,
        additional_melee=2,
        protection=4,
        hearing=3,
        eyesight=10,
        poison_resistance=0.1,
        ),
    actor_state=ActorState(
        size=1,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[jumping_spider.status.difficulty].append(jumping_spider)


### gaion
gaion = Actor(
    char="s",
    fg=(160, 77, 255),
    name="가이온",
    entity_id="gaion",
    entity_desc=("가이온은 상반신은 인간, 하반신은 전갈의 모습을 한 반인반수이다. 이들은 굉장히 호전적이고, 대체로 인간과 비슷한 수준의 지능을 가지고 있다고 알려져 있다. "
        "그러나 인간과 달리 대다수의 가이온들은 무리를 이루지 않고 홀로 살아가며, 갓 태어난 새끼들 조차 독립적으로 생활하는 모습을 보인다. "
        "이들이 위험한 던전 속에서 무리를 이루지 않아도 살아갈 수 있는 이유는 바로 이들의 강인한 신체능력 덕분인데, "
        "가이온의 하반신은 단단한 껍질로 둘러쌓여 있으며, 꼬리에 달린 독침에는 맞은 생명체를 마비시키는 강력한 신경독이 들어있다. "
        "많은 학자들은 가이온이 만약 인간처럼 사회를 이루는 생명체였다면 인류에게 지금 이상으로 큰 위협이 됐으리라고 추측한다."),
    actor_quote=("어디서 피 냄새가 나서 주변을 살펴보니 가이온 한 놈이 다른 가이온을 뜯어먹고 있더군. 젠장할, 잊고 싶어도 평생 잊지 못할거야."),
    rarity=33,
    weight=135.2,
    spawnable=True,
    edible=edible.InsectEdible(nutrition=180, cook_bonus=50),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','b','c','d','n','l','O'),
        attracted_eat_type=("insect","meat",),
    ),
    status=Status(
        hp=81,
        mp=50,
        strength=19,
        dexterity=24,
        agility=14,
        intelligence=15,
        constitution=16,
        charm=13,
        difficulty=12,
        base_melee=28,
        additional_melee=20,
        protection=25,
        hearing=15,
        eyesight=15,
        poison_resistance=0.3,
        sleep_resistance=0.3,
        melee_effects_var=((0,2),(3, 1, 0, 7),),
        melee_effects=(("paralyze_target", 0.1),("poison_target",0.2)),
        ),
    actor_state=ActorState(
        size=4,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        has_head=1,
        can_think=True,
        can_talk=True,
        can_move_on_surface=True,
        need_breathe=True,
    ),
    inventory=Inventory(capacity=4),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[gaion.status.difficulty].append(gaion)


####################################################
#####################  w - worms  ##################
####################################################

### earthworm
earthworm = Actor(
    char="w",
    fg=(171, 108, 56),
    name="지렁이",
    entity_id="earthworm",
    entity_desc=("던전 속 식물들이 태양빛 없이 자랄 수 있는 가장 큰 이유는 바로 지렁이들이 배출한 양분 덕분일 것이다. "
        "이들은 지상의 평범한 지렁이들의 수 십 배 이상으로 토지를 기름지게 만들며, 식물들이 햇빛 없이도 자랄 수 있게 해 주는 알 수 없는 성분을 배출한다. "
        "이 알 수 없는 성분은 던전에서 방출되는 \'던전의 기운\'과 연관이 있는 것으로 추정되며, 때문에 던전 속 지렁이들은 지상의 토양에서는 금새 말라 비틀어져 죽고 만다. "
        "이들을 지상에서 사육해 농사에 사용하려는 수많은 시도가 있었으나, 아직까지 성공한 사례는 없다. "
        "때문에 이들을 던전 밖에서 사육하는 법을 고안해낸다면 황제로부터 훈장을 수여받으리라는 말도 떠돌곤 한다. "),
    actor_quote=("내가 형씨였으면 모험이니 뭐니 할 거 없이 그 아래에서 농사나 지을 거야. 형씨도 지금보다 백 배는 많이 벌 수 있을텐데. "),
    rarity=30,
    weight=0.1,
    spawnable=True,
    edible=edible.InsectEdible(nutrition=10, cook_bonus=2),
    ai_cls=BaseAI(
        alignment=(("neutral",), (1, )),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        attracted_eat_type=("fruit", "vegetable",),
    ),
    status=Status(
        hp=8,
        mp=0,
        strength=1,
        dexterity=1,
        agility=3,
        intelligence=1,
        constitution=2,
        charm=1,
        difficulty=1,
        base_melee=0,
        additional_melee=2,
        protection=3,
        hearing=3,
        eyesight=3,
        ),
    actor_state=ActorState(
        size=1,
        has_head=1,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=False,
        has_torso=False,
        has_blood=True,
        has_soul=False,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[earthworm.status.difficulty].append(earthworm)

### maggot
maggot = Actor(
    char="w",
    fg=(222, 222, 222),
    name="구더기",
    entity_id="maggot",
    entity_desc=("모험가들이 가장 무서워하는 생물이 무엇일까? 악마? 드래곤? 답은 바로 구더기이다. "
        "구더기들은 앞에 놓인 것이 무엇이든 간에 쉬지 않고 먹어치우며, 모험가들의 비상식량도 예외는 아니다. "),
    actor_quote=("구더기가 가득한 고기가 싫다면 고기 대신 치즈를 들고 다니면 돼. 구더기가 파먹은 치즈는 나름대로 별미거든. "),
    rarity=0,
    weight=0.01,
    spawnable=False, # NOTE: does not spawn naturally.
    edible=edible.InsectEdible(nutrition=1, maggot_chance=0), # Cannot spawn maggots to prevent continuos spawning
    ai_cls=BaseAI(
        alignment=(("neutral",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
        attracted_eat_type=("fruit", "vegetable", "meat", "insect", "food",),
    ),
    status=Status(
        hp=4,
        mp=0,
        strength=1,
        dexterity=1,
        agility=1,
        intelligence=1,
        constitution=1,
        charm=1,
        difficulty=1,
        base_melee=0,
        additional_melee=1,
        protection=2,
        hearing=1,
        eyesight=3,
        ),
    actor_state=ActorState(
        size=1,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=False,
        has_torso=False,
        has_blood=False,
        has_soul=False,
        hunger=25,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[maggot.status.difficulty].append(maggot)


####################################################
##################### B - BEARS  ###################
####################################################

### Brown bear
brown_bear = Actor(
    char="B",
    fg=(222, 208, 169),
    name="불곰",
    entity_id="brown_bear",
    entity_desc=("던전 속의 불곰들은 지상의 불곰은 애교로 보이게 할 정도로 거대하고 흉폭하다. "
                 "이들은 앞발을 살짝 휘두르는 것 만으로 나무를 베어 넘길 수 있을 정도로 강한 힘을 가졌으며 "
                 "인간을 먹잇감으로 생각하기 때문에 이들을 마주친다면 전력으로 도망치는 것이 권장된다. "),
    actor_quote=("불곰을 마주쳤을 땐 그냥 그 자리에 드러눕는게 최고야. 어차피 붙잡혀 갈갈히 찢겨나갈텐데 굳이 힘쓸 필요 없잖아?"),
    rarity=30,
    weight=1160,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=400, cook_bonus=150),
    ai_cls=BaseAI(
        alignment=(("hostile",),(1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','l'),
        attracted_eat_type=("insect","meat"),
    ),
    status=Status(
        hp=108,
        mp=10,
        strength=23,
        dexterity=16,
        agility=15,
        intelligence=6,
        constitution=20,
        charm=18,
        difficulty=14,
        base_melee=25,
        additional_melee=12,
        protection=18,
        hearing=15,
        eyesight=15,
        ),
    actor_state=ActorState(
        size=5,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
    ),
    inventory=Inventory(capacity=30),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[brown_bear.status.difficulty].append(brown_bear)


####################################################
#################### D - DRAGONS  ##################
####################################################


### Baby Spearhorn Dragon
baby_spearhorn_dragon = Actor(
    char="D",
    fg=(122, 105, 255),
    name="새끼 스피어혼 드래곤",
    entity_id="baby_spearhorn_dragon",
    entity_desc=(""),
    actor_quote=(""),
    rarity=4,
    weight=2123,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=323, cook_bonus=50),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','O','l','T','F'),
    ),
    status=Status(
        hp=83,
        mp=88,
        strength=23,
        dexterity=20,
        agility=18,
        intelligence=13,
        constitution=15,
        charm=20,
        difficulty=15,
        base_melee=25,
        additional_melee=20,
        protection=25,
        hearing=15,
        eyesight=15,
        fire_resistance=0.2,
        ),
    actor_state=ActorState(
        size=4,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        has_head=1,
        can_think=True,
        can_talk=True,
        can_move_on_surface=True,
        can_swim=True,
        can_fly=True,
        is_flying=False, # Can fly
        need_breathe=True,
    ),
    inventory=Inventory(capacity=4),
    ability_inventory=AbilityInventory(capacity=20),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[baby_spearhorn_dragon.status.difficulty].append(baby_spearhorn_dragon)


### Baby Armored Dragon
baby_armored_dragon = Actor(
    char="D",
    fg=(50, 168, 68),
    name="새끼 아머 드래곤",
    entity_id="baby_armored_dragon",
    entity_desc=(""),
    actor_quote=(""),
    rarity=4,
    weight=2310,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=350, cook_bonus=52),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','O','l','T','F'),
    ),
    status=Status(
        hp=85,
        mp=88,
        strength=25,
        dexterity=18,
        agility=17,
        intelligence=13,
        constitution=14,
        charm=20,
        difficulty=15,
        base_melee=20,
        additional_melee=30,
        protection=29,
        hearing=15,
        eyesight=15,
        fire_resistance=0.2,
        ),
    actor_state=ActorState(
        size=4,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        has_head=1,
        can_think=True,
        can_talk=True,
        can_move_on_surface=True,
        can_swim=True,
        can_fly=True,
        is_flying=False, # Can fly
        need_breathe=True,
    ),
    inventory=Inventory(capacity=4),
    ability_inventory=AbilityInventory(capacity=20),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[baby_armored_dragon.status.difficulty].append(baby_armored_dragon)


####################################################
################## E - ELEMENTALS  #################
####################################################

### Fire Elemental
fire_elemental = Actor(
    char="E",
    fg=(255, 0, 0),
    name="불의 정령",
    entity_id="fire_elemental",
    actor_type_desc=("정령들의 존재는 익히 알려져 있지만, 그들의 기원을 두고는 무수한 추측만이 오갈 뿐이다. "
        "이들이 자연의 산물이라고 주장하는 자들이 있는가 하면, 고대의 마법사들의 창조물이라고 주장하는 자들도 있다. "
        "정령은 수 천년 이상 인간과 오랜 시간 공존해 왔고, 아주 드문 경우 이들은 자신들이 존경하는 인간을 위해 자신의 힘을 내어주기까지 했다. "
        "그러나 근 몇 백 년간 인류가 급격하게 자연을 파괴하기 시작하자 이들은 인간에게도 적대감을 드러내기 시작했고, 지금은 던전 속에서 위협적인 존재로 군림하고 있다. "),
    entity_desc=("불의 정령은 신체의 대부분이 강렬한 화염으로 이루어져 있다. "
        "그러나 이들의 골격만큼은 불꽃이 아닌 알 수 없는 금속으로 이루어져 있으며, 이 금속은 정령이 소멸할 때 함께 기화되어 사라진다. "),
    actor_quote=("난 이거 하나만큼은 자신있게 말할 수 있었지. '불은 끄려면 물을 뿌려라'라고. 녀석을 만나기 전까지는 말이야. "),
    rarity=15,
    weight=203,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile","neutral"), (1,1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=95,
        mp=205,
        strength=23,
        dexterity=20,
        agility=16,
        intelligence=21,
        constitution=19,
        charm=20,
        difficulty=17,
        base_melee=25,
        additional_melee=10,
        protection=21,
        hearing=20,
        eyesight=20,
        fire_resistance=1,
        sleep_resistance=1,
        psychic_resistance=1,
        magic_resistance=0.2,
        melee_effects_var=((5, 5, 0, 6),),
        melee_effects=(("burn_target", 0.5),),
        ),
    actor_state=ActorState(
        size=4,
        sexuality="None",
        can_breathe_underwater=True,
        can_fly=True,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=False,
        has_eye=True,
        has_torso=True,
        has_blood=False,
        has_soul=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=10),
    equipments=Equipments(),
    tile_effect_on_path="burn",
)
ActorDB.monster_difficulty[fire_elemental.status.difficulty].append(fire_elemental)


### Ice Elemental
ice_elemental = Actor(
    char="E",
    fg=(207, 247, 255),
    name="얼음 정령",
    entity_id="ice_elemental",
    actor_type_desc=("정령들의 존재는 익히 알려져 있지만, 그들의 기원을 두고는 무수한 추측만이 오갈 뿐이다. "
                     "이들이 자연의 산물이라고 주장하는 자들이 있는가 하면, 고대의 마법사들의 창조물이라고 주장하는 자들도 있다. "
                     "정령은 수 천년 이상 인간과 오랜 시간 공존해 왔고, 아주 드문 경우 이들은 자신들이 존경하는 인간을 위해 자신의 힘을 내어주기까지 했다. "
                     "그러나 근 몇 백 년간 인류가 급격하게 자연을 파괴하기 시작하자 이들은 인간에게도 적대감을 드러내기 시작했고, 지금은 던전 속에서 위협적인 존재로 군림하고 있다. "),
    entity_desc=("얼음 정령은 푸른 얼음으로 이루어진 전신에서 생명체의 뼛 속까지 얼어붙일 수 있는 냉기를 내뿜는다. "
            "지금까지 이 얼음을 녹이려는 시도는 전부 실패했지만, 정령이 소멸할 때 얼음도 함꼐 기화되어 사라진다. "),
    actor_quote=("두꺼운 옷으로 꽁꽁 싸맨다고? 그런 건 자네의 얼어붙은 시체를 땅에 묻기 어렵게 만들 뿐이라네. "),
    rarity=15,
    weight=461,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=95,
        mp=205,
        strength=23,
        dexterity=20,
        agility=15,
        intelligence=22,
        constitution=16,
        charm=20,
        difficulty=17,
        base_melee=25,
        additional_melee=12,
        protection=22,
        hearing=20,
        eyesight=20,
        cold_resistance=1,
        sleep_resistance=1,
        psychic_resistance=1,
        magic_resistance=0.2,
        melee_effects_var=((2, 1, 0.2, 0, 3),),
        melee_effects=(("freeze_target", 0.5),),
        ),
    actor_state=ActorState(
        size=4,
        sexuality="None",
        can_breathe_underwater=True,
        can_fly=True,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=False,
        has_eye=True,
        has_torso=True,
        has_blood=False,
        has_soul=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=5),
    equipments=Equipments(),
    tile_effect_on_path="freeze",
)
ActorDB.monster_difficulty[ice_elemental.status.difficulty].append(ice_elemental)


### Earth Elemental
earth_elemental = Actor(
    char="E",
    fg=(117, 52, 0),
    name="땅의 정령",
    entity_id="earth_elemental",
    actor_type_desc=("정령들의 존재는 익히 알려져 있지만, 그들의 기원을 두고는 무수한 추측만이 오갈 뿐이다. "
                     "이들이 자연의 산물이라고 주장하는 자들이 있는가 하면, 고대의 마법사들의 창조물이라고 주장하는 자들도 있다. "
                     "정령은 수 천년 이상 인간과 오랜 시간 공존해 왔고, 아주 드문 경우 이들은 자신들이 존경하는 인간을 위해 자신의 힘을 내어주기까지 했다. "
                     "그러나 근 몇 백 년간 인류가 급격하게 자연을 파괴하기 시작하자 이들은 인간에게도 적대감을 드러내기 시작했고, 지금은 던전 속에서 위협적인 존재로 군림하고 있다. "),
    entity_desc=("땅의 정령의 신체는 아직까지 밝혀지지 않은 종류의 암석으로 구성되어 있으며, 이 암석들은 보이지 않는 힘에 의해 서로 떨어지지 않고 하나의 형태를 유지하고 있다. "
                "이 암석은 열, 부식 등에 대해 놀라우리만큼 강한 저항성을 지니고 있으나, 정령이 소멸할 때 암석도 함꼐 기화되어 사라진다. "),
    actor_quote=("혹시나 해서 말하는데, 바위 골렘 같은 조잡한 돌덩어리라고 생각했다가는 넌 눈 깜빡할 사이에 곤죽이 될 거야. "),
    rarity=15,
    weight=550,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=95,
        mp=205,
        strength=24,
        dexterity=20,
        agility=13,
        intelligence=22,
        constitution=17,
        charm=20,
        difficulty=17,
        base_melee=25,
        additional_melee=20,
        protection=24,
        hearing=20,
        eyesight=20,
        fire_resistance=1,
        cold_resistance=1,
        poison_resistance=1,
        acid_resistance=1,
        shock_resistance=1,
        sleep_resistance=1,
        psychic_resistance=1,
        magic_resistance=0.2,
        ),
    actor_state=ActorState(
        size=4,
        sexuality="None",
        can_breathe_underwater=True,
        can_fly=True,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=False,
        has_eye=True,
        has_torso=True,
        has_blood=False,
        has_soul=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=5),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[earth_elemental.status.difficulty].append(earth_elemental)


### Acid Elemental
acid_elemental = Actor(
    char="E",
    fg=(155, 179, 0),
    name="융해의 정령",
    entity_id="acid_elemental_ai",
    actor_type_desc=("정령들의 존재는 익히 알려져 있지만, 그들의 기원을 두고는 무수한 추측만이 오갈 뿐이다. "
        "이들이 자연의 산물이라고 주장하는 자들이 있는가 하면, 고대의 마법사들의 창조물이라고 주장하는 자들도 있다. "
        "정령은 수 천년 이상 인간과 오랜 시간 공존해 왔고, 아주 드문 경우 이들은 자신들이 존경하는 인간을 위해 자신의 힘을 내어주기까지 했다. "
        "그러나 근 몇 백 년간 인류가 급격하게 자연을 파괴하기 시작하자 이들은 인간에게도 적대감을 드러내기 시작했고, 지금은 던전 속에서 위협적인 존재로 군림하고 있다. "),
    entity_desc=("융해의 정령의 신체는 알 수 없는 생명체의 뼈로 이루어져 있으며, 그 중 머리 부분은 인간의 두개골과 유사한 형상을 하고 있다. "
                "이들의 신체 전체는 점액성을 띄는 강산성 물질로 덮어져 있으며, 이 강산성 점액질은 현재까지 알려진 거의 대부분의 유기물을 녹일 수 있는 것으로 알려져 있다. "),
    actor_quote=("놈과 싸운 어떤 한 기사의 이야기를 들은 적이 있어. 갑옷의 구멍 사이로 붉은 살덩이들이 흘려 내렸다더군. "),
    rarity=15,
    weight=430,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=95,
        mp=205,
        strength=22,
        dexterity=20,
        agility=15,
        intelligence=20,
        constitution=19,
        charm=20,
        difficulty=17,
        base_melee=25,
        additional_melee=12,
        protection=20,
        hearing=20,
        eyesight=20,
        acid_resistance=1,
        sleep_resistance=1,
        psychic_resistance=1,
        magic_resistance=0.2,
        melee_effects_var=((9, 1, 0, 6),),
        melee_effects=(("melt_target", 0.5),),
        ),
    actor_state=ActorState(
        size=4,
        sexuality="None",
        can_breathe_underwater=True,
        can_fly=True,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=False,
        has_eye=True,
        has_torso=True,
        has_blood=False,
        has_soul=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=5),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[acid_elemental.status.difficulty].append(acid_elemental)


### Poison Elemental
poison_elemental = Actor(
    char="E",
    fg=(101, 0, 179),
    name="맹독의 정령",
    entity_id="poison_elemental",
    actor_type_desc=("정령들의 존재는 익히 알려져 있지만, 그들의 기원을 두고는 무수한 추측만이 오갈 뿐이다. "
                     "이들이 자연의 산물이라고 주장하는 자들이 있는가 하면, 고대의 마법사들의 창조물이라고 주장하는 자들도 있다. "
                     "정령은 수 천년 이상 인간과 오랜 시간 공존해 왔고, 아주 드문 경우 이들은 자신들이 존경하는 인간을 위해 자신의 힘을 내어주기까지 했다. "
                     "그러나 근 몇 백 년간 인류가 급격하게 자연을 파괴하기 시작하자 이들은 인간에게도 적대감을 드러내기 시작했고, 지금은 던전 속에서 위협적인 존재로 군림하고 있다. "),
    entity_desc=("맹독의 정령은 마치 거대한 독사와도 같은 형상을 하고 있다. "
                "이들의 신체는 치명적인 독성을 띄는 보랏빛 액체로 이루어져 있으며, 이 액체와 단순히 접촉하는 것만으로도 심각한 피해를 줄 수 있다고 알려져 있다. "),
    actor_quote=("맹독의 정령을 찾는 건 어렵지 않아. 던전 속에 널부러진 시체들을 쭉 따라가다 보면 만날 수 있을 거야. "),
    rarity=15,
    weight=417,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=95,
        mp=205,
        strength=22,
        dexterity=20,
        agility=15,
        intelligence=21,
        constitution=20,
        charm=20,
        difficulty=17,
        base_melee=25,
        additional_melee=15,
        protection=20,
        hearing=20,
        eyesight=20,
        poison_resistance=1,
        sleep_resistance=1,
        psychic_resistance=1,
        magic_resistance=0.2,
        melee_effects_var=((4, 2, 0, 10),),
        melee_effects=(("poison_target", 0.2),),
        ),
    actor_state=ActorState(
        size=4,
        sexuality="None",
        can_breathe_underwater=True,
        can_fly=True,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=False,
        has_eye=True,
        has_torso=True,
        has_blood=False,
        has_soul=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=5),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[poison_elemental.status.difficulty].append(poison_elemental)


### Lightning Elemental
lightning_elemental = Actor(
    char="E",
    fg=(0, 255, 251),
    name="번개 정령",
    entity_id="lightning_elemental",
    actor_type_desc=("정령들의 존재는 익히 알려져 있지만, 그들의 기원을 두고는 무수한 추측만이 오갈 뿐이다. "
                     "이들이 자연의 산물이라고 주장하는 자들이 있는가 하면, 고대의 마법사들의 창조물이라고 주장하는 자들도 있다. "
                     "정령은 수 천년 이상 인간과 오랜 시간 공존해 왔고, 아주 드문 경우 이들은 자신들이 존경하는 인간을 위해 자신의 힘을 내어주기까지 했다. "
                     "그러나 근 몇 백 년간 인류가 급격하게 자연을 파괴하기 시작하자 이들은 인간에게도 적대감을 드러내기 시작했고, 지금은 던전 속에서 위협적인 존재로 군림하고 있다. "),
    entity_desc=("번개의 정령의 신체는 먹구름과 같이 보이는 알 수 없는 검은 기체로 이루어져 있으며, 전신에서 번개와도 같은 푸른 색 스파크를 내뿜는다. "
                "그러나 이들의 골격만큼은 기체가 아닌 알 수 없는 금속으로 이루어져 있으며, 이 금속은 정령이 소멸할 때 함께 기화되어 사라진다. "),
    actor_quote=("세상에 전기가 덜 흐르는 물질은 있어도, 전기가 흐르지 않는 물질은 없다는 거 알아? "),
    rarity=15,
    weight=153,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=95,
        mp=205,
        strength=23,
        dexterity=21,
        agility=20,
        intelligence=22,
        constitution=18,
        charm=20,
        difficulty=17,
        base_melee=25,
        additional_melee=10,
        protection=21,
        hearing=20,
        eyesight=20,
        shock_resistance=1,
        sleep_resistance=1,
        psychic_resistance=1,
        magic_resistance=0.2,
        melee_effects_var=((8, 0.7),),
        melee_effects=(("electrocute_target", 1),),
        ),
    actor_state=ActorState(
        size=4,
        sexuality="None",
        can_breathe_underwater=True,
        can_fly=True,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=False,
        has_eye=True,
        has_torso=True,
        has_blood=False,
        has_soul=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=5),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[lightning_elemental.status.difficulty].append(lightning_elemental)


####################################################
################ F - Fiends  #######################
####################################################

red_prophet = Actor(
    char="F",
    fg=(122, 8, 0),
    name="붉은 선지자",
    entity_id="red_prophet",
    actor_type_desc=("통상 '악마'라고 불리우는 이 저주받은 존재들은 생명 그 자체를 혐오하는 사악한 존재들이다. "
                     "이들은 굉장히 위험하기 때문에 발견하는 즉시 도망치거나 전투 준비를 갖춰야 한다."),
    entity_desc=("붉은 선지자라는 이름의 이 악마는 인간과 유사한 외형을 하고 있으나, 눈, 코, 귀가 없고, 비정상적으로 많은 치아를 가지고 있다. "
                 "이들의 피부는 진한 붉은 색을 띄며, 마치 양서류의 살가죽과 유사한 매끄러운 표면을 하고 있다. "
                 "선지자라는 이름에 걸맞게 이들의 가장 큰 목표는 자신들, 혹은 악마라는 종족 자체의 사상을 다른 생명체들에게 전도하는 것인데, "
                 "그 방식은 항상 전도 대상을 살해하는 것으로 이어진다. 이들은 다른 생명체들의 목숨을 끊어놓는 것만이 자신들의 사상을 전파할 수 있는 유일한 방법이라고 생각하며, "
                 "이러한 행위에 저항하더라도 크게 개의치 않고 생명체들을 살해한다. "
                 "다행히 붉은 선지자들은 고위 악마들에 비하면 비교적 덜 위협적이지만, 그렇다고 해도 이들은 여전히 극단적으로 적대적인 존재이기에 많은 주의가 필요하다."),
    rarity=35,
    weight=92.2,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("allied",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        allied_type=('F',),
    ),
    status=Status(
        hp=90,
        mp=103,
        strength=20,
        dexterity=20,
        agility=20,
        intelligence=28,
        constitution=20,
        charm=30,
        difficulty=14,
        base_melee=18,
        additional_melee=25,
        protection=15,
        hearing=20,
        eyesight=25,
        psychic_resistance=1,
        sleep_resistance=1,
        melee_effects_var=((3, 0, 3),),
        melee_effects=(("bleed_target", 0.2),),
        ),
    actor_state=ActorState(
        size=4,
        regain_mana=True,
        has_left_arm=True,
        has_right_arm=True,
        has_wing=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=False,
        can_talk=True,
        has_head=1,
        sexuality="None",
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=7),
    initial_items=(
        {"item":item_factories.satanic_bible, "chance":0.2, "count":(1, 1), "BUC": None, "upgrade":None},
    ),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[red_prophet.status.difficulty].append(red_prophet)


####################################################
################### H - HORSES #####################
####################################################

unicorn = Actor(
    char="H",
    fg=(255, 255, 255),
    name="유니콘",
    entity_id="unicorn",
    entity_desc=("유니콘은 하얀색 말과 유사한 외형을 하고 있으며, 머리에 달린 기다란 뿔과 등에 달린 한 쌍의 날개가 이들을 말들과 구분할 수 있게 해준다. "
            "던전 속에는 인간에게 적대적인 유니콘들과 그렇지 않은 유니콘들이 모두 존재하며, 때문에 유니콘을 마주한다면 설사 적대적이지 않아 보이더라도 극심한 주의를 가하는 게 권장된다."
            "유니콘들은 뿔에서 광선을 발사해 적을 공격하기 때문에 적대적인 유니콘을 마주친다면 엄폐물을 활용해 전투하는 것이 권장된다."),
    actor_quote=("그 미친 말대가리들은 보이는 대로 잡아 죽여야 돼. 뭐? 평화의 상징? 그 자식이 뿔로 네 뱃가죽을 헤집어놓으면 그런 소리 못할 걸?"),
    rarity=10,
    weight=980.5,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=330, cook_bonus=100),
    ai_cls=BaseAI(
        alignment=(("neutral","hostile"), (1,1)), # FIXME: neutral only when human is female
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=True,
        hostile_type=('@','F','C',),
        attracted_own_type=(InventoryOrder.GEM,),
    ),
    status=Status(
        hp=90,
        mp=120,
        strength=21,
        dexterity=13,
        agility=20,
        intelligence=17,
        constitution=19,
        charm=25,
        difficulty=13,
        base_melee=10,
        additional_melee=20,
        protection=24,
        hearing=15,
        eyesight=20,
        fire_resistance=0.1,
        acid_resistance=0.1,
        poison_resistance=0.1,
        psychic_resistance=0.1,
        shock_resistance=0.1,
        magic_resistance=0.2,
        ),
    actor_state=ActorState(
        size=4,
        regain_mana=True,
        has_left_arm=False,
        has_right_arm=False,
        has_wing=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_fly=True,
        is_flying=False, # but can fly
        can_talk=False,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=7),
    initial_items=(
        {"item":item_factories.worthless_piece_of_white_glass, "chance":0.01, "count":(1, 1), "BUC":None, "upgrade":None},
        {"item": item_factories.worthless_piece_of_blue_glass, "chance": 0.01, "count": (1, 1), "BUC": None,"upgrade": None},
        {"item": item_factories.worthless_piece_of_green_glass, "chance": 0.01, "count": (1, 1), "BUC": None,"upgrade": None},
        {"item": item_factories.worthless_piece_of_red_glass, "chance": 0.01, "count": (1, 1), "BUC": None,"upgrade": None},
        {"item": item_factories.diamond, "chance": 0.005, "count": (1, 1), "BUC": None,"upgrade": None},
        {"item": item_factories.ruby, "chance": 0.005, "count": (1, 1), "BUC": None,"upgrade": None},
        {"item": item_factories.sapphire, "chance": 0.005, "count": (1, 1), "BUC": None,"upgrade": None},
        {"item": item_factories.emerald, "chance": 0.005, "count": (1, 1), "BUC": None,"upgrade": None},
    ),
    initial_drop_on_death=None, #TODO add unicorn horn
    # (
    #     {"item":item_factories.shine, "chance":1, "count":(2000,3500), "BUC":None, "upgrade":None},
    # ),
    equipments=Equipments(),
    initial_abilities=((ability_factories.spectral_beam, 1),)
)
ActorDB.monster_difficulty[unicorn.status.difficulty].append(unicorn)


####################################################
################### I - IMPOSTERS  #################
####################################################

### Chatterbox
chatterbox = Actor(
    char="I",
    fg=(255, 230, 230),
    name="수다쟁이 괴물",
    entity_id="chatterbox",
    entity_desc=("던전에서 누군가 당신을 부르는 소리가 들린다면 뒤를 돌아보기보다는 검을 뽑아드는 편이 더 현명한 선택일지도 모른다. "
        "'수다쟁이'라는 이름으로 불리는 이 생명체는, 극단적으로 팔다리가 긴 여성 인간과 유사한 형태를 하고 있다. "
        "시각 기관의 부재에도 불구하고, 이들의 긴 팔과 날카로운 손톱은 가까운 거리의 인간을 갈기갈기 찢어 놓기에 충분하다. "
        "이들은 털이 없는 창백한 피부를 가졌으며, 머리에는 눈,코,귀 대신 '입'이 수 십여개 달려 있는 것이 특징이다. "
        "이들은 '입'을 통해 인간이나 다른 생명체들의 소리를 흉내내어 먹잇감을 유인하며, 성별, 인종, 나이에 관계없이 나양한 인간의 목소리를 내는 것으로 알려졌다. "
        "다만 이들이 자신들이 내뱉는 말들의 뜻을 이해하고 있는 것인지는 밝혀지지 않았다. "),
    actor_quote=("부탁이야... 말리지 말아줘... 이렇게 해서라도 죽어버린 그녀의 목소리를 듣고 싶어... "),
    rarity=27,
    weight=81,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=280),
    ai_cls=ai_factories.Chatterbox_Ai(),
    status=Status(
        hp=73,
        mp=13,
        strength=19,
        dexterity=18,
        agility=15,
        intelligence=13,
        constitution=19,
        charm=12,
        difficulty=7,
        base_melee=5,
        additional_melee=15,
        protection=16,
        hearing=40,
        eyesight=2,
        melee_effects_var=((4, 0, 6),),
        melee_effects=(("bleed_target", 0.3),),
        ),
    actor_state=ActorState(
        size=4,
        sexuality="None",
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[chatterbox.status.difficulty].append(chatterbox)


####################################################
#################### K - Kraken  ###################
####################################################

### Kraken
kraken = Actor(
    char="K",
    fg=(255, 51, 0),
    name="크라켄",
    entity_id="kraken",
    entity_desc=("크라켄은 거대한 문어와 유사한 외형을 하고 있으며, 수 십개가 넘는 거대한 촉수들에서 적을 휘감아 공격해온다. "
                 "크라켄의 촉수에 달린 빨판에서는 생명체를 마비시키는 신경독 성분이 포함된 점액이 분비되며, 이 점액질 성분은 마비 포션의 원료로써 사용되기도 한다. "
                 "크라켄은 개체별로 조금씩 차이가 있으나 대체적으로 돛단배 하나 정도의 압도적인 크기를 자랑하며, "
                 "이러한 거대한 크기 때문에 수중에 사는 생명체들 중에서 크라켄에게 위협이 될 만한 생명체는 거의 존재하지 않는다. "),
    rarity=5,
    weight=2150,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=1200, cook_bonus=150),
    ai_cls=BaseAI(
        alignment=(("hostile", ), (1, )),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','O','l'),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=420,
        mp=0,
        strength=32,
        dexterity=28,
        agility=7,
        intelligence=8,
        constitution=12,
        charm=10,
        difficulty=22,
        base_melee=35,
        additional_melee=60,
        protection=48,
        hearing=3,
        eyesight=8,
        melee_effects_var=((0,5),),
        melee_effects=(("paralyze_target", 0.1),),
        ),
    actor_state=ActorState(
        size=6,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        can_talk=False,
        can_move_on_surface=True,
        can_breathe_air=True,
        can_breathe_underwater=True,
        live_underwater=True,
    ),
    inventory=Inventory(capacity=40),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[kraken.status.difficulty].append(kraken)



####################################################
################ M - Mythical Beasts  ##############
####################################################

### Baby Phoenix
baby_phoenix = Actor(
    char="M",
    fg=(255, 115, 0),
    name="새끼 불사조",
    entity_id="baby_phoenix",
    actor_type_desc=("불사조는 인류보다도 오랜 세월을 이 땅에서 살아온 환상의 존재들이며, 마치 거대한 독수리와 공작새를 합친 듯한 외형을 하고 있다. "
            "이들은 살과 근육이 아닌, 붉은 화염을 연상케 하는 무언가로 구성되어 있으며, 이 '화염'이 무엇인지에 대한 의견은 학자들마다 분분하다. "
            "학자들 사이에서 가장 지지받는 이론은 바로 이 '화염'이 마력 에너지의 일종이며, "
            "불사조는 사실 우리들과 같은 유기적인 생명체가 아니라 막대한 양의 마력 에너지가 자아를 갖게 되면서 생겨난 존재라는 이론이다. "),
    rarity=3,
    weight=10.3,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 50,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','F','C',),
    ),
    status=Status(
        hp=75,
        mp=320,
        strength=19,
        dexterity=16,
        agility=18,
        intelligence=16,
        constitution=40,
        charm=19,
        difficulty=10,
        base_melee=10,
        additional_melee=15,
        protection=15,
        hearing=15,
        eyesight=17,
        fire_resistance=0.5,
        acid_resistance=0.5,
        poison_resistance=0.5,
        psychic_resistance=0.5,
        sleep_resistance=0.5,
        shock_resistance=0.5,
        magic_resistance=0.2,
        melee_effects_var=((7, 2, 0, 4),),
        melee_effects=(("burn_target", 0.3),),
        ),
    actor_state=ActorState(
        size=4,
        heal_wounds=True,
        regain_mana=True,
        sexuality="None",
        has_left_arm=False,
        has_right_arm=False,
        has_wing=True,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=False,
        has_soul=True,
        can_fly=True,
        is_flying=True,
        can_talk=False,
        can_revive_self=True,
        revive_as=None, #TODO
    ),
    inventory=Inventory(capacity=8),
    ability_inventory=AbilityInventory(capacity=7),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[baby_phoenix.status.difficulty].append(baby_phoenix)


### Phoenix
phoenix = Actor(
    char="M",
    fg=(255, 8, 0),
    name="불사조",
    entity_id="phoenix",
    actor_type_desc=("불사조는 인류보다도 오랜 세월을 이 땅에서 살아온 환상의 존재들이며, 마치 거대한 독수리와 공작새를 합친 듯한 외형을 하고 있다. "
            "이들은 살과 근육이 아닌, 붉은 화염을 연상케 하는 무언가로 구성되어 있으며, 이 '화염'이 무엇인지에 대한 의견은 학자들마다 분분하다. "
            "학자들 사이에서 가장 지지받는 이론은 바로 이 '화염'이 마력 에너지의 일종이며, "
            "불사조는 사실 우리들과 같은 유기적인 생명체가 아니라 막대한 양의 마력 에너지가 자아를 갖게 되면서 생겨난 존재라는 이론이다. "),
    rarity=4,
    weight=157,
    spawnable=True,
    edible=None,
    ai_cls=BaseAI(
        alignment=(("hostile", "neutral"), (1, 50,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','F','C',),
    ),
    status=Status(
        hp=120,
        mp=632,
        strength=22,
        dexterity=20,
        agility=18,
        intelligence=18,
        constitution=40,
        charm=23,
        difficulty=19,
        base_melee=20,
        additional_melee=20,
        protection=20,
        hearing=15,
        eyesight=22,
        fire_resistance=1,
        acid_resistance=1,
        poison_resistance=1,
        psychic_resistance=1,
        sleep_resistance=1,
        shock_resistance=1,
        magic_resistance=0.2,
        melee_effects_var=((10, 5, 0, 6),),
        melee_effects=(("burn_target", 0.5),),
        ),
    actor_state=ActorState(
        size=5,
        heal_wounds=True,
        regain_mana=True,
        sexuality="None",
        has_left_arm=False,
        has_right_arm=False,
        has_wing=True,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=False,
        has_soul=True,
        can_fly=True,
        is_flying=True,
        can_talk=False,
        can_revive_self=True,
        revive_as=None,  # TODO
    ),
    inventory=Inventory(capacity=10),
    ability_inventory=AbilityInventory(capacity=10),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[phoenix.status.difficulty].append(phoenix)


####################################################
###################### O - Orcs ####################
####################################################

### Orc patrol
orc_patrol = Actor(
    char="O",
    fg=(135, 184, 0),
    name="오크 정찰병",
    entity_id="orc_patrol",
    actor_type_desc=("인간과 가장 오랫동안 대립해온 종족인 오크는 힘과 명예를 중시하는 문화를 가지고 있다. "
                     "오크 사회에서 위계 질서는 절대적이며, 오크들간의 서열은 오직 힘으로 결정된다. "
                     "대중에게 오크는 흔히 무식하고 힘만 센 종족으로 알려져 있는데, 이는 사실이 아니다. "
                     "오크 종족은 기술, 마법 분야에서도 많은 성과를 이뤄냈으며, 일부 분야에서는 인간 사회의 수준을 웃돌기도 한다. "
                     ),
    entity_desc=("오크 정찰병은 전사들에 비해서는 비교적 가벼운 무장을 하고 있으며, 던전의 보다 더 얕은 층에서도 마주칠 수 있다. "),
    rarity=46,
    weight=118,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=403),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','l', 'F', 'I'),
    ),
    status=Status(
        hp=65,
        mp=15,
        strength=17,
        dexterity=14,
        agility=15,
        intelligence=13,
        constitution=14,
        charm=14,
        difficulty=9,
        base_melee=10,
        additional_melee=8,
        protection=15,
        hearing=15,
        eyesight=15,
        ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.potion_of_monster_detection, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.shine, "chance": 0.3, "count": (10, 80), "BUC": None, "upgrade": None},
        {"item": item_factories.scroll_of_magic_mapping, "chance": 0.05, "count": (1, 1), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item":item_factories.iron_dagger, "chance":1, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.leather_armor, "chance":0.3, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.leather_boots, "chance":0.3, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
    ),
)
ActorDB.monster_difficulty[orc_patrol.status.difficulty].append(orc_patrol)


### Orc warrior
orc_warrior = Actor(
    char="O",
    fg=(0, 181, 15),
    name="오크 전사",
    entity_id="orc_warrior",
    actor_type_desc=("인간과 가장 오랫동안 대립해온 종족인 오크는 힘과 명예를 중시하는 문화를 가지고 있다. "
                     "오크 사회에서 위계 질서는 절대적이며, 오크들간의 서열은 오직 힘으로 결정된다. "
                     "대중에게 오크는 흔히 무식하고 힘만 센 종족으로 알려져 있는데, 이는 사실이 아니다. "
                     "오크 종족은 기술, 마법 분야에서도 많은 성과를 이뤄냈으며, 일부 분야에서는 인간 사회의 수준을 웃돌기도 한다. "
                     ),
    entity_desc=("다양한 장비들로 무장하고 있는 오크 전사들은 오크 종족의 핵심 병력이다. "
                 "이들은 평균적으로 인간보다 강인한 신체 능력을 가지고 있기에 전투 시 주의가 필요하다. "),
    rarity=55,
    weight=125,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=410),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','l', 'F', 'I'),
    ),
    status=Status(
        hp=70,
        mp=15,
        strength=18,
        dexterity=16,
        agility=14,
        intelligence=14,
        constitution=17,
        charm=15,
        difficulty=11,# Unarmed 7
        base_melee=10,
        additional_melee=8,
        protection=15,
        hearing=15,
        eyesight=15,
        ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.shine, "chance": 0.2, "count": (10, 80), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item":item_factories.shortsword, "chance":1, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.wooden_shield, "chance":0.3, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.iron_chain_mail, "chance":0.3, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.iron_headpiece, "chance":0.3, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.leather_boots, "chance":0.3, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
    ),
)
ActorDB.monster_difficulty[orc_warrior.status.difficulty].append(orc_warrior)


### Orc blacksmith
orc_blacksmith = Actor(
    char="O",
    fg=(255, 132, 66),
    name="오크 대장장이",
    entity_id="orc_blacksmith",
    actor_type_desc=("인간과 가장 오랫동안 대립해온 종족인 오크는 힘과 명예를 중시하는 문화를 가지고 있다. "
                     "오크 사회에서 위계 질서는 절대적이며, 오크들간의 서열은 오직 힘으로 결정된다. "
                     "대중에게 오크는 흔히 무식하고 힘만 센 종족으로 알려져 있는데, 이는 사실이 아니다. "
                     "오크 종족은 기술, 마법 분야에서도 많은 성과를 이뤄냈으며, 일부 분야에서는 인간 사회의 수준을 웃돌기도 한다. "
                     ),
    entity_desc=("오크 종족은 제련술에 능숙하며, 그중에서도 실력이 뛰어난 대장장이들은 다른 오크들로부터 많은 존경을 받는다. "),
    rarity=20,
    weight=118,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=409),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','l', 'F', 'I'),
    ),
    status=Status(
        hp=72,
        mp=40,
        strength=18,
        dexterity=20,
        agility=13,
        intelligence=16,
        constitution=10,
        charm=15,
        difficulty=10,# Unarmed 7
        base_melee=11,
        additional_melee=8,
        protection=15,
        hearing=15,
        eyesight=15,
        ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.potion_of_flame, "chance": 0.08, "count": (1, 2), "BUC": None,"upgrade": None},
        {"item": item_factories.scroll_of_enchantment, "chance": 0.05, "count": (1, 2), "BUC": None,"upgrade": None},
        {"item": item_factories.shine, "chance": 0.2, "count": (80, 150), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item":item_factories.forging_hammer, "chance":0.9, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.leather_pants, "chance":0.5, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.leather_boots, "chance":0.2, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
    ),
)
ActorDB.monster_difficulty[orc_blacksmith.status.difficulty].append(orc_blacksmith)


### Orc lord
orc_lord = Actor(
    char="O",
    fg=(222, 196, 0),
    name="오크 족장",
    entity_id="orc_lord",
    actor_type_desc=("인간과 가장 오랫동안 대립해온 종족인 오크는 힘과 명예를 중시하는 문화를 가지고 있다. "
                     "오크 사회에서 위계 질서는 절대적이며, 오크들간의 서열은 오직 힘으로 결정된다. "
                     "대중에게 오크는 흔히 무식하고 힘만 센 종족으로 알려져 있는데, 이는 사실이 아니다. "
                     "오크 종족은 기술, 마법 분야에서도 많은 성과를 이뤄냈으며, 일부 분야에서는 인간 사회의 수준을 웃돌기도 한다. "
                     ),
    entity_desc=("오크 사회에는 여러 부족들이 존재하며, 이 부족들은 각 부족별 족장들에 의해 통솔된다. "
                 "오크들에게 족장의 말은 절대적이며, 이러한 권력의 기반이 되는 것은 족장 본인이 가진 힘이다. "
                 "이렇게 여러 부족들이 나뉘어있지만 이들은 오크라는 하나의 정체성을 가지고 움직이며, "
                 "오크 종족이 지금까지 인간과 맞설 수 있던 것도 이러한 부족 간의 결합력 덕분이다. "),
    rarity=8,
    weight=135,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=420),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=True,
        hostile_type=('@','l', 'F', 'I'),
    ),
    status=Status(
        hp=80,
        mp=100,
        strength=21,
        dexterity=19,
        agility=14,
        intelligence=15,
        constitution=18,
        charm=20,
        difficulty=12,
        base_melee=15,
        additional_melee=10,
        protection=15,
        hearing=15,
        eyesight=15,
        ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
        regain_mana=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.scroll_of_lightning, "chance": 0.05, "count": (1, 1), "BUC": None,"upgrade": None},
        {"item": item_factories.shine, "chance": 0.1, "count": (100, 300), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item":item_factories.battle_axe, "chance":1, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.iron_armored_pants, "chance":0.5, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
        {"item":item_factories.iron_boots, "chance":0.3, "count":(1,1), "BUC": None, "upgrade":{-1:3,0:5,1:1}},
    ),
    initial_abilities=((ability_factories.call_of_the_orc_lord, 1),)
)
ActorDB.monster_difficulty[orc_lord.status.difficulty].append(orc_lord)


### Orc shaman
orc_shaman = Actor(
    char="O",
    fg=(209, 240, 153),
    name="오크 주술사",
    entity_id="orc_shaman",
    actor_type_desc=("인간과 가장 오랫동안 대립해온 종족인 오크는 힘과 명예를 중시하는 문화를 가지고 있다. "
                     "오크 사회에서 위계 질서는 절대적이며, 오크들간의 서열은 오직 힘으로 결정된다. "
                     "대중에게 오크는 흔히 무식하고 힘만 센 종족으로 알려져 있는데, 이는 사실이 아니다. "
                     "오크 종족은 기술, 마법 분야에서도 많은 성과를 이뤄냈으며, 일부 분야에서는 인간 사회의 수준을 웃돌기도 한다. "
                     ),
    entity_desc=("오크는 대체적으로 마법에 능통하지 않지만, 예로부터 부두술과 주술만큼은 꾸준하게 연구되어왔다. "
                 "오크 주술사들은 주로 영혼을 다루고 죽은 자와 소통하는 마법을 다룬다. "),
    rarity=25,
    weight=118,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=355),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=True,
        hostile_type=('@','l','F','I'),
    ),
    status=Status(
        hp=66,
        mp=105,
        strength=14,
        dexterity=16,
        agility=13,
        intelligence=17,
        constitution=13,
        charm=13,
        difficulty=10,
        base_melee=10,
        additional_melee=6,
        protection=11,
        hearing=15,
        eyesight=15,
        ),
    actor_state=ActorState(
        size=4,
        can_talk=True,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=True,
        has_head=1,
        regain_mana=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=(
        {"item": item_factories.potion_of_mana, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.shine, "chance": 0.1, "count": (30, 80), "BUC": None, "upgrade": None},
    ),
    initial_equipments=(
        {"item": item_factories.wooden_dagger, "chance": 0.1, "count": (1, 1), "BUC": None, "upgrade": None},
        {"item": item_factories.leather_pants, "chance": 0.3, "count": (1, 1), "BUC": None, "upgrade": None},
    ),
    initial_abilities=((ability_factories.soul_bolt, 1),)
)
ActorDB.monster_difficulty[orc_shaman.status.difficulty].append(orc_shaman)



####################################################
############## R - Reptiles  #######################
####################################################

### Primeval tortoise
primeval_tortoise = Actor(
    char="R",
    fg=(0, 13, 255),
    name="태고의 거북",
    entity_id="primeval_tortoise",
    entity_desc=("코끼리 정도의 몸집을 가진 이 거대한 육지거북은 평균 수명이 2천년 가량을 웃도는 것으로 알려져 있다. "
                 "이들은 육중한 몸 때문에 빠르게 움직이지 못하지만 단단한 등껍질과 거대한 앞발로 스스로를 보호한다. "),
    rarity=12,
    weight=5500,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=650),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=True,
        hostile_type=('@', 'c', 'd'),
        attracted_eat_type=("meat",),
    ),
    status=Status(
        hp=160,
        mp=50,
        strength=29,
        dexterity=16,
        agility=5,
        intelligence=20,
        constitution=14,
        charm=15,
        difficulty=12,
        base_melee=16,
        additional_melee=36,
        protection=45,
        hearing=10,
        eyesight=10,
        fire_resistance=0.5,
        acid_resistance=0.3,
        sleep_resistance=0.3,
        ),
    actor_state=ActorState(
        size=5,
        can_talk=False,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_swim=False,
        has_head=1,
        regain_mana=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_drop_on_death=({"item":item_factories.primeval_tortoise_shell, "chance":0.3, "count":(1,1), "BUC": {-1:0,0:1,1:0}, "upgrade":{0:1}},),
)
ActorDB.monster_difficulty[primeval_tortoise.status.difficulty].append(primeval_tortoise)



####################################################
######## T - GIANTS & TITANS & TROLLS  #############
####################################################

### Troll
troll = Actor(
    char="T",
    fg=(160, 176, 111),
    name="트롤",
    entity_id="troll",
    entity_desc=("거대한 인간형 신체와 흉폭한 성격을 지닌 트롤들은 극단적으로 공격적인 성향을 보인다. "
        "이들은 지적으로 뛰어나지 못하며, 항상 피를 갈구하는 위험한 생명체이다. "
        "일부 학자들은 트롤은 사실 선한 심성을 가진 생명체라고 주장하지만, 학계에서는 이 이론은 아직 받아들여지고 있지 않다. "),
    actor_quote=("트롤이 사실은 착한 놈들이라느니 뭐니 하는 안경잽이 나부랭이들이 있는 모양인데, 내 앞에 보이면 눈알을 뽑아버릴 거야. "
                 "우리 부대원들이 트롤들에게 찢겨 나가고 있을 때 그 자식들은 뭘 하고 있었지? 방에서 고대 시집이나 분석하고 있었으려나?"),
    rarity=28,
    weight=1855,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=350),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=110,
        mp=16,
        strength=22,
        dexterity=15,
        agility=12,
        intelligence=3,
        constitution=10,
        charm=8,
        difficulty=13,
        base_melee=25,
        additional_melee=20,
        protection=18,
        hearing=15,
        eyesight=13,
        ),
    actor_state=ActorState(
        size=5,
        can_talk=False,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_equipments=(
        {"item":item_factories.rags, "chance":1, "count":(1,1), "BUC": None, "upgrade":None},
    ),
)
ActorDB.monster_difficulty[troll.status.difficulty].append(troll)


### Giant
giant = Actor(
    char="T",
    fg=(150, 30, 190),
    name="자이언트",
    entity_id="giant",
    entity_desc=("자이언트는 오우거, 트롤 등의 야수들보다도 더 큰 거대한 몸집을 가졌지만, 이들에 비하면 비교적 지능적인 존재이다. "
        "이들은 말을 할 수 있는 수준의 지성을 가지고 있으며, 간혹 무기를 만들어 사용하는 것이 관찰되기도 했다. "
        "자이언트는 믿을 수 없이 강한 힘을 가지고 있지만 거대한 몸집 때문에 비교적 둔한 움직임을 보여준다."),
    actor_quote=("저놈들을 잘 길들여 병사로 만들면 우리 제국은 최강이 될 게야. 젊을 적의 영광을 다시 보는 날이 오면 좋겠구만. "),
    rarity=25,
    weight=4802,
    spawnable=True,
    edible=edible.RawMeatEdible(nutrition=420),
    ai_cls=BaseAI(
        alignment=(("hostile","neutral"), (3,1)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@',),
    ),
    status=Status(
        hp=150,
        mp=20,
        strength=30,
        dexterity=14,
        agility=11,
        intelligence=15,
        constitution=13,
        charm=18,
        difficulty=19,
        base_melee=39,
        additional_melee=15,
        protection=20,
        hearing=10,
        eyesight=14,
        fire_resistance=0.2,
        cold_resistance=0.2,
        poison_resistance=0.9,
        ),
    actor_state=ActorState(
        size=6,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
        can_talk=True,
    ),
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_equipments=(
        {"item":item_factories.rags, "chance":1, "count":(1,1), "BUC": None, "upgrade":None},
        {"item":item_factories.giant_wood_club, "chance":0.8, "count":(1,1), "BUC": None, "upgrade":None},
    )
)
ActorDB.monster_difficulty[giant.status.difficulty].append(giant)


####################################################
#################### Y - Yeti ######################
####################################################

### Yeti
yeti = Actor(
    char="Y",
    fg=(171, 249, 255),
    name="예티",
    entity_id="yeti",
    entity_desc=("예티는 두꺼운 털가죽으로 덮여있는 유인원과 유사한 외형을 하고 있으며, 뾰족한 뿔과 긴 송곳니 한 쌍이 가장 큰 특징이다. "
                 "주로 추운 곳에서 살아간다는 대중들의 인식과는 다르게 예티는 기후를 가리지 않고 다양한 곳에서 살아가며, 극단적으로는 사막에서 살아가는 것이 포착되기도 한다. "
                 "이들이 이렇게 다양한 기온에서 살아남을 수 있는 가장 큰 이유는 이들의 혈액이 항상 영하를 웃도는 낮은 온도를 유지하고 있기 때문인데, "
                 "덕분에 예티는 어느 기온에서나 몸의 체온을 낮게 유지하며 살아갈 수 있다. "
                 "예티는 이러한 특성을 이용해 적을 공격할 때 신체 일부를 급속도로 냉각시켜 몸을 경질화시켜 위력을 증가시키기도 한다. "
                 ),
    rarity=20,
    weight=1450,
    spawnable=True,
    edible=edible.YetiEdible(nutrition=300),
    ai_cls=BaseAI(
        alignment=(("hostile",), (1,)),
        do_melee_atk=True,
        do_ranged_atk=False,
        use_ability=False,
        hostile_type=('@','O','l'),
    ),
    status=Status(
        hp=105,
        mp=30,
        strength=21,
        dexterity=19,
        agility=15,
        intelligence=10,
        constitution=8,
        charm=12,
        difficulty=15,
        base_melee=30,
        additional_melee=10,
        protection=19,
        hearing=15,
        eyesight=10,
        cold_resistance=1,
        poison_resistance=1,
        melee_effects_var=((2, 1, 0.1, 0, 3),),
        melee_effects=(("freeze_target", 0.1),),
        ),
    actor_state=ActorState(
        size=5,
        can_talk=False,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=20),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
)
ActorDB.monster_difficulty[yeti.status.difficulty].append(yeti)


######################################### Adding monsters to actual database ############################################
# This code will run when the program starts.
# "ActorDB.monster_rarity_for_each_difficulty" contains lists of monsters' rarity for each difficulty level.
# This lists are used as weigth value when the game generates monsters.
for diff in list(ActorDB.monster_difficulty.keys()):
    for actor in ActorDB.monster_difficulty[diff]:
        ActorDB.monster_rarity_for_each_difficulty[diff].append(actor.rarity)

for k, v in ActorDB.monster_difficulty.items():
    for actor in v:
        if actor.actor_state.live_underwater:
            if not k in ActorDB.underwater_monster_difficulty:
                ActorDB.underwater_monster_difficulty[k] = []
            ActorDB.underwater_monster_difficulty[k].append(actor)
        else:
            if not k in ActorDB.surface_monster_difficulty:
                ActorDB.surface_monster_difficulty[k] = []
            ActorDB.surface_monster_difficulty[k].append(actor)

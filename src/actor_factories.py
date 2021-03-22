import ai_factories
import item_factories
import ability_factories
from components.status import Status
from components.inventory import Inventory
from components.ability_inventory import AbilityInventory
from components.equipments import Equipments
from components.actor_state import ActorState
from components.edible import GiantWaspEdible, RawMeatEdible, FireAntEdible, VoltAntEdible, FloatingEyeEdible
from entity import Actor
from order import RenderOrder

monster_difficulty = {
    0:[],
    1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[],
    11:[],12:[],13:[],14:[],15:[],16:[],17:[],18:[],19:[],20:[],
    21:[],22:[],23:[],24:[],25:[],26:[],27:[],28:[],29:[],30:[],
}

monster_rarity_for_each_difficulty = {
    0:[],
    1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[],
    11:[],12:[],13:[],14:[],15:[],16:[],17:[],18:[],19:[],20:[],
    21:[],22:[],23:[],24:[],25:[],26:[],27:[],28:[],29:[],30:[],
}


### Player
player = Actor(
    char="@",
    fg=(0, 255, 0),
    name="조나단",
    entity_id="player",
    entity_desc="\
        당신은 쿠가의 아뮬렛을 가져오라는 임무를 받고 끝이 보이지 않는 던전으로 발을 들였다.\n\
        ",
    rarity=0,
    spawnable=False,
    growthable=True,
    edible=RawMeatEdible(nutrition=300),
    render_order=RenderOrder.PLAYER,
    ai_cls=None,
    status=Status(
        hp=80000,#80
        mp=1000,
        strength=15,
        dexterity=15,
        agility=15,
        intelligence=15,
        constitution=15,
        charm=15,
        difficulty=0,
        base_melee=8,
        additional_melee=5,
        protection=10,
        eyesight=20,
        ),
    actor_state=ActorState(
        hunger=-1,##DEBUG 1200 TODO
        heal_wounds=True,
        size=4,
        weight=70,
    ),
    inventory=Inventory(capacity=52, is_fireproof=False),
    ability_inventory=AbilityInventory(capacity=10),
    equipments=Equipments(),
    initial_items=[
        (item_factories.scroll_of_enchantment, 1, (1,5)), 
        (item_factories.scroll_of_identify, 1, (1,4)), 
        (item_factories.scroll_of_remove_curse, 1, (1,4)), 
        (item_factories.scroll_of_piercing_flame, 1, (1,4)),
        (item_factories.scroll_of_tame, 1, (1,4)),
        (item_factories.scroll_of_meteor_storm, 1, (1,4)),
        (item_factories.potion_of_healing, 1, (1,4)),
        (item_factories.potion_of_paralysis, 1, (1,4)),
        (item_factories.potion_of_monster_detection, 1, (3,4)),
        ],
    initial_equipments=[
        (item_factories.leather_armor, 1),
        (item_factories.shortsword, 1,),
        (item_factories.amulet_of_kugah, 1),
        ],
    initial_abilities=[(ability_factories.lightning_bolt, 1), (ability_factories.steal, 1)],
)

### DEBUG
DEBUG = Actor(
    char="?",
    fg=(63, 127, 63),
    name="DEBUG",
    entity_id="DEBUG",
    entity_desc="DEBUG",
    rarity=0,
    spawnable=False,
    edible=RawMeatEdible(nutrition=300),
    ai_cls=ai_factories.DEBUG_ai,
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
monster_difficulty[DEBUG.status.difficulty].append(DEBUG)



####################################################
###################### a - ants  ###################
####################################################

### ant
ant = Actor(
    char="a",
    fg=(26, 33, 0),
    name="개미",
    entity_id="ant",
    entity_desc="\
        던전에서 뿜어나오는 어두운 기운은 동물은 물론 곤충들까지 거대하고 흉측한 괴수로 변이시켰다.\n\
        그렇지만 개중에는 어두운 기운의 영향을 덜 받은 개체들도 있기 마련이다.\n\
        비교적 던전의 기운을 덜 받은 이 개미들은 기껏해야 사람 손가락 남짓한 크기로, 대체로 별 위협이 되지 않는다.\n\
        \n\
        \"생각해보라고, 좁아터진 개미굴에 비하면 놈들은 거대한 저택에 사는 거나 마찬가지라니까?\"\
        ",
    rarity=9,
    spawnable=True,
    edible=RawMeatEdible(nutrition=5),
    ai_cls=ai_factories.ant_ai,
    status=Status(
        hp=4,
        mp=0,
        strength=2,
        dexterity=5,
        agility=9,
        intelligence=3,
        constitution=3,
        charm=1,
        difficulty=2,
        base_melee=1,
        additional_melee=1,
        protection=2,
        eyesight=9,
        acid_resistance=0.2,
        ),
    actor_state=ActorState(
        size=1,
        weight=0.05,
        can_talk=False,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[ant.status.difficulty].append(ant)


### fire ant
fire_ant = Actor(
    char="a",
    fg=(255, 0, 0),
    name="불개미",
    entity_id="fire_ant",
    entity_desc="\
        던전의 불개미들은 만지면 따끔한 수준의 지상의 불개미들과는 차원이 다른 존재이다.\n\
        성인 남성 주먹 정도의 크기인 이들은, 전신에 두른 약한 화염으로 자신을 방어한다.\n\
        이들이 턱에서 쏘는 작은 불꽃은 인간에게 크게 위협적이지는 않지만,\n\
        책이나 주문서를 가지고 다니는 마법사들에게는 큰 골칫거리로 여겨진다.\n\
        \n\
        \"빌어먹을 불개미녀석들, 이번에는 400샤인짜리 주문서를 태워먹었다고 썅.\"\
        ",
    rarity=5,
    spawnable=True,
    edible=FireAntEdible(nutrition=10, cook_bonus=5),
    ai_cls=ai_factories.fire_ant_ai,
    status=Status(
        hp=25,
        mp=2,
        strength=6,
        dexterity=8,
        agility=12,
        intelligence=5,
        constitution=7,
        charm=9,
        difficulty=4,
        base_melee=3,
        additional_melee=2,
        protection=6,
        eyesight=15,
        fire_resistance=0.9,
        ),
    actor_state=ActorState(
        size=2,
        weight=0.05,
        can_talk=False,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[fire_ant.status.difficulty].append(fire_ant)


### volt ant
volt_ant = Actor(
    char="a",
    fg=(99, 255, 193),
    name="스파크 개미",
    entity_id="volt_ant",
    entity_desc="\
        스파크 개미들은 몸에 두른 전류를 통해 적으로부터 자신을 보호한다.\n\
        스파크 개미는 시큼텁텁한 맛이 나는 것으로 알려져 있으며, 일부 모험가들 사이에서는 별미로 꼽힌다.\n\
        \n\
        \"이놈들을 잔뜩 잡아서 지상에서 안주로 팔면 대박이 날 거야, 암.\"\
        ",
    rarity=5,
    spawnable=True,
    edible=VoltAntEdible(nutrition=10, cook_bonus=5),
    ai_cls=ai_factories.volt_ant_ai,
    status=Status(
        hp=25,
        mp=2,
        strength=6,
        dexterity=8,
        agility=12,
        intelligence=5,
        constitution=7,
        charm=9,
        difficulty=4,
        base_melee=2,
        additional_melee=5,
        protection=6,
        eyesight=15,
        shock_resistance=0.9,
        ),
    actor_state=ActorState(
        size=2,
        weight=0.05,
        can_talk=False,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[volt_ant.status.difficulty].append(volt_ant)


####################################################
#################  b- bats / birds  ################
####################################################

### Bat
bat = Actor(
    char="b",
    fg=(94, 0, 122),
    name="박쥐",
    entity_id="bat",
    entity_desc="\
        박쥐는 공중에서 자유자재로 날아다닐 수 있는 비행능력을 보유하고 있다.\n\
        설치류와 조류 사이에 걸친 애매한 외형 때문에 이들은 오랜 시간 인간들에게 박해받아왔지만,\n\
        대부분의 박쥐는 무해하며, 인간에게 먼저 공격을 거는 경우는 드물다고 한다.\n\
        \n\
        \"난 솔직히 걔들이 해를 끼치던 말던 관심없어. 생긴 게 징그럽잖아?\"\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=13, cook_bonus=8),
    ai_cls=ai_factories.bat_ai,
    status=Status(
        hp=14,
        mp=1,
        strength=5,
        dexterity=7,
        agility=15,
        intelligence=3,
        constitution=13,
        charm=5,
        difficulty=3,
        base_melee=1,
        additional_melee=3,
        protection=3,
        eyesight=20,
        ),
    actor_state=ActorState(
        size=2,
        weight=0.3,
        can_fly=True,
        is_flying=True,
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
monster_difficulty[bat.status.difficulty].append(bat)


####################################################
#####################  c- cats  ####################
####################################################

### Kitten
kitten = Actor(
    char="c",
    fg=(222, 208, 169),
    name="새끼고양이",
    entity_id="kitten",
    entity_desc="\
        던전 속에서 새끼고양이는 둘 중 하나로 취급된다.\n\
        작고 귀여운 동물,\n\
        혹은 영양가 넘치는 자그마한 고깃덩어리.\n\
        \n\
        \"얼마 전 옆집 고양이가 새끼를 낳았다던데, 그 집 식구들이 건강해보이는 건 기분 탓인가?\"\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=66, cook_bonus=30),
    ai_cls=ai_factories.kitten_ai,
    status=Status(
        hp=32,
        mp=3,
        strength=6,
        dexterity=10,
        agility=11,
        intelligence=4,
        constitution=10,
        charm=15,
        difficulty=3,
        base_melee=2,
        additional_melee=4,
        protection=6,
        eyesight=20,
        ),
    actor_state=ActorState(
        size=2,
        weight=3,
        can_swim=False,# NOTE: baby cats cannot swim
        can_talk=False,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=2),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[kitten.status.difficulty].append(kitten)


### Cat
cat = Actor(
    char="c",
    fg=(217, 184, 91),
    name="고양이",
    entity_id="cat",
    entity_desc="\
        고양이들은 게으르지만 맹수의 본능을 지닌 민첩한 사냥꾼들이다.\n\
        이들은 잡식성이고 시력이 좋기 때문에 많은 모험꾼들에게 애완동물로 사랑받는다.\n\
        고양이들이 사람의 꿈을 조종하는 영적인 능력을 지녔다고 주장하는 학자들도 있지만, 명확히 밝혀진 것은 없다.\n\
        \n\
        \"그 녀석하고 눈이 마주친 날이면 난 항상 악몽을 꿔. 그런데도 왜일까, 녀석만 보면 자꾸 먹이를 주게 돼.\"\
        ",
    rarity=8,
    spawnable=True,
    edible=RawMeatEdible(nutrition=83, cook_bonus=30),
    ai_cls=ai_factories.cat_ai,
    status=Status(
        hp=48,
        mp=5,
        strength=9,
        dexterity=12,
        agility=14,
        intelligence=6,
        constitution=16,
        charm=15,
        difficulty=4,
        base_melee=4,
        additional_melee=3,
        protection=7,
        eyesight=20,
        ),
    actor_state=ActorState(
        size=3,
        weight=5,
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
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
)
monster_difficulty[cat.status.difficulty].append(cat)


### Large Cat
large_cat = Actor(
    char="큰 고양이",
    fg=(230, 169, 0),
    name="Large Cat",
    entity_id="large_cat",
    entity_desc="\
        던전의 기운을 받은 고양이들은 지상의 맹수에 가까운 크기로 자라기도 한다.\n\
        이들은 결코 맹수는 아니지만, 무방비한 모험가에게는 충분한 위협이 될 수 있다.\n\
        \n\
        \"이 흉터가 고양이 때문에 생겼다는 건 죽어도 비밀이다, 알겠지?\"\
        ",
    rarity=3,
    spawnable=True,
    edible=RawMeatEdible(nutrition=110, cook_bonus=35),
    ai_cls=ai_factories.large_cat_ai,
    status=Status(
        hp=55,
        mp=5,
        strength=12,
        dexterity=17,
        agility=19,
        intelligence=10,
        constitution=15,
        charm=17,
        difficulty=5,
        base_melee=7,
        additional_melee=6,
        protection=8,
        eyesight=22,
        ),
    actor_state=ActorState(
        size=3,
        weight=5,
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
    inventory=Inventory(capacity=10),
    ability_inventory=AbilityInventory(capacity=3),
    equipments=Equipments(),
)
monster_difficulty[large_cat.status.difficulty].append(large_cat)


####################################################
####################  d - dogs  ####################
####################################################


### puppy
puppy = Actor(
    char="d",
    fg=(196, 220, 255),
    name="강아지",
    entity_id="puppy",
    entity_desc="\
        강아지들은 호기심이 넘치는 존재이다.\n\
        성체에 비하면 한참 뒤떨어지는 신체능력을 가졌지만, 넘치는 에너지 만큼은 성체를 압도한다.\n\
        \n\
        \"포션술사는 절대 강아지를 길러선 안돼. 집이 언제 불바다가 될 지 모르거든.\"\
        ",
    rarity=3,
    spawnable=True,
    edible=RawMeatEdible(nutrition=45, cook_bonus=10),
    ai_cls=ai_factories.puppy_ai,
    status=Status(
        hp=34,
        mp=3,
        strength=7,
        dexterity=9,
        agility=9,
        intelligence=5,
        constitution=15,
        charm=13,
        difficulty=3,
        base_melee=3,
        additional_melee=4,
        protection=6,
        eyesight=18,
        ),
    actor_state=ActorState(
        size=3,
        weight=5,
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
    inventory=Inventory(capacity=2),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[puppy.status.difficulty].append(puppy)


### Dog
dog = Actor(
    char="d",
    fg=(105, 165, 255),
    name="개",
    entity_id="dog",
    entity_desc="\
        인간 최고의 친구라는 이명은 던전 안에서도 예외가 아니다.\n\
        이들은 한 번 충성을 바친 주인에게는 무슨 일이 있어도 복종하며, 자신의 목숨을 바치는 데도 망설임이 없다.\n\
        \n\
        \"가족이 날 버려도 너만은 함께 해주는구나, 토비.\"\
        ",
    #TODO fix desc
    rarity=8,
    spawnable=True,
    edible=RawMeatEdible(nutrition=80, cook_bonus=20),
    ai_cls=ai_factories.dog_ai,
    status=Status(
        hp=50,
        mp=5,
        strength=11,
        dexterity=12,
        agility=15,
        intelligence=9,
        constitution=12,
        charm=13,
        difficulty=4,
        base_melee=5,
        additional_melee=4,
        protection=7,
        eyesight=18,
        ),
    actor_state=ActorState(
        size=3,
        weight=35,
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
    inventory=Inventory(capacity=5),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[dog.status.difficulty].append(dog)


### Large Dog
large_dog = Actor(
    char="d",
    fg=(0, 102, 255),
    name="큰 개",
    entity_id="large_dog",
    entity_desc="\
        인간 최고의 친구라는 이명은 던전 안에서도 예외가 아니다.\n\
        ...적으로 마주치지만 않는다면.\n\
        \n\
        \"사냥꾼의 가장 강력한 무기는 단검도, 활도 아니야. 그건 바로 녀석의 사냥개야.\"\
        ",
    rarity=3,
    spawnable=True,
    edible=RawMeatEdible(nutrition=120, cook_bonus=30),
    ai_cls=ai_factories.large_dog_ai,
    status=Status(
        hp=70,
        mp=9,
        strength=15,
        dexterity=16,
        agility=17,
        intelligence=11,
        constitution=14,
        charm=17,
        difficulty=6,
        base_melee=8,
        additional_melee=4,
        protection=12,
        eyesight=21,
        ),
    actor_state=ActorState(
        size=4,
        weight=5,
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
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
)
monster_difficulty[large_dog.status.difficulty].append(large_dog)


####################################################
################  e - eyes & brains  ###############
####################################################

### floating eye
floating_eye = Actor(
    char="e",
    fg=(255, 255, 255),
    name="떠다니는 눈",
    entity_id="floating_eye",
    entity_desc="\
        던전 안의 많은 생명체들은 그 정체가 베일에 감추어져 있다.\n\
        그러나 그 중에서도 가장 기원을 알 수 없고, 알려진 게 없는 존재가 바로 '떠다니는 눈' 들이다.\n\
        이들은 눈을 마주치는 것으로 생명체를 마비시킬 수 있는 강력한 힘을 가졌지만, 다행히 이들은 호전적이지 않을 뿐더러\n\
        물리적으로는 전혀 위협이 되지 않는다.\n\
        \n\
        \"마치 몸의 지배권을 빼앗기는 느낌이었어. 내가 녀석이 되고 녀석이 내가 되는 듯한 느낌이었지.\"\
        ",
    rarity=4,
    spawnable=True,
    edible=FloatingEyeEdible(nutrition=20),#cannot be cooked
    ai_cls=ai_factories.floating_eye_ai,
    status=Status(
        hp=50,
        mp=5,
        strength=8,
        dexterity=8,
        agility=5,
        intelligence=12,
        constitution=17,
        charm=15,
        difficulty=5,
        base_melee=0,
        additional_melee=0,
        protection=7,
        eyesight=35,
        sleep_resistance=1,
        ),
    actor_state=ActorState(
        size=3,
        weight=20,
        sexuality="None",
        can_breathe_underwater=True, # Don't Breathe
        can_fly=True,
        is_flying=True,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[floating_eye.status.difficulty].append(floating_eye)


####################################################
############### i = flying insects  ################
####################################################

### giant wasp
giant_wasp = Actor(
    char="i",
    fg=(250, 250, 0),
    name="거대 말벌",
    entity_id="giant_wasp",
    entity_desc="\
        어릴 적 꿀벌을 잡으며 놀아본 적은 있을 것이다.\n\
        하지만 꿀벌이 아니라 말벌이라면 이야기는 달라진다.\n\
        거기에 독침이 사람 손가락 정도 크기라면,\n\
        우리는 이들을 다른 종으로 분류해야 할 지도 모른다.\n\
        \n\
        \"독이 묻은 단검에 찔린다고 생각해봐. 거기에 그 단검이 날아다니면서 너를 쫓아온다면 난 분명 오줌을 지릴거야.\"\
        ",
    rarity=5,
    spawnable=True,
    edible=GiantWaspEdible(nutrition=50, cook_bonus=5),
    ai_cls=ai_factories.giant_wasp_ai,
    status=Status(
        hp=50,
        mp=0,
        strength=11,
        dexterity=17,
        agility=17,
        intelligence=7,
        constitution=15,
        charm=10,
        difficulty=6,
        base_melee=5,
        additional_melee=8,
        protection=8,
        eyesight=20,
        ),
    actor_state=ActorState(
        size=3,
        weight=6.1,
        can_fly=True,
        is_flying=True,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[giant_wasp.status.difficulty].append(giant_wasp)


####################################################
############### j - jellies / slimes  ##############
####################################################

### black jelly
black_jelly = Actor(
    char="j",
    fg=(10, 20, 10),
    name="검정색 덩어리",
    entity_id="black_jelly",
    entity_desc="\
        TODO\n\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=10), #TODO
    ai_cls=ai_factories.black_jelly_ai,
    status=Status(
        hp=45,
        mp=0,
        strength=8,
        dexterity=6,
        agility=3,
        intelligence=2,
        constitution=20,
        charm=3,
        difficulty=3,#5
        base_melee=2,
        additional_melee=5,
        protection=7,
        eyesight=15,
        poison_resistance=1,
        ),
    actor_state=ActorState(
        size=3,
        weight=55,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=False,
        has_torso=False,
        has_blood=False,
        has_soul=False,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
    initial_items=[(item_factories.acid_goo, 1, (-1,-1))],
)
monster_difficulty[black_jelly.status.difficulty].append(black_jelly)


####################################################
#################### n - nymphs  ###################
####################################################

### nymph
nymph = Actor(
    char="n",
    fg=(63, 245, 39),
    name="Nymph",
    entity_id="nymph",
    entity_desc="\
        TODO\n\
        ",
    rarity=99,
    spawnable=True,
    edible=RawMeatEdible(nutrition=230), #TODO
    ai_cls=ai_factories.nymph_ai,
    status=Status(
        hp=73,
        mp=35,
        strength=14,
        dexterity=25,
        agility=17,
        intelligence=16,
        constitution=18,
        charm=40,
        difficulty=5,##TODO : 7
        base_melee=2,
        additional_melee=8,
        protection=10,
        eyesight=26,
        ),
    actor_state=ActorState(
        size=4,
        weight=45,
        has_left_arm=True,
        has_right_arm=True,
        has_leg=True,
        has_eye=True,
        has_torso=True,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=2),
    equipments=Equipments(),
    initial_items=[],
    initial_equipments=[],
    initial_abilities=[(ability_factories.lightning_bolt, 1), (ability_factories.steal, 1)]
)
monster_difficulty[nymph.status.difficulty].append(nymph)


####################################################
#################### o - spheres ###################
####################################################
sphere_of_acid = Actor(
    char="o",
    fg=(123, 255, 0),
    name="Sphere of acid",
    entity_id="sphere_of_acid",
    entity_desc="\
        TODO\n\
        ",
    rarity=99, #TODO DEBUG
    spawnable=True,
    edible=None,
    ai_cls=ai_factories.sphere_of_acid_ai,
    status=Status(
        hp=50,
        mp=0,
        strength=12,
        dexterity=14,
        agility=8,
        intelligence=8,
        constitution=16,
        charm=5,
        difficulty=3,#TODO 6
        base_melee=0,
        additional_melee=0,
        protection=10,
        eyesight=15,
        poison_resistance=1,
        acid_resistance=1,
        psychic_resistance=1,
        sleep_resistance=1,
        ),
    actor_state=ActorState(
        size=3,
        weight=40,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=False,
        has_torso=False,
        has_blood=False,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[sphere_of_acid.status.difficulty].append(sphere_of_acid)


####################################################
############# s - spiders & scorpions  #############
####################################################

### jumping spider
jumping_spider = Actor(
    char="s",
    fg=(127, 235, 224),
    name="Jumping Spider",
    entity_id="jumping_spider",
    entity_desc="\
        TODO\n\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=10), #TODO
    ai_cls=ai_factories.jumping_spider_ai,
    status=Status(
        hp=3,
        mp=0,
        strength=1,
        dexterity=4,
        agility=8,
        intelligence=1,
        constitution=3,
        charm=2,
        difficulty=1,
        base_melee=0,
        additional_melee=1,
        protection=1,
        eyesight=5,
        poison_resistance=0.1,
        ),
    actor_state=ActorState(
        size=1,
        weight=0.01,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=True,
        has_eye=True,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[jumping_spider.status.difficulty].append(jumping_spider)


####################################################
#####################  w - worms  ##################
####################################################

### earthworm
earthworm = Actor(
    char="w",
    fg=(171, 108, 56),
    name="Earthworm",
    entity_id="earthworm",
    entity_desc="\
        TODO\n\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=10),
    ai_cls=ai_factories.earthworm_ai,
    status=Status(
        hp=2,
        mp=0,
        strength=1,
        dexterity=1,
        agility=3,
        intelligence=1,
        constitution=4,
        charm=1,
        difficulty=1,
        base_melee=0,
        additional_melee=0,
        protection=1,
        eyesight=3,
        ),
    actor_state=ActorState(
        size=1,
        weight=0.01,
        has_left_arm=False,
        has_right_arm=False,
        has_leg=False,
        has_eye=False,
        has_torso=False,
        has_blood=True,
        has_soul=True,
    ),
    inventory=Inventory(capacity=1),
    ability_inventory=AbilityInventory(capacity=1),
    equipments=Equipments(),
)
monster_difficulty[earthworm.status.difficulty].append(earthworm)

### maggot
maggot = Actor(
    char="w",
    fg=(222, 222, 222),
    name="Maggot",
    entity_id="maggot",
    entity_desc="\
        TODO\n\
        ",
    rarity=1,
    spawnable=False,# TODO : 인벤토리 외의 지형 위에 존재하는 시체 썩을 경우 일정 확률로 구더기 스폰(?)
    edible=RawMeatEdible(nutrition=1), #TODO
    ai_cls=ai_factories.maggot_ai,
    status=Status(
        hp=1,
        mp=0,
        strength=1,
        dexterity=1,
        agility=1,
        intelligence=1,
        constitution=1,
        charm=1,
        difficulty=1,
        base_melee=0,
        additional_melee=0,
        protection=1,
        eyesight=2,
        ),
    actor_state=ActorState(
        size=1,
        weight=0.01,
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
monster_difficulty[maggot.status.difficulty].append(maggot)


####################################################
################## E - ELEMENTALS  #################
####################################################

### Ice Elemental
ice_elemental = Actor(
    char="E",
    fg=(207, 247, 255),
    name="Ice Elemental",
    entity_id="ice_elemental",
    entity_desc="\
        Elementals are mystical beings. No human being truly understands the full story behind who created them.\n\
        Some say they are the will of mother nature, while the other says they are a creation of ancient wizards.\n\
        Despite all these mysteries, one thing remains clear: elementals are powerful.\n\
        And sometimes, they are willing to handle these powers to one they admire, rarely even to humans.\
        ",
    rarity=4,#TODO
    spawnable=True,
    edible=None, # 시체 없음
    ai_cls=ai_factories.ice_elemental_ai,
    status=Status(#TODO : 슽텟조정
        hp=110,
        mp=50,
        strength=16,
        dexterity=20,
        agility=15,
        intelligence=15,
        constitution=18,
        charm=18,
        difficulty=12,#TODO
        base_melee=8,
        additional_melee=8,
        protection=8,
        eyesight=20,
        cold_resistance=1,
        poison_resistance=1,
        ),
    actor_state=ActorState(
        size=4,
        weight=95,
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
monster_difficulty[ice_elemental.status.difficulty].append(ice_elemental)


####################################################
################### I - IMPOSTERS  #################
####################################################

### Chatterbox
chatterbox = Actor(
    char="I",
    fg=(255, 230, 230),
    name="Chatterbox",
    entity_id="chatterbox",
    entity_desc="\
        TODO\
        ",
    rarity=2,
    spawnable=True,
    edible=RawMeatEdible(nutrition=280),
    ai_cls=ai_factories.chatterbox_ai,
    status=Status(
        hp=83,
        mp=10,
        strength=17,
        dexterity=16,
        agility=16,
        intelligence=17,
        constitution=17,
        charm=17,
        difficulty=6,
        base_melee=1,
        additional_melee=10,
        protection=10,
        eyesight=2,
        ),
    actor_state=ActorState(
        size=4,
        weight=60,
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
monster_difficulty[chatterbox.status.difficulty].append(chatterbox)


####################################################
################ T - GIANTS & TITANS  ##############
####################################################

### Giant
giant = Actor(
    char="T",
    fg=(150, 30, 190),
    name="Giant",
    entity_id="giant",
    entity_desc="\
        Giants are not the most sharp-minded entity in the dungeon, but they are also not the most hostile ones either.\n\
        Giants tend to avoid conflicts, and they usually don't enjoy human flesh.\n\
        When a giant gets angry, it smashes the opponent with its bare fists, often resulting in tremendous damage.\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=1200),
    ai_cls=ai_factories.giant_ai,
    status=Status(#TODO : 스텟조정
        hp=150,
        mp=10,
        strength=19,
        dexterity=9,
        agility=5,
        intelligence=5,
        constitution=10,
        charm=9,
        difficulty=9,
        base_melee=10,
        additional_melee=5,
        protection=7,
        eyesight=12,
        fire_resistance=0.5,
        poison_resistance=0.9,
        cold_resistance=0.5,
        shock_resistance=0.3,
        ),
    actor_state=ActorState(
        size=5,
        weight=500,
        can_talk=False,
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
monster_difficulty[giant.status.difficulty].append(giant)


######################################### Adding monsters to actual database ############################################
# This code will run when the program starts.
# "monster_rarity_for_each_difficulty" contains lists of monsters' rarity for each difficulty level.
# This lists are used as weigth value when the game generates monsters.
for diff in list(monster_difficulty.keys()):
    for actor in monster_difficulty[diff]:
        monster_rarity_for_each_difficulty[diff].append(actor.rarity)
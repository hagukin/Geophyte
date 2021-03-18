import ai_factories
import item_factories
import ability_factories
from components.status import Status
from components.inventory import Inventory
from components.ability_inventory import AbilityInventory
from components.equipments import Equipments
from components.actor_state import ActorState
from components.edible import RawMeatEdible, FireAntEdible, VoltAntEdible, FloatingEyeEdible
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
    name="Player",
    entity_id="player",
    entity_desc="Player desc",
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
        has_telepathy=True,##TEST DEBUG TODO
    ),
    inventory=Inventory(capacity=52, is_fireproof=False),
    ability_inventory=AbilityInventory(capacity=10),
    equipments=Equipments(),
    initial_items=[
        (item_factories.scroll_of_enchantment, 1, (1,5)), 
        (item_factories.scroll_of_identify, 1, (1,4)), 
        (item_factories.scroll_of_remove_curse, 1, (1,4)), 
        (item_factories.scroll_of_magic_missile, 1, (1,4)),
        (item_factories.scroll_of_tame, 1, (1,4)),
        (item_factories.scroll_of_meteor_storm, 1, (1,4)),
        (item_factories.potion_of_healing, 1, (1,4)),
        (item_factories.potion_of_paralysis, 1, (1,4)),
        (item_factories.potion_of_telepathy, 1, (3,4)),
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
    name="Ant",
    entity_id="ant",
    entity_desc="\
        Some ants are slightly less affected by the dark energy emerging from the dungeon.\n\
        However these ants are still much larger than typical ants, scaling about the size of a human finger.\n\
        Their bites can be irritating but hardly does any damage.\
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
    name="Fire Ant",
    entity_id="fire_ant",
    entity_desc="\
        Fire ants are about the size of a human fist.\n\
        While they are not as large as some other massive creatures in the dungeon,\n\
        they have a unique ability that let them start a small flame from their jaw.\
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
    name="Volt Ant",
    entity_id="volt_ant",
    entity_desc="\
        Volt ants are about the size of a human fist.\n\
        Their body is surrounded by a weak electrical spark, which helps them to protect themselves from other creatures.\
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
    name="Bat",
    entity_id="bat",
    entity_desc="\
        Bats are very maneuvrable when they are flying.\n\
        Their odd resemblance with both birds and rats makes them a hated creatures among many humans.\n\
        However, a regular bats are relatively harmless, and are not much of a threat.\
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
    name="Kitten",
    entity_id="kitten",
    entity_desc="\
        Creatures in the dungeon see kittens in two different ways.\n\
        One sees them as an adorable little animal,\n\
        while the other sees them no more than a delicious chunk of meat.\n\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=36, cook_bonus=9),
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
    name="Cat",
    entity_id="cat",
    entity_desc="\
        Cats are lazy, mysterious, natural-born hunters.\n\
        They are incredibly flexible, have very sensitive eyesight, and eat pretty much anything, which makes them ideal for a friendly pet.\n\
        Some believe that cats possess spiritual forces and can manipulate one's dream, but nothing is yet to be confirmed.\n\
        ",
    rarity=8,
    spawnable=True,
    edible=RawMeatEdible(nutrition=50, cook_bonus=30),
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
    char="c",
    fg=(230, 169, 0),
    name="Large Cat",
    entity_id="large_cat",
    entity_desc="\
        Some cats in the dungeon grow much bigger than the others.\n\
        They are by no means a beast, but they definitely can be a threat when engaged unprepared.\
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
    name="Puppy",
    entity_id="puppy",
    entity_desc="\
        Puppies are sparkly and curious beings.\n\
        While they are much weaker than the adults, they are definitely more energetic.\
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
        constitution=11,
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
    name="Dog",
    entity_id="dog",
    entity_desc="\
        Men's best friend.\
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
        constitution=13,
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
    name="Large Dog",
    entity_id="large_dog",
    entity_desc="\
        Men's best friend.\n\
        ...Unless you angered it.\n\
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
    name="Floating Eye",
    entity_id="floating_eye",
    entity_desc="\
        Like many other creatures dwelling in the dungeon, floating eyes are considered mysterious and weird.\n\
        It has no limbs, torso, or any other body parts except for one giant eyeball.\n\
        Floating eyes\' gaze can cause paralyzation for reasons unknown, so it is better not to engage with these creatures.\n\
        Despite its potential danger, floating eyes can't physically hurt other beings.\
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
    name="Giant Wasp",
    entity_id="giant_wasp",
    entity_desc="\
        TODO\n\
        ",
    rarity=5,
    spawnable=True,
    edible=RawMeatEdible(nutrition=130),
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
    name="Black Jelly",
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
    initial_items=[(item_factories.toxic_goo, 1, (-1,-1))],
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
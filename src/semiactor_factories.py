from entity import SemiActor
from actions import DoorOpenAction, DoorUnlockAction
from language import interpret as i
import components.rule_factories as rule
import components.walkable as walkable
import components.semiactor_info as semiactor_info


##########################################################################
##########################################################################
########################## SEMIACTORS WITH AI ############################
##########################################################################
##########################################################################

fire = SemiActor(
    char="^",
    fg=(255, 243, 108),
    bg=None,
    name=i("불","fire"),
    entity_id="fire",
    entity_desc=" ",
    action_point=60, # 0 to 60
    action_speed=10, # 0 to 60
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=rule.normal_fire_rule,
)


##########################################################################
##########################################################################
################################# TRAPS ##################################
##########################################################################
##########################################################################

spike_trap = SemiActor(
    char="₪",
    fg=(255, 100, 100),
    bg=None,
    name=i("가시 함정","spike trap"),
    entity_id="spike_trap",
    entity_desc=i("가시 함정이다. 뾰족한 가시들이 솟아있다.",
                  "It has many sharp spikes on it."),
    do_action=False,
    walkable=walkable.low_dmg_spike_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


flame_trap = SemiActor(
    char="₪",
    fg=(255, 51, 0),
    bg=None,
    name=i("화염 함정","flame trap"),
    entity_id="flame_trap",
    entity_desc=i("화염 함정이다. 밟으면 뜨거운 불꽃이 피어오른다.",
                  "When stepped on, it emits a strong flame for a brief time."),
    do_action=False,
    walkable=walkable.low_dmg_flame_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


icicle_trap = SemiActor(
    char="₪",
    fg=(194, 255, 254),
    bg=None,
    name=i("고드름 함정","icicle trap"),
    entity_id="icicle_trap",
    entity_desc=i("고드름 함정이다. 뾰족한 고드름들이 솟아있다.",
                  "It has downside-up icicles attached onto it."),
    do_action=False,
    walkable=walkable.low_dmg_icicle_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


acid_spray_trap = SemiActor(
    char="₪",
    fg=(60, 255, 0),
    bg=None,
    name=i("염산 분사 함정","acid spray trap"),
    entity_id="acid_spray_trap",
    entity_desc=i("염산 분사 함정이다. 밟으면 강력한 염산을 분사한다.",
                  "When stepped on, it sprays an acidic liquid."),
    do_action=False,
    walkable=walkable.low_dmg_acid_spray_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


poison_spike_trap = SemiActor(
    char="₪",
    fg=(195, 0, 255),
    bg=None,
    name=i("독침 함정", "poison spike trap"),
    entity_id="poison_spike_trap",
    entity_desc=i("독침 함정이다. 독극물이 묻어있는 가시들이 솟아있다.",
                  "It has many poison-tipped spikes on it."),
    do_action=False,
    walkable=walkable.low_dmg_poison_spike_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


sonic_boom_trap = SemiActor(
    char="₪",
    fg=(255, 242, 0),
    bg=None,
    name=i("소닉붐 함정","sonicboom trap"),
    entity_id="sonic_boom_trap",
    entity_desc=i("소닉붐 함정이다. 밟으면 굉음을 발생시킨다."
                  "When stepped on, it makes an incredibly large noise that could attracts other creatures in the dungeon."),
    do_action=False,
    walkable=walkable.sonic_boom_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


explosion_trap = SemiActor(
    char="₪",
    fg=(255, 0, 0),
    bg=None,
    name=i("폭발 함정","explosion trap"),
    entity_id="explosion_trap",
    entity_desc=i("폭발 함정이다. 밟으면 화염과 함께 폭발한다.",
                  "When stepped on, it explodes."),
    do_action=False,
    walkable=walkable.low_dmg_explosion_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


##########################################################################
##########################################################################
################################# MISCS ##################################
##########################################################################
##########################################################################

altar = SemiActor(
char="▄",# bottom half block (ascii)
    fg=(255, 215, 0),
    bg=None,
    name=i("제단","altar"),
    entity_id="altar",
    entity_desc=i("종교 제사에 사용되는 제단이다.",
                  "A flat table that is used in some religious ceremonies."),
    do_action=False,
    walkable=walkable.altar_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)



##########################################################################
##########################################################################
################################ PLANTS ##################################
##########################################################################
##########################################################################

oak_tree = SemiActor(
    char="♠",
    fg=(79, 181, 38),
    bg=None,
    name=i("참나무", "oak tree"),
    entity_id="oak_tree",
    entity_desc=i("참나무다. 넓은 잎사귀를 가지고 있으며 몸체는 단단하다.",
                  "Oak tree has a wide leaves and is well known for its hardness."),
    do_action=False,
    walkable=None,
    safe_to_move=True,
    semiactor_info=semiactor_info.Default(flammable=0.8, corrodable=0.01),
    blocks_movement=False,
    blocks_sight=True,
    rule_cls=None,
    trigger_bump=False,
)

cactus = SemiActor(
    char="¥",
    fg=(96, 168, 50),
    bg=None,
    name=i("선인장", "cactus"),
    entity_id="cactus",
    entity_desc=i("선인장이다. 비가 적게 내리는 지역에서 서식하며, 몸체 전체에 뾰족한 가시가 나있다.",
                  "Cactus grows in dry places, and its covered with many spikes."),
    do_action=False,
    walkable=walkable.cactus_walkable,
    safe_to_move=False,
    semiactor_info=semiactor_info.Default(flammable=0.3, corrodable=0.3),
    blocks_movement=False,
    blocks_sight=False,
    rule_cls=None,
    trigger_bump=False,
)


##########################################################################
##########################################################################
########################## DOORS #########################################
##########################################################################
##########################################################################

closed_door = SemiActor(
    char="+",
    fg=(10, 10, 10),
    bg=(170, 140, 75),
    name=i("닫힌 문", "closed door"),
    entity_id="closed_door",
    entity_desc=i("나무로 된 문이다. 닫혀있다.",
                  "Its a wooden door. It is closed."),
    do_action=False,
    walkable=None,
    safe_to_move=True,
    semiactor_info=semiactor_info.Door(flammable=0.7, corrodable=0.1),
    blocks_movement=True,
    blocks_sight=True,
    rule_cls=None,
    trigger_bump=True,
)

opened_door = SemiActor(
    char="-",
    fg=(170, 140, 75),
    bg=None,
    name=i("열린 문","opened door"),
    entity_id="opened_door",
    entity_desc=i("나무로 된 문이다. 열려있다.",
                  "Its a wooden door. It is opened."),
    do_action=False,
    walkable=None,
    safe_to_move=True,
    semiactor_info=semiactor_info.Door(flammable=0.5, corrodable=0.1),
    blocks_movement=False,
    blocks_sight=False,
    rule_cls=None,
    trigger_bump=False,
)

locked_door = SemiActor(
    char="+",
    fg=(10, 10, 10),
    bg=(170, 140, 75),
    name=i("잠긴 문", "locked door"),
    entity_id="locked_door",
    entity_desc=i("나무로 된 문이다. 잠겨있다.",
                  "Its a wooden door. It is locked."),
    do_action=False,
    walkable=None,
    safe_to_move=True,
    semiactor_info=semiactor_info.Door(flammable=0.2, corrodable=0.1, unlock_chance=1),
    blocks_movement=True,
    blocks_sight=True,
    rule_cls=None,
    trigger_bump=True,
)

chained_locked_door = SemiActor(
    char="+",
    fg=(10, 10, 10),
    bg=(170, 140, 75),
    name=i("강철 사슬로 잠긴 문", "chained door"),
    entity_id="chained_locked_door",
    entity_desc=i("나무로 된 문 위에 강철판이 덧대어져 있다. 강철 사슬로 잠겨있다.",
                  "Its a wooden door padded with iron plates. It is locked with chains."),
    do_action=False,
    walkable=None,
    safe_to_move=True,
    semiactor_info=semiactor_info.Door(flammable=0, corrodable=0.02, break_str_req=(20,25), unlock_chance=0.7),
    blocks_movement=True,
    blocks_sight=True,
    rule_cls=None,
    trigger_bump=True,
)
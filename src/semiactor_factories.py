from entity import SemiActor
from actions import DoorOpenAction, DoorUnlockAction
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
    name="불",
    entity_id="fire",
    entity_desc="description of a fire",
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
    char="#",
    fg=(255, 100, 100),
    bg=None,
    name="가시 함정",
    entity_id="spike_trap",
    entity_desc="description of spike trap",
    do_action=False,
    walkable=walkable.low_dmg_spike_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


flame_trap = SemiActor(
    char="#",
    fg=(255, 51, 0),
    bg=None,
    name="화염 함정",
    entity_id="flame_trap",
    entity_desc="description of flame trap",
    do_action=False,
    walkable=walkable.low_dmg_flame_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


icicle_trap = SemiActor(
    char="#",
    fg=(194, 255, 254),
    bg=None,
    name="고드름 함정",
    entity_id="icicle_trap",
    entity_desc="description of trap",
    do_action=False,
    walkable=walkable.low_dmg_icicle_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


acid_spray_trap = SemiActor(
    char="#",
    fg=(60, 255, 0),
    bg=None,
    name="염산 분사 함정",
    entity_id="acid_spray_trap",
    entity_desc="description of trap",
    do_action=False,
    walkable=walkable.low_dmg_acid_spray_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


poison_spike_trap = SemiActor(
    char="#",
    fg=(195, 0, 255),
    bg=None,
    name="독침 함정",
    entity_id="poison_spike_trap",
    entity_desc="description of poison spike trap",
    do_action=False,
    walkable=walkable.low_dmg_poison_spike_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


sonic_boom_trap = SemiActor(
    char="#",
    fg=(255, 242, 0),
    bg=None,
    name="소닉붐 함정",
    entity_id="sonic_boom_trap",
    entity_desc="description of spike trap",
    do_action=False,
    walkable=walkable.sonic_boom_trap_walkable,
    semiactor_info=semiactor_info.Default(),
    blocks_movement=False,
    rule_cls=None,
)


explosion_trap = SemiActor(
    char="#",
    fg=(255, 0, 0),
    bg=None,
    name="폭발 함정",
    entity_id="explosion_trap",
    entity_desc="description of trap",
    do_action=False,
    walkable=walkable.low_dmg_explosion_trap_walkable,
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
    name="참나무",
    entity_id="oak_tree",
    entity_desc="description of oak tree",
    do_action=False,
    walkable=None,
    safe_to_move=True,
    semiactor_info=semiactor_info.Default(flammable=0.8, corrodable=0.01),
    blocks_movement=False,
    blocks_sight=True,
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
    name="닫힌 문",
    entity_id="closed_door",
    entity_desc="description of closed door",
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
    name="열린 문",
    entity_id="opened_door",
    entity_desc="description of opened door",
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
    name="잠긴 문",
    entity_id="locked_door",
    entity_desc="description of locked door",
    do_action=False,
    walkable=None,
    safe_to_move=True,
    semiactor_info=semiactor_info.Door(flammable=0.5, corrodable=0.1),
    blocks_movement=True,
    blocks_sight=True,
    rule_cls=None,
    trigger_bump=True,
)
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


##########################################################################
##########################################################################
################ INTERACTABLE SEMIACTORS WITH NO AI ######################
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
    semiactor_info=semiactor_info.Door(flammable=True, corrodable=True),
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
    semiactor_info=semiactor_info.Door(flammable=True, corrodable=True),
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
    semiactor_info=semiactor_info.Door(flammable=True, corrodable=True),
    blocks_movement=True,
    blocks_sight=True,
    rule_cls=None,
    trigger_bump=True,
)
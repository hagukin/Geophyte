import random
from components import semiactor_info
from chests import ChestSemiactor
from typing import List
from components.inventory import Inventory
from language import interpret as i

default_chest_checklist = {} # Terrain.gen_chests["checklist"]
chest_id_to_chest = {} # key: str, value: semiactor
def choose_random_chest_id(k=1) -> List[str]:
    """Returns entity_id
    WARNING: Can return chest that are not spawnable."""
    chests_chosen = random.choices(list(default_chest_checklist.keys()), weights=list(default_chest_checklist.values()), k=k)
    return [x.entity_id for x in chests_chosen] #TODO: Disable spawning if chest is not spawnable


large_wooden_chest = ChestSemiactor(
        char="©",
        fg=(191, 128, 0),
        bg=None,
        name=i("대형 나무 상자","large wooden chest"),
        entity_id="large_wooden_chest",
        entity_desc="나무로 만들어진 커다란 상자이다.",
        do_action=False,
        walkable=None,
        safe_to_move=True,
        semiactor_info=semiactor_info.Chest(flammable=0.2, corrodable=0.1),
        blocks_movement=False,
        blocks_sight=False,
        rule_cls=None,
        trigger_bump=True,
        storage=Inventory(capacity=52, is_fireproof=False, is_acidproof=False, is_waterproof=False),
        initial_items=None,
        randomized_items_num_range=(1,4),
        rarity=10,
        better_randomized_item=0,
    )
default_chest_checklist[large_wooden_chest] = large_wooden_chest.rarity
chest_id_to_chest[large_wooden_chest.entity_id] = large_wooden_chest


golden_chest = ChestSemiactor(
        char="©",
        fg=(255, 215, 0),
        bg=None,
        name=i("황금색 상자", "golden chest"),
        entity_id="golden_chest",
        entity_desc="황금색 빛을 내뿜는 상자이다.",
        do_action=False,
        walkable=None,
        safe_to_move=True,
        semiactor_info=semiactor_info.Chest(flammable=0, corrodable=0),
        blocks_movement=False,
        blocks_sight=False,
        rule_cls=None,
        trigger_bump=True,
        storage=Inventory(capacity=10, is_fireproof=True, is_acidproof=True, is_waterproof=True),
        initial_items=None, # Also can specify in terrain.
        randomized_items_num_range=(1,3),
        rarity=1,
        better_randomized_item=50,
    )
default_chest_checklist[golden_chest] = golden_chest.rarity
chest_id_to_chest[golden_chest.entity_id] = golden_chest
from ast import walk
from components import semiactor_info
from components.semiactor_info import SemiactorInfo
from order import RenderOrder
import random
from typing import Tuple, List
from entity import SemiActor

class ChestSemiactor(SemiActor):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Tuple[int, int, int] = None,
        name: str = "<Unnamed>",
        entity_id: str = "<Undefined id>",
        entity_desc: str = "<Undefined description>",
        do_action: bool = True,
        action_point: int = 60,
        action_speed: int = 0,
        walkable = None,
        safe_to_move: bool = True,
        semiactor_info: SemiactorInfo,
        blocks_movement: bool = False,
        blocks_sight: bool = False,
        rule_cls = None,
        trigger_bump: bool = True,
        storage = None,
        initial_items = None,
        rarity: int = 0,
        randomized_items_num_range: Tuple = (0,4),
    ):
        """
        Args:
            storage:
                It works the same way as Actor's Inventory component does.
            initial_items:
                A list that consists of tuples.
                Each tuple consists of 
                (
                    Item, 
                    Chance of having this Item when generated, 
                    (min_item_num, max_item_num)
                )
        """
        super().__init__(
            x=x,
            y=y,
            char=char,
            fg=fg,
            bg=bg,
            name=name,
            entity_id=entity_id,
            entity_desc=entity_desc,
            do_action=do_action,
            action_point=action_point,
            action_speed=action_speed,
            walkable=walkable,
            safe_to_move=safe_to_move,
            semiactor_info=semiactor_info,
            blocks_movement=blocks_movement,
            blocks_sight=blocks_sight,
            rule_cls=rule_cls,
            trigger_bump=trigger_bump,
            render_order=RenderOrder.SEMIACTOR_OBJ,
        )
        self.storage = storage
        if self.storage:
            self.storage.parent = self
        if initial_items is not None:
            self.initial_items = initial_items
        else:
            self.initial_items = []
        self.randomized_items_num_range = randomized_items_num_range
        self.rarity = rarity # Rarity of the chest


    def initialize_chest(self, initial_items: List=None):
        """
        Generate the initial items that this chest spawns with.
        """
        # Randomize Chest
        for item in random.choices(self.engine.item_manager.items_lists, self.engine.item_manager.items_rarity,
                       k=random.randint(self.randomized_items_num_range[0], self.randomized_items_num_range[1])):
            if item.spawnable:
                self.initial_items.append((item, 1, (1,1)))

        if initial_items:
            self.initial_items = initial_items
        for item in self.initial_items:
            if random.random() <= item[1]:
                temp = item[0].copy(gamemap=self.gamemap, exact_copy=False)
                temp.stack_count = random.randint(item[2][0], item[2][1])
                self.storage.add_item(temp)


    def spawn(self, gamemap, x: int, y: int, lifetime=-1, initial_items: List=None):
        """Spawn a copy of this instance at the given location."""
        clone = super().spawn(gamemap, x, y, lifetime)
        clone.initialize_chest(initial_items)
        return clone



from components.inventory import Inventory
import item_factories

default_chest_checklist = {} # Terrain.gen_chests["checklist"]
def choose_random_chest(k=1) -> List[str]:
    """Returns entity_id"""
    chests_chosen = random.choices(list(default_chest_checklist.keys()), weights=list(default_chest_checklist.values()), k=k)
    return chests_chosen


large_wooden_chest = ChestSemiactor(
        char="▣",
        fg=(191, 128, 0),
        bg=None,
        name="대형 나무 상자",
        entity_id="large_wooden_chest",
        entity_desc="large wooden chest desc",
        do_action=False,
        walkable=None,
        safe_to_move=True,
        semiactor_info=semiactor_info.Chest(),
        blocks_movement=False,
        blocks_sight=False,
        rule_cls=None,
        trigger_bump=True,
        storage=Inventory(capacity=52, is_fireproof=False),
        initial_items=None,
        randomized_items_num_range=(1,4),
        rarity=10
    )
default_chest_checklist[large_wooden_chest.entity_id] = large_wooden_chest.rarity
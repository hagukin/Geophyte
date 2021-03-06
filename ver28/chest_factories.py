from ast import walk
from order import RenderOrder
import random
from typing import Tuple, List
from entity import SemiActor
from actions import ChestOpenAction

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
        safe_to_move: bool = False,
        blocks_movement: bool = True,
        blocks_sight: bool = False,
        rule_cls = None,
        bump_action = None,
        storage = None,
        initial_items = [],
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
            blocks_movement=blocks_movement,
            blocks_sight=blocks_sight,
            rule_cls=rule_cls,
            bump_action=bump_action,
            render_order=RenderOrder.SEMIACTOR_OBJ,
        )
        self.storage = storage
        if self.storage:
            self.storage.parent = self
        self.initial_items = initial_items

    def spawn(self, gamemap, x: int, y: int, lifetime=-1, initial_items: List=None):
        """Spawn a copy of this instance at the given location."""
        clone = super().spawn(gamemap, x, y, lifetime)
        clone.initialize_chest(initial_items)
        return clone

    def initialize_chest(self, initial_items: List=None):
        """
        Generate the initial items that this chest spawns with.
        """
        if initial_items:
            self.initial_items = initial_items

        for item in self.initial_items:
            if random.random() <= item[1]:
                temp = item[0].spawn(gamemap=self.gamemap, x=0, y=0) # spawn items first to set item's gamemap value
                temp.stack_count = random.randint(item[2][0], item[2][1])
                self.storage.add_item(temp)


from components.inventory import Inventory
import item_factories

large_wooden_chest = ChestSemiactor(
        char="♫",
        fg=(191, 128, 0),
        bg=None,
        name="large wooden chest",
        entity_id="large_wooden_chest",
        entity_desc="large wooden chest desc",
        do_action=False,
        walkable=None,
        safe_to_move=True,
        blocks_movement=True,
        blocks_sight=False,
        rule_cls=None,
        bump_action=ChestOpenAction,
        storage=Inventory(capacity=52, is_fireproof=False),
        initial_items=[(item_factories.potion_of_healing, 1, (1,5))],
    )

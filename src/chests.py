from components.semiactor_info import SemiactorInfo
from order import RenderOrder
import random
from typing import Tuple, List
from entity import SemiActor, Actor

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
        better_randomized_item: int = 0,
        randomized_items_num_range: Tuple = (0,4), # NOTE: there can be less items in the chest than the minimum value due to spwanable checking
        trigger_when_take: List[Actor] = None,
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
            trigger_when_take:
                List of actors to trigger when any actor interacted with the chest.
            better_randomized_item:
                higher the value, there are better chance of this chest to contain better quality items.
                This value does nothing if the initial items are specified.

                NOTE:
                    how it works -
                    if rarity 1 and rarity 10 items exists, the chance of having rarity 1 item is 1/11.
                    However, if we both add 10 to each rarity, the chance of having rarity 1 item is 11/31, which is much higher.
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
        self.trigger_when_take = trigger_when_take
        self.better_randomized_item = better_randomized_item


    def initialize_chest(self, initial_items: List=None):
        """
        Generate the initial items that this chest spawns with.
        """
        if initial_items:
            self.initial_items = initial_items
        else:
            # Randomize Chest
            for item in random.choices(self.engine.item_manager.items_lists, [r+self.better_randomized_item for r in self.engine.item_manager.items_rarity],
                                       k=random.randint(self.randomized_items_num_range[0],
                                                        self.randomized_items_num_range[1])):
                if item.spawnable and not self.engine.item_manager.check_artifact_id_generated(item.entity_id):
                    self.initial_items.append((item, 1, (1, 1)))

        for item in self.initial_items:
            if random.random() <= item[1]:
                temp = item[0].copy(gamemap=self.gamemap, exact_copy=False)
                temp.stack_count = random.randint(item[2][0], item[2][1])
                if not self.storage.add_item(temp):
                    print(f"ERROR::Chest is full {self.entity_id} - initialize_chest()")


    def spawn(self, gamemap, x: int, y: int, lifetime=-1, initial_items: List=None):
        """Spawn a copy of this instance at the given location."""
        clone = super().spawn(gamemap, x, y, lifetime)
        clone.initialize_chest(initial_items)
        return clone

    def on_actor_take_trigger(self, interacted_with: Actor) -> None:
        """When any actor interacted with this chest, trigger_when_interact actors are triggered."""
        if self.trigger_when_take is None:
            return None

        delete = []
        for triggered in self.trigger_when_take:
            if triggered.actor_state.is_dead:
                delete.append(triggered)
                continue
            triggered.status.take_damage(amount=0, attacked_from=interacted_with)
            delete.append(triggered)

        for delete_actor in delete: # Prevent memory loss - remove references if actor is dead, or triggered
            self.trigger_when_take.remove(delete_actor)


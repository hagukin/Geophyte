from __future__ import annotations
from actions import WaitAction
import copy
import math
import random
import numpy as np

from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, List
from numpy.core.shape_base import block
from order import RenderOrder, InventoryOrder
from components.experience import Experience
from korean import grammar as g

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.readable import Readable
    from components.quaffable import Quaffable
    from components.equipable import Equipable
    from components.throwable import Throwable
    from components.walkable import Walkable
    from components.edible import Edible
    from components.status import Status
    from components.inventory import Inventory
    from components.ability_inventory import AbilityInventory
    from components.equipments import Equipments
    from components.item_state import ItemState
    from components.actor_state import ActorState
    from components.semiactor_info import SemiactorInfo
    from game_map import GameMap

T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(
        self,
        gamemap: GameMap = None,
        indestructible: bool = False,
        x: int = 0,
        y: int = 0,
        _char: str = "?",
        _fg: Tuple[int, int, int] = (255, 255, 255),
        _bg: Tuple[int, int, int] = None,
        _name: str = "<Unnamed>",
        entity_id: str = "<Undefined id>",
        _entity_desc: str = "",
        rarity: int = 0,
        action_point: int = 60, # 0 to 60
        action_speed: int = 0, # 0 to 60 (60 being fastest)
        spawnable: bool = False,
        walkable: Walkable = None,
        swappable: bool = False,
        blocks_movement: bool = False,
        blocks_sight: bool = False,
        render_order: RenderOrder = RenderOrder.LOWEST,
    ):
        """
        Args:
            indestructible:
                If true, this entity cannot be destroyed by remove_self().
            entity_desc:
                Recommended not to write more than 5 lines.
                Each lines should contain less than 110 characters. (Including blanks)
            rarity:
                ranges from 0 to 10.
                0 being genocided / not spawned naturally,
                1 being extremely rare,
                10 being extremely common
            action_point:
                points that are used when the entity performs an action.
                ranges from 0 to 60.
            action_speed:
                action points gained per turn.
            swappable:
                whether player can swap position with it or not.
        """
        self.indestructible = indestructible
        self.x = x
        self.y = y
        self._char = _char
        self._fg = _fg
        self._bg = _bg
        self._name = _name
        self.entity_id = entity_id
        self._entity_desc = _entity_desc
        self.rarity = rarity
        self.action_point = action_point
        self.action_speed = action_speed
        self.spawnable = spawnable
        self.walkable = walkable
        if self.walkable:
            self.walkable.parent = self
        self.swappable = swappable
        self.blocks_movement = blocks_movement
        self.blocks_sight = blocks_sight
        self.render_order = render_order
        self.entity_order = 0
        self.gamemap = gamemap
    @property
    def engine(self):
        return self.gamemap.engine

    @property
    def char(self):
        return self._char
    
    @property
    def fg(self):
        return self._fg

    @property
    def bg(self):
        return self._bg

    @property
    def name(self):
        return self._name
    def change_name(self, name):
        self._name = name

    @property
    def entity_desc(self):
        return self._entity_desc

    def do_environmental_effects(self):
        """
        Handle things that happens because of this entity's location.
        e.g. standing on traps, walking on grasses

        This function must be overriden in the child classes such as Actor, Item, etc.
        And the child class MUST call the parent function by super().do_environmental_effects()

        NOTE: This feature was use to be handled from action(MoveAction) objects.
        But by making this as an entity's method, the game is able to apply environmental effects regardless of the type of the movements.
        (e.g. teleporting on traps will still activate the traps.)
        """
        # When entity is on a grass
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "dense_grass":
            self.gamemap.tiles[self.x, self.y] = self.gamemap.tileset["t_sparse_grass"]()

        # When entity is on a water
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "shallow_water":
            self.gamemap.tiles[self.x, self.y] = self.gamemap.tileset["t_shallow_water"]()
            change_water_color = True
        elif self.gamemap.tiles[self.x, self.y]["tile_id"] == "deep_water":
            self.gamemap.tiles[self.x, self.y] = self.gamemap.tileset["t_deep_water"]()
            change_water_color = True
        else:
            change_water_color = False

        # Change the color of the water this entity is on (to simulate basic water movements)
        if change_water_color:
            for x_add in range(3):
                for y_add in range(3):
                    if self.gamemap.tiles[self.x-1+x_add, self.y-1+y_add]["tile_id"] == "shallow_water":
                        self.gamemap.tiles[self.x-1+x_add, self.y-1+y_add] = self.gamemap.tileset["t_shallow_water"]()
                    elif self.gamemap.tiles[self.x-1+x_add, self.y-1+y_add]["tile_id"] == "deep_water":
                        self.gamemap.tiles[self.x-1+x_add, self.y-1+y_add] = self.gamemap.tileset["t_deep_water"]()

    def gain_action_point(self):
        """Gain action points every game time."""
        # NOTE: The maximum amount of action point that can be saved is 180.
        # This means that the fastest possible entity in game can be as fast as three-times the speed of the player, but no more.
        self.action_point = min(180, self.action_point + self.action_speed)

    def spend_action_point(self, value=60):
        """Spend action points every entity turn."""
        # TODO: maybe add a feature that consumes different amount of action points depending on the action?
        self.action_point = max(0, self.action_point - value)

    def remove_self(self) -> None:
        if self.indestructible:
            print(f"ENTITY_REMOVE_SELF()::{self.name} IS INDESTRUCTIBLE. ENTITY.REMOVE_SELF() IS NULLIFIED.")
            return None
        elif self.gamemap:
            # If the gamemap value is not yet set for the entity, an error might pop up here.
            # If so, it can be safely ignored.
            # example of these errors: a flame that is generated on non-flammable tile may cause an error
            try:
                self.gamemap.entities.remove(self)
            except ValueError:
                print(f"ENTITY_REMOVE_SELF()::{self.name} HAS NO GAMEMAP. THIS MIGHT NOT BE A SERIOUS ISSUE.")
                pass

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.append(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entitiy at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            self.gamemap = gamemap
            gamemap.entities.append(self)

        # Apply environmental effects when placed.
        self.do_environmental_effects()

    def chebyshevDist(self, x: int, y: int) -> float:
        """
        Return the Chebyshev distance between the current entity and the given (x, y) coordinate.
        """
        return max(abs(x-self.x), abs(y - self.y))

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

        # Apply environmental effects when moved.
        self.do_environmental_effects()

    def collided_with_fire(self):
        pass


class Actor(Entity):
    def __init__(
        self,
        *,
        gamemap: Optional[GameMap] = None,
        indestructible: bool = False,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Tuple[int, int, int] = None,
        name: str = "<Unnamed>",
        entity_id: str = "<Undefined id>",
        entity_desc: str = "<Undefined description>",
        rarity: int = 0, # 1 to 10
        action_point: int = 60, # 0 to 60
        action_speed: int = 0, # 0 to 60
        spawnable: bool = False,
        walkable: Walkable = None,
        swappable: bool = True,
        growthable: bool = False,
        blocks_movement: bool = True,
        blocks_sight: bool = False,
        render_order: RenderOrder = RenderOrder.ACTOR,
        edible: Edible = None,
        ai_cls: Type[BaseAI],
        status: Status,
        actor_state: ActorState,
        inventory: Inventory,
        ability_inventory: AbilityInventory,
        equipments: Equipments,
        initial_items: List = [],
        initial_abilities: List = [],
        initial_equipments: List = [],
    ):
        """
        Args:
            growthable:
                boolean, whether this actor is capable of gaining experience points and strengthening the status
            blocks_movement:
                boolean, whether this actor blocks other entities
            blocks_sight:
                boolean, whether this actor blocks sight
            edible:
                information about this actor's corpse nutrition. if this actor has no corpse, leave it as None.
            initial_items:
                List of items that this actor spawns with.
                The list could contains multiple tuples, and tuple contains the following
                ( Item object, chance of spawning with the item, Tuple(min number of item, max number of item) )
            initial_abilities:
                List of abilities that this actor spawns with.
                The list could contains multiple tuples, and tuple contains the following
                ( Ability object, chance of spawning with the item )
            initial_equipments:
                List of equipments that this actor spawns with.
                The list could contains multiple tuples, and tuple contains the following
                ( Item object(that is equippable), chance of spawning with the item )
        """
        super().__init__(
            gamemap=gamemap,
            indestructible=indestructible,
            x=x,
            y=y,
            _char=char,
            _fg=fg,
            _bg=bg,
            _name=name,
            entity_id=entity_id,
            _entity_desc=entity_desc,
            rarity=rarity,
            action_point=action_point,
            action_speed=action_speed,
            spawnable= spawnable,
            walkable=walkable,
            swappable=swappable,
            blocks_movement=blocks_movement,
            blocks_sight=blocks_sight,
            render_order=render_order,
        )
        self.ai = ai_cls
        if ai_cls:
            self.ai.parent = self

        self.actor_state = actor_state
        self.actor_state.parent = self

        self.status = status
        self.status.parent = self
        self.growthable = growthable
        if growthable:
            self.status.experience = Experience()
            self.status.experience.parent = self.status

        self.inventory = inventory
        self.inventory.parent = self

        self.ability_inventory = ability_inventory
        self.ability_inventory.parent = self

        self.equipments = equipments
        self.equipments.parent = self

        self.edible = edible
        if self.edible:
            self.edible.parent = None

        self.initial_items = initial_items
        self.initial_abilities = initial_abilities
        self.initial_equipments = initial_equipments

    @property
    def is_dead(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return self.actor_state.is_dead

    @property
    def actor_speed(self) -> int:
        """
        Returns the value of regenerated action points(or action_speed) per game turn.
        action_speed of an actor is caculated regarding Actor's agility status.
        A single turn in game is a single loop of the gameloop.
        """
        self.action_speed = self.status.agility
        return self.action_speed

    def remove_self(self):
        super().remove_self()

    def do_environmental_effects(self):
        """
        Overriding the entity method.
        """
        ### Call parent function ###
        super().do_environmental_effects()

        ### A. Tile related ###
        if not self.actor_state.is_flying:
            ### 1. Deep pit
            if self.gamemap.tiles[self.x, self.y]["tile_id"] == "deep_pit":
                if not self.actor_state.is_in_deep_pit:
                    pass#TODO: Add an effect that happens only right after when the actor fell into the pit

                self.actor_state.is_in_deep_pit = True #TODO : action에서 deep pit 처리
            else:
                self.actor_state.is_in_deep_pit = False
            
            ### 2. Shallow pit
            if self.gamemap.tiles[self.x, self.y]["tile_id"] == "shallow_pit":
                self.actor_state.is_in_shallow_pit = True
            else:
                self.actor_state.is_in_shallow_pit = False

            ### 3. Deep water, shallow water
            # copy is_submerged to was_submerged
            self.actor_state.was_submerged = self.actor_state.is_submerged

            if self.gamemap.tiles[self.x, self.y]["tile_id"] == "deep_water":
                self.actor_state.is_submerged = True

                # Actor that is bigger than size 7 does not fully sink in the water.
                if self.actor_state.size < 7:
                    self.actor_state.is_underwater = True
            elif self.gamemap.tiles[self.x, self.y]["tile_id"] == "shallow_water":
                self.actor_state.is_submerged = True

                # Actor that is smaller than size 1 will fully sink in the water even if its shallow.
                if self.actor_state.size <= 1:
                    self.actor_state.is_underwater = True
                else:
                    self.actor_state.is_underwater = False
            else:
                self.actor_state.is_submerged = False
                self.actor_state.is_underwater = False
                self.actor_state.is_drowning = [0,0]
   
        ### B. Semiactor related ###
        semiactor_collided = self.gamemap.get_semiactor_at_location(self.x, self.y)

        if semiactor_collided:
            if semiactor_collided.walkable:
                semiactor_collided.walkable.perform(target=self)
            
    def gain_action_point(self):
        """
        Gain action points every game time.
        This method is overriden.
        """
        self.action_point = min(180, self.action_point + self.actor_speed)

    def initialize_actor(self):
        """
        Sets initial items, abilities, and equipments of this actor.
        This method is called from spawn().
        """
        for item in self.initial_items:
            if random.random() <= item[1]:
                temp = item[0].spawn(gamemap=self.gamemap, x=0, y=0)
                temp.stack_count = random.randint(item[2][0], item[2][1])
                self.inventory.add_item(temp)
        
        for equipment in self.initial_equipments:
            if equipment != None:
                if random.random() <= equipment[1]:
                    eq = equipment[0].spawn(gamemap=self.gamemap, x=0, y=0)
                    self.inventory.add_item(eq)
                    self.equipments.equip_equipment(item=eq, forced=True)

        for ability in self.initial_abilities:
            if random.random() <= ability[1]:
                self.ability_inventory.add_ability(ability[0].spawn())

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """
        Spawn a copy of this instance at the given location.
        """
        clone = super().spawn(gamemap, x, y)
        clone.initialize_actor()#NOTE: initialize_actor() should be called AFTER super().spawn(), so that the actor's gamemap is set.
        return clone

    def check_for_immobility(self):
        """
        Check if this actor is incapable of doing anything except for waiting.
        This function should be called inside of every action subclasses' top row.
        """
        # Paralyzation
        if self.actor_state.is_paralyzing != [0,0] or self.actor_state.is_frozen != [0,0,0]:
            return True

        return False
    
    def inventory_on_fire(self):
        # Ignite items in inventory
        if self.inventory.is_fireproof == False:
            for item in self.inventory.items:
                item.collided_with_fire()

    def collided_with_fire(self, fire):
        """
        Args:
            fire:
                Fire semiactor that this entity collided with.
        """
        super().collided_with_fire()
        # Burn the actor
        if self.actor_state.is_burning == [0,0,0,0]: # was not already burning
            self.engine.message_log.add_message(f"{self.name}에 불이 붙었다!",target=self)
            self.actor_state.apply_burning([fire.rule.base_damage, fire.rule.add_damage, 0, fire.rule.fire_duration])


class Item(Entity):
    def __init__(
        self,
        *,
        parent: Optional[Inventory] = None,
        gamemap: Optional[GameMap] = None,
        indestructible: bool = False,
        x: int = 0,
        y: int = 0,
        should_randomize: bool = False,
        char: str = "?",
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Tuple[int, int, int] = None,
        name: str = "<Unnamed>",
        entity_id: str = "<Undefined id>",
        entity_desc: str = "<Undefined description>",
        rarity: int = 0, # 1 to 10
        action_point: int = 60, # 0 to 60
        action_speed: int = 0, # 0 to 60
        weight: float = 0, # kg
        price: int = -1, # -1: cannot sell nor buy
        item_type: InventoryOrder = InventoryOrder.MISC,
        item_state: ItemState,
        blocks_movement: bool = False,
        blocks_sight: bool = False,
        spawnable: bool = False,
        walkable: Walkable=None,
        swappable: bool=False,
        flammable: float = 0, # 0 to 1, 1 being always flammable
        corrodible: float = 0, # 0 to 1, 1 being will always corrode
        droppable: bool = True,
        stackable: bool = True,
        stack_count: int = 1,
        throwable: Throwable = None,
        readable: Readable = None,
        quaffable: Quaffable = None,
        equipable: Equipable = None,
        edible: Edible = None,
        lockpickable: Tuple[float, float] = (0, 0),
        counter_at_front: bool = False,
        initial_BUC: dict = { 1: 0, 0: 1, -1: 0 },
        initial_identified: float = 0,
        initial_upgrades: List = [], #TODO
    ):
        """
        Args:
            initial_BUC:
                Chance of this item spawning with certain BUC status.
                { BUC number : chance of having that BUC number indicated as weight, ...)
                e.g. { 1: 3, 0: 5, -1: 1 } -> Has highest chance of spawing as uncursed.
            initial_identification:
                Chance of this item spawning as already identified. (semi-identified)
            initial_upgrades:
                TODO
            lockpickable:
                0 to 1 OR -1, 1 being always successfully unlocking something when used by actor of dex 18 or higher, and -1 being ALWAYS unlocking regardless of the actor's status. 
                0 to 1, 1 being item always being broken when used to lockpick/unlock things.
            counter_at_front:
                if True, display this item as 100 xxx instead of xxx (x100).
        """
        super().__init__(
            gamemap=gamemap,
            indestructible=indestructible,
            x=x,
            y=y,
            _char=char,
            _fg=fg,
            _bg=bg,
            _name=name,
            entity_id=entity_id,
            _entity_desc=entity_desc,
            rarity=rarity,
            action_point=action_point,
            action_speed=action_speed,
            spawnable=spawnable,
            walkable=walkable,
            swappable=swappable,
            blocks_movement=blocks_movement,
            blocks_sight=blocks_sight,
            render_order=RenderOrder.ITEM,
        )
        self.should_randomize = should_randomize
        self.parent = parent
        self.weight = weight
        self.price = price
        self.item_type = item_type

        self.item_state = item_state
        self.item_state.parent = self

        self.flammable = flammable
        self.corrodible = corrodible
        self.droppable = droppable

        self.stackable = stackable
        self.stack_count = stack_count

        self.throwable = throwable
        if throwable:
            self.throwable.parent = self
        self.readable = readable
        if readable:
            self.readable.parent = self
        self.quaffable = quaffable
        if quaffable:
            self.quaffable.parent = self
        self.equipable = equipable
        if equipable:
            self.equipable.parent = self
        self.edible = edible
        if edible:
            self.edible.parent = self
        
        self.lockpickable = lockpickable

        self.counter_at_front = counter_at_front

        self.initial_BUC = initial_BUC
        self.initial_identified = initial_identified
        self.initial_upgrades = initial_upgrades

    @property
    def char(self):
        char = self.gamemap.engine.item_manager.items_fake_info[self.entity_id]["char"]
        if char:
            return char
        else:
            return self._char
    
    @property
    def fg(self):
        fg = self.gamemap.engine.item_manager.items_fake_info[self.entity_id]["fg"]
        if fg:
            return fg
        else:
            return self._fg

    @property
    def bg(self):
        bg = self.gamemap.engine.item_manager.items_fake_info[self.entity_id]["bg"]
        if bg:
            return bg
        else:
            return self._bg

    @property
    def name(self):
        if self.item_state.check_if_semi_identified():
            return self._name
        else:
            name = self.gamemap.engine.item_manager.items_fake_info[self.entity_id]["name"]
            if name:
                return name
            else:
                return self._name
            
    @property
    def entity_desc(self):
        if self.item_state.check_if_semi_identified():
            return self._entity_desc
        else:
            entity_desc = self.gamemap.engine.item_manager.items_fake_info[self.entity_id]["entity_desc"]
            if entity_desc:
                return entity_desc
            else:
                return self._entity_desc

    def price_of(self, buyer: Actor, discount: float=1) -> int:
        """Return the price of the given item for given actor."""
        if self.stack_count < 1:
            return 0
        return round(discount * self.price * self.stack_count) #TODO: Make charm affect the price

    def remove_self(self):
        super().remove_self()
        if self.indestructible:
            print(f"DEBUG::{self.name} IS INDESTRUCTIBLE. ITEM.REMOVE_SELF() IS NULLIFIED.")
            return None

        if self.parent:
            if self.equipable: # If the item can be equipped, try to remove it from its wearer. (if there is any)
                self.parent.parent.equipments.remove_equipment(region=self.equipable.equip_region, forced=True)
            self.parent.remove_item(self, remove_count=self.stack_count)

    def initialize_item(self):
        """
        Sets initial BUC, identification status, etc.
        This method is called from spawn().
        """
        if random.random() <= self.initial_identified:
            self.item_state.identify_self()
        else:
            self.item_state.unidentify_self()
        
        self.item_state.BUC = random.choices(list(self.initial_BUC.keys()), list(self.initial_BUC.values()), k=1)[0]

        #TODO: upgrades initialization

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """
        Spawn a copy of this instance at the given location.
        """
        clone = super().spawn(gamemap, x, y)
        clone.initialize_item()#NOTE: initialize_item() should be called AFTER super().spawn(), so that the actor's gamemap is set.
        return clone

    def get_info(self) -> dict:
        """
        Get values from this item's components, and return them as a single dictionary.
        This method is used for item copying.

        NOTE: This method should be constantly updated as the game grows.
        """
        info = {}

        # Get variables from entity class that can be modified after generation.
        info["gamemap"] = self.gamemap
        info["parent"] = self.parent
        info["char"] = self._char
        info["fg"] = self._fg
        info["bg"] = self._bg
        info["name"] = self._name
        info["entity_desc"] = self._entity_desc
        info["weight"] = self.weight
        info["price"] = self.price
        info["flammable"] = self.flammable
        info["droppable"] = self.droppable
        info["action_speed"] = self.action_speed
        info["action_point"] = self.action_point

        # Get variables from item_state class that can be modified after generation.
        info["is_burning"] = self.item_state.is_burning
        info["burntness"] = self.item_state.burntness
        info["corrosion"] = self.item_state.corrosion
        info["BUC"] = self.item_state.BUC
        info["is_identified"] = self.item_state.is_identified
        info["is_being_sold_from"] = self.item_state.is_being_sold_from

        # Copy the entire component if possible
        # NOTE: If something goes wrong, try copying the values manually like above.
        info["equipable"] = self.equipable
        info["edible"] = self.edible
        info["throwable"] = self.throwable
        info["readable"] = self.readable
        info["quaffable"] = self.quaffable

        return info

    def set_info(self, info:dict) -> None:
        """
        Get values from the get_info(), and set this item's values with those.
        """
        # Entity
        self.gamemap = info["gamemap"]
        self.parent = info["parent"]
        self._char = info["char"]
        self._fg = info["fg"]
        self._bg = info["bg"]
        self._name = info["name"]
        self._entity_desc = info["entity_desc"]
        self.weight = info["weight"]
        self.price = info["price"]
        self.flammable = info["flammable"]
        self.droppable = info["droppable"]
        self.action_speed = info["action_speed"]
        self.action_point = info["action_point"]

        # item_state
        self.item_state.is_burning = info["is_burning"]
        self.item_state.burntness = info["burntness"]
        self.item_state.corrosion = info["corrosion"]
        self.item_state.BUC = info["BUC"]
        self.item_state.is_identified = info["is_identified"]
        self.item_state.is_being_sold_from = info["is_being_sold_from"]

        # components
        #NOTE: the parent variable must be changed.
        self.equipable = info["equipable"]
        if self.equipable:
            self.equipable.parent = self

        self.edible = info["edible"]
        if self.edible:
            self.edible.parent = self

        self.throwable = info["throwable"]
        if self.throwable:
            self.throwable.parent = self

        self.readable = info["readable"]
        if self.readable:
            self.readable.parent = self

        self.quaffable = info["quaffable"]
        if self.quaffable:
            self.quaffable.parent = self

    def duplicate_self(self, quantity:int=None):
        """
        Create and return new item that is a direct copy of this item.

        Args:
            quantity:
                If set to None, the copied item's stack_count is copied from the original.
                If it has any value, the method will use it instead.
        """
        # Create new item instance from item_factories
        dup_item = None
        for i in self.engine.item_manager.items_lists:
            if i.entity_id == self.entity_id:
                dup_item = copy.deepcopy(i)

                # Copy item informations
                dup_item.set_info(info=self.get_info())
                break
        if dup_item == None:
            print(f"DEBUG::ITEM {self.name} FAILED TO DUPLICATE ITSELF. - ITEM.DUPLICATE_SELF()")
            return None

        # Set quantity
        if quantity:
            dup_item.stack_count = quantity
        else:
            dup_item.stack_count = self.stack_count
        
        return dup_item

    def collided_with_fire(self, fire=None):
        """
        Args:
            fire:
                Fire semiactor that this entity collided with.
        """
        if fire:
            super().collided_with_fire(fire)
        will_catch_fire = random.random()
        if will_catch_fire < self.flammable:
            self.item_state.is_burning = True
        

class SemiActor(Entity):
    def __init__(
        self,
        *,
        gamemap: Optional[GameMap] = None,
        indestructible: bool = False,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Tuple[int, int, int] = None,
        name: str = "<Unnamed>",
        entity_id: str = "<Undefined id>",
        entity_desc: str = "<Undefined description>",
        do_action: bool = True,
        action_point: int = 60, # 0 to 60
        action_speed: int = 0, # 0 to 60
        semiactor_info: SemiactorInfo,
        walkable: Walkable = None,
        swappable: bool = False,
        safe_to_move: bool = False,
        blocks_movement: bool = False,
        blocks_sight: bool = False,
        rule_cls = None,
        bump_action = None,
        render_order = RenderOrder.SEMIACTOR, #NOTE: Might change depending on the entity itself
    ):
        """
        Args:
            do_action:
                Boolean. 
                This indicates whether this semiactor spends its action points, and does actions just like Actors, e.g. Fires
                or does it only involuntarily react to other entity's actions. e.g. Traps
            safe_to_move:
                Boolean. 
                This indicates whether it is safe to move to this entity's location or not.
                NOTE: This value might not be True to some types of actors, but it should work against most of the actors.
            bump_action:
                This variable is an object, and it is a child of SemiactorActionWithDirection class.
                When a BumpAction is called upon this semiactor, the game calls this instead.
                If its set to None, the game will call MoveAction.
        """
        super().__init__(
            gamemap=gamemap,
            indestructible=indestructible,
            x=x,
            y=y,
            _char=char,
            _fg=fg,
            _bg=bg,
            _name=name,
            entity_id=entity_id,
            _entity_desc=entity_desc,
            action_point=action_point,
            action_speed=action_speed,
            walkable=walkable,
            swappable=swappable,
            blocks_movement=blocks_movement,
            blocks_sight=blocks_sight,
            render_order=render_order,
        )
        self.rule = rule_cls
        if rule_cls:
            self.rule.parent = self

        self.lifetime = 0
        self.do_action = do_action

        if not do_action:
            self.action_point = 0
            self.action_speed = 0

        self.safe_to_move = safe_to_move
        self.bump_action = bump_action
        self.semiactor_info = semiactor_info
        self.semiactor_info.parent = self

    @property
    def is_active(self) -> bool:
        """Returns True if the lifetime has any value other than zero. (includes negatives)"""
        if self.lifetime == 0:
            return False
        else:
            return True
    
    def remove_self(self):
        super().remove_self()
        
    def spawn(self: T, gamemap: GameMap, x: int, y: int, lifetime: int=3) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.lifetime = lifetime
        clone.gamemap = gamemap
        gamemap.entities.append(clone)
        return clone

    def collided_with_fire(self):
        """
        Args:
            fire:
                Fire semiactor that this entity collided with.
        """
        super().collided_with_fire()
        if self.semiactor_info.flammable:
            will_catch_fire = random.random()
            if will_catch_fire < self.semiactor_info.flammable:
                self.semiactor_info.is_burning = True
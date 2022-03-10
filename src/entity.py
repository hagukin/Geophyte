from __future__ import annotations

from tcod.tileset import get_default
import copy
import math
import random
import color
import numpy as np

from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, List, Dict
from numpy.core.shape_base import block

from input_handlers import ForceAttackInputHandler, ChestPutEventHandler, ChestTakeEventHandler
from order import RenderOrder, InventoryOrder
from korean import grammar as g
from language import interpret as i
from tiles import TileUtil
from game import Game

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.usable import Usable
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
    from actions import Action

T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(
        self,
        is_deleted_from_game: bool = False,
        gamemap: GameMap = None,
        indestructible: bool = False,
        x: int = 0,
        y: int = 0,
        is_on_air: bool = False,
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
            is_on_air:
                Whether this entity is physically on air or not.
            indestructible:
                If true, this entity cannot be destroyed by remove_self().
            _entity_desc:
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
        Vars:
           

        NOTE: Current(20210710) list of in-game bump actions:
            attack
            move
            takeout
            putin
            purchase (NOTE: "purchase" should not be added to the list.)
            swap
        """
        self.is_deleted_from_game = is_deleted_from_game
        self.indestructible = indestructible
        self.x = x
        self.y = y
        self.is_on_air = is_on_air
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
        self.entity_order = id(self)
        self.gamemap = gamemap
    
    @property
    def engine(self):
        return Game.engine

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

    def float(self, start_floating: bool) -> None:
        """
        Args:
            start_floating:
                if True, try making this entity go on air.
                if False, try making this entity go down to the ground.
        """
        if start_floating:
            self.is_on_air = True
        else:
            self.is_on_air = False
        self.do_physics()

    def get_possible_bump_action_keywords(self, actor: Actor) -> List[str]:
        """Returns the amount of different bump actions this entity can do."""
        allactions = ("move", "swap", "attack", "takeout", "putin", "open", "close", "unlock", "break", "purchase", "sell") # Removed 'forceattack'
        tmp = []
        for action in allactions:
            if self.check_if_bump_action_possible(actor, action):
                tmp.append(action)
        return tmp

    def how_many_bump_action_possible(self, actor: Actor) -> int:
        """Returns the amount of different bump actions this entity can do."""
        return len(self.get_possible_bump_action_keywords(actor))

    def check_if_bump_action_possible(self, actor: Actor, keyword: str) -> bool:
        """Returns a default list of bump action that are available for this entity.
        e.g. an entity that has blocks_movement = True will not get "move" bump action.
        NOTE: "purchase" only exists as a form, and its active condition is decided during NonHostileBumpHandler."""
        from chests import ChestSemiactor
        if keyword == "move" and not self.blocks_movement:
            return True
        elif keyword == "swap" and self.swappable:
            if isinstance(self, Actor):
                if self.ai:
                    if self.ai.check_if_enemy(actor=actor):
                        return False
            return True
        elif keyword == "attack" and hasattr(self, "status"):
            return True
        elif keyword == "force_attack" and hasattr(self, "status"):
            if isinstance(self, Actor):
                if self.ai:
                    if self.ai.check_if_enemy(actor=actor):
                        return False
            return True
        elif (keyword == "takeout" or keyword == "putin") and isinstance(self, ChestSemiactor):
            return True
        elif keyword == "open" and self.entity_id[-11:] == "closed_door":
            return True
        elif keyword == "close" and self.entity_id[-11:] == "opened_door":
            return True
        elif keyword == "unlock" and self.entity_id[-11:] == "locked_door":#TODO Add lock
            return True
        elif keyword == "break" and self.entity_id[-11:] == "locked_door":
            return True
        elif keyword == "purchase" and self.entity_id[-10:] == "shopkeeper":
            # Will assume that if entity_id[:-10] is shopkeeper than it has shopping mechanics in its ai.
            if not actor in self.ai.thieves: # Can sell/buy items from shopkeeper only if you are not a thief.
                if self.ai.has_dept(actor):
                    return True
        elif keyword == "sell" and self.entity_id[-10:] == "shopkeeper":
            # Will assume that if entity_id[:-10] is shopkeeper than it has shopping mechanics in its ai.
            if not actor in self.ai.thieves: # Can sell/buy items from shopkeeper only if you are not a thief.
                return True
        return False

    def get_bumpaction(self, actor: Actor, keyword: str) -> Optional[Action]:
        """returns the action of given keyword.
        NOTE: Self is the one getting bumped.
        NOTE: This function MUST do one of the following:
            a) return a Action
            or
            b) set current eventhandler to a one that ALWAYS returns an action when .perform(), and return None"""
        import actions
        dx, dy = self.x - actor.x, self.y - actor.y
        if keyword == "move":
            return actions.MovementAction(actor, dx, dy)
        elif keyword == "swap":
            return actions.PlaceSwapAction(actor, self)
        elif keyword == "attack":
            return actions.MeleeAction(actor, dx, dy)
        elif keyword == "force_attack":
            self.engine.event_handler = ForceAttackInputHandler(melee_action=actions.MeleeAction(actor, dx, dy))
            return None
        elif keyword == "takeout":
            if actor == self.engine.player:
                self.engine.event_handler = ChestTakeEventHandler(self.storage)
                return None  # TODO Turn should pass
            else:
                raise NotImplementedError("ERROR::Nonplayer tried to take out something from a chest.")
        elif keyword == "putin":
            if actor == self.engine.player:
                self.engine.event_handler = ChestPutEventHandler(actor.inventory, self.storage)
                return None  # TODO Turn should pass
            else:
                raise NotImplementedError("ERROR::Nonplayer tried to put in something from a chest.")
        elif keyword == "open":
            return actions.DoorOpenAction(actor, dx, dy)
        elif keyword == "close":
            return actions.DoorCloseAction(actor, dx, dy)
        elif keyword == "unlock":
            return actions.DoorUnlockAction(actor, dx, dy)
        elif keyword == "break":
            return actions.DoorBreakAction(actor, dx, dy)
        elif keyword == "purchase":
            if actor == self.engine.player:
                from input_handlers import MainGameEventHandler
                self.engine.event_handler = MainGameEventHandler()
                self.ai.sell_all_picked_ups(customer=actor)
                return None
            else:
                raise NotImplementedError("ERROR::Nonplayer tried to purchase something from a shopkeeper.")
        elif keyword == "sell":
            if actor == self.engine.player:
                from input_handlers import SellItemsHandler
                self.engine.event_handler = SellItemsHandler(sell_to=self)
                return None
            else:
                raise NotImplementedError("ERROR::Nonplayer tried to sell something to a shopkeeper.")
        raise Exception(f"FATAL ERROR::Cannot find the given keyword {keyword}")

    def environmental_hole(self):
        """Handle entity on a hole tile."""
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "hole":
            new_gamemap = self.engine.world.get_map(depth=self.gamemap.depth + 1)
            if not new_gamemap:
                print(f"ERROR::Depth {self.gamemap.depth + 1} is not generated yet. Ignoring environmental_hole(). entity:{self.entity_id}")
                return None
            x, y = new_gamemap.get_random_tile(should_no_entity=True, should_walkable=True, should_safe_to_walk=True,
                                               should_not_protected=True, should_connected_with_stair=True)
            self.engine.change_entity_depth(entity=self, depth=self.gamemap.depth + 1, xpos=x, ypos=y)
            return None

    def environmental_grass(self):
        """Handle entity on a grass tile"""
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "dense_grass":
            self.gamemap.tiles[self.x, self.y] = self.gamemap.tileset["t_sparse_grass"]()

    def environmental_water(self):
        """Handle entity on water.
        NOTE: is different from Actor.environmental_water"""
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
                    if self.gamemap.tiles[self.x - 1 + x_add, self.y - 1 + y_add]["tile_id"] == "shallow_water":
                        self.gamemap.tiles[self.x - 1 + x_add, self.y - 1 + y_add] = self.gamemap.tileset[
                            "t_shallow_water"]()
                    elif self.gamemap.tiles[self.x - 1 + x_add, self.y - 1 + y_add]["tile_id"] == "deep_water":
                        self.gamemap.tiles[self.x - 1 + x_add, self.y - 1 + y_add] = self.gamemap.tileset[
                            "t_deep_water"]()

    def do_environmental_effects(self) -> None:
        """
        Handle things that happens because of this entity's location.
        e.g. standing on traps, walking on grasses

        This function must be overriden in the child classes such as Actor, Item, etc.
        And the child class MUST call the parent function by super().do_environmental_effects()

        NOTE: This feature was use to be handled from action(MoveAction) objects.
        But by making this as an entity's method, the game is able to apply environmental effects regardless of the type of the movements.
        (e.g. teleporting on traps will still activate the traps.)
        """
        if not self.is_on_air:
            self.environmental_hole()
            self.environmental_grass()
            self.environmental_water()

        semiactor_collided = self.gamemap.get_semiactor_at_location(self.x, self.y)
        if semiactor_collided:
            if semiactor_collided.walkable and not self.is_on_air:
                semiactor_collided.walkable.perform(target=self)

    def gain_action_point(self):
        """Gain action points every game time."""
        # NOTE: The maximum amount of action point that can be saved is 180.
        # This means that the fastest possible entity in game can be as fast as three-times the speed of the player, but no more.
        self.action_point = min(180, self.action_point + self.action_speed)

    def spend_action_point(self, value=60):
        """Spend action points every entity turn."""
        # TODO: maybe add a feature that consumes different amount of action points depending on the action?
        self.action_point = max(0, self.action_point - value)

    def check_is_deleted_from_game(self) -> bool:
        return self.is_deleted_from_game

    def delete_from_game(self) -> None:
        self.is_deleted_from_game = True

    def remove_self(self) -> None:
        if self.indestructible:
            print(f"DEBUG::{self.name} IS INDESTRUCTIBLE. ENTITY.REMOVE_SELF() IS NULLIFIED.")
            return None

        if self.check_is_deleted_from_game():
            print(f"ERROR::{self.name} IS ALREADY REMOVED FROM GAME.")
        self.delete_from_game()
        if self.gamemap:
            # If the gamemap value is not yet set for the entity, an error might pop up here.
            # If so, it can be safely ignored.
            # example of these errors: a flame that is generated on non-flammable tile may cause an error
            try:
                self.gamemap.entities.remove(self)
            except ValueError:
                if isinstance(self, Item):
                    if self.parent:
                        return None
                print(f"WARNING::entity.remove_self() - Tried to remove {self.name}, but its not in gamemap.entities. (It has self.gamemap)")
                pass

    def initialize_self(self) -> None:
        """Initialize this entity.
        Most of the time it is overwritten."""
        pass

    def copy(self, gamemap: GameMap, exact_copy: bool=False) -> Entity:
        clone = copy.deepcopy(self)
        clone.gamemap = gamemap
        if not exact_copy:
            clone.initialize_self()
        return clone

    def spawn(self: T, gamemap: GameMap, x: int, y: int, exact_copy: bool=False, apply_physics: bool=True) -> T:
        """
        Spawn a new copy of this instance at the given location.
        NOTE: So technically you are not spawning THIS SPECIFIC ENTITY, instead you are copying this entity and spawning the copy.
        Args:
            apply_physics:
                if True, call environmental() functions during .place() call.
        """
        if gamemap.tiles[x, y]["tile_id"][-4:] == "hole":
            print(f"ERROR::You should avoid spawning an entities on holes. This could cause an unexpected issue! - entity: {self.entity_id}, depth: {gamemap.depth}, xy:{x,y}")
        clone = self.copy(gamemap, exact_copy=exact_copy) # Most of the time, spawn() will have exact_copy param as False
        clone.place(x, y, gamemap, apply_physics=apply_physics)
        return clone

    def do_physics(self) -> None:
        self.do_environmental_effects()

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None, apply_physics: bool=True) -> None:
        """
        Place this entitiy at a new location.
        If new gamemap is given, remove entity from previous gamemap, and place it onto new gamemap."""
        self.x = x
        self.y = y
        if gamemap:
            self.gamemap = gamemap
            gamemap.entities.append(self)

        # Apply environmental effects when placed.
        if apply_physics:
            self.do_physics()

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
        self.do_physics()

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
        actor_type_desc: str = "",
        entity_desc: str = "",
        actor_quote: str = "",
        rarity: int = 0, # 1 to 10
        action_point: int = 60, # 0 to 60
        action_speed: int = 0, # 0 to 60
        weight: float = 0,  # kg
        spawnable: bool = False,
        walkable: Walkable = None,
        swappable: bool = True,
        growthable: bool = False,
        tameable: float = None, # If None use default. Set to 0 to make untameable.
        blocks_movement: bool = True,
        blocks_sight: bool = False,
        render_order: RenderOrder = RenderOrder.ACTOR,
        edible: Edible = None,
        ai_cls: Optional,
        status: Status,
        actor_state: ActorState,
        inventory: Inventory,
        ability_inventory: AbilityInventory,
        equipments: Equipments,
        initial_items: Tuple[Dict] = None,
        initial_drop_on_death: Tuple[Dict] = None,
        initial_abilities: Tuple[Tuple] = None,
        initial_equipments: Tuple[Dict] = None,
        tile_effect_on_path: str = None,
        actor_to_spawn_on_path: Actor = None,
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
            initial_items, drop_on_death:
                List of items that this actor spawns with.
                The list could contains multiple tuples, and tuple contains the following
                {
                    "item":Item object,
                    "chance":chance of spawning with the item,
                    "count":Tuple(min number of item,max number of item),
                    "BUC":format - same as Item.initial_BUC,
                    "upgrade":format - same as Item.initial_upgrades,
                }
            initial_abilities:
                List of abilities that this actor spawns with.
                The list could contains multiple tuples, and tuple contains the following
                ( Ability object, chance of spawning with the item )
            initial_equipments:
                List of equipments that this actor spawns with.
                The list could contains multiple tuples, and tuple contains the following
                format same as initial_items
            tameable:
                Integer. 0 means the actor(ai) is always tameable, and the higher the number is, the harder it becomes to tame it.
                Negative values means that the actor cannot be tamed.
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
        self.actor_type_desc = actor_type_desc
        self.actor_quote = actor_quote
        self.weight = weight
        self.tile_effect_on_path = tile_effect_on_path
        self.actor_to_spawn_on_path = actor_to_spawn_on_path

        self.ai = ai_cls
        if ai_cls:
            self.ai.parent = self

        self.actor_state = actor_state
        self.actor_state.parent = self

        self.status = status
        self.status.parent = self
        self.growthable = growthable
        if growthable:
            from components.experience import Experience
            self.status.experience = Experience()
            self.status.experience.parent = self.status
            self.status.experience.init_experience()

        self.inventory = inventory
        self.inventory.parent = self

        self.ability_inventory = ability_inventory
        self.ability_inventory.parent = self

        self.equipments = equipments
        self.equipments.parent = self

        self.edible = edible
        if self.edible:
            self.edible.parent = None

        if tameable is not None: # tameable can be set to 0
            self.tameable = tameable
        else:
            self.tameable = self.status.difficulty

        if initial_items == None or initial_items == ():
            self.initial_items = []
        else:
            self.initial_items = list(initial_items)

        if initial_drop_on_death == None or initial_drop_on_death == ():
            self.initial_drop_on_death = []
        else:
            self.initial_drop_on_death = list(initial_drop_on_death)

        if initial_abilities == None or initial_abilities == ():
            self.initial_abilities = []
        else:
            self.initial_abilities = list(initial_abilities)

        if initial_equipments == None or initial_equipments == ():
            self.initial_equipments = []
        else:
            self.initial_equipments = list(initial_equipments)

    @property
    def actor_desc(self):
        return self.actor_type_desc + "\n" + self.entity_desc

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

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None, apply_physics: bool=True) -> None:
        super().place(x, y, gamemap, apply_physics=apply_physics)
        if self.ai:
            if self.ai.path:
                self.ai.path.clear() #NOTE: If actor is moving towards a nearby tile, use move() instead.

    def discount_value(self) -> float:
        """A discout value for this actor.
        The higher the actor's charm is, the higher this value gets.
        If the actor is buying, subtract this value from 1.
        Return:
            float range between -0.4 to 0.4."""
        return min(0.4, max(-0.4, -0.4 + (self.status.changed_status["charm"]-11)*0.1))

    def drop_all_items(self) -> None:
        """Drop all items this status' parent owns. Mainly used during die()"""
        from actions import DropItem
        drop_list = []
        for item in self.inventory.items:
            drop_list.append(item)
        for item in self.inventory.drop_on_death:
            drop_list.append(item)
        for drop_item in drop_list:
            DropItem(entity=self, item=drop_item).perform()

    def drop_corpse(self) -> None:
        if self.edible:  # if edible is None, no corpse is spawned.
            import item_factories
            new_corpse = item_factories.corpse.spawn(self.gamemap, self.x, self.y)
            new_corpse.weight = max(self.weight * max(0.2, random.random()*0.9), 0.001)
            new_corpse.change_name(self.name + i(" 시체"," corpse"))
            new_corpse.edible = self.edible  # copy edible value from parent
            new_corpse.edible.parent = new_corpse

    def die(self, cause:str="low_hp", drop_item: bool=True, drop_edible: bool=True):
        if self.actor_state.is_dead:
            print(f"ERROR::Tried to call actor.die() to dead actor {self.name}. Call cancelled.")
            return None
        if drop_item:
            self.equipments.remove_all_equipments(forced=True, play_fx=False)
            self.drop_all_items()
        if drop_edible:
            self.drop_corpse()
        self.status.death(cause)

    def float(self, start_floating: bool) -> None:
        # Actor can go down only when actor is not flying and not levitating.
        if start_floating:
            super().float(start_floating)
        elif not start_floating and not self.actor_state.is_flying and self.actor_state.is_levitating == [0, 0]:
            super().float(start_floating)
        else:
            print(f"LOG::cannot stop floating since actor is either flying or levitating. {self.entity_id} - Actor.float()")

    def remove_self(self):
        super().remove_self()

    def environmental_pit(self):
        """Handles when actor is in pit"""
        # Deep pit
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "deep_pit":
            if not self.actor_state.is_in_deep_pit:
                pass  # TODO: Add an effect that happens only right after when the actor falls into the pit
            self.actor_state.is_in_deep_pit = True
        else:
            self.actor_state.is_in_deep_pit = False

        # Shallow pit
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "shallow_pit":
            self.actor_state.is_in_shallow_pit = True
        else:
            self.actor_state.is_in_shallow_pit = False

    def environmental_water(self):
        """Handles when actor is in water"""
        # Do not call the parent function since entity.do_environmental_effects() is called anyway
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "deep_water":
            # FX
            if self == self.engine.player and self.engine.sound_manager:
                if not self.actor_state.is_underwater or not self.actor_state.is_submerged:
                    self.engine.sound_manager.add_sound_queue("fx_water_splash")

            self.actor_state.is_submerged = True
            if self.actor_state.size < 6:
                self.actor_state.is_underwater = True
        elif self.gamemap.tiles[self.x, self.y]["tile_id"] == "shallow_water":
            # FX
            if self == self.engine.player and self.engine.sound_manager:
                if not self.actor_state.is_submerged:
                    self.engine.sound_manager.add_sound_queue("fx_water_splash_short")

            self.actor_state.is_submerged = True
            if self.actor_state.size <= 1:
                self.actor_state.is_underwater = True
            else:
                self.actor_state.is_underwater = False
        else:
            # FX
            if self == self.engine.player and self.engine.sound_manager:
                if self.actor_state.is_submerged:
                    self.engine.sound_manager.add_sound_queue("fx_water_splash_short")

            self.actor_state.is_submerged = False
            self.actor_state.is_underwater = False

        # Immediate debuff
        if self.actor_state.is_submerged:
            self.actor_state.actor_submerged()

    def environmental_hole(self):# Is a override, do not call super().environmental_hole in this function. You should manually sync the changes.
        """Handle entity on a hole tile."""
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "hole":
            new_gamemap = self.engine.world.get_map(depth=self.gamemap.depth + 1)
            x, y = new_gamemap.get_random_tile(should_no_entity=True, should_walkable=True, should_safe_to_walk=True,
                                               should_not_protected=True, should_connected_with_stair=True)
            self.engine.change_entity_depth(entity=self, depth=self.gamemap.depth + 1, xpos=x, ypos=y)

            fall_damage = int(min(200, round(self.weight)))
            fall_damage = max(0, random.randint(int(fall_damage/2), fall_damage))
            if self == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 추락으로부터 {fall_damage} 데미지를 받았다!",
                                                      f"You took {fall_damage} damage from the fall!"), fg=color.player_severe)
                self.engine.sound_manager.add_sound_queue("fx_fall_impact")
            self.status.take_damage(amount=fall_damage, attacked_from=None)
            if not self.actor_state.is_dead:
                bleed_damage = max(0, int(fall_damage / 10))
                self.actor_state.apply_bleeding([bleed_damage, 0, 6])

    def environmental_airborne(self):
        """Handles environmental effects when the actor is on air"""
        self.actor_state.is_submerged = False
        self.actor_state.is_underwater = False
        self.actor_state.is_in_shallow_pit = False
        self.actor_state.is_in_deep_pit = False

    def environmental_general(self):
        """Handles general things such as drowning check"""
        if not self.actor_state.is_underwater:
            self.actor_state.apply_drowning([0, 0])
            self.status.remove_bonus("submerged_bonus", ignore_warning=True)

    def environmental_save_previous_status(self):
        self.actor_state.was_submerged = self.actor_state.is_submerged

    def do_environmental_effects(self):
        """
        Overriding the entity method.
        """
        # Save status from previous turn before doing anything else
        self.environmental_save_previous_status()

        super().do_environmental_effects()
        self.environmental_general()

        if self.is_on_air:
            self.environmental_airborne()
        else:
            # Prevent any error (Mainly prevent flying actor not being on air when first initialized.)
            if self.actor_state.is_flying or self.actor_state.is_levitating != [0, 0]:
                self.float(True)
            else:
                self.environmental_pit()
                self.environmental_water()
                self.do_special_environmental_effect()  # Do action on tile
            
    def gain_action_point(self):
        """
        Gain action points every game time.
        This method is overriden.
        """
        self.action_point = min(180, self.action_point + self.actor_speed)

    def initialize_actor_possesion(self, args) -> Item:
        """Initialize items that the actor owns.
        a single args represents a single item."""
        temp = args["item"].copy(gamemap=self.gamemap, exact_copy=False) # First initialization done here

        # Override initialization if one of these values are not None (using custom)
        temp.initialize_BUC(use_custom=args["BUC"]) # Override initialized values
        temp.initialize_upgrade(use_custom=args["upgrade"])

        temp.stack_count = random.randint(args["count"][0], args["count"][1])
        temp.parent = self.inventory

        if not self.inventory.add_item(temp):
            print(f"WARNING::{self.entity_id}'s inventory is full. {temp.entity_id} - initialize_actor_possesion()")
        if temp.is_artifact:
            print(f"WARNING::{self.entity_id} initialized with an artifact {temp.entity_id} in its possesion.")
            if temp.spawnable:
                print(f"ERROR::{self.entity_id} initialized with an artifact {temp.entity_id} in its possesion WHICH IS A SPAWNABLE ITEM. You have potential risk of duplicated artifacts.")
        return temp

    def initialize_actor_drop_on_death(self, args) -> Item:
        """Initialize items that the actor owns.
        a single args represents a single item."""
        temp = args["item"].copy(gamemap=self.gamemap, exact_copy=False) # First initialization done here

        # Override initialization if one of these values are not None (using custom)
        temp.initialize_BUC(use_custom=args["BUC"]) # Override initialized values
        temp.initialize_upgrade(use_custom=args["upgrade"])

        temp.stack_count = random.randint(args["count"][0], args["count"][1])
        temp.parent = self.inventory

        self.inventory.drop_on_death.append(temp)
        return temp

    def initialize_actor_state(self) -> None:
        # use setter function to make actor float
        self.actor_state.is_flying = self.actor_state.is_flying

    def initialize_self(self) -> None:
        """
        Sets initial items, abilities, and equipments of this actor.
        This method is called from spawn().
        """
        if self.ai:
            self.ai.initialize()

        self.initialize_actor_state()

        for args in self.initial_items:
            if random.random() <= args["chance"]:
                self.initialize_actor_possesion(args)
        for args in self.initial_drop_on_death:
            if random.random() <= args["chance"]:
                self.initialize_actor_drop_on_death(args)
        for args in self.initial_equipments:
            if random.random() <= args["chance"]:
                item = self.initialize_actor_possesion(args)
                self.equipments.equip_equipment(item=item, forced=True)
        for ability in self.initial_abilities:
            if random.random() <= ability[1]:
                self.ability_inventory.add_ability(ability[0].copy())

    def copy(self, gamemap: GameMap, exact_copy: bool=False):
        """
        No additional input required
        """
        clone = super().copy(gamemap=gamemap, exact_copy=exact_copy)
        return clone

    def spawn(self: T, gamemap: GameMap, x: int, y: int, is_active: bool=False, apply_physics:bool=True) -> T:
        """
        Spawn a copy of this instance at the given location.
        """
        clone = super().spawn(gamemap, x, y, apply_physics=apply_physics)
        if is_active and clone.ai:
            clone.ai.activate()
        return clone

    def check_for_immobility(self):
        """
        Check if this actor is incapable of doing anything except for waiting.
        This function should be called inside of every action subclasses' top row.
        """
        # Paralyzation
        if self.actor_state.is_paralyzing != [0,0]:
            if self == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 마비되어 아무 것도 할 수 없다!",
                                                      f"You are paralyzed and can't do anything!"), color.player_severe)
            return True
        if self.actor_state.is_frozen != [0,0,0]:
            if self == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 완전히 얼어붙어 아무 것도 할 수 없다!",
                                                      f"You are completely frozen and can't do anything!"), color.player_severe)
            return True
        if self.actor_state.is_sleeping != [0,0]:
            if self == self.engine.player:
                self.engine.message_log.add_message(i(f"당신은 잠에 들어 아무 것도 할 수 없다!",
                                                      f"You are fallen asleep and can't do anything!"), color.player_severe)
            return True
        return False
    
    def inventory_on_fire(self):
        # Ignite items in inventory
        if self.inventory.is_fireproof == False:
            for item in self.inventory.items:
                item.collided_with_fire()

    def inventory_extinguish(self):
        # Ignite items in inventory
        for item in self.inventory.items:
            item.item_state.is_burning = False

    def inventory_on_acid(self):
        # Corrode items in inventory
        if self.inventory.is_acidproof == False:
            for item in self.inventory.items:
                item.collided_with_acid()

    def inventory_on_water(self):
        # Corrode items in inventory
        if self.inventory.is_waterproof == False:
            for item in self.inventory.items:
                item.collided_with_water()

    def collided_with_fire(self, fire):
        """
        Args:
            fire:
                Fire semiactor that this entity collided with.
        """
        super().collided_with_fire()
        # Burn the actor
        if self.actor_state.is_burning == [0,0,0,0]: # was not already burning
            if self == self.engine.player:
                self.engine.message_log.add_message(i(f"당신의 몸에 불이 붙었다!",
                                                      f"You catch on fire!"),target=self, fg=color.player_bad)
            else:
                self.engine.message_log.add_message(i(f"{self.name}에게 불이 붙었다!",
                                                      f"{self.name} catches on fire!"), target=self, fg=color.enemy_unique)
            self.actor_state.apply_burning([fire.rule.base_damage, fire.rule.add_damage, 0, fire.rule.fire_duration])

    def change_tile_on_path(self):
        """This method will apply some effect to the tile of this actor's location whenever the actor physically moves.
        You should not directly override this function, instead edit actor.change_tile_to variable(which is a id to get value from the tileset) instead."""
        if self.tile_effect_on_path != None:
            if self.tile_effect_on_path == "freeze":
                self.gamemap.tiles[self.x, self.y] = TileUtil.freeze(self.gamemap.tiles[self.x, self.y])
            elif self.tile_effect_on_path == "unfreeze":
                self.gamemap.tiles[self.x, self.y] = TileUtil.unfreeze(self.gamemap.tiles[self.x, self.y])
            elif self.tile_effect_on_path == "burn":
                self.gamemap.tiles[self.x, self.y] = TileUtil.burn(self.gamemap.tiles[self.x, self.y]) #NOTE: You are not spawning a fire, instead you are only burning the tile.

    def spawn_actor_on_path(self):
        if self.actor_to_spawn_on_path != None:
            self.actor_to_spawn_on_path.spawn(self.gamemap, self.x, self.y, True)

    def do_special_environmental_effect(self):
        """NOTE: Do not override this method. Override actor_special_environmental_effect instead."""
        self.change_tile_on_path()
        self.spawn_actor_on_path()


class Item(Entity):
    def __init__(
        self,
        *,
        parent: Optional[Inventory] = None,
        gamemap: Optional[GameMap] = None,
        indestructible: bool = False,
        x: int = 0,
        y: int = 0,
        should_initialize: bool = True,
        should_randomize: bool = False,
        char: str = "?",
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Tuple[int, int, int] = None,
        name: str = "<Unnamed>",
        entity_id: str = "<Undefined id>",
        item_type_desc: str = "",
        entity_desc: str = "",
        item_quote: str = "",
        rarity: int = 0, # 1 to 10
        action_point: int = 60, # 0 to 60
        action_speed: int = 0, # 0 to 60
        weight: float = 0, # kg
        price: int = -1, # -1: cannot sell nor buy
        item_type: InventoryOrder = InventoryOrder.MISC,
        item_state: ItemState,
        blocks_movement: bool = False,
        blocks_sight: bool = False,
        tradable: bool = True,
        spawnable: bool = False,
        uncursable: bool = True,
        cursable: bool = True,
        blessable: bool = True,
        walkable: Walkable=None,
        swappable: bool=False,
        flammable: float = 0, # 0 to 1, 1 being always flammable
        corrodible: float = 0, # 0 to 1, 1 being will always corrode
        droppable: bool = True,
        change_stack_count_when_dropped: Optional[Tuple[int,int]] = None, # (min, max) e.g. when black jelly drops toxic goo, it should only drop a few.
        stackable: bool = True,
        stack_count: int = 1,
        throwable: Throwable = None,
        readable: Readable = None,
        quaffable: Quaffable = None,
        usable: Usable = None,
        equipable: Equipable = None,
        edible: Edible = None,
        lockpickable: Tuple[float, float] = (0, 0),
        counter_at_front: bool = False,
        initial_BUC=None,
        initial_upgrades=None,
        is_artifact: bool=False,
    ):
        """
        Args:
            initial_BUC:
                Chance of this item spawning with certain BUC status.
                { BUC number : chance of having that BUC number indicated as weight, ...)
                e.g. { 1: 3, 0: 5, -1: 1 } -> Has highest chance of spawing as uncursed.
            initial_upgrades:
                default = {-3:1, -2:2, -1:4, 0:15, 1:4, 2:2, 3:1}
                can customize.
                e.g. {-5:1, 0:10, 1:1} -> Can only be spawned as -5 or 0 or 1
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
        self.should_initialize = should_initialize
        self.should_randomize = should_randomize
        self.parent = parent
        self.weight = weight
        self.price = price
        self.item_type = item_type

        self.item_type_desc = item_type_desc
        self.item_quote = item_quote

        self.item_state = item_state
        self.item_state.parent = self

        self.tradable = tradable
        self.flammable = flammable
        self.uncursable = uncursable # whether can change BUC to 0 from -1
        self.cursable = cursable
        self.blessable = blessable
        self.corrodible = corrodible
        self.droppable = droppable
        self.change_stack_count_when_dropped = change_stack_count_when_dropped

        self.stackable = stackable
        self.stack_count = stack_count

        self.throwable = throwable
        if throwable:
            self.throwable.parent = self
        self.usable = usable
        if usable:
            self.usable.parent = self
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

        if initial_BUC == None:
            self.initial_BUC = {1: 1, 0: 8, -1: 2} # Default not-cursed
        else:
            self.initial_BUC = initial_BUC

        if initial_upgrades == None:
            self.initial_upgrades = {-3:1, -2:5, -1:10, 0:30, 1:5, 2:2, 3:1}
        else:
            self.initial_upgrades = initial_upgrades

        self.is_artifact = is_artifact
        

    @property
    def char(self):
        char = self.engine.item_manager.items_fake_info[self.entity_id]["char"]
        if char:
            return char
        else:
            return self._char
    
    @property
    def fg(self):
        fg = self.engine.item_manager.items_fake_info[self.entity_id]["fg"]
        if fg:
            return fg
        else:
            return self._fg

    @property
    def bg(self):
        bg = self.engine.item_manager.items_fake_info[self.entity_id]["bg"]
        if bg:
            return bg
        else:
            return self._bg

    @property
    def name(self):
        if self.item_state.check_if_semi_identified():
            return self._name
        else:
            name = self.engine.item_manager.items_fake_info[self.entity_id]["name"]
            if name:
                return name
            else:
                return self._name
            
    @property
    def entity_desc(self):
        if self.item_state.check_if_semi_identified():
            return self._entity_desc
        else:
            entity_desc = self.engine.item_manager.items_fake_info[self.entity_id]["entity_desc"]
            if entity_desc:
                return entity_desc
            else:
                return self._entity_desc

    def environmental_water(self) -> None:
        super().environmental_water()
        if self.gamemap.tiles[self.x, self.y]["tile_id"][-5:] == "water":
            self.collided_with_water()

    def price_of_single_item(self, is_shopkeeper_is_selling: bool, discount: float=1) -> int:
        """
        Return the price of the given item for given actor.
        NOTE: This function will not handle the change of the price depending on the actor's charm.
        NOTE: If dicount value is over 1, the function will return an overrated price for the item.
        """
        if self.item_type.value == InventoryOrder.GEM.value:
            if self.item_state.check_if_unidentified():
                if is_shopkeeper_is_selling:
                    return round(discount * 3000)
                else:
                    return round(discount * 1)
            else:
                return round(discount * self.price)
        return round(discount * self.price)  # TODO: Make charm affect the price

    def price_of_all_stack(self, is_shopkeeper_is_selling: bool=False, discount: float=1) -> int:
        """
        Return the price of the given item for given actor.
        NOTE: This function will not handle the change of the price depending on the actor's charm.
        """
        if self.stack_count < 1:
            return 0
        return self.price_of_single_item(is_shopkeeper_is_selling, discount) * self.stack_count

    def remove_self(self):
        super().remove_self()
        if self.indestructible:
            print(f"DEBUG::{self.name} IS INDESTRUCTIBLE. ITEM.REMOVE_SELF() IS NULLIFIED.")
            return None

        if self.parent:
            if self.equipable: # If the item can be equipped, try to remove it from its wearer. (if there is any)
                if self.item_state.equipped_region:
                    self.parent.parent.equipments.remove_equipment(region=self.item_state.equipped_region, forced=True, play_fx=False)
            self.parent.delete_item_from_inv(self)

    def initialize_BUC(self, use_custom: Optional[dict] = None) -> None:
        if use_custom:
            using = use_custom
        else:
            using = self.initial_BUC
        buc = random.choices(list(using.keys()), list(using.values()), k=1)[0]
        if not self.item_state.change_buc(BUC=buc):
            print(f"DEBUG::Cannot initialize buc of {self.entity_id} as given value {buc}.")

    def initialize_upgrade(self, use_custom: Optional[dict] = None) -> None:
        if use_custom:
            using = use_custom
        else:
            using = self.initial_upgrades
        if self.equipable:
            upgrade = random.choices(list(using.keys()), list(using.values()), k=1)[0]
            self.equipable.upgrade_this(amount=upgrade)

    def initialize_self(self):
        """
        Sets initial BUC, identification status, etc.
        This method is called from spawn().
        """
        self.item_state.parent = self
        if self.should_initialize:
            self.initialize_BUC(use_custom=None)
            self.initialize_upgrade(use_custom=None)

    def copy(self, gamemap: GameMap, exact_copy: bool=False, parent: Optional[Inventory]=None):
        """
        Item initialized at super.copy()
        """
        clone = super().copy(gamemap=gamemap, exact_copy=exact_copy)
        clone.parent = parent
        return clone

    def spawn(self: T, gamemap: GameMap, x: int, y: int, exact_copy: bool=False, apply_physics:bool=True) -> T:
        """
        Spawn a copy of this instance at the given location.
        Item cannot be spawned with parent(Inventory)
        """
        clone = super().spawn(gamemap, x, y, exact_copy, apply_physics=apply_physics)
        if self.is_artifact:
            if self.engine.item_manager.check_artifact_id_generated(self.entity_id):
                print(f"WARNING::Spawning item {self.entity_id} which cannot be naturally spawned. This might not be an error. - Item.spawn()")  # Does not stop the spawning
            self.engine.item_manager.disable_artifact_from_spawning(self.entity_id)
        return clone

    def update_component_parent_to(self, item: Item) -> None:
        if self.equipable:
            self.equipable.parent = item
        if self.edible:
            self.edible.parent = item
        if self.throwable:
            self.throwable.parent = item
        if self.readable:
            self.readable.parent = item
        if self.quaffable:
            self.quaffable.parent = item
        if self.equipable:
            self.equipable.parent = item
        if self.edible:
            self.edible.parent = item
        if self.throwable:
            self.throwable.parent = item
        if self.readable:
            self.readable.parent = item
        if self.quaffable:
            self.quaffable.parent = item

    def collided_with_fire(self):
        will_catch_fire = random.random()
        if will_catch_fire < self.flammable:
            self.item_state.is_burning = True

    def collided_with_acid(self):
        will_corrode = random.random()
        owner = None
        if self.parent:
            if self.parent.parent:
                owner = self.parent.parent
        if will_corrode < self.corrodible:
            self.item_state.corrode(owner, amount=1)

    def collided_with_water(self):
        will_corrode = random.random() * 0.1 # its less likely to corrode in water than acid
        owner = None
        if self.parent:
            if self.parent.parent:
                owner = self.parent.parent
        if will_corrode < self.corrodible and self.corrodible >= 0.1: # only corrodes when corrodible 0.08 or higher
            self.item_state.corrode(owner, amount=1)

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
        semiactor_type_desc: str = "",
        entity_desc: str = "",
        semiactor_quote: str = "",
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
        trigger_bump: bool = True,
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
            trigger_bump:
                If True, player will open NonHostileInputHandler instead of moving onto this semiactor.
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

        self.semiactor_type_desc = semiactor_type_desc
        self.semiactor_quote = semiactor_quote

        self.lifetime = 0
        self.do_action = do_action

        if not do_action:
            self.action_point = 0
            self.action_speed = 0

        self.safe_to_move = safe_to_move
        self.trigger_bump = trigger_bump
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

    def copy(self, gamemap: GameMap, exact_copy: bool=False, lifetime: int=3) -> SemiActor:
        clone = super().copy(gamemap=gamemap, exact_copy=exact_copy)
        clone.lifetime = lifetime
        return clone
        
    def spawn(self: T, gamemap: GameMap, x: int, y: int, lifetime: int=3, apply_physics:bool=True) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = super().spawn(gamemap, x, y, apply_physics=apply_physics)
        clone.lifetime = lifetime
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
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
from tiles import TileUtil

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
    from actions import Action

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

    def get_possible_bump_action_keywords(self, actor: Actor) -> List[str]:
        """Returns the amount of different bump actions this entity can do."""
        allactions = ("move", "swap", "force_attack", "attack", "takeout", "putin", "open", "close", "unlock", "break")
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
        from chest_factories import ChestSemiactor
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
            self.engine.event_handler = ChestTakeEventHandler(self.storage)
            return None  # TODO Turn should pass
        elif keyword == "putin":
            self.engine.event_handler = ChestPutEventHandler(actor.inventory, self.storage)
            return None  # TODO Turn should pass
        elif keyword == "open":
            return actions.DoorOpenAction(actor, dx, dy)
        elif keyword == "close":
            return actions.DoorCloseAction(actor, dx, dy)
        elif keyword == "unlock":
            return actions.DoorUnlockAction(actor, dx, dy)
        elif keyword == "break":
            return actions.DoorBreakAction(actor, dx, dy)
        raise Exception(f"FATAL ERROR::Cannot find the given keyword {keyword}")

    def environmental_hole(self):
        """Handle entity on a hole tile."""
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "hole":
            new_gamemap = self.engine.world.get_map(depth=self.gamemap.depth + 1)
            x, y = new_gamemap.get_random_tile(should_no_entity=True, should_walkable=True, should_safe_to_walk=True,
                                               should_not_protected=True)
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
            if semiactor_collided.walkable:
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

    def remove_self(self) -> None:
        if self.indestructible:
            print(f"DEBUG::{self.name} IS INDESTRUCTIBLE. ENTITY.REMOVE_SELF() IS NULLIFIED.")
            return None
        elif self.gamemap:
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

    def copy(self, gamemap: GameMap) -> Entity:
        clone = copy.deepcopy(self)
        clone.gamemap = gamemap
        return clone

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a new copy of this instance at the given location.
        NOTE: So technically you are not spawning THIS SPECIFIC ENTITY, instead you are copying this entity and spawning the copy."""
        clone = self.copy(gamemap)
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
        ai_cls: Optional[Type[BaseAI]],
        status: Status,
        actor_state: ActorState,
        inventory: Inventory,
        ability_inventory: AbilityInventory,
        equipments: Equipments,
        initial_items: Tuple[Dict] = None,
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
            initial_items:
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

        if initial_items == None:
            self.initial_items = []
        else:
            self.initial_items = list(initial_items)

        if initial_abilities == None:
            self.initial_abilities = []
        else:
            self.initial_abilities = list(initial_abilities)

        if initial_equipments == None:
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

    def discount_value(self) -> float:
        """A discout value for this actor.
        The higher the actor's charm is, the higher this value gets.
        If the actor is buying, subtract this value from 1.
        Return:
            float range between -0.4 to 0.4."""
        return max(-0.4, min(0.4, (self.status.changed_status["charm"] / 15) - 1) * 0.75)

    def drop_all_items(self) -> None:
        """Drop all items this status' parent owns. Mainly used during die()"""
        drop_list = []
        for item in self.inventory.items:
            drop_list.append(item)
        for drop_item in drop_list:
            self.inventory.drop(item=drop_item, show_msg=False)

    def drop_corpse(self) -> None:
        if self.edible:  # if edible is None, no corpse is spawned.
            import item_factories
            new_corpse = item_factories.corpse.spawn(self.gamemap, self.x, self.y)
            new_corpse.weight = max(self.weight * max(0.2, random.random()*0.9), 0.001)
            new_corpse.change_name(self.name + " 시체")
            new_corpse.edible = self.edible  # copy edible value from parent
            new_corpse.edible.parent = new_corpse

    def die(self, cause:str="low_hp", drop_item: bool=True, drop_edible: bool=True):
        if drop_item:
            self.drop_all_items()
        if drop_edible:
            self.drop_corpse()
        self.status.death(cause)

    def float(self, start_floating: bool) -> None:
        super().float(start_floating)
        if start_floating:
            self.is_on_air = True
        else:
            # Actor can go down only when actor is not flying and not levitating.
            if self.actor_state.is_flying == False and self.actor_state.is_levitating != [0, 0]:
                self.is_on_air = False

    def remove_self(self):
        super().remove_self()

    def environmental_pit(self):
        """Handles when actor is in pit"""
        # Deep pit
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "deep_pit":
            if not self.actor_state.is_in_deep_pit:
                pass  # TODO: Add an effect that happens only right after when the actor fell into the pit

            self.actor_state.is_in_deep_pit = True  # TODO : action에서 deep pit 처리
        else:
            self.actor_state.is_in_deep_pit = False

        # Shallow pit
        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "shallow_pit":
            self.actor_state.is_in_shallow_pit = True
        else:
            self.actor_state.is_in_shallow_pit = False

    def environmental_water(self):
        """Handles when actor is in water"""
        self.actor_state.was_submerged = self.actor_state.is_submerged

        if self.gamemap.tiles[self.x, self.y]["tile_id"] == "deep_water":
            self.actor_state.is_submerged = True
            if self.actor_state.size < 6: #TODO Size
                self.actor_state.is_underwater = True
        elif self.gamemap.tiles[self.x, self.y]["tile_id"] == "shallow_water":
            self.actor_state.is_submerged = True
            if self.actor_state.size <= 1: #TODO Size
                self.actor_state.is_underwater = True
        else:
            self.actor_state.is_submerged = False
            self.actor_state.is_underwater = False
            self.actor_state.apply_drowning([0, 0])
            if not self.actor_state.is_underwater:
                self.status.remove_bonus("submerged_bonus", ignore_warning=True)

        # Immediate debuff
        if self.actor_state.is_submerged:
            self.actor_state.actor_submerged()

    def do_environmental_effects(self):
        """
        Overriding the entity method.
        """
        ### Call parent function ###
        super().do_environmental_effects()

        ### A. Tile related ###
        if not self.is_on_air:
            # Prevent any error (Mainly prevent flying actor not being on air when first initialized.)
            if self.actor_state.is_flying or self.actor_state.is_levitating != [0, 0]:
                self.float(True)

            self.environmental_pit()
            self.environmental_water()
            self.do_special_environmental_effect() # Do action on tile
            
    def gain_action_point(self):
        """
        Gain action points every game time.
        This method is overriden.
        """
        self.action_point = min(180, self.action_point + self.actor_speed)

    def initialize_actor_possesion(self, args) -> Item:
        """Initialize items that the actor owns.
        a single args represents a single item."""
        temp = args["item"].copy(gamemap=self.gamemap)
        temp.stack_count = random.randint(args["count"][0], args["count"][1])
        temp.parent = self.inventory

        if args["BUC"] != None or "BUC" not in args.keys():
            temp.initialize_BUC(use_custom=args["BUC"])
        if args["upgrade"] != None and temp.equipable or "upgrade" not in args.keys():
            temp.equipable.reset_upgrade()
            temp.initialize_upgrade(use_custom=args["upgrade"])
        self.inventory.add_item(temp)
        return temp

    def initialize_actor(self):
        """
        Sets initial items, abilities, and equipments of this actor.
        This method is called from spawn().
        """
        if self.ai:
            self.ai.init_vision()

        for args in self.initial_items:
            if random.random() <= args["chance"]:
                self.initialize_actor_possesion(args)
        for args in self.initial_equipments:
            if random.random() <= args["chance"]:
                item = self.initialize_actor_possesion(args)
                self.equipments.equip_equipment(item=item, forced=True)
        for ability in self.initial_abilities:
            if random.random() <= ability[1]:
                self.ability_inventory.add_ability(ability[0].copy())

    def copy(self, gamemap: GameMap):
        clone = super().copy(gamemap=gamemap)
        clone.initialize_actor() # must be called after entity.copy(gamemap)
        return clone

    def spawn(self: T, gamemap: GameMap, x: int, y: int, is_active: bool=False) -> T:
        """
        Spawn a copy of this instance at the given location.
        """
        clone = super().spawn(gamemap, x, y)
        if is_active and clone.ai:
            clone.ai.activate()
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
                self.engine.message_log.add_message(f"당신의 몸에 불이 붙었다!",target=self, fg=color.player_bad)
            else:
                self.engine.message_log.add_message(f"{self.name}에게 불이 붙었다!", target=self, fg=color.enemy_unique)
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
        should_randomize: bool = False,
        char: str = "?",
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Tuple[int, int, int] = None,
        name: str = "<Unnamed>",
        entity_id: str = "<Undefined id>",
        item_type_desc: str = "",
        entity_desc: str = "<Undefined description>",
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
        equipable: Equipable = None,
        edible: Edible = None,
        lockpickable: Tuple[float, float] = (0, 0),
        counter_at_front: bool = False,
        initial_BUC=None,
        initial_identified: float = 0,
        initial_upgrades: List = None, #TODO
    ):
        """
        Args:
            initial_BUC:
                Chance of this item spawning with certain BUC status.
                { BUC number : chance of having that BUC number indicated as weight, ...)
                e.g. { 1: 3, 0: 5, -1: 1 } -> Has highest chance of spawing as uncursed.
            initial_identified:
                Chance of this item spawning as already identified. (semi-identified)
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

        if initial_BUC is None:
            self.initial_BUC = {1: 1, 0: 8, -1: 2} # Default not-cursed
        else:
            self.initial_BUC = initial_BUC
        self.initial_identified = initial_identified

        if initial_upgrades == None:
            self.initial_upgrades = {-4:1, -3:2, -2:3, -1:6, 0:15, 1:7, 2:4, 3:2, 4:1}
        else:
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

    def price_of_single_item(self, is_shopkeeper_is_selling: bool, discount: float=1) -> int:
        """
        Return the price of the given item for given actor.
        NOTE: This function will not handle the change of the price depending on the actor's charm.
        NOTE: If dicount value is over 1, the function will return an overrated price for the item.
        """
        if self.item_type.value == InventoryOrder.GEM.value:
            if self.item_state.is_identified == 0:
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
                    self.parent.parent.equipments.remove_equipment(region=self.item_state.equipped_region, forced=True)
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

    def initialize_item(self):
        """
        Sets initial BUC, identification status, etc.
        This method is called from spawn().
        """
        if random.random() <= self.initial_identified:
            self.item_state.identify_self()
        else:
            self.item_state.unidentify_self()

        self.item_state.parent = self
        self.initialize_BUC(use_custom=None)
        self.initialize_upgrade(use_custom=None)

    def copy(self, gamemap: GameMap, parent: Optional[Inventory]=None):
        clone = super().copy(gamemap=gamemap)
        clone.parent = parent
        clone.initialize_item() # must be called after entity.copy(gamemap) so that gamemap is set
        return clone

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """
        Spawn a copy of this instance at the given location.
        """
        clone = super().spawn(gamemap, x, y)
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
        entity_desc: str = "<Undefined description>",
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

    def copy(self, gamemap: GameMap, lifetime: int=3) -> SemiActor:
        clone = super(SemiActor, self).copy(gamemap)
        clone.lifetime = lifetime
        return clone
        
    def spawn(self: T, gamemap: GameMap, x: int, y: int, lifetime: int=3) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = super().spawn(gamemap, x, y)
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
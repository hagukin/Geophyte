from __future__ import annotations
from components.inventory import Inventory
from typing import Callable, Optional, Tuple, TYPE_CHECKING
from order import InventoryOrder
from actions import (
    Action,
    BumpAction,
    PickupAction,
    WaitAction,
    DoorCloseAction,
    DropItem,
    SplitItem,
    EquipItem,
    UnequipItem,
    DescendAction,
    AscendAction,
    PlaceSwapAction,
)
from loader.data_loader import save_game

import tcod
import time
import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Item
    from ability import Ability


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        return self.handle_action(self.dispatch(event))

    def handle_action(self, action: Optional[Action]) -> bool:
        """
        Handle actions returned from event methods.
        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.

        return True

    def get_mouse_dir(self) -> None:
        dx = self.engine.mouse_location[0] - self.engine.player.x 
        dy = self.engine.mouse_location[1] - self.engine.player.y
        if dx == 0: dir_x = 0
        else: dir_x = int(dx / abs(dx))
        if dy == 0: dir_y = 0
        else: dir_y = int(dy / abs(dy))

        self.engine.mouse_dir = dir_x, dir_y

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        temp_x, temp_y = self.engine.camera.get_absolute_coordinate(relative_x=event.tile.x, relative_y=event.tile.y)
        if self.engine.camera.in_bounds(temp_x, temp_y):
            self.engine.mouse_location = temp_x, temp_y
            self.get_mouse_dir()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> None:
        # Get the x, y coordinates of the mouse cursor.
        mouse_map_x, mouse_map_y = self.engine.camera.get_absolute_coordinate(relative_x=event.tile.x, relative_y=event.tile.y)

        # Check if the mouse is in bounds
        if not self.engine.camera.in_bounds(abs_x=mouse_map_x, abs_y=mouse_map_y):
            return None
        
        # LClick
        if event.button == tcod.event.BUTTON_LEFT:
            dx = mouse_map_x - self.engine.player.x
            dy = mouse_map_y - self.engine.player.y

            if abs(dx) <= 1 and abs(dy) <= 1:# If clicked nearby
                self.engine.player_dir = (dx, dy)
            else: 
                self.engine.set_player_path(dest_x=mouse_map_x, dest_y=mouse_map_y)

        # This will not advacne a turn
        return None

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def handle_action(self, action: Optional[Action]) -> bool:
        """Return to the main event handler when a valid action was performed."""
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[Action]:
        """
        Called when the user is trying to exit or cancel an action.
        By default this returns to the main event handler.
        """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


class SaveInputHandler(AskUserEventHandler):

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.message_log.add_message(f"Do you really want to save current game? (Y/N)", color.lime, stack=False, show_once=True)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        engine = self.engine

        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            self.engine.event_handler = MainGameEventHandler(self.engine)
            self.engine.message_log.add_message(f"Game saved.", color.lime, stack=False)
            save_game(player=player, engine=engine)
        else:
            self.engine.message_log.add_message(f"Saving canceled.", color.lime, stack=False)
        return super().ev_keydown(event)


class AbilityEventHandler(AskUserEventHandler):
    """
    This handler lets the user select an ability to use / cast.
    What happens then depends on the subclass.
    """

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.TITLE = "Abilities"

    def on_render(self, console: tcod.Console) -> None:
        """
        Render an ability inventory menu, which displays the abilities in the inventory, and the alphabet key to select them.
        """
        super().on_render(console)
        number_of_abilities_in_inventory = len(self.engine.player.ability_inventory.abilities)

        height = number_of_abilities_in_inventory + 2
        if height <= 3:
            height = 3

        x = 0
        y = 0
        x_space = 5 # for each sides
        y_space = 3
        width = self.engine.config["screen_width"] - (x_space * 2)

        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height + 1, # 2 extra lines for bottom
            title=self.TITLE,
            clear=True,
            fg=color.gui_inventory_fg,
            bg=color.gui_inventory_bg,
        )

        if number_of_abilities_in_inventory > 0:
            i = -1

            for ability_key, ability in self.engine.player.ability_inventory.ability_hotkeys.items():
                if ability == None:
                    continue
                i += 1
                ability_text = f"({ability_key}) {ability.name}"
                ability_text_color = color.white

                # Assign color of its type
                # TODO
                
                # Message log
                console.print(x + x_space + 1, y + i + y_space + 1, ability_text, fg=ability_text_color)
        else:
            console.print(x + x_space + 1, y + y_space + 1, "(Nothing)", color.gray)

        console.print(x + x_space + 1, height + 3, "\"/\"key: - Sort Inventory", color.gui_inventory_fg)


    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player

        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None

        # Sort inventory
        if event.sym == tcod.event.K_SLASH or event.sym == tcod.event.K_KP_DIVIDE: # Sort Inventory by type
            player.inventory.sort_inventory()
            return None
        elif event.sym == tcod.event.K_ESCAPE: # Escape inventory window
            return super().ev_keydown(event)

        # Check modifier
        if event.mod & tcod.event.K_LSHIFT:
            alphabet = {
                tcod.event.K_a:"A",tcod.event.K_b:"B",tcod.event.K_c:"C",tcod.event.K_d:"D",tcod.event.K_e:"E",tcod.event.K_f:"F",tcod.event.K_g:"G",tcod.event.K_h:"H",tcod.event.K_i:"I",tcod.event.K_j:"J",tcod.event.K_k:"K",tcod.event.K_l:"L",tcod.event.K_m:"M",tcod.event.K_n:"N",tcod.event.K_o:"O",tcod.event.K_p:"P",tcod.event.K_q:"Q",tcod.event.K_r:"R",tcod.event.K_s:"S",tcod.event.K_t:"T",tcod.event.K_u:"U",tcod.event.K_v:"V",tcod.event.K_w:"W",tcod.event.K_x:"X",tcod.event.K_y:"Y",tcod.event.K_z:"Z",
            }
        else:
            alphabet = {
                tcod.event.K_a:"a",tcod.event.K_b:"b",tcod.event.K_c:"c",tcod.event.K_d:"d",tcod.event.K_e:"e",tcod.event.K_f:"f",tcod.event.K_g:"g",tcod.event.K_h:"h",tcod.event.K_i:"i",tcod.event.K_j:"j",tcod.event.K_k:"k",tcod.event.K_l:"l",tcod.event.K_m:"m",tcod.event.K_n:"n",tcod.event.K_o:"o",tcod.event.K_p:"p",tcod.event.K_q:"q",tcod.event.K_r:"r",tcod.event.K_s:"s",tcod.event.K_t:"t",tcod.event.K_u:"u",tcod.event.K_v:"v",tcod.event.K_w:"w",tcod.event.K_x:"x",tcod.event.K_y:"y",tcod.event.K_z:"z",
            }

        # Select ability to cast/use
        try:
            key = alphabet[event.sym]
            selected_ability = player.ability_inventory.ability_hotkeys[key]
            return self.on_ability_selected(selected_ability)
        except Exception as e:
            print(e)
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            return None

    def on_ability_selected(self, ability: Ability) -> Optional[Action]:
        """Called when the user selects a valid ability."""
        raise NotImplementedError()


class AbilityActivateHandler(AbilityEventHandler):
    """Handle using an ability called from inventory."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.TITLE = "Abilities"

    def on_ability_selected(self, ability: Ability) -> Optional[Action]:
        """Return the action for the selected item."""
        self.engine.event_handler = AbilityActionSelectHandler(self.engine, ability)
        return None


class AbilityActionSelectHandler(AskUserEventHandler):
    """Handle choosing the action for selected ability."""

    def __init__(self, engine, ability: Ability):
        super().__init__(engine)
        self.ability = ability
        self.TITLE = f"{self.ability.name}"

    def on_render(self, console: tcod.Console) -> None:
        """
        Renders an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(console)

        self.possible_actions = []
        self.possible_keys = []

        if self.ability.activatable:
            self.possible_actions.append("cast/conduct")
            self.possible_keys.append(tcod.event.K_c)

        # get ability description height
        desc_height = self.ability.ability_desc.count('\n') + 1
        desc_width = len(self.ability.ability_desc)

        number_of_possible_actions = len(self.possible_actions)

        height = number_of_possible_actions + desc_height + 3
        if height <= 3:
            height = 3

        x = 0
        y = 0
        x_space = 5 # per side
        y_space = 3

        width = self.engine.config["screen_width"] - (x_space * 2)

        # draw frame
        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=color.gui_action_fg,
            bg=color.gui_inventory_bg,
        )

        # print ability description
        console.print(x + x_space + 1, y + y_space + 1, self.ability.ability_desc, fg=color.gui_item_description)

        # print possible actions
        for i, action in enumerate(self.possible_actions):
            
            if action == "cast/conduct":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(c) Cast / Conduct", fg=color.gui_item_action)
            else:
                console.print(x + x_space + 1, y + desc_height + 2 + y_space, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym

        if key in self.possible_keys:
            if key == tcod.event.K_c:
                return self.ability.activatable.get_action(self.engine.player)
        elif key == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None


class StorageSelectEventHandler(AskUserEventHandler):
    def __init__(
            self, 
            engine: Engine, 
            inventory_component: Inventory, 
            show_only_types: Tuple(InventoryOrder)=None, 
            show_only_status: Tuple(str) = None,
            show_if_satisfy_both: bool = True,
            ):
        """
        Args:
            inventory_component:
                component you are trying to use(open)
            show_only_types:
                Tuple that contains enums. The input handler will show only the given types of items
                If its set to None, show every type of items.
            show_only_status:
                Tuple that contains strings that indicate status.
                If its set to None, show every type of items.
                "full-identified-blessed"
                "semi-identified-uncursed"
                "unidentified-cursed"
                "semi-identified-all" -> Show all semi-identified
                "unidentified-all" -> Show all unidentified
            show_if_satisfy_both:
                show item only if both types and status is satisfied.
                if False, show items if they satisfy either one.
        """
        super().__init__(engine)
        self.inventory_component = inventory_component 
        self.show_only_types = show_only_types
        self.show_only_status = show_only_status
        self.show_if_satisfy_both = show_if_satisfy_both
        if hasattr(self.inventory_component.parent, "name"):
            self.TITLE = f"{self.inventory_component.parent.name}"
        else:
            self.TITLE = ""

    def check_should_render_item(self, item: Item) -> bool:
        if self.show_if_satisfy_both:
            if (self.check_should_render_type(item) and self.check_should_render_status(item)):
                return True
        else:
            if (self.check_should_render_type(item) or self.check_should_render_status(item)):
                return True

    def check_should_render_type(self, item: Item) -> bool:
        """
        Return whether this input handler should render or take input of given item.
        """
        if self.show_only_types: # If there is show_only_types value, display only the given types of items
            if item.item_type in self.show_only_types:
                return True
            else:
                return False
        else:
            return True

    def check_should_render_status(self, item: Item) -> bool:
        """
        Return whether this input handler should render or take input of given item.
        """
        if self.show_only_status:
            # Check BUC
            pair = {0:"uncursed", -1:"cursed", 1:"blessed"}
            buc = item.item_state.BUC

            # Find if string contains substring
            for valid_string in self.show_only_status:

                # Check identification
                if item.item_state.check_if_semi_identified() and ("semi-identified" in valid_string):
                    # Check BUC
                    if pair[buc] in valid_string:
                        return True
                    elif "all" in valid_string:
                        return True
                elif item.item_state.check_if_full_identified() and ("full-identified" in valid_string):
                    # Check BUC
                    if pair[buc] in valid_string:
                        return True
                    elif "all" in valid_string:
                        return True
                elif (not item.item_state.check_if_semi_identified()) and ("unidentified" in valid_string):
                    # Check BUC
                    if pair[buc] in valid_string:
                        return True
                    elif "all" in valid_string:
                        return True

            return False
        else:
            return True

    def on_render(self, console: tcod.Console) -> None:
        return super().on_render(console)


class StorageSelectSingleEventHandler(StorageSelectEventHandler):
    """
    Inherit this class if the action requires selecting one single itme.
    e.g. Item inventory
    """
    def on_render(self, console: tcod.Console) -> None:
        """
        Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        """
        super().on_render(console)

        # Get valid item number
        number_of_valid_items = 0
        for item in self.inventory_component.items:
            if self.check_should_render_item(item):
                number_of_valid_items += 1

        height = number_of_valid_items + 2
        if height <= 3:
            height = 3

        x = 0
        y = 0
        x_space = 5 # per side
        y_space = 3
        width = self.engine.config["screen_width"] - (x_space * 2)

        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height + 1, # 2 extra line for "press slash to sort inventory"
            title=self.TITLE,
            clear=True,
            fg=color.gui_inventory_fg,
            bg=color.gui_inventory_bg,
        )

        if number_of_valid_items > 0:
            i = -1

            for item_key, item in self.inventory_component.item_hotkeys.items():
                if item == None:
                    continue

                if not self.check_should_render_item(item):
                    continue
                
                i += 1
                item_text = f"({item_key}) "
                if item.item_state.check_if_full_identified(): # Display BUC only if fully identified
                    if item.item_state.BUC == 0:
                        item_text += "uncursed "
                    if item.item_state.BUC >= 1:
                        item_text += "blessed "
                    if item.item_state.BUC <= -1:
                        item_text += "cursed "

                item_text += f"{item.name}"
                item_text_color = None
                item_damage_text = ""
                item_state_text = ""
                item_equip_text = ""

                # Assign color of its type
                if item.item_type == InventoryOrder.POTION:
                    item_text_color = color.gui_potion_name
                elif item.item_type == InventoryOrder.SCROLL:
                    item_text_color = color.gui_scroll_name
                elif item.item_type == InventoryOrder.ARMOR:
                    item_text_color = color.gui_armor_name
                
                # Display item counts if it is greater than 1
                if item.stack_count > 1:
                    item_text += f" (x{item.stack_count})"
                    
                # Display damage status if their is one
                if item.item_state.burntness == 1:
                    item_damage_text += " (partly burnt)"
                elif item.item_state.burntness == 2:
                    item_damage_text += " (severely burnt)"
                    
                # Display special states if it is true
                if item.item_state.is_burning:
                    item_state_text += " [on fire]"

                # Display equip info if it is true(if value isn't None)
                if item.item_state.is_equipped:
                    item_equip_text += f" [equipped on {item.item_state.is_equipped}]"

                # Print
                console.print(x + x_space + 1, y + i + y_space + 1, item_text, fg=item_text_color)
                console.print(x + x_space + 1 + len(item_text), y + i + y_space + 1, item_damage_text, fg=color.gray)
                console.print(x + x_space + 1 + len(item_text) + len(item_damage_text), y + i + y_space + 1, item_equip_text, fg=color.gui_item_equip)
                console.print(x + x_space + 1 + len(item_text) + len(item_damage_text) + len(item_equip_text), y + i + y_space + 1, item_state_text, fg=color.gui_item_state)
        else:
            console.print(x + x_space + 1, y + y_space + 1, "(Empty)", color.gray)

        console.print(x + x_space + 1, height + 4, "\"/\"key: - Sort Items", color.gui_inventory_fg)
        
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None

        # Sort inventory
        if event.sym == tcod.event.K_SLASH or event.sym == tcod.event.K_KP_DIVIDE: # Sort Inventory by type
            self.inventory_component.sort_inventory()
            return None
        elif event.sym == tcod.event.K_ESCAPE: # Escape inventory window
            return super().ev_keydown(event)
        elif event.sym == tcod.event.K_KP_ENTER or event.sym == tcod.event.K_RETURN: # Confirm choices
            return self.choice_confirmed()

        # Check modifier
        if event.mod & tcod.event.K_LSHIFT:
            alphabet = {
                tcod.event.K_a:"A",tcod.event.K_b:"B",tcod.event.K_c:"C",tcod.event.K_d:"D",tcod.event.K_e:"E",tcod.event.K_f:"F",tcod.event.K_g:"G",tcod.event.K_h:"H",tcod.event.K_i:"I",tcod.event.K_j:"J",tcod.event.K_k:"K",tcod.event.K_l:"L",tcod.event.K_m:"M",tcod.event.K_n:"N",tcod.event.K_o:"O",tcod.event.K_p:"P",tcod.event.K_q:"Q",tcod.event.K_r:"R",tcod.event.K_s:"S",tcod.event.K_t:"T",tcod.event.K_u:"U",tcod.event.K_v:"V",tcod.event.K_w:"W",tcod.event.K_x:"X",tcod.event.K_y:"Y",tcod.event.K_z:"Z",
            }
        else:
            alphabet = {
                tcod.event.K_a:"a",tcod.event.K_b:"b",tcod.event.K_c:"c",tcod.event.K_d:"d",tcod.event.K_e:"e",tcod.event.K_f:"f",tcod.event.K_g:"g",tcod.event.K_h:"h",tcod.event.K_i:"i",tcod.event.K_j:"j",tcod.event.K_k:"k",tcod.event.K_l:"l",tcod.event.K_m:"m",tcod.event.K_n:"n",tcod.event.K_o:"o",tcod.event.K_p:"p",tcod.event.K_q:"q",tcod.event.K_r:"r",tcod.event.K_s:"s",tcod.event.K_t:"t",tcod.event.K_u:"u",tcod.event.K_v:"v",tcod.event.K_w:"w",tcod.event.K_x:"x",tcod.event.K_y:"y",tcod.event.K_z:"z",
            }

        # Choose item
        try:
            key = alphabet[event.sym]
            selected_item = self.inventory_component.item_hotkeys[key]
            if not self.check_should_render_item(selected_item):
                raise Exception()
            if selected_item:
                return self.on_item_selected(selected_item)
            else:
                self.engine.message_log.add_message(f"Invalid entry.", color.invalid)
                return None
        except:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            return None

    def on_item_selected(self, item: Item) -> Optional[Action]:
        raise NotImplementedError()


class InventoryChooseItemAndCallbackHandler(StorageSelectSingleEventHandler):
    """
    Choose one item from inventory(or any inv component)
    and call given callback function.
    e.g. reading scroll of enchantment -> choosing an item to upgrade
    """
    def __init__(
            self, 
            engine: Engine, 
            inventory_component: Inventory, 
            callback: Callable, 
            show_only_types: Tuple(InventoryOrder)=None, 
            show_only_status: Tuple(str) = None, 
            show_if_satisfy_both: bool = True,
        ):
        super().__init__(engine, inventory_component, show_only_types, show_only_status, show_if_satisfy_both)
        self.TITLE = "Inventory"
        self.selected_item = None
        self.callback = callback
    

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Return the action for the selected item."""
        self.selected_item = item
        return self.callback(self.selected_item)


class InventoryEventHandler(StorageSelectSingleEventHandler):

    def __init__(
            self, 
            engine: Engine, 
            inventory_component: Inventory,
            show_only_types: Tuple(InventoryOrder)=None, 
            show_only_status: Tuple(str) = None, 
            show_if_satisfy_both: bool = True,
        ):
        super().__init__(engine, inventory_component, show_only_types, show_only_status, show_if_satisfy_both)
        self.TITLE = "Inventory"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Return the action for the selected item."""
        self.engine.event_handler = InventoryActionSelectHandler(self.engine, item)
        return None
    

class InventoryActionSelectHandler(AskUserEventHandler):
    """Handle choosing the action for selected item."""

    def __init__(self, engine, item):
        super().__init__(engine)
        self.item = item
        if item.stack_count > 1:
            self.TITLE = f"{self.item.name} (x{self.item.stack_count})"
        else:
            self.TITLE = f"{self.item.name}"

    def on_render(self, console: tcod.Console) -> None:
        """
        Render an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(console)

        self.possible_actions = []
        self.possible_keys = []

        if self.item.readable:
            self.possible_actions.append("read")
            self.possible_keys.append(tcod.event.K_r)
        if self.item.quaffable:
            self.possible_actions.append("quaff")
            self.possible_keys.append(tcod.event.K_q)
        if self.item.edible:
            self.possible_actions.append("eat")
            self.possible_keys.append(tcod.event.K_a)
        if self.item.equipable and self.item.item_state.is_equipped == None:
            self.possible_actions.append("equip")
            self.possible_keys.append(tcod.event.K_e)
        if self.item.equipable and self.item.item_state.is_equipped != None:
            self.possible_actions.append("unequip")
            self.possible_keys.append(tcod.event.K_u)
        if self.item.stackable and self.item.stack_count > 1:
            self.possible_actions.append("split")
            self.possible_keys.append(tcod.event.K_s)
        if self.item.throwable:
            self.possible_actions.append("throw")
            self.possible_keys.append(tcod.event.K_t)
        if self.item.droppable:
            self.possible_actions.append("drop")
            self.possible_keys.append(tcod.event.K_d)

        # get item description height
        desc_height = self.item.entity_desc.count('\n') + 1
        desc_width = len(self.item.entity_desc)

        number_of_possible_actions = len(self.possible_actions)

        height = number_of_possible_actions + desc_height + 3
        if height <= 3:
            height = 3

        x = 0
        y = 0
        x_space = 5 # per side
        y_space = 3

        width = self.engine.config["screen_width"] - (x_space * 2)

        # draw frame
        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=color.gui_action_fg,
            bg=color.gui_inventory_bg,
        )

        # print item description
        console.print(x + x_space + 1, y + y_space + 1, self.item.entity_desc, fg=color.gui_item_description)

        # print possible actions
        for i, action in enumerate(self.possible_actions):
            
            if action == "read":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(r) Read", fg=color.gui_item_action)
            elif action == "quaff":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(q) Quaff", fg=color.gui_item_action)
            elif action == "eat":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(a) Eat", fg=color.gui_item_action)
            elif action == "equip":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(e) Equip", fg=color.gui_item_action)
            elif action == "unequip":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(u) Unequip", fg=color.gui_item_action)
            elif action == "split":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(s) Split", fg=color.gui_item_action)
            elif action == "throw":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(t) Throw", fg=color.gui_item_action)
            elif action == "drop":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(d) Drop", fg=color.gui_item_action)
            else:
                console.print(x + x_space + 1, y + desc_height + 2 + y_space, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym

        if key in self.possible_keys:
            if key == tcod.event.K_r:
                return self.item.readable.get_action(self.engine.player)
            elif key == tcod.event.K_q:
                return self.item.quaffable.get_action(self.engine.player)
            elif key == tcod.event.K_a:
                return self.item.edible.get_action(self.engine.player)
            elif key == tcod.event.K_e:
                return EquipItem(self.engine.player, self.item)
            elif key == tcod.event.K_u:
                return UnequipItem(self.engine.player, self.item)
            elif key == tcod.event.K_s:
                self.engine.event_handler = InventorySplitHandler(self.engine, self.item)
            elif key == tcod.event.K_t:
                if self.item.item_state.is_equipped:
                    self.engine.message_log.add_message("You can't throw something you are equipping.", color.invalid)
                    self.engine.event_handler = MainGameEventHandler(self.engine)
                    return None
                return self.item.throwable.get_action(self.engine.player)
            elif key == tcod.event.K_d:
                if self.item.item_state.is_equipped:
                    self.engine.message_log.add_message("You can't drop something you are equipping.", color.invalid)
                    self.engine.event_handler = MainGameEventHandler(self.engine)
                    return None
                return DropItem(self.engine.player, self.item)
        elif key == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None


class InventorySplitHandler(AskUserEventHandler):
    """Handle dropping an inventory item."""

    def __init__(self, engine, item):
        super().__init__(engine)
        self.item = item
        if item.stack_count > 1:
            self.TITLE = f"{self.item.name} (x{self.item.stack_count})"
        else:
            self.TITLE = f"{self.item.name}"
        self.split_amount = 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        # get item description height
        desc_height = self.item.entity_desc.count('\n') + 1

        height = desc_height + 3 + 1 #+1 for split_amount displaying
        if height <= 3:
            height = 3

        x = 0
        y = 0
        x_space = 5 # per side
        y_space = 3
        width = self.engine.config["screen_width"] - (x_space * 2)

        # draw frame
        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=color.gui_action_fg,
            bg=color.gui_inventory_bg,
        )

        # Texts
        console.print(x + x_space + 1, height + 3, "Use +, - key to alter the amount of items you want to split.", color.gui_inventory_fg)
        console.print(x + x_space + 1, y + y_space + 1, self.item.entity_desc, fg=color.gui_item_description)
        console.print(x + x_space + 1, y + y_space + 3, f"{self.split_amount} items chosen.", fg=color.gui_item_description)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym

        if key == tcod.event.K_PLUS or key == tcod.event.K_KP_PLUS:
            if self.split_amount < self.item.stack_count - 1:
                self.split_amount += 1
            else:
                self.engine.message_log.add_message("You have reached the maximum amount.", color.invalid)
        elif key == tcod.event.K_MINUS or key == tcod.event.K_KP_MINUS:
            if self.split_amount > 1:
                self.split_amount -= 1
            else:
                self.engine.message_log.add_message("You must selected more than one.", color.invalid)
        elif key == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None
        elif key == tcod.event.K_RETURN:
            return SplitItem(self.engine.player, self.item, self.split_amount)
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None


class StorageSelectMultipleEventHandler(StorageSelectEventHandler):
    """
    Inherit this class if the action requires selecting multiple items.
    e.g. Opening and taking items from chest

    A child of this class MUST modify the choice_confirmed() method to its use.
    """
    def __init__(
            self, 
            engine: Engine, 
            inventory_component: Inventory, 
            show_only_types: Tuple(InventoryOrder)=None, 
            show_only_status: Tuple(str) = None,
            show_if_satisfy_both: bool = True,
            ):
        super().__init__(engine, inventory_component, show_only_types, show_only_status, show_if_satisfy_both)
        self.selected_items = set()

    def on_render(self, console: tcod.Console) -> None:
        """
        Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        """
        super().on_render(console)
        # Get valid item number
        number_of_valid_items = 0
        for item in self.inventory_component.items:
            if self.check_should_render_item(item):
                number_of_valid_items += 1

        height = number_of_valid_items + 2
        if height <= 3:
            height = 3

        x = 0
        y = 0
        x_space = 5 # per side
        y_space = 3
        width = self.engine.config["screen_width"] - (x_space * 2)

        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height + 1, # 2 extra line for "press slash to sort inventory"
            title=self.TITLE,
            clear=True,
            fg=color.gui_inventory_fg,
            bg=color.gui_inventory_bg,
        )

        if number_of_valid_items > 0:
            i = -1

            for item_key, item in self.inventory_component.item_hotkeys.items():
                if item == None:
                    continue
                i += 1
                item_text = f"({item_key}) "

                if item.item_state.check_if_full_identified(): # Display BUC only if fully identified
                    if item.item_state.BUC == 0:
                        item_text += "uncursed "
                    if item.item_state.BUC >= 1:
                        item_text += "blessed "
                    if item.item_state.BUC <= -1:
                        item_text += "cursed "

                item_text += f"{item.name}"
                item_text_color = None
                item_damage_text = ""
                item_state_text = ""
                item_equip_text = ""

                # Assign color of its type
                if item.item_type == InventoryOrder.POTION:
                    item_text_color = color.gui_potion_name
                elif item.item_type == InventoryOrder.SCROLL:
                    item_text_color = color.gui_scroll_name
                elif item.item_type == InventoryOrder.ARMOR:
                    item_text_color = color.gui_armor_name

                # Change color of the selected items
                if item in self.selected_items:
                    item_text_color = color.gui_selected_item #TODO: Maybe add a short string in front of item name? like (selected)
                
                # Display item counts if it is greater than 1
                if item.stack_count > 1:
                    item_text += f" (x{item.stack_count})"
                    
                # Display damage status if their is one
                if item.item_state.burntness == 1:
                    item_damage_text += " (partly burnt)"
                elif item.item_state.burntness == 2:
                    item_damage_text += " (severely burnt)"
                    
                # Display special states if it is true
                if item.item_state.is_burning:
                    item_state_text += " [on fire]"

                # Display equip info if it is true(if value isn't None)
                if item.item_state.is_equipped:
                    item_equip_text += f" [equipped on {item.item_state.is_equipped}]"

                # Print
                console.print(x + x_space + 1, y + i + y_space + 1, item_text, fg=item_text_color)
                console.print(x + x_space + 1 + len(item_text), y + i + y_space + 1, item_damage_text, fg=color.gray)
                console.print(x + x_space + 1 + len(item_text) + len(item_damage_text), y + i + y_space + 1, item_equip_text, fg=color.gui_item_equip)
                console.print(x + x_space + 1 + len(item_text) + len(item_damage_text) + len(item_equip_text), y + i + y_space + 1, item_state_text, fg=color.gui_item_state)
        else:
            console.print(x + x_space + 1, y + y_space + 1, "(Empty)", color.gray)

        console.print(x + x_space + 1, height + 4, "\"/\"key: - Sort Items | \"Enter\"key - Confirm Choices", color.gui_inventory_fg)

    def choice_confirmed(self):
        raise NotImplementedError()
        
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None

        # Sort inventory
        if event.sym == tcod.event.K_SLASH or event.sym == tcod.event.K_KP_DIVIDE: # Sort Inventory by type
            self.inventory_component.sort_inventory()
            return None
        elif event.sym == tcod.event.K_ESCAPE: # Escape inventory window
            return super().ev_keydown(event)
        elif event.sym == tcod.event.K_KP_ENTER or event.sym == tcod.event.K_RETURN: # Confirm choices
            return self.choice_confirmed()

        # Check modifier
        if event.mod & tcod.event.K_LSHIFT:
            alphabet = {
                tcod.event.K_a:"A",tcod.event.K_b:"B",tcod.event.K_c:"C",tcod.event.K_d:"D",tcod.event.K_e:"E",tcod.event.K_f:"F",tcod.event.K_g:"G",tcod.event.K_h:"H",tcod.event.K_i:"I",tcod.event.K_j:"J",tcod.event.K_k:"K",tcod.event.K_l:"L",tcod.event.K_m:"M",tcod.event.K_n:"N",tcod.event.K_o:"O",tcod.event.K_p:"P",tcod.event.K_q:"Q",tcod.event.K_r:"R",tcod.event.K_s:"S",tcod.event.K_t:"T",tcod.event.K_u:"U",tcod.event.K_v:"V",tcod.event.K_w:"W",tcod.event.K_x:"X",tcod.event.K_y:"Y",tcod.event.K_z:"Z",
            }
        else:
            alphabet = {
                tcod.event.K_a:"a",tcod.event.K_b:"b",tcod.event.K_c:"c",tcod.event.K_d:"d",tcod.event.K_e:"e",tcod.event.K_f:"f",tcod.event.K_g:"g",tcod.event.K_h:"h",tcod.event.K_i:"i",tcod.event.K_j:"j",tcod.event.K_k:"k",tcod.event.K_l:"l",tcod.event.K_m:"m",tcod.event.K_n:"n",tcod.event.K_o:"o",tcod.event.K_p:"p",tcod.event.K_q:"q",tcod.event.K_r:"r",tcod.event.K_s:"s",tcod.event.K_t:"t",tcod.event.K_u:"u",tcod.event.K_v:"v",tcod.event.K_w:"w",tcod.event.K_x:"x",tcod.event.K_y:"y",tcod.event.K_z:"z",
            }

        # Choose item
        try:
            key = alphabet[event.sym]
            selected_item = self.inventory_component.item_hotkeys[key]
            if selected_item:
                self.on_item_selected(selected_item)
                return None
            else:
                self.engine.message_log.add_message(f"Invalid entry.", color.invalid)
                return None
        except:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            return None

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Called when the user selects a valid item."""
        if item in self.selected_items:
            self.selected_items.remove(item)
        else:
            self.selected_items.add(item)


class ChestEventHandler(AskUserEventHandler):
    def __init__(self, engine, inventory_component: Inventory):
        super().__init__(engine)
        self.inventory_component = inventory_component
        if hasattr(self.inventory_component.parent, "name"):
            self.TITLE = f"What do you want to do with {self.inventory_component.parent.name}?"
        else:
            self.TITLE = "What do you want to do?"

    def on_render(self, console: tcod.Console) -> None:
        """
        Render an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(console)

        height = 9 #TODO hard-coded
        if height <= 3:
            height = 3

        x = 0
        y = 0
        x_space = 5 # per side
        y_space = 3
        width = self.engine.config["screen_width"] - (x_space * 2)

        # draw frame
        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=color.gui_action_fg,
            bg=color.gui_inventory_bg,
        )

        # Message log
        console.print(x + x_space + 1, y + y_space + 2, "(t) - Take out something", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 4, "(p) - Put in something", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 6, "(s) - Swap places", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 8, "esc - Cancel", fg=color.white)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        key = event.sym

        if key == tcod.event.K_t:
            self.engine.event_handler = ChestTakeEventHandler(self.engine, self.inventory_component)
            return None
        elif key == tcod.event.K_p:
            self.engine.event_handler = ChestPutEventHandler(self.engine, self.engine.player.inventory, self.inventory_component)
            return None
        elif key == tcod.event.K_s:
            return PlaceSwapAction(self.engine.player, self.inventory_component.parent)
        elif key == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return None


class ChestTakeEventHandler(StorageSelectMultipleEventHandler):    
    def choice_confirmed(self):
        """
        Move the selected items to player's inventory.
        """
        for item in self.selected_items:
            self.inventory_component.remove_item(item, -1) #TODO: Add feature to choose certain amounts
            self.engine.player.inventory.add_item(item)
            
            if item.stack_count <= 1:
                self.engine.message_log.add_message(f"You obtained {item.name}", color.gray)
            else:
                self.engine.message_log.add_message(f"You obtained {item.name} (x{item.stack_count})", color.gray)

        return self.on_exit() #NOTE: game turn is already passed at the moment player opened the chest, so taking something wont cost additional turn.


class ChestPutEventHandler(StorageSelectMultipleEventHandler):
    """Handle putting in an inventory item to a chest."""

    def __init__(self, engine: Engine, actor_inventory_component: Inventory, chest_inventory_component: Inventory):
        super().__init__(engine, actor_inventory_component)
        if hasattr(chest_inventory_component.parent, "name"):
            self.TITLE = f"Select items to put inside of {chest_inventory_component.parent.name}"
        else:
            self.TITLE = "Select items to put in"
        self.actor_inv = actor_inventory_component
        self.chest_inv = chest_inventory_component

    def choice_confirmed(self):
        """
        Move the selected items to chest's storage.
        """
        for item in self.selected_items:
            if item.item_state.is_equipped:
                self.engine.message_log.add_message("You can't move something away while equipping it.", color.invalid)
                continue
            self.actor_inv.remove_item(item, -1) #TODO: Add feature to choose certain amounts
            self.chest_inv.add_item(item)
            
            if item.stack_count > 1:
                self.engine.message_log.add_message(f"You put {item.name} inside the {self.chest_inv.parent.name}", color.gray)
            else:
                self.engine.message_log.add_message(f"You put {item.name} inside the {self.chest_inv.parent.name} (x{item.stack_count})", color.gray)

        return self.on_exit() #NOTE: game turn is already passed at the moment player opened the chest, so putting something in wont cost additional turn.


class InventoryDropHandler(StorageSelectMultipleEventHandler):
    """Handle dropping an inventory item."""

    def __init__(self, engine: Engine, inventory_component: Inventory):
        super().__init__(engine, inventory_component)
        self.TITLE = "Select items to drop"

    def choice_confirmed(self):
        """
        Drop all the selected items.
        """
        for item in self.selected_items:
            if item.item_state.is_equipped:
                self.engine.message_log.add_message("You can't drop something you are equipping.", color.invalid)
                continue
            DropItem(self.engine.player, item).perform()

        self.engine.event_handler = MainGameEventHandler(self.engine)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_relative_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier

            # Clamp the cursor index to the map size.
            x = max(self.engine.camera.xpos, min(x, self.engine.camera.biggest_x - 1))
            y = max(self.engine.camera.ypos, min(y, self.engine.camera.biggest_y - 1))

            self.engine.mouse_location = x, y
            self.get_mouse_dir()

            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """Left click confirms a selection."""
        if self.engine.camera.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*self.engine.camera.get_absolute_coordinate(relative_x=event.tile.x, relative_y=event.tile.y))
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> None:
        """Return to main handler."""
        self.engine.event_handler = MainGameEventHandler(self.engine)


class SelectDirectionHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_relative_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            x = self.engine.player.x
            y = self.engine.player.y
            x += dx
            y += dy

            # Clamp the cursor index to the map size.
            x = max(self.engine.camera.xpos, min(x, self.engine.camera.biggest_x - 1))
            y = max(self.engine.camera.ypos, min(y, self.engine.camera.biggest_y - 1))
            self.engine.mouse_location = x, y
            self.get_mouse_dir()
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """Left click confirms a selection."""
        if self.engine.camera.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*self.engine.camera.get_absolute_coordinate(relative_x=event.tile.x, relative_y=event.tile.y))
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Called when an index is selected."""
        raise NotImplementedError()


class MagicMappingLookHandler(AskUserEventHandler):
    """Lets the player look around using the keyboard."""
    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym == tcod.event.K_ESCAPE:
            return self.on_exit()

    def on_exit(self) -> Optional[Action]:
        """Called when the user is trying to exit or cancel an action."""
        return self.callback(0)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""
    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""
    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)
        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        # Use relative coordinates for rendering
        x, y = self.engine.mouse_relative_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_rect(
            x=x - self.radius,
            y=y - self.radius,
            width=self.radius * 2 + 1,
            height=self.radius * 2 + 1,
            ch=0,
            fg=color.red,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class RayRangedInputHandler(SelectDirectionHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""
    def __init__(
        self,
        engine: Engine,
        actor: Actor,
        max_range: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)
        self.actor = actor
        self.max_range = max_range
        self.callback = callback
        self.target = None

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        dx, dy = self.engine.mouse_dir
        dest_x, dest_y = self.actor.x + dx, self.actor.y + dy
        path = []

        while True:
            if not self.engine.game_map.in_bounds(dest_x, dest_y):
                # Destination is out of bounds.
                break
            if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
                # Destination is blocked by a tile.
                break
            if not self.engine.game_map.explored[dest_x, dest_y]:
                break
            if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
                # Destination is blocked by an entity. (graphic is displayed on entity's tile)
                path.append((dest_x, dest_y))
                break
            path.append((dest_x, dest_y))
            dest_x += dx
            dest_y += dy

        range_count = 0
        while len(path) > 0:
            loc = path.pop(0)
            range_count += 1
            if range_count > self.max_range:
                break
            # Use relative coords for rendering
            if self.engine.camera.in_bounds(abs_x=loc[0], abs_y=loc[1]):# Prevents the yellow guide line from going out the camera boundaries
                relative_x, relative_y = self.engine.camera.get_relative_coordinate(abs_x=loc[0], abs_y=loc[1])
                console.tiles_rgb["bg"][relative_x, relative_y] = color.ray_path
            else:
                continue
        
        self.dx = dx
        self.dy = dy

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        self.engine.refresh_screen()
        return self.callback((self.dx, self.dy))


class RayDirInputHandler(SelectDirectionHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""
    def __init__(
        self,
        engine: Engine,
        actor: Actor,
        max_range: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)
        self.actor = actor
        self.max_range = max_range
        self.callback = callback
        self.target = None
        self.engine.message_log.add_message(
                "Choose a direction (1~9)", color.needs_target
            )

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        dx, dy = self.engine.mouse_dir
        dest_x, dest_y = self.actor.x + dx, self.actor.y + dy
        path = []

        while True:
            if not self.engine.game_map.in_bounds(dest_x, dest_y):
                # Destination is out of bounds.
                break
            if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
                # Destination is blocked by a tile.
                break
            if not self.engine.game_map.explored[dest_x, dest_y]:
                break
            if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
                # Destination is blocked by an entity. (graphic is displayed on entity's tile)
                path.append((dest_x, dest_y))
                break
            path.append((dest_x, dest_y))
            dest_x += dx
            dest_y += dy

        range_count = 0
        while len(path) > 0:
            loc = path.pop(0)
            range_count += 1
            if range_count > self.max_range:
                break
            # Use relative coords for rendering
            if self.engine.camera.in_bounds(abs_x=loc[0], abs_y=loc[1]):# Prevents the yellow guide line from going out the camera boundaries
                relative_x, relative_y = self.engine.camera.get_relative_coordinate(abs_x=loc[0], abs_y=loc[1])
                console.tiles_rgb["bg"][relative_x, relative_y] = color.ray_path
            else:
                continue
        
        self.dx = dx
        self.dy = dy

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        self.engine.refresh_screen()
        return self.callback(self.dx, self.dy)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None
        key = event.sym
        player = self.engine.player

        if event.mod & tcod.event.K_LSHIFT: # Check Shift Modifier
            if key == tcod.event.K_PERIOD:
                action = DescendAction(player)
            elif key == tcod.event.K_COMMA:
                action = AscendAction(player)
            
            elif key == tcod.event.K_q:
                raise SystemExit()
            elif key == tcod.event.K_s:
                self.engine.event_handler = SaveInputHandler(
                    engine=self.engine
                )
        else:
            if key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[key]
                action = BumpAction(player, dx, dy)
            elif key in WAIT_KEYS:
                action = WaitAction(player)

            elif key == tcod.event.K_v:
                self.engine.event_handler = HistoryViewer(self.engine)
            elif key == tcod.event.K_g:
                action = PickupAction(player)
            elif key == tcod.event.K_i:
                self.engine.event_handler = InventoryEventHandler(self.engine, self.engine.player.inventory)
            elif key == tcod.event.K_d:
                self.engine.event_handler = InventoryDropHandler(self.engine, self.engine.player.inventory)
            elif event.sym == tcod.event.K_SLASH or event.sym == tcod.event.K_KP_DIVIDE:
                self.engine.event_handler = LookHandler(self.engine)
            elif key == tcod.event.K_c:
                self.engine.event_handler = RayDirInputHandler(
                    engine=self.engine,
                    actor=player,
                    max_range=1,
                    callback=lambda dx, dy: DoorCloseAction(player, dx, dy)
                    )
            elif key == tcod.event.K_a:
                self.engine.event_handler = AbilityActivateHandler(self.engine)

            elif key == tcod.event.K_F12:
                time_str = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
                pic_name = self.engine.player.name + "_" + time_str
                self.engine.context.save_screenshot(f"./screenshots/{pic_name}.png")
                self.engine.message_log.add_message(f"Screenshot saved as {pic_name}.png", color.needs_target)

        # No valid key was pressed
        return action


class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.
        log_console = tcod.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            self.engine.event_handler = MainGameEventHandler(self.engine)

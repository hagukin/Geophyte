from __future__ import annotations
from entity import SemiActor
from components.inventory import Inventory
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Any
from order import InventoryOrder
from actions import (
    Action,
    BumpAction,
    DoorBreakAction, 
    DoorOpenAction, 
    MeleeAction,
    MovementAction,
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
    DoorUnlockAction,
)
from loader.data_loader import save_game, quit_game
from entity import Actor, Item, Entity
from util import create_surface_with_text
from korean import grammar as g
from interactables import MouseInteractable

import pygame.key
import tcod
import time
import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from ability import Ability

MOVE_KEYS = {
    # Arrow keys.
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_HOME: (-1, -1),
    pygame.K_END: (-1, 1),
    pygame.K_PAGEUP: (1, -1),
    pygame.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    pygame.K_KP_1: (-1, 1),
    pygame.K_KP_2: (0, 1),
    pygame.K_KP_3: (1, 1),
    pygame.K_KP_4: (-1, 0),
    pygame.K_KP_6: (1, 0),
    pygame.K_KP_7: (-1, -1),
    pygame.K_KP_8: (0, -1),
    pygame.K_KP_9: (1, -1),
    # Vi keys.
    pygame.K_h: (-1, 0),
    pygame.K_j: (0, 1),
    pygame.K_k: (0, -1),
    pygame.K_l: (1, 0),
    pygame.K_y: (-1, -1),
    pygame.K_u: (1, -1),
    pygame.K_b: (-1, 1),
    pygame.K_n: (1, 1),
}

WAIT_KEYS = {
    pygame.K_PERIOD,
    pygame.K_KP_5,
    pygame.K_CLEAR,
}

CONFIRM_KEYS = {
    pygame.K_RETURN,
    pygame.K_KP_ENTER,
}

class InputHandler():
    def __init__(self, engine: Optional[Engine]=None, screen=None):
        self.engine = engine
        if screen:
            self.screen = screen
        else:
            self.screen = self.engine.screen
        self.mouse_interactables = [] # List of interactables

    def ev_mousemotion(self, event: pygame.event.Event, pressed) -> None:
        pass

    def ev_quit(self, event: pygame.event.Event, pressed) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, event: pygame.event.Event, pressed) -> None:
        pass

    def ev_keyup(self, event: pygame.event.Event, pressed) -> None:
        pass

    def m_lclicked(self, pressed) -> Any:
        for interactable in self.mouse_interactables:
            interactable.update_mouse_status(pygame.mouse.get_pos())
            if interactable.mouse_on:
                return interactable.mouse_down_return
        return None

    def m_rclicked(self, pressed) -> None:
        pass

    def ev_mousebuttondown(self, event: pygame.event.Event, pressed) -> None:
        # Get the x, y coordinates of the mouse cursor.
        mouse_map_x, mouse_map_y = pygame.mouse.get_pos()

        if event.button == 1: #left
            return self.m_lclicked(pressed)
        elif event.button == 3: #right
            return self.m_rclicked(pressed)

    def ev_mousebuttonup(self, event: pygame.event.Event, pressed):
        pass

    def ev_mousewheel(self, event: pygame.event.Event, pressed):
        pass

    def dispatch_event(self, event: pygame.event.Event, pressed) -> Optional[str]:
        if event.type == pygame.MOUSEMOTION:
            return self.ev_mousemotion(event, pressed)
        elif event.type == pygame.KEYDOWN:
            return self.ev_keydown(event, pressed)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self.ev_mousebuttondown(event, pressed)
        elif event.type == pygame.KEYUP:
            return self.ev_keyup(event, pressed)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self.ev_mousebuttonup(event, pressed)
        elif event.type == pygame.MOUSEWHEEL:
            return self.ev_mousewheel(event, pressed)
        # X button / alt-f4
        if event.type == pygame.QUIT:
            return

    def add_mouse_interactable(self, interactable: MouseInteractable):
        self.mouse_interactables.append(interactable)

    def render_interactables(self, mouse_pos):
        """Render all interactable objects attached to the eventhandler."""
        for interactable in self.mouse_interactables:
            interactable.render(self.screen, mouse_pos)

    def on_render(self, mouse_pos) -> None:
        self.render_interactables(mouse_pos)

class EventHandler(InputHandler):
    def __init__(self, engine: Engine, revert_callback: Callable = None):
        """
        Args:
            revert_callback:
                If there is a value(lambda function),
                this event will call that function when the item usage has been cancelled.
                (However, items will still get consumed)
        """
        super().__init__(engine)
        self.revert_callback = revert_callback

    @property
    def center_x(self):
        return self.screen.get_width() // 2

    @property
    def center_y(self):
        return self.screen.get_height() // 2

    def handle_event(self, event_id: str) -> bool:
        """Handles actual implementation of each event.
        Returns:
            boolean that indicates whether the event costs a player turn or not."""
        # e.g. if event_id == "attack":
        #           self.engine.player.attack(xxx) ...
        pass

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
            print(f"Impossible action : {exc.args[0]}")
            return False # Trying to do something impossible will not cost a turn
        except Exception as exc:
            self.engine.message_log.add_message(exc.args[0], color.red)
            print(f"ERROR::an error has occurred during processing the following: {exc.args[0]} - input_handlers - handle_action")
            raise exc
            #TODO: return False  # Skip enemy turn on exceptions.

        if action.free_action:
            return False
        return True

    def on_render(self, mouse_pos) -> None:
        self.engine.render(self.screen) # Render game first
        super().on_render(mouse_pos)


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""
    def handle_event(self, event_id: str) -> bool:
        if event_id == "cancel":
            self.on_exit()
            return False
        elif event_id == "item_cancel":
            self.engine.event_handler = ItemUseCancelHandler(self.engine, self.revert_callback)
            return False
        elif event_id == "invalid":
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return False

    def handle_action(self, action: Optional[Action]) -> bool:
        """Return to the main event handler when a valid action was performed."""
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        """By default any key exits this input handler."""
        if self.revert_callback is None:
            return "cancel"
        else:
            return "item_cancel"

    def ev_mousebuttondown(self, event: pygame.event.Event, pressed) -> str:
        """By default any mouse click exits this input handler."""
        return "cancel"

    def on_exit(self) -> None:
        """
        Called when the user is trying to exit or cancel an action.
        By default this returns to the main event handler.
        """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


class ItemUseCancelHandler(AskUserEventHandler):
    def __init__(self, engine, revert_callback: Callable = None):
        super().__init__(engine, revert_callback)

        self.add_mouse_interactable(MouseInteractable((self.center_x, self.center_y), {
            "default": create_surface_with_text("정말 아이템 사용을 취소하시겠습니까? 아이템은 여전히 소모됩니다.",
                                                color.gui_item_action, None, self.engine.get_font("default", 16))}))
        self.add_mouse_interactable(MouseInteractable((self.center_x, self.center_y + 20*2), {
            "default": create_surface_with_text("Yes", color.white, None, self.engine.get_font("default", 16)),
            "mouse_on": create_surface_with_text("Yes", color.white, None, self.engine.get_font("default", 20))}, None,
                                                      mouse_down_return="confirm_cancel"))
        self.add_mouse_interactable(MouseInteractable((self.center_x + 20*2, self.center_y + 20*2), {
            "default": create_surface_with_text("No", color.white, None, self.engine.get_font("default", 16)),
            "mouse_on": create_surface_with_text("No", color.white, None, self.engine.get_font("default", 20))}, None,
                                                      mouse_down_return="decline_cancel"))

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "confirm_cancel":
            self.engine.event_handler = MainGameEventHandler(self.engine)
            self.engine.message_log.add_message(f"아이템 사용 취소됨.", color.white, stack=False, show_once=True)
            return self.revert_callback(True)  # passing True (action is cancelled)
        elif event_id == "decline_cancel":
            return self.revert_callback(False)# passing False (action is not cancelled)

    def on_render(self, mouse_pos) -> None:
        super().on_render(mouse_pos)
        self.engine.draw_window(console, text="", title="아이템 사용 취소", frame_fg=color.lime, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        if event.key == pygame.K_y or event.key == pygame.K_KP_ENTER:
            return "confirm_cancel"
        elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            return "decline_cancel"


class SaveInputHandler(AskUserEventHandler):
    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "confirm_save":
            self.engine.event_handler = MainGameEventHandler(self.engine)
            self.engine.message_log.add_message(f"게임 저장됨.", color.lime, stack=False)
            save_game(player=self.engine.player, engine=self.engine)
            return False
        elif event_id == "decline_save":
            self.engine.message_log.add_message(f"저장 취소됨.", color.lime, stack=False)
            return False

    def on_render(self, mouse_pos) -> None:
        super().on_render(mouse_pos)
        self.engine.draw_window(console, text="정말 현재 게임을 저장하시겠습니까? (Y/N)", title="저장", frame_fg=color.lime, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        if event.key == pygame.K_y or event.key == pygame.K_KP_ENTER:
            return "confirm_save"
        elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            return "decline_save"
        return super().ev_keydown(event, pressed)


class GameClearInputHandler(AskUserEventHandler): #TODO Unfinished
    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp
        #TODO

    def on_render(self, mouse_pos) -> None:
        super().on_render(mouse_pos)
        self.engine.draw_window(
            self.engine.console,
            text="쿠가의 아뮬렛을 탈환했다!",
            title="승리했습니다!",
            frame_fg=color.yellow,
        )


class AbilityEventHandler(AskUserEventHandler):
    """
    This handler lets the user select an ability to use / cast.
    What happens then depends on the subclass.
    """

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.TITLE = "능력"

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "sort_inventory":
            self.engine.player.inventory.sort_inventory()
            return False

    def on_render(self, mouse_pos) -> None:
        """
        Render an ability inventory menu, which displays the abilities in the inventory, and the alphabet key to select them.
        """
        super().on_render(mouse_pos)
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
            console.print(x + x_space + 1, y + y_space + 1, "(없음)", color.gray)

        console.print(x + x_space + 1, height + 3, "\"/\"키: - 인벤토리 정렬", color.gui_inventory_fg)


    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        player = self.engine.player

        # Sort inventory
        if event.key == pygame.K_SLASH or event.key == pygame.K_KP_DIVIDE: # Sort Inventory by type
            return "sort_inventory"
        elif event.key == pygame.K_ESCAPE: # Escape inventory window
            return "cancel"

        # Check modifier
        if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
            alphabet = {
                pygame.K_a:"A",pygame.K_b:"B",pygame.K_c:"C",pygame.K_d:"D",pygame.K_e:"E",pygame.K_f:"F",pygame.K_g:"G",pygame.K_h:"H",pygame.K_i:"I",pygame.K_j:"J",pygame.K_k:"K",pygame.K_l:"L",pygame.K_m:"M",pygame.K_n:"N",pygame.K_o:"O",pygame.K_p:"P",pygame.K_q:"Q",pygame.K_r:"R",pygame.K_s:"S",pygame.K_t:"T",pygame.K_u:"U",pygame.K_v:"V",pygame.K_w:"W",pygame.K_x:"X",pygame.K_y:"Y",pygame.K_z:"Z",
            }
        else:
            alphabet = {
                pygame.K_a:"a",pygame.K_b:"b",pygame.K_c:"c",pygame.K_d:"d",pygame.K_e:"e",pygame.K_f:"f",pygame.K_g:"g",pygame.K_h:"h",pygame.K_i:"i",pygame.K_j:"j",pygame.K_k:"k",pygame.K_l:"l",pygame.K_m:"m",pygame.K_n:"n",pygame.K_o:"o",pygame.K_p:"p",pygame.K_q:"q",pygame.K_r:"r",pygame.K_s:"s",pygame.K_t:"t",pygame.K_u:"u",pygame.K_v:"v",pygame.K_w:"w",pygame.K_x:"x",pygame.K_y:"y",pygame.K_z:"z",
            }

        # Select ability to cast/use
        try:
            key = alphabet[event.key]
            selected_ability = player.ability_inventory.ability_hotkeys[key]
            return self.on_ability_selected(selected_ability)
        except Exception as e:
            print(e)
            return "invalid"

    def on_ability_selected(self, ability: Ability) -> Optional[Action]:
        """Called when the user selects a valid ability."""
        raise NotImplementedError()


class AbilityActivateHandler(AbilityEventHandler):
    """Handle using an ability called from inventory."""
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.TITLE = "능력"

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

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "cast_or_conduct":
            return self.handle_action(self.ability.activatable.get_action(self.engine.player))


    def on_render(self, mouse_pos) -> None:
        """
        Renders an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(mouse_pos)

        self.possible_actions = []
        self.possible_keys = []

        if self.ability.activatable:
            self.possible_actions.append("cast/conduct")
            self.possible_keys.append(pygame.K_c)

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
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(c) 마법/기술 사용", fg=color.gui_item_action)
            else:
                console.print(x + x_space + 1, y + desc_height + 2 + y_space, "(없음)")

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        player = self.engine.player
        key = event.key

        if key in self.possible_keys:
            if key == pygame.K_c:
                return "cast_or_conduct"
        elif key == pygame.K_ESCAPE:
            return "cancel"
        else:
            return "invalid"


class StorageSelectEventHandler(AskUserEventHandler):
    def __init__(
            self, 
            engine: Engine, 
            inventory_component: Inventory, 
            show_only_types: Tuple[InventoryOrder]=None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
            revert_callback: Callable = None,
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
        super().__init__(engine, revert_callback)
        self.inventory_component = inventory_component 
        self.show_only_types = show_only_types
        self.show_only_status = show_only_status
        self.show_if_satisfy_both = show_if_satisfy_both
        self.selected_items = [] # Can be unused
        if hasattr(self.inventory_component.parent, "name"):
            self.TITLE = f"{self.inventory_component.parent.name}"
        else:
            self.TITLE = ""

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "sort_inventory":
            self.inventory_component.sort_inventory()
            return False

    def choice_confirmed(self) -> bool:
        raise NotImplementedError()

    def get_item_rendered_text(self, item: Item, item_key, choose_multiple: bool) -> Optional[Tuple]:
        """
        Returns:
            item_text, item_damage_text, item_state_text, item_equip_text, item_text_color
        """
        item_text = f"({item_key}) "

        # if item is a cash, display amount in front of the name
        if item.counter_at_front:
            item_text += f"{item.stack_count} "

        if item.item_state.check_if_full_identified(): # Display BUC only if fully identified
            if item.item_state.BUC == 0:
                item_text += "저주받지 않은 "
            if item.item_state.BUC >= 1:
                item_text += "축복받은 "
            if item.item_state.BUC <= -1:
                item_text += "저주받은 "

        item_text += f"{item.name} "
        item_count = ""
        item_damage_text = ""
        item_state_text = ""
        item_equip_text = ""
        item_price_text = ""
        item_text_color = None

        # Display item counts if it is greater than 1
        if item.stack_count > 1 and not item.counter_at_front:
            item_count += f"(x{item.stack_count}) "

        # Assign color of its type
        if item.item_type == InventoryOrder.POTION:
            item_text_color = color.gui_potion_name
        elif item.item_type == InventoryOrder.SCROLL:
            item_text_color = color.gui_scroll_name
        elif item.item_type == InventoryOrder.ARMOR:
            item_text_color = color.gui_armor_name

        # Change color of the selected items
        if choose_multiple:
            if item in self.selected_items:
                item_text_color = color.gui_selected_item #TODO: Maybe add a short string in front of item name? like (selected)
            
        # Display damage status if their is one
        if item.item_state.burntness == 1:
            item_damage_text += "(다소 그을림) "
        elif item.item_state.burntness == 2:
            item_damage_text += "(상당히 그을림) "
        if item.item_state.corrosion == 1:
            item_damage_text += "(다소 부식됨) "
        elif item.item_state.corrosion == 2:
            item_damage_text += "(심하게 부식됨) "
            
        # Display special states if it is true
        if item.item_state.is_burning:
            item_state_text += "[불붙음] "

        # Display equip info if it is true(if value isn't None)
        if self.engine.config["lang"] == "ko":
            translated = ""
            
            if item.item_state.is_equipped:
                if item.item_state.is_equipped == "main hand":
                    translated = "메인 핸드"
                elif item.item_state.is_equipped == "off hand":
                    translated = "오프 핸드"
                elif item.item_state.is_equipped == "head":
                    translated = "머리"
                elif item.item_state.is_equipped == "face":
                    translated = "얼굴"
                elif item.item_state.is_equipped == "torso":
                    translated = "상반신"
                elif item.item_state.is_equipped == "hand":
                    translated = "손"
                elif item.item_state.is_equipped == "belt":
                    translated = "허리춤"
                elif item.item_state.is_equipped == "leg":
                    translated = "다리"
                elif item.item_state.is_equipped == "feet":
                    translated = "발"
                elif item.item_state.is_equipped == "cloak":
                    translated = "망토"
                elif item.item_state.is_equipped == "amulet":
                    translated = "아뮬렛"
                elif item.item_state.is_equipped == "left ring":
                    translated = "왼손 반지"
                elif item.item_state.is_equipped == "right ring":
                    translated = "오른손 반지"

                item_equip_text += f"[{translated}에 장착] "
        else:
            if item.item_state.is_equipped:
                item_equip_text += f"[equipped on {item.item_state.is_equipped}] "

        # Display the price of the item if it is currently being sold
        if item.item_state.is_being_sold_from:
            item_price_text += f"<{item.price_of(self.engine.player,1)}샤인, 미구매> " #discount set as 1 (hard-coded)

        return item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_price_text, item_text_color

    def render_item(
        self, 
        xpos, ypos,
        item_text: str,
        item_count: str,
        item_damage_text: str,
        item_state_text: str, 
        item_equip_text: str, 
        item_price_text: str, 
        item_text_color: Tuple[int,int,int], 
        y_padding: int
    ) -> None:

        # Print
        self.engine.console.print(xpos, ypos + y_padding, item_text, fg=item_text_color)
        xpos += len(item_text)
        self.engine.console.print(xpos, ypos + y_padding, item_count, fg=color.white)
        xpos += len(item_count)
        self.engine.console.print(xpos, ypos + y_padding, item_damage_text, fg=color.gray)
        xpos += len(item_damage_text)
        self.engine.console.print(xpos, ypos + y_padding, item_equip_text, fg=color.gui_item_equip)
        xpos += len(item_equip_text)
        self.engine.console.print(xpos, ypos + y_padding, item_state_text, fg=color.gui_item_state)
        xpos += len(item_state_text)
        self.engine.console.print(xpos, ypos + y_padding, item_price_text, fg=color.gui_item_price)

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

    def on_render(self, mouse_pos) -> None:
        return super().on_render(mouse_pos)


class StorageSelectSingleEventHandler(StorageSelectEventHandler):
    """
    Inherit this class if the action requires selecting one single itme.
    e.g. Item inventory
    """
    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "confirm_selected":
            return self.choice_confirmed()


    def on_render(self, mouse_pos) -> None:
        """
        Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        """
        super().on_render(mouse_pos)

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
            y_padding = -1

            for item_key, item in self.inventory_component.item_hotkeys.items():
                if item == None:
                    continue

                if not self.check_should_render_item(item):
                    continue

                y_padding += 1
                
                item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_price_text, item_text_color = self.get_item_rendered_text(item, item_key, choose_multiple=False)
                xpos = x + x_space + 1
                ypos = y + y_space + 1
                self.render_item(xpos, ypos, item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_price_text, item_text_color, y_padding=y_padding)
        else:
            console.print(x + x_space + 1, y + y_space + 1, "(없음)", color.gray)

        console.print(x + x_space + 1, height + 4, "\"/\"키 - 아이템 정렬", color.gui_inventory_fg)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        # Sort inventory
        if event.key == pygame.K_SLASH or event.key == pygame.K_KP_DIVIDE: # Sort Inventory by type
            return "sort_inventory"
        elif event.key == pygame.K_ESCAPE: # Escape inventory window
            return "cancel"
        elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN: # Confirm choices
            return "confirm_selected"

        # Check modifier
        if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
            alphabet = {
                pygame.K_a:"A",pygame.K_b:"B",pygame.K_c:"C",pygame.K_d:"D",pygame.K_e:"E",pygame.K_f:"F",pygame.K_g:"G",pygame.K_h:"H",pygame.K_i:"I",pygame.K_j:"J",pygame.K_k:"K",pygame.K_l:"L",pygame.K_m:"M",pygame.K_n:"N",pygame.K_o:"O",pygame.K_p:"P",pygame.K_q:"Q",pygame.K_r:"R",pygame.K_s:"S",pygame.K_t:"T",pygame.K_u:"U",pygame.K_v:"V",pygame.K_w:"W",pygame.K_x:"X",pygame.K_y:"Y",pygame.K_z:"Z",
            }
        else:
            alphabet = {
                pygame.K_a:"a",pygame.K_b:"b",pygame.K_c:"c",pygame.K_d:"d",pygame.K_e:"e",pygame.K_f:"f",pygame.K_g:"g",pygame.K_h:"h",pygame.K_i:"i",pygame.K_j:"j",pygame.K_k:"k",pygame.K_l:"l",pygame.K_m:"m",pygame.K_n:"n",pygame.K_o:"o",pygame.K_p:"p",pygame.K_q:"q",pygame.K_r:"r",pygame.K_s:"s",pygame.K_t:"t",pygame.K_u:"u",pygame.K_v:"v",pygame.K_w:"w",pygame.K_x:"x",pygame.K_y:"y",pygame.K_z:"z",
            }

        # Choose item
        try:
            key = alphabet[event.key]
            selected_item = self.inventory_component.item_hotkeys[key]
            if not self.check_should_render_item(selected_item):
                raise Exception()
            if selected_item:
                return self.on_item_selected(selected_item)
            else:
                return "invalid"
        except:
            return "invalid"

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
            title: str = "인벤토리",
            show_only_types: Tuple[InventoryOrder]=None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
            revert_callback: Callable = None,
        ):
        super().__init__(engine, inventory_component, show_only_types, show_only_status, show_if_satisfy_both, revert_callback)
        self.TITLE = title
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
            show_only_types: Tuple[InventoryOrder]=None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
        ):
        super().__init__(engine, inventory_component, show_only_types, show_only_status, show_if_satisfy_both)
        self.TITLE = "인벤토리"

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

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "read_item":
            return self.handle_action(self.item.readable.get_action(self.engine.player))
        elif event_id == "quaff_item":
            return self.handle_action(self.item.quaffable.get_action(self.engine.player))
        elif event_id == "eat_item":
            return self.handle_action(self.item.edible.get_action(self.engine.player))
        elif event_id == "equip_item":
            return self.handle_action(EquipItem(self.engine.player, self.item))
        elif event_id == "unequip_item":
            return self.handle_action(UnequipItem(self.engine.player, self.item))
        elif event_id == "split_item":
            self.engine.event_handler = InventorySplitHandler(self.engine, self.item)
            return False
        elif event_id == "throw_item":
            if self.item.item_state.is_equipped:
                self.engine.message_log.add_message("장착하고 있는 아이템을 던질 수 없습니다.", color.invalid)
                self.engine.event_handler = MainGameEventHandler(self.engine)
                return False
            return self.handle_action(self.item.throwable.get_action(self.engine.player))
        elif event_id == "drop_item":
            if self.item.item_state.is_equipped:
                self.engine.message_log.add_message("장착하고 있는 아이템을 떨어뜨릴 수 없습니다.", color.invalid)
                self.engine.event_handler = MainGameEventHandler(self.engine)
                return False
            return self.handle_action(DropItem(self.engine.player, self.item))

    def on_render(self, mouse_pos) -> None:
        """
        Render an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(mouse_pos)

        self.possible_actions = []
        self.possible_keys = []

        if self.item.readable:
            self.possible_actions.append("read")
            self.possible_keys.append(pygame.K_r)
        if self.item.quaffable:
            self.possible_actions.append("quaff")
            self.possible_keys.append(pygame.K_q)
        if self.item.edible:
            self.possible_actions.append("eat")
            self.possible_keys.append(pygame.K_a)
        if self.item.equipable and self.item.item_state.is_equipped == None:
            self.possible_actions.append("equip")
            self.possible_keys.append(pygame.K_e)
        if self.item.equipable and self.item.item_state.is_equipped != None:
            self.possible_actions.append("unequip")
            self.possible_keys.append(pygame.K_u)
        if self.item.stackable and self.item.stack_count > 1:
            self.possible_actions.append("split")
            self.possible_keys.append(pygame.K_s)
        if self.item.throwable:
            self.possible_actions.append("throw")
            self.possible_keys.append(pygame.K_t)
        if self.item.droppable:
            self.possible_actions.append("drop")
            self.possible_keys.append(pygame.K_d)

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
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(r) 읽기", fg=color.gui_item_action)
            elif action == "quaff":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(q) 마시기", fg=color.gui_item_action)
            elif action == "eat":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(a) 먹기", fg=color.gui_item_action)
            elif action == "equip":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(e) 장착하기", fg=color.gui_item_action)
            elif action == "unequip":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(u) 장착 해제하기", fg=color.gui_item_action)
            elif action == "split":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(s) 아이템 나누기", fg=color.gui_item_action)
            elif action == "throw":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(t) 던지기", fg=color.gui_item_action)
            elif action == "drop":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(d) 아이템 떨어뜨리기", fg=color.gui_item_action)
            else:
                console.print(x + x_space + 1, y + desc_height + 2 + y_space, "(없음)")

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        player = self.engine.player
        key = event.key

        if key in self.possible_keys:
            if key == pygame.K_r:
                return "read_item"
            elif key == pygame.K_q:
                return "quaff_item"
            elif key == pygame.K_a:
                return "eat_item"
            elif key == pygame.K_e:
                return "equip_item"
            elif key == pygame.K_u:
                return "unequip_item"
            elif key == pygame.K_s:
                return "split_item"
            elif key == pygame.K_t:
                return "throw_item"
            elif key == pygame.K_d:
                return "drop_item"
        elif key == pygame.K_ESCAPE:
            return "cancel"
        else:
            return "invalid"


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

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "split_plus":
            if self.split_amount < self.item.stack_count - 1:
                self.split_amount += 1
            else:
                self.engine.message_log.add_message("나눌 수 있는 수의 최대치에 도달하였습니다.", color.invalid, show_once=True)
            return False
        elif event_id == "split_minus":
            if self.split_amount > 1:
                self.split_amount -= 1
            else:
                self.engine.message_log.add_message("1 이상을 선택하셔야 합니다.", color.invalid, show_once=True)
        elif event_id == "confirm_split":
            return self.handle_action(SplitItem(self.engine.player, self.item, self.split_amount))


    def on_render(self, mouse_pos) -> None:
        super().on_render(mouse_pos)

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
        console.print(x + x_space + 1, height + 3, "마우스 휠 또는 +,- 키를 사용해 나누고 싶은 아이템의 수를 선택하고 ENTER 키로 확인하세요.", color.gui_inventory_fg)
        console.print(x + x_space + 1, y + y_space + 1, self.item.entity_desc, fg=color.gui_item_description)
        console.print(x + x_space + 1, y + y_space + 3, f"{self.split_amount}개 선택됨.", fg=color.gui_item_description)

    def ev_mousewheel(self, event: pygame.event.Event, pressed):
        raise NotImplementedError() #TODO

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        player = self.engine.player
        key = event.key

        if key == pygame.K_PLUS or key == pygame.K_KP_PLUS or key == pygame.K_EQUALS:
            return "split_plus"
        elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS:
            return "split_minus"
        elif key == pygame.K_ESCAPE:
            return "cancel"
        elif key == pygame.K_RETURN:
            return "confirm_split"
        else:
            return "invalid"


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
            show_only_types: Tuple[InventoryOrder]=None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
            ):
        super().__init__(engine, inventory_component, show_only_types, show_only_status, show_if_satisfy_both)
        self.selected_items = set()

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "confirm_selected":
            return False

    def on_render(self, mouse_pos) -> None:
        """
        Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        """
        super().on_render(mouse_pos)
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
            y_padding = -1
            for item_key, item in self.inventory_component.item_hotkeys.items():
                if item == None:
                    continue

                if not self.check_should_render_item(item):
                    continue
                
                y_padding += 1

                item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_price_text, item_text_color = self.get_item_rendered_text(item, item_key, choose_multiple=True)
                xpos = x + x_space + 1
                ypos = y + y_space + 1
                self.render_item(xpos, ypos, item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_price_text, item_text_color, y_padding=y_padding)
        else:
            console.print(x + x_space + 1, y + y_space + 1, "(없음)", color.gray)

        console.print(x + x_space + 1, height + 4, "\"/\"키 - 아이템 정렬 | ENTER 키- 선택 확인", color.gui_inventory_fg)
        
    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        # Check modifier
        if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
            alphabet = {
                pygame.K_a:"A",pygame.K_b:"B",pygame.K_c:"C",pygame.K_d:"D",pygame.K_e:"E",pygame.K_f:"F",pygame.K_g:"G",pygame.K_h:"H",pygame.K_i:"I",pygame.K_j:"J",pygame.K_k:"K",pygame.K_l:"L",pygame.K_m:"M",pygame.K_n:"N",pygame.K_o:"O",pygame.K_p:"P",pygame.K_q:"Q",pygame.K_r:"R",pygame.K_s:"S",pygame.K_t:"T",pygame.K_u:"U",pygame.K_v:"V",pygame.K_w:"W",pygame.K_x:"X",pygame.K_y:"Y",pygame.K_z:"Z",
            }
        else:
            alphabet = {
                pygame.K_a:"a",pygame.K_b:"b",pygame.K_c:"c",pygame.K_d:"d",pygame.K_e:"e",pygame.K_f:"f",pygame.K_g:"g",pygame.K_h:"h",pygame.K_i:"i",pygame.K_j:"j",pygame.K_k:"k",pygame.K_l:"l",pygame.K_m:"m",pygame.K_n:"n",pygame.K_o:"o",pygame.K_p:"p",pygame.K_q:"q",pygame.K_r:"r",pygame.K_s:"s",pygame.K_t:"t",pygame.K_u:"u",pygame.K_v:"v",pygame.K_w:"w",pygame.K_x:"x",pygame.K_y:"y",pygame.K_z:"z",
            }

        # Choose item
        try:
            key = alphabet[event.key]
            selected_item = self.inventory_component.item_hotkeys[key]
            if selected_item:
                self.on_item_selected(selected_item)
                return "confirm_selected"
            else:
                return "invalid"
        except:
            return "invalid"

    def on_item_selected(self, item: Item) -> None:
        """Called when the user selects a valid item."""
        if item in self.selected_items:
            self.selected_items.remove(item)
        else:
            self.selected_items.add(item)


class LockedDoorEventHandler(AskUserEventHandler):
    def __init__(self, engine, door: SemiActor):
        super().__init__(engine)
        self.door = door
        self.TITLE = "문이 잠겨 있습니다. 무엇을 하시겠습니까?"

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "unlock_door":
            return self.handle_action(DoorUnlockAction(self.engine.player, self.door.x - self.engine.player.x,
                             self.door.y - self.engine.player.y))
        elif event_id == "break_door":
            DoorBreakAction(self.engine.player, self.door.x - self.engine.player.x, self.door.y - self.engine.player.y) \
                .break_door(self.door, self.engine.player.status.changed_status["strength"])
            return True


    def on_render(self, mouse_pos) -> None:
        """
        Render an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(mouse_pos)

        height = 7 #TODO hard-coded
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
        console.print(x + x_space + 1, y + y_space + 2, "(u) - 잠금 해제", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 4, "(b) - 파괴", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 6, "ESC - 취소", fg=color.white)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        key = event.key

        if key == pygame.K_u:
            return "unlock_door"
        elif key == pygame.K_b:
            return "break_door"
        elif key == pygame.K_ESCAPE:
            return "cancel"
        else:
            return "invalid"


class ChestEventHandler(AskUserEventHandler):
    def __init__(self, engine, inventory_component: Inventory):
        super().__init__(engine)
        self.inventory_component = inventory_component
        if hasattr(self.inventory_component.parent, "name"):
            self.TITLE = f"{self.inventory_component.parent.name}?"
        else:
            self.TITLE = "무엇을 하시겠습니까?"

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "take_out":
            self.engine.event_handler = ChestTakeEventHandler(self.engine, self.inventory_component)
            return False
        elif event_id == "put_in":
            self.engine.event_handler = ChestPutEventHandler(self.engine, self.engine.player.inventory,self.inventory_component)
            return False
        elif event_id == "swap_position":
            return self.handle_action(PlaceSwapAction(self.engine.player, self.inventory_component.parent))


    def on_render(self, mouse_pos) -> None:
        """
        Render an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(mouse_pos)

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
        console.print(x + x_space + 1, y + y_space + 2, "(t) - 무언가를 꺼낸다", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 4, "(i) - 무언가를 넣는다", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 6, "(s) - 위치를 바꾼다", fg=color.white)
        console.print(x + x_space + 1, y + y_space + 8, "ESC - 취소", fg=color.white)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        key = event.key

        if key == pygame.K_t:
            return "take_out"
        elif key == pygame.K_i:
            return "put_in"
        elif key == pygame.K_s:
            return "swap_position"
        elif key == pygame.K_ESCAPE:
            return "cancel"
        else:
            return "invalid"


class NonHostileBumpHandler(AskUserEventHandler):
    def __init__(self, engine, target: Entity):
        """
        Vars:
            can_pay_shopkeeper:
                인풋으로 받은 타겟이 shopkeeper이고, 또 플레이어가 현재 빚을 진 상태인 경우.
        """
        super().__init__(engine)
        self.target = target
        self.TITLE = "무엇을 하시겠습니까?"
        self.can_pay_shopkeeper = False
        self.dx, self.dy = self.target.x - self.engine.player.x, self.target.y - self.engine.player.y
        self.update_pay_status()

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "move":
            return self.handle_action(MovementAction(self.engine.player, self.dx, self.dy))
        elif event_id == "pay":
            self.engine.event_handler = MainGameEventHandler(self.engine)
            self.target.ai.sell_all_picked_ups(customer=self.engine.player)
            return False
        elif event_id == "swap":
            return self.handle_action(PlaceSwapAction(self.engine.player, self.target))
        elif event_id == "attack":
            self.engine.event_handler = ForceAttackInputHandler(self.engine,melee_action=MeleeAction(self.engine.player, dx, dy))
            return False
        elif event_id == "take_out":
            self.engine.event_handler = ChestTakeEventHandler(self.engine, self.target.storage)
            return False
        elif event_id == "put_in":
            self.engine.event_handler = ChestPutEventHandler(self.engine, self.engine.player.inventory,self.target.storage)
            return False
        
    def update_pay_status(self):
        if hasattr(self.target, "ai"):
            if self.target.ai:
                if hasattr(self.target.ai, "has_dept"):
                    if self.target.ai.has_dept(self.engine.player):
                        self.can_pay_shopkeeper = True
        
    def on_render(self, mouse_pos) -> None:
        """
        Render an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(mouse_pos)

        height = 5 #TODO hard-coded
        if not self.target.blocks_movement:
            height += 2
        if self.can_pay_shopkeeper: # pay
            height += 2
        if self.target.swappable: # swap
            height += 2
        if isinstance(self.target, Actor): # attack
            height += 2
        from chest_factories import ChestSemiactor
        if isinstance(self.target, ChestSemiactor): # take, put
            height += 4
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
        y_pad = 2
        # Check if target is a shopkeeper
        if isinstance(self.target, ChestSemiactor):
            console.print(x + x_space + 1, y + y_space + y_pad, "(t) - 무언가를 꺼낸다", fg=color.white)
            y_pad += 2
            console.print(x + x_space + 1, y + y_space + y_pad, "(i) - 무언가를 넣는다", fg=color.white)
            y_pad += 2
        if not self.target.blocks_movement:
            console.print(x + x_space + 1, y + y_space + y_pad, "(m) - 해당 칸으로 이동한다", fg=color.white)
            y_pad += 2
        if self.can_pay_shopkeeper:
            console.print(x + x_space + 1, y + y_space + y_pad, "(p) - 소지중인 판매물품들을 구매한다", fg=color.white)
            y_pad += 2
        if self.target.swappable:
            console.print(x + x_space + 1, y + y_space + y_pad, "(s) - 위치를 바꾼다", fg=color.white)
            y_pad += 2
        if isinstance(self.target, Actor):
            console.print(x + x_space + 1, y + y_space + y_pad, "(a) - 공격한다", fg=color.white)
            y_pad += 2
        console.print(x + x_space + 1, y + y_space + y_pad, "ESC - 취소", fg=color.white)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        from chest_factories import ChestSemiactor
        key = event.key

        if not self.target.blocks_movement and key == pygame.K_m:
            return "move"
        elif self.can_pay_shopkeeper and key == pygame.K_p:
            return "pay"
        elif self.target.swappable and key == pygame.K_s:
            return "swap"
        elif isinstance(self.target, Actor) and key == pygame.K_a:
            return "attack"
        elif key == pygame.K_t and isinstance(self.target, ChestSemiactor):
            return "take_out"
        elif key == pygame.K_i and isinstance(self.target, ChestSemiactor):
            return "put_in"
        elif key == pygame.K_ESCAPE:
            return "cancel"
        else:
            return "invalid"


class ChestTakeEventHandler(StorageSelectMultipleEventHandler):    
    def choice_confirmed(self):
        """
        Move the selected items to player's inventory.
        """
        for item in self.selected_items:
            self.inventory_component.remove_item(item, -1) #TODO: Add feature to choose certain amounts
            self.engine.player.inventory.add_item(item)
            
            if item.stack_count <= 1:
                self.engine.message_log.add_message(f"{g(item.name, '을')} 얻었다.", color.white)
            else:
                self.engine.message_log.add_message(f"{g(item.name, '을')} 얻었다. (x{item.stack_count})", color.white)

        self.on_exit() #NOTE: game turn is already passed at the moment player opened the chest, so taking something wont cost additional turn.
        return False

class ChestPutEventHandler(StorageSelectMultipleEventHandler):
    """Handle putting in an inventory item to a chest."""

    def __init__(self, engine: Engine, actor_inventory_component: Inventory, chest_inventory_component: Inventory):
        super().__init__(engine, actor_inventory_component)
        if hasattr(chest_inventory_component.parent, "name"):
            self.TITLE = f"{chest_inventory_component.parent.name}에 넣을 아이템을 선택하세요."
        else:
            self.TITLE = "넣을 아이템을 선택하세요."
        self.actor_inv = actor_inventory_component
        self.chest_inv = chest_inventory_component

    def choice_confirmed(self):
        """
        Move the selected items to chest's storage.
        """
        for item in self.selected_items:
            if item.item_state.is_equipped:
                self.engine.message_log.add_message("장착하고 있는 아이템을 넣을 수 없습니다.", color.invalid)
                continue
            self.actor_inv.remove_item(item, -1) #TODO: Add feature to choose certain amounts
            self.chest_inv.add_item(item)
            
            if item.stack_count > 1:
                self.engine.message_log.add_message(f"{g(item.name, '을')} {self.chest_inv.parent.name}에 넣었다.", color.gray)
            else:
                self.engine.message_log.add_message(f"{g(item.name, '을')} {self.chest_inv.parent.name}에 넣었다. (x{item.stack_count})", color.gray)

        self.on_exit() #NOTE: game turn is already passed at the moment player opened the chest, so putting something in wont cost additional turn.
        return True

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
                self.engine.message_log.add_message("장착하고 있는 아이템을 떨어뜨릴 수 없습니다.", color.invalid)
                continue
            DropItem(self.engine.player, item).perform()

        self.on_exit()
        return True


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""
    def __init__(self, engine: Engine, revert_callback: Callable = None):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine, revert_callback)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp
        if event_id == "move_index":
            return False
        if event_id == "confirm_index":
            self.on_index_selected(*self.engine.mouse_location)
            return False

    def on_render(self, mouse_pos) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(mouse_pos)
        x, y = self.engine.mouse_relative_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        """Check for key movement or confirmation keys."""
        key = event.key
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
                modifier *= 5
            if pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]:
                modifier *= 10
            if pressed[pygame.K_LALT] or pressed[pygame.K_RALT]:
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

            return "move_index"
        elif key in CONFIRM_KEYS:
            return "cofirm_index"
        return super().ev_keydown(event, pressed)

    def ev_mousebuttondown(self, event: pygame.MouseButtonDown) -> Optional[str]:
        """Left click confirms a selection."""
        if self.engine.camera.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*self.engine.camera.abs_cor(event.tile.x, event.tile.y))
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> None:
        """Return to main handler."""
        self.on_exit()


class SelectDirectionHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""
    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp
        if event_id == "move_direction":
            return False
        elif event_id == "confirm_direction":
            self.on_index_selected(*self.engine.mouse_location)
            return False

    def __init__(self, engine: Engine, revert_callback: Callable = None):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine, revert_callback)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, mouse_pos) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(mouse_pos)
        x, y = self.engine.mouse_relative_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        """Check for key movement or confirmation keys."""
        key = event.key
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
            return "move_direction"
        elif key in CONFIRM_KEYS:
            return "confirm_direction"
        return super().ev_keydown(event, pressed)

    def m_lclicked(self, pressed) -> Optional[Action]:
        """Left click confirms a selection."""
        #TODO
        # if self.engine.camera.in_bounds(*event.tile):
        #     if event.button == 1: #left
        #         return self.on_index_selected(*self.engine.camera.get_absolute_coordinate(relative_x=event.tile.x, relative_y=event.tile.y))
        # return super().ev_mousebuttondown(event)

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

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        """By default any key exits this input handler."""
        if event.key == pygame.K_ESCAPE:
            return "cancel"
        #TODO Scroll map

    def on_exit(self) -> Optional[Action]:
        """Called when the user is trying to exit or cancel an action."""
        return self.callback(0)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""
    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]], revert_callback: Callable = None
    ):
        super().__init__(engine, revert_callback=revert_callback)
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
        revert_callback: Callable = None,
    ):
        super().__init__(engine, revert_callback)
        self.radius = radius
        self.callback = callback

    def on_render(self, mouse_pos) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(mouse_pos)

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
        revert_callback: Callable = None,
    ):
        super().__init__(engine, revert_callback)
        self.actor = actor
        self.max_range = max_range
        self.callback = callback
        self.target = None

    def on_render(self, mouse_pos) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(mouse_pos)
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
                "방향을 선택하세요. (1~9)", color.needs_target
            )

    def on_render(self, mouse_pos) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(mouse_pos)

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


class QuitInputHandler(AskUserEventHandler):
    def on_render(self, mouse_pos) -> None:
        super().on_render(mouse_pos)
        self.engine.draw_window(console, text="정말 현재 게임을 종료하시겠습니까? 모든 저장하지 않은 내역은 지워집니다. (Y/N)", title="Quit", frame_fg=color.lime, frame_bg=color.gui_inventory_bg)

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "confirm_quit":
            self.engine.event_handler = MainGameEventHandler(self.engine)
            quit_game()

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        player = self.engine.player
        engine = self.engine

        if event.key == pygame.K_y or event.key == pygame.K_KP_ENTER:
            return "confirm_quit"
        elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            return "cancel"
        return super().ev_keydown(event, pressed)


class ForceAttackInputHandler(AskUserEventHandler):
    def __init__(self, engine: Engine, melee_action: MeleeAction, revert_callback: Callable = None, ):
        super().__init__(engine, revert_callback)
        self.melee_action = melee_action

    def on_render(self, mouse_pos) -> None:
        super().on_render(mouse_pos)
        self.engine.draw_window(console, text="정말로 공격하시겠습니까? (Y/N)", title="공격 확인", frame_fg=color.red, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[Action]:
        if event.key == pygame.K_y or event.key == pygame.K_KP_ENTER:
            return self.melee_action
        elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            pass
            #self.engine.message_log.add_message(f"취소됨.", color.lime, stack=False)
        return super().ev_keydown(event, pressed)


class MainGameEventHandler(EventHandler):
    def __init__(self, engine: Engine, revert_callback: Callable = None):
        super().__init__(engine, revert_callback)
        self.dx = None
        self.dy = None

    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp

        if event_id == "descend":
            return self.handle_action(DescendAction(self.engine.player))
        elif event_id == "ascend":
            return self.handle_action(AscendAction(self.engine.player))
        elif event_id == "quit":
            self.engine.event_handler = QuitInputHandler(self.engine)
        elif event_id == "save":
            self.engine.event_handler = SaveInputHandler(self.engine)
        elif event_id == "move":
            return self.handle_action(BumpAction(self.engine.player, self.dx, self.dy))
        elif event_id == "wait":
            return self.handle_action(WaitAction(self.engine.player))
        elif event_id == "view_history":
            self.engine.event_handler = HistoryViewer(self.engine)
            return False
        elif event_id == "pickup":
            return self.handle_action(PickupAction(self.engine.player))
        elif event_id == "inventory":
            self.engine.event_handler = InventoryEventHandler(self.engine, self.engine.player.inventory)
            return False
        elif event_id == "drop":
            self.engine.event_handler = InventoryDropHandler(self.engine, self.engine.player.inventory)
            return False
        elif event_id == "look":
            self.engine.event_handler = LookHandler(self.engine)
            return False
        elif event_id == "close_door":
            self.engine.event_handler = RayDirInputHandler(
                engine=self.engine,
                actor=self.engine.player,
                max_range=1,
                callback=lambda dx, dy: DoorCloseAction(self.engine.player, dx, dy)
            )
            return False
        elif event_id == "open_door":
            self.engine.event_handler = RayDirInputHandler(
                engine=self.engine,
                actor=self.engine.player,
                max_range=1,
                callback=lambda dx, dy: DoorOpenAction(self.engine.player, dx, dy)
            )
            return False
        elif event_id == "use_ability":
            self.engine.event_handler = AbilityActivateHandler(self.engine)
            return False
        elif event_id == "take_screenshot":
            time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            pic_name = time_str
            # pic_name = self.engine.player.name + "-" + time_str # bugs occur when using certain unicode chars.
            self.engine.context.save_screenshot(f"./screenshots/{pic_name}.png")
            self.engine.message_log.add_message(f"Screenshot saved as {pic_name}.png", color.needs_target)

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        action: Optional[Action] = None
        key = event.key
        player = self.engine.player

        if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]: # Check Shift Modifier
            if key == pygame.K_PERIOD:
                return "descend"
            elif key == pygame.K_COMMA:
                return "ascend"
            elif key == pygame.K_q:
                return "quit"
            elif key == pygame.K_s:
                return "save"
        else:
            if key in MOVE_KEYS:
                self.dx, self.dy = MOVE_KEYS[key]
                return "move"
            elif key in WAIT_KEYS:
                return "wait"
            elif key == pygame.K_v:
                return "view_history"
            elif key == pygame.K_g:
                return "pickup"
            elif key == pygame.K_i:
                return "inventory"
            elif key == pygame.K_d:
                return "drop"
            elif event.key == pygame.K_SLASH or event.key == pygame.K_KP_DIVIDE:
                return "look"
            elif key == pygame.K_c:
                return "close_door"
            elif key == pygame.K_o:
                return "open_door"
            elif key == pygame.K_a:
                return "use_ability"
            elif key == pygame.K_F12:
                return "take_screenshot"
            elif key == pygame.K_F11:#TODO DEBUG
                from explosion_action import ExplodeAction
                ExplodeAction(self.engine.player, False, True, radius=50, expl_dmg=3000, cause_fire=5).perform()
                return "cancel"
            elif key == pygame.K_F10:#TODO DEBUG
                for actor in self.engine.game_map.actors:
                    if actor.ai:
                        actor.ai.activate()
                return "cancel"
            elif key == pygame.K_F9:#TODO DEBUG
                self.engine.player.actor_state.is_poisoned = [1,1,0,3]
                print("ACTIVATED ALL ACTORS IN THIS LEVEL")
                return "cancel"
            elif key == pygame.K_F8:#TODO DEBUG
                import actor_factories
                x = actor_factories.dog.spawn(self.engine.game_map, self.engine.player.x + 1, self.engine.player.y)
                x.ai.activate()
                print("SPAWNED DOG")
                return "cancel"
            elif key == pygame.K_F7:#TODO DEBUG
                return "cancel"
            elif key == pygame.K_KP_PLUS:#TODO DEBUG
                self.engine.camera.zoom_in()
                return "cancel"
            elif key == pygame.K_KP_MINUS:#TODO DEBUG
                self.engine.camera.zoom_out()
                return "cancel"


class GameOverEventHandler(EventHandler):
    def handle_event(self, event_id: str) -> bool:
        tmp = super().handle_event(event_id)
        if tmp != None:
            return tmp
        if event_id == "quit":
            raise SystemExit()

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        if event.key == pygame.K_ESCAPE:
            return "quit"

CURSOR_Y_KEYS = {
    pygame.K_UP: -1,
    pygame.K_DOWN: 1,
    pygame.K_PAGEUP: -10,
    pygame.K_PAGEDOWN: 10,
}

#TODO
class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, mouse_pos) -> None:
        super().on_render(mouse_pos)  # Draw the main state as the background.
        log_console = tcod.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height, title="게임 로그", fg=color.msg_log_frame, bg=color.msg_log_bg)

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

    def ev_keydown(self, event: pygame.event.Event, pressed) -> None:
        if event.key in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.key]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.key == pygame.K_HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.key == pygame.K_END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            self.engine.event_handler = MainGameEventHandler(self.engine)

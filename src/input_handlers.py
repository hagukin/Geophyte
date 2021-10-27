from __future__ import annotations

import random

from components.inventory import Inventory
from typing import Callable, Optional, Tuple, TYPE_CHECKING, List
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
    TurnPassAction,
    SplitItem,
    EquipItem,
    UnequipItem,
    DescendAction,
    AscendAction,
    FlyAction,
    PlaceSwapAction,
    DoorUnlockAction,
    ChestTakeAction,
    ChestPutAction,
)
from base.data_loader import save_game, quit_game
from game import Game
from korean import grammar as g

import math
import tcod
import time
import color
import exceptions
import traceback

if TYPE_CHECKING:
    from ability import Ability
    from entity import SemiActor, Actor, Item, Entity


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
    def __init__(self, item_cancel_callback: Callable = None):
        """
        Args:
            item_cancel_callback:
                If there is a value(lambda function), 
                this event will call that function when the item usage has been cancelled. 
                NOTE: WARNING - you should only use item_cancel_callback when item usage has been cancelled. any other form of calling a callback function should use something else instead.
                (However, items will still get consumed)
        """
        self.help_msg = "" # message that will show up when user calls the handler.
        self.help_msg_color = color.help_msg
        self.item_cancel_callback = item_cancel_callback
        self.cursor_loc = (0,0)

    @property
    def engine(self):
        return Game.engine

    @property
    def cursor_dir(self):
        mx, my = self.engine.camera.rel_to_abs(*self.cursor_loc)
        dx, dy = mx - self.engine.player.x, my - self.engine.player.y
        if dx == 0:
            dir_x = 0
        else:
            dir_x = int(dx / abs(dx))
        if dy == 0:
            dir_y = 0
        else:
            dir_y = int(dy / abs(dy))
        return dir_x, dir_y

    def handle_events(self, event: tcod.event.Event) -> Optional[bool]:
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
            print(f"WARNING::Tried to do something impossible - {exc.args[0]}")
            return False  # Skip enemy turn on exceptions.
        except Exception as exc:
            traceback.print_exc()
            print(f"FATAL ERROR::input_handler.handle_action() - {exc.args[0]}")

        if action.free_action:
            return False
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        # Refresh
        self.cursor_loc = event.tile.x, event.tile.y

    def on_exit(self) -> Optional[Action]:
        """
        Called when the user is trying to exit or cancel an action.
        By default this returns to the main event handler.
        """
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_mousewheel(self, event: tcod.event.MouseWheel):
        return None

    def on_render(self, console: tcod.Console) -> None:
        self.engine.message_log.add_message(self.help_msg, self.help_msg_color, show_once=True)
        self.engine.render(console)


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def handle_action(self, action: Optional[Action]) -> bool:
        """Return to the main event handler when a valid action was performed."""
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler()
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
        # ESCAPE
        if self.item_cancel_callback is None:
            return self.on_exit()
        else:
            self.engine.event_handler = ItemUseCancelHandler(self.item_cancel_callback)
            return None

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """By default any mouse click exits this input handler."""
        # ESCAPE
        if self.item_cancel_callback is None:
            return self.on_exit()
        else:
            self.engine.event_handler = ItemUseCancelHandler(self.item_cancel_callback)
            return None

    def on_exit(self) -> Optional[Action]:
        """
        Called when the user is trying to exit or cancel an action.
        By default this returns to the main event handler.
        """
        self.engine.camera.reset_dxdy() # reset camera position
        self.engine.update_fov() # Prevent any sort of visual effects lasting after taking an input. (e.g. magic mapping)
        self.engine.event_handler = MainGameEventHandler()
        return None


class ItemUseCancelHandler(AskUserEventHandler):
    def __init__(self, item_cancel_callback: Callable):
        super().__init__(item_cancel_callback)

    def on_render(self, console: tcod.Console,) -> None:
        super().on_render(console)
        self.engine.draw_window(console, text="정말 아이템 사용을 취소하시겠습니까? 아이템은 여전히 소모될 수 있습니다. (Y/N)", title="아이템 사용 취소", frame_fg=color.red, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            self.engine.event_handler = MainGameEventHandler()
            return self.item_cancel_callback(True)# passing True (action is cancelled)
        elif event.sym == tcod.event.K_n or event.sym == tcod.event.K_ESCAPE:
            return self.item_cancel_callback(False)# passing False (action is not cancelled)


class SaveInputHandler(AskUserEventHandler):

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.draw_window(console, text="정말 현재 게임을 저장하시겠습니까? (Y/N)", title="저장", frame_fg=color.lime, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        engine = self.engine

        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            self.engine.event_handler = MainGameEventHandler()
            self.engine.message_log.add_message(f"게임 저장됨.", color.lime, stack=False)
            save_game(player=player, engine=engine)
        elif event.sym == tcod.event.K_n or event.sym == tcod.event.K_ESCAPE:
            self.engine.message_log.add_message(f"저장 취소됨.", color.lime, stack=False)
        return super().ev_keydown(event)


class DangerousTileWalkHandler(AskUserEventHandler):
    def __init__(self, dx: int, dy: int):
        super().__init__()
        self.dx = dx
        self.dy = dy

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.draw_window(console, text="정말 해당 위치로 이동하시겠습니까? (Y/N)", title="위험할 수 있는 타일로 이동", frame_fg=color.red, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            self.on_exit()
            return MovementAction(self.engine.player, self.dx, self.dy).perform()
        elif event.sym == tcod.event.K_n or event.sym == tcod.event.K_ESCAPE:
            self.on_exit()
        return super().ev_keydown(event)


class GameClearInputHandler(AskUserEventHandler): #TODO Unfinished
    """Renders Game Over Screen and wait for player to quit.
        TODO: Render player History"""
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.draw_window(console, text="(v):로그 살펴보기 | (/):맵 둘러보기 | F12:스크린샷 | ESC:게임 종료 | (g):아직 할 일이 남아있다", title="승리했습니다!", text_fg=color.black,
                                frame_fg=color.black, frame_bg=color.gold)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        key = event.sym
        if key == tcod.event.K_ESCAPE:
            self.engine.event_handler = GameQuitHandler(prev_event_handler=self)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer()
        elif key == tcod.event.K_SLASH or key == tcod.event.K_KP_DIVIDE:
            self.engine.event_handler = LookHandler()
        elif key == tcod.event.K_F12:
            time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            pic_name = time_str
            # pic_name = self.engine.player.name + "-" + time_str # bugs occur when using certain unicode chars.
            self.engine.context.save_screenshot(f"./screenshots/{pic_name}.png")
            self.engine.message_log.add_message(f"스크린샷 저장됨. {pic_name}.png", color.cyan)
        elif key == tcod.event.K_g:
            self.engine.revert_victory()
            self.engine.event_handler = MainGameEventHandler()

    def ev_mousebuttondown(self, event: tcod.event.KeyDown) -> None:
        return None

class AbilityEventHandler(AskUserEventHandler):
    """
    This handler lets the user select an ability to use / cast.
    What happens then depends on the subclass.
    """

    def __init__(self):
        super().__init__()
        self.TITLE = "능력"

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
        y_space = 0
        width = self.engine.config["screen_width"] - (x_space * 2)

        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height, # 2 extra lines for bottom
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

        console.print(x + x_space + 1, height - 1, "/키:능력 정렬 | ESC:취소", color.gui_inventory_fg)

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
        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT):
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
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            return None

    def on_ability_selected(self, ability: Ability) -> Optional[Action]:
        """Called when the user selects a valid ability."""
        raise NotImplementedError()


class AbilityActivateHandler(AbilityEventHandler):
    """Handle using an ability called from inventory."""

    def __init__(self):
        super().__init__()
        self.TITLE = "능력"

    def on_ability_selected(self, ability: Ability) -> Optional[Action]:
        """Return the action for the selected item."""
        self.engine.event_handler = AbilityActionSelectHandler(ability)
        return None


class AbilityActionSelectHandler(AskUserEventHandler):
    """Handle choosing the action for selected ability."""

    def __init__(self, ability: Ability):
        super().__init__()
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
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(c) 마법/기술 사용", fg=color.gui_item_action)
            else:
                console.print(x + x_space + 1, y + desc_height + 2 + y_space, "(없음)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym

        if key in self.possible_keys:
            if key == tcod.event.K_c:
                return self.ability.activatable.get_action(self.engine.player)
        elif key == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler()
            return None
        else:
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            self.engine.event_handler = MainGameEventHandler()
            return None


class StorageSelectEventHandler(AskUserEventHandler):
    """
    Handles selecting Item or Items from given inventory component.
    NOTE: Seperated from ability select handler
    """
    def __init__(
            self,
            inventory_component: Inventory,
            show_only_types: Tuple[InventoryOrder] =None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
            hide_not_tradable: bool = False,
            hide_not_owned: bool = False, #e.g. stolen items
            hide_equipped: bool = False,
            render_sell_price: bool = False,
            item_cancel_callback: Callable = None,
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
        Vars:
            display_sell_price:
                bool. if True, the input handler will render the selling price information of all items in stroage.
        """
        super().__init__(item_cancel_callback)
        self.inventory_component = inventory_component
        self.show_only_types = show_only_types
        self.show_only_status = show_only_status
        self.show_if_satisfy_both = show_if_satisfy_both
        self.hide_not_tradable = hide_not_tradable
        self.hide_not_owned = hide_not_owned
        self.hide_equipped = hide_equipped
        if hasattr(self.inventory_component.parent, "name"):
            self.TITLE = f"{self.inventory_component.parent.name}"
        else:
            self.TITLE = ""
        self.render_sell_price = render_sell_price

    def get_item_rendered_text(self, item: Item, item_key, choose_multiple: bool):
        """
        Returns:
            item_text, item_damage_text, item_state_text, item_equip_text, item_text_color
        """
        item_text = f"({item_key}) "

        # if item is a cash, display amount in front of the name
        if item.counter_at_front:
            item_text += f"{item.stack_count} "

        if item.item_state.check_if_full_identified(): # Display BUC only if fully identified
            if item.equipable:
                item_text += f"{item.equipable.upgrade:+d} "

            if item.item_state.BUC == 0:
                item_text += "저주받지 않은 "
            elif item.item_state.BUC >= 1:
                item_text += "축복받은 "
            elif item.item_state.BUC <= -1:
                item_text += "저주받은 "

        item_text += f"{item.name} "
        item_count = ""
        item_damage_text = ""
        item_state_text = ""
        item_equip_text = ""
        item_buy_price_text = ""
        item_sell_price_text = ""
        item_text_color = None

        # Display item counts if it is greater than 1
        if item.stack_count > 1 and not item.counter_at_front:
            item_count += f"(x{item.stack_count}) "

        # Assign color of its type
        if item.item_type.value == InventoryOrder.POTION.value:
            item_text_color = color.gui_potion_name
        elif item.item_type.value == InventoryOrder.SCROLL.value:
            item_text_color = color.gui_scroll_name
        elif item.item_type.value == InventoryOrder.ARMOR.value:
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

            if item.item_state.equipped_region:
                from util import equip_region_name_to_str
                item_equip_text += f"[장착됨-{equip_region_name_to_str(item.item_state.equipped_region)}] "
        else:
            if item.item_state.equipped_region:
                item_equip_text += f"[equipped on {item.item_state.equipped_region}] "

        # Display the price of the item if it is currently being sold
        if item.item_state.is_being_sold_from:
            item_buy_price_text += f"<개당 {item.price_of_single_item(is_shopkeeper_is_selling=True, discount=1 - self.engine.player.discount_value())}샤인, 미구매> "

        if self.render_sell_price:
            if item.stack_count == 1:
                item_sell_price_text += f"<{item.price_of_single_item(is_shopkeeper_is_selling=False, discount=0.5)}샤인에 판매 가능>"
            else:
                item_sell_price_text += f"<{item.stack_count}개 총 {item.price_of_all_stack(is_shopkeeper_is_selling=False, discount=0.5)}샤인에 판매 가능>"

        return item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_buy_price_text, item_sell_price_text, item_text_color

    def render_item(
        self,
        xpos, ypos,
        item_text: str,
        item_count: str,
        item_damage_text: str,
        item_state_text: str,
        item_equip_text: str,
        item_buy_price_text: str,
        item_sell_price_text: str,
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
        self.engine.console.print(xpos, ypos + y_padding, item_buy_price_text, fg=color.gui_item_price)
        xpos += len(item_buy_price_text)
        self.engine.console.print(xpos, ypos + y_padding, item_sell_price_text, fg=color.gui_item_sell_price)

    def check_should_render_item(self, item: Item) -> bool:
        if not item.tradable and self.hide_not_tradable:
            return False
        if item.item_state.is_being_sold_from and self.hide_not_owned:
            return False
        if item.item_state.equipped_region != None and self.hide_equipped:
            return False
        if self.show_if_satisfy_both:
            if (self.check_should_render_type(item) and self.check_should_render_status(item)):
                return True
        else:
            if (self.check_should_render_type(item) or self.check_should_render_status(item)):
                return True
        return False

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
    def choice_confirmed(self):
        """There is no 'Choice' in single selection, so this function does nothing."""
        return None

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
        y_space = 0
        width = self.engine.config["screen_width"] - (x_space * 2)

        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height, # 2 extra line for "press slash to sort inventory"
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

                item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_buy_price_text, item_sell_price_text, item_text_color = self.get_item_rendered_text(item, item_key, choose_multiple=False)
                xpos = x + x_space + 1
                ypos = y + y_space + 1
                self.render_item(xpos, ypos, item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_buy_price_text, item_sell_price_text, item_text_color, y_padding=y_padding)
        else:
            console.print(x + x_space + 1, y + y_space + 1, "(없음)", color.gray)
        console.print(x + x_space + 1, height - 1, "/키:인벤토리 정렬 | 아이템에 해당하는 알파뱃:아이템 상호작용 | ESC:취소", color.gui_inventory_fg)

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
        elif event.sym in CONFIRM_KEYS: # Confirm choices
            return self.choice_confirmed()

        # Check modifier
        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT):
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
                if not self.check_should_render_item(selected_item):  # Cannot select hidden item index.
                    self.engine.message_log.add_message(f"잘못된 입력입니다.", color.invalid)
                    return None
                return self.on_item_selected(selected_item)
            else:
                self.engine.message_log.add_message(f"잘못된 입력입니다.", color.invalid)
                return None
        except KeyError:
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            return None
        except:
            import traceback
            traceback.print_exc()

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
            inventory_component: Inventory,
            callback: Callable,
            title: str = "인벤토리",
            show_only_types: Optional[Tuple[InventoryOrder,...]] =None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
            hide_not_tradable: bool = False,
            hide_not_owned: bool = False,  # e.g. stolen items
            hide_equipped: bool = False,
            render_sell_price: bool = False,
            item_cancel_callback: Callable = None,
        ):
        super().__init__(inventory_component, show_only_types, show_only_status, show_if_satisfy_both, hide_not_tradable, hide_not_owned, hide_equipped, render_sell_price, item_cancel_callback)
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
            inventory_component: Inventory,
            show_only_types: Tuple[InventoryOrder] =None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
        ):
        super().__init__(inventory_component, show_only_types, show_only_status, show_if_satisfy_both)
        self.TITLE = "인벤토리"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Return the action for the selected item."""
        self.engine.event_handler = InventoryActionSelectHandler(item)
        return None


class InventoryActionSelectHandler(AskUserEventHandler):
    """Handle choosing the action for selected item."""

    def __init__(self, item):
        super().__init__()
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

        if self.item.usable:
            self.possible_actions.append("use")
            self.possible_keys.append(tcod.event.K_y)
        if self.item.readable:
            self.possible_actions.append("read")
            self.possible_keys.append(tcod.event.K_r)
        if self.item.quaffable:
            self.possible_actions.append("quaff")
            self.possible_keys.append(tcod.event.K_q)
        if self.item.edible:
            self.possible_actions.append("eat")
            self.possible_keys.append(tcod.event.K_a)
        if self.item.equipable and self.item.item_state.equipped_region == None:
            self.possible_actions.append("equip")
            self.possible_keys.append(tcod.event.K_e)
        if self.item.equipable and self.item.item_state.equipped_region != None:
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
        console.print(x + x_space + 1, y + y_space + 2, "(/) 아이템 정보", fg=color.gui_item_action)

        # print possible actions
        for i, action in enumerate(self.possible_actions):
            if action == "use":
                console.print(x + x_space + 1, y + i + desc_height + 2 + y_space, "(y) 사용하기", fg=color.gui_item_action)
            elif action == "read":
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

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym

        if key == tcod.event.K_SLASH or key == tcod.event.K_KP_DIVIDE:
            from book import ItemInfoHandler
            self.engine.event_handler = ItemInfoHandler(item=self.item)
            return None

        if key in self.possible_keys:
            if key == tcod.event.K_y:
                return self.item.usable.get_action(self.engine.player)
            elif key == tcod.event.K_r:
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
                self.engine.event_handler = InventorySplitHandler(self.item)
                return None
            elif key == tcod.event.K_t:
                self.item.throwable.get_action(self.engine.player)
                return None
            elif key == tcod.event.K_d:
                return DropItem(self.engine.player, self.item)
        elif key == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler()
            return None
        else:
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            self.engine.event_handler = MainGameEventHandler()
            return None


class InventorySplitHandler(AskUserEventHandler):
    """Handle dropping an inventory item."""

    def __init__(self, item):
        super().__init__()
        self.item = item
        if item.stack_count > 1:
            self.TITLE = f"{self.item.name} (x{self.item.stack_count})"
        else:
            self.TITLE = f"{self.item.name}"
        self.split_amount = 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        height = 5 #+1 for split_amount displaying
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
        console.print(x + x_space + 1, height + 3, "+,-키:갯수 조작 | 쉬프트를 누른채 조작:10개씩 선택 | 엔터:확인 | ESC:취소", color.gui_inventory_fg)
        console.print(x + x_space + 1, y + y_space + 2, f"{self.split_amount}개 선택됨.", fg=color.gui_item_description)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym

        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT):  # Check Shift Modifier
            if key == tcod.event.K_PLUS or key == tcod.event.K_KP_PLUS or key == tcod.event.K_EQUALS:
                if self.split_amount < self.item.stack_count - 10:
                    self.split_amount += 10
                else:
                    self.engine.message_log.add_message(f"최대 {self.item.stack_count - 1}개 만큼 선택할 수 있습니다.", color.invalid, show_once=True)
            elif key == tcod.event.K_MINUS or key == tcod.event.K_KP_MINUS:
                if self.split_amount > 10:
                    self.split_amount -= 10
                else:
                    self.engine.message_log.add_message("1개 이상을 선택하셔야 합니다.", color.invalid, show_once=True)
        else:
            if key == tcod.event.K_PLUS or key == tcod.event.K_KP_PLUS or key == tcod.event.K_EQUALS:
                if self.split_amount < self.item.stack_count - 1:
                    self.split_amount += 1
                else:
                    self.engine.message_log.add_message(f"최대 {self.item.stack_count - 1}개 만큼 선택할 수 있습니다.", color.invalid, show_once=True)
            elif key == tcod.event.K_MINUS or key == tcod.event.K_KP_MINUS:
                if self.split_amount > 1:
                    self.split_amount -= 1
                else:
                    self.engine.message_log.add_message("1개 이상을 선택하셔야 합니다.", color.invalid, show_once=True)
            elif key == tcod.event.K_ESCAPE:
                self.engine.event_handler = MainGameEventHandler()
                return None
            elif key in CONFIRM_KEYS:
                return SplitItem(self.engine.player, self.item, self.split_amount)
            else:
                self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
                self.engine.event_handler = MainGameEventHandler()
                return None


class SleepTurnSelectHandler(AskUserEventHandler):
    """Handle dropping an inventory item."""

    def __init__(self):
        super().__init__()
        self.TITLE = f"몇 턴 간 주무시겠습니까?"
        self.sleep_turn = 10

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        height = 5
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
        console.print(x + x_space + 1, height + 3, "+,-키:턴수 조작 | 쉬프트를 누른채 조작:10턴씩 선택 | 엔터:확인 | ESC:취소", color.gui_inventory_fg)
        console.print(x + x_space + 1, y + y_space + 2, f"{self.sleep_turn}턴 선택됨.", fg=color.gui_item_description)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym

        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT):  # Check Shift Modifier
            if key == tcod.event.K_PLUS or key == tcod.event.K_KP_PLUS or key == tcod.event.K_EQUALS:
                if self.sleep_turn < 90:
                    self.sleep_turn += 10
                else:
                    self.engine.message_log.add_message(f"최대 99턴까지 선택할 수 있습니다.", color.invalid, show_once=True)
            elif key == tcod.event.K_MINUS or key == tcod.event.K_KP_MINUS:
                if self.sleep_turn >= 20:
                    self.sleep_turn -= 10
                else:
                    self.engine.message_log.add_message("10턴 이상을 선택하셔야 합니다.", color.invalid, show_once=True)
        else:
            if key == tcod.event.K_PLUS or key == tcod.event.K_KP_PLUS or key == tcod.event.K_EQUALS:
                if self.sleep_turn < 99:
                    self.sleep_turn += 1
                else:
                    self.engine.message_log.add_message(f"최대 99턴까지 선택할 수 있습니다.", color.invalid, show_once=True)
            elif key == tcod.event.K_MINUS or key == tcod.event.K_KP_MINUS:
                if self.sleep_turn > 10:
                    self.sleep_turn -= 1
                else:
                    self.engine.message_log.add_message("10턴 이상을 선택하셔야 합니다.", color.invalid, show_once=True)
            elif key == tcod.event.K_ESCAPE:
                self.engine.event_handler = MainGameEventHandler()
                return None
            elif key in CONFIRM_KEYS: # Sleep
                self.engine.event_handler = MainGameEventHandler()
                self.engine.player.actor_state.apply_sleeping([0,self.sleep_turn], sleep_on_will=True) # Is not forced.
                return None
            else:
                self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
                self.engine.event_handler = MainGameEventHandler()
                return None


class StorageSelectMultipleEventHandler(StorageSelectEventHandler):
    """
    Inherit this class if the action requires selecting multiple items.
    e.g. Opening and taking items from chest

    A child of this class MUST modify the choice_confirmed() method to its use.
    """
    def __init__(
            self,
            inventory_component: Inventory,
            show_only_types: Tuple[InventoryOrder] =None,
            show_only_status: Tuple[str] = None,
            show_if_satisfy_both: bool = True,
            render_sell_price: bool = False,
            hide_not_tradable: bool = False,
            hide_not_owned: bool = False,
            hide_equipped: bool = False,
            ):
        super().__init__(inventory_component, show_only_types, show_only_status, show_if_satisfy_both, render_sell_price, hide_not_tradable, hide_not_owned, hide_equipped)
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
        y_space = 0
        width = self.engine.config["screen_width"] - (x_space * 2)

        console.draw_frame(
            x=x + x_space,
            y=y + y_space,
            width=width,
            height=height, # 2 extra line for "press slash to sort inventory"
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

                item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_buy_price_text, item_sell_price_text, item_text_color = self.get_item_rendered_text(item, item_key, choose_multiple=True)
                xpos = x + x_space + 1
                ypos = y + y_space + 1
                self.render_item(xpos, ypos, item_text, item_count, item_damage_text, item_state_text, item_equip_text, item_buy_price_text, item_sell_price_text, item_text_color, y_padding=y_padding)
        else:
            console.print(x + x_space + 1, y + y_space + 1, "(없음)", color.gray)

        console.print(x + x_space + 1, height - 1, "/키:인벤토리 정렬 | 엔터:확인 | ESC:취소", color.gui_inventory_fg)

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
        elif event.sym in CONFIRM_KEYS: # Confirm choices
            return self.choice_confirmed()

        # Check modifier
        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT):
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
                if not self.check_should_render_item(selected_item):  # Cannot select hidden item index.
                    self.engine.message_log.add_message(f"잘못된 입력입니다.", color.invalid)
                    return None
                self.on_item_selected(selected_item)
                return None
            else:
                self.engine.message_log.add_message(f"잘못된 입력입니다.", color.invalid)
                return None
        except:
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            return None

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Called when the user selects a valid item."""
        if item in self.selected_items:
            self.selected_items.remove(item)
        else:
            self.selected_items.add(item)


class NonHostileBumpHandler(AskUserEventHandler):
    def __init__(self, target: Entity):
        """
        Vars:
            can_pay_shopkeeper:
                인풋으로 받은 타겟이 shopkeeper이고, 또 플레이어가 현재 빚을 진 상태인 경우.
                만약 이 이벤트 핸들러가 상인이 아닌 다른 무언가에 의해 호출되었다면 이 값은 사용되지 않는다.
        """
        super().__init__()
        self.target = target
        self.TITLE = "무엇을 하시겠습니까?"
        self.can_pay_shopkeeper = False
        self.can_sell_to_shopkeeper = False
        self.update_pay_status()

    def update_pay_status(self):
        if hasattr(self.target, "ai"):
            if self.target.ai:
                from shopkeeper import Shopkeeper_Ai
                if isinstance(self.target.ai, Shopkeeper_Ai):
                    if not self.engine.player in self.target.ai.thieves: # Can sell/buy items from shopkeeper only if you are not a thief.
                        self.can_sell_to_shopkeeper = True
                        if self.target.ai.has_dept(self.engine.player):
                            self.can_pay_shopkeeper = True

    def on_render(self, console: tcod.Console) -> None:
        """
        Render an action selection menu, which displays the possible actions of the selected item.
        """
        super().on_render(console)

        number_of_possible_actions = self.target.how_many_bump_action_possible(self.engine.player)
        height = 5 + 2*number_of_possible_actions
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

        if self.target.check_if_bump_action_possible(self.engine.player, "open"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(o) - 문을 연다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "close"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(c) - 문을 닫는다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "unlock"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(u) - 문의 잠금을 해제한다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "break"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(b) - 문을 힘으로 개방한다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "takeout"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(t) - 무언가를 꺼낸다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "putin"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(i) - 무언가를 넣는다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "move"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(m) - 해당 칸으로 이동한다", fg=color.white)
            y_pad += 2
        if self.can_pay_shopkeeper: # NOTE: does not check for "purchase" keyword
            console.print(x + x_space + 1, y + y_space + y_pad, "(p) - 소지중인 판매물품들을 구매한다", fg=color.white)
            y_pad += 2
        if self.can_sell_to_shopkeeper: # NOTE: does not check for "sell" keyword
            console.print(x + x_space + 1, y + y_space + y_pad, "(e) - 인벤토리에서 물품들을 선택해 판매한다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "swap"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(s) - 위치를 바꾼다", fg=color.white)
            y_pad += 2
        if self.target.check_if_bump_action_possible(self.engine.player, "attack") or self.target.check_if_bump_action_possible(self.engine.player, "force_attack"):
            console.print(x + x_space + 1, y + y_space + y_pad, "(a) - 공격한다", fg=color.white)
            y_pad += 2
        console.print(x + x_space + 1, y + y_space + y_pad, "ESC - 취소", fg=color.white)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        from chest_factories import ChestSemiactor
        from entity import Actor
        key = event.sym
        dx, dy = self.target.x - self.engine.player.x, self.target.y - self.engine.player.y

        if not self.target.blocks_movement and key == tcod.event.K_m:
            return self.target.get_bumpaction(self.engine.player, "move")
        elif self.can_pay_shopkeeper and key == tcod.event.K_p:
            self.engine.event_handler = MainGameEventHandler()
            self.target.ai.sell_all_picked_ups(customer=self.engine.player)
            return None
        elif self.can_sell_to_shopkeeper and key == tcod.event.K_e:
            self.engine.event_handler = SellItemsHandler(sell_to=self.target)
            return None
        elif self.target.swappable and key == tcod.event.K_s:
            return self.target.get_bumpaction(self.engine.player, "swap")
        elif isinstance(self.target, Actor) and key == tcod.event.K_a:
            if self.target.check_if_bump_action_possible(self.engine.player, "force_attack"): # prioritize force_attack
                return self.target.get_bumpaction(self.engine.player, "force_attack")
            else:
                return self.target.get_bumpaction(self.engine.player, "attack")
        elif key == tcod.event.K_t and isinstance(self.target, ChestSemiactor):
            return self.target.get_bumpaction(self.engine.player, "takeout")
        elif key == tcod.event.K_i and isinstance(self.target, ChestSemiactor):
            return self.target.get_bumpaction(self.engine.player, "putin")
        elif key == tcod.event.K_o:
            return self.target.get_bumpaction(self.engine.player, "open")
        elif key == tcod.event.K_c:
            return self.target.get_bumpaction(self.engine.player, "close")
        elif key == tcod.event.K_u:
            return self.target.get_bumpaction(self.engine.player, "unlock")
        elif key == tcod.event.K_b:
            return self.target.get_bumpaction(self.engine.player, "break")
        elif key == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler()
            return None
        else:
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            self.engine.event_handler = MainGameEventHandler()
            return None


class SellItemsHandler(StorageSelectMultipleEventHandler):
    def __init__(self, sell_to: Entity):
        super().__init__(self.engine.player.inventory, render_sell_price=True, hide_not_tradable=True, hide_not_owned=True, hide_equipped=True)
        self.TITLE = "판매할 아이템들을 선택하세요."
        self.sell_to = sell_to
        self.engine.message_log.add_message(
            "아이템에 해당하는 알파뱃:아이템 선택/취소 | 엔터:확인 | ESC:나가기", color.help_msg
        )

    def choice_confirmed(self):
        """
        Remove the selected items from player's inventory and place them in shops.
        """
        if hasattr(self.sell_to, "ai"):
            from shopkeeper import Shopkeeper_Ai
            if isinstance(self.sell_to.ai, Shopkeeper_Ai):
                self.sell_to.ai.purchase_items(customer=self.engine.player, items=list(self.selected_items))
                return TurnPassAction(entity=self.engine.player)
        return self.on_exit()


class ChestTakeEventHandler(StorageSelectMultipleEventHandler):
    def __init__(self, chest_inventory_component: Inventory):
        super().__init__(chest_inventory_component)
        if hasattr(chest_inventory_component.parent, "name"):
            self.TITLE = f"{chest_inventory_component.parent.name}에서 가져갈 아이템을 선택하세요."
        else:
            self.TITLE = "가져갈 아이템들을 선택하세요."
        self.engine.message_log.add_message(
            "아이템에 해당하는 알파뱃:아이템 선택/취소 | 엔터:확인 | ESC:나가기", color.help_msg
        )
        self.chest_inv = chest_inventory_component


    def choice_confirmed(self):
        """
        Move the selected items to player's inventory.
        """
        return ChestTakeAction(entity=self.engine.player, entities=list(self.selected_items), chest_storage=self.chest_inv)


class ChestPutEventHandler(StorageSelectMultipleEventHandler):
    """Handle putting in an inventory item to a chest."""
    def __init__(self, actor_inventory_component: Inventory, chest_inventory_component: Inventory):
        super().__init__(actor_inventory_component)
        if hasattr(chest_inventory_component.parent, "name"):
            self.TITLE = f"{chest_inventory_component.parent.name}에 넣을 아이템을 선택하세요."
        else:
            self.TITLE = "넣을 아이템들을 선택하세요."
        self.engine.message_log.add_message(
            "아이템에 해당하는 알파뱃:아이템 선택/취소 | 엔터:확인 | ESC:나가기", color.help_msg
        )
        self.actor_inv = actor_inventory_component
        self.chest_inv = chest_inventory_component


    def choice_confirmed(self):
        """
        Remove the selected items from player's inventory.
        """
        return ChestPutAction(entity=self.engine.player, entities=list(self.selected_items), chest_storage=self.chest_inv)


class InventoryDropHandler(StorageSelectMultipleEventHandler):
    """Handle dropping an inventory item."""
    def __init__(self, inventory_component: Inventory):
        super().__init__(inventory_component)
        self.TITLE = "드랍할 아이템들을 선택하세요."
        self.engine.message_log.add_message(
            "아이템에 해당하는 알파뱃:아이템 선택/취소 | 엔터:확인 | ESC:나가기", color.help_msg
        )

    def choice_confirmed(self):
        """
        Drop all the selected items.
        """
        for item in self.selected_items:
            DropItem(self.engine.player, item).perform()

        return TurnPassAction(self.engine.player)  # Return an action if the item is the last one to drop to cost a turn


class PickupMultipleHandler(StorageSelectMultipleEventHandler):
    """Handle picking up an multiple items."""
    def __init__(self, inventory_component: Inventory):
        super().__init__(inventory_component)
        self.TITLE = "주울 아이템들을 선택하세요."
        self.engine.message_log.add_message(
            "아이템에 해당하는 알파뱃:아이템 선택/취소 | 엔터:확인 | ESC:나가기", color.help_msg
        )

    def choice_confirmed(self):
        """
        Pick up all the selected items.
        """
        PickupAction(self.engine.player).pickup_given_items(items=list(self.selected_items))
        return TurnPassAction(self.engine.player)  # Return an action if the item is the last one to drop to cost a turn


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""
    def __init__(self, item_cancel_callback: Callable = None):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(item_cancel_callback)
        self.help_msg += "이동키:커서 조작 | CTRL키를 누른 채로 이동:카메라 조작 | 엔터:확인 | ESC:취소"
        player = self.engine.player
        self.cursor_loc = self.engine.camera.abs_to_rel(player.x, player.y) # use player coordinates instead of 0,0

    def render_cursor(self, console) -> None:
        x, y = self.cursor_loc
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        self.render_cursor(console)

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        # Refresh
        self.cursor_loc = self.engine.clamp_mouse_on_map_rel(event.tile.x, event.tile.y)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """Check for key movement or confirmation keys.
        When ctrl key is pressed down, the camera will move instead of the cursor."""
        key = event.sym
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]

            # Press down ctrl to move camera
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                if not self.engine.camera.move(dx, dy):
                    self.engine.message_log.add_message("더 이상 카메라를 움직일 수 없습니다.", fg=color.impossible)
                self.cursor_loc = self.engine.clamp_mouse_on_map_rel(*self.cursor_loc)
                return None

            x, y = self.cursor_loc
            x += dx
            y += dy
            self.cursor_loc = self.engine.clamp_mouse_on_map_rel(x, y)

            return None
        elif key in CONFIRM_KEYS:
            abs_cursor_loc = self.engine.camera.rel_to_abs(*self.cursor_loc)
            return self.on_index_selected(*abs_cursor_loc)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        """Left click confirms a selection."""
        abs_cursor_loc = self.engine.camera.rel_to_abs(*self.cursor_loc)
        if self.engine.camera.in_bounds(*abs_cursor_loc):# Only accepts the input if mouse is in gamemap boundaries
            if event.button == tcod.event.BUTTON_LEFT:
                return self.on_index_selected(*abs_cursor_loc)
        else:
            self.engine.message_log.add_message("맵 안의 영역을 클릭하세요.", fg=color.invalid)
            if self.item_cancel_callback != None:
                return self.item_cancel_callback(0)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""
    def __init__(self, item_cancel_callback: Callable = None):
        super().__init__(item_cancel_callback)

    def on_index_selected(self, x: int, y: int) -> None:
        """Return to main handler."""
        from entity import Actor, Item, SemiActor
        entity = self.engine.game_map.get_any_type_entity_prioritize_actor_item_semiactor(x=x, y=y) # View entity

        if isinstance(entity, Actor):
            from book import MonsterInfoHandler
            self.engine.event_handler = MonsterInfoHandler(entity, page=None)
            return None
        elif isinstance(entity, Item):
            from book import ItemInfoHandler
            self.engine.event_handler = ItemInfoHandler(entity, page=None)
            return None
        elif isinstance(entity, SemiActor):
            from book import SemiActorInfoHandler
            self.engine.event_handler = SemiActorInfoHandler(entity, page=None)
            return None
        else:
            self.on_exit()


class MagicMappingLookHandler(LookHandler):
    """Lets the player look around using the keyboard."""
    def __init__(
        self, callback: Callable[[Tuple[int, int]], Optional[Action]] #Has no revert callback parameter
    ):
        super().__init__()

        self.callback = callback

    def on_exit(self) -> Optional[Action]:
        """Called when the user is trying to exit or cancel an action."""
        super().on_exit()
        return self.callback(0)


class SelectDirectionHandler(SelectIndexHandler):
    """Handles asking the user for an index on the map."""
    def __init__(self, item_cancel_callback: Callable = None):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(item_cancel_callback)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Called when an index is selected."""
        raise NotImplementedError()


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""
    def __init__(self, callback: Callable[[Tuple[int, int]], Optional[Action]], item_cancel_callback: Callable = None):
        super().__init__(item_cancel_callback=item_cancel_callback)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""
    def __init__(
        self,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
        item_cancel_callback: Callable = None,
    ):
        super().__init__(item_cancel_callback)
        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        # Use relative coordinates for rendering
        x, y = self.cursor_loc

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
        actor: Actor,
        max_range: int,
        callback: Callable, # Callable[[Tuple[int, int]], Optional[Action]]
        item_cancel_callback: Callable = None,
    ):
        super().__init__(item_cancel_callback)
        self.actor = actor
        self.max_range = max_range
        self.callback = callback
        self.target = None

    @property
    def throw_range(self):
        """
        Can be both static and non static.
        RayRangedInputHandler - static
        RayRangedWithDirectionInputHandler - nonstatic (user decides the range)
        """
        return self.max_range

    def get_path(self) -> Tuple[List[Tuple[int,int]], int, int]:
        """
        Calculate the estimated pathway of the ray.
        NOTE: The function will always check for a collision
        regardless of whether the ray penetrates objects or not.
        """
        dx, dy = self.cursor_dir
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

        return path, dest_x, dest_y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        path, dest_x, dest_y = self.get_path()

        range_count = 0
        while len(path) > 0:
            loc = path.pop(0)
            range_count += 1
            if range_count > self.throw_range:
                break
            # Use relative coords for rendering
            if self.engine.camera.in_bounds(abs_x=loc[0], abs_y=loc[1]):# Prevents the yellow guide line from going out the camera boundaries
                rel_x, rel_y = self.engine.camera.abs_to_rel(abs_x=loc[0], abs_y=loc[1])
                console.tiles_rgb["bg"][rel_x, rel_y] = color.ray_path
            else:
                continue

        self.dx, self.dy = self.cursor_dir
        self.render_cursor(console)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        self.engine.refresh_screen()
        return self.callback((self.dx, self.dy))


class RayRangedWithDistanceInputHandler(RayRangedInputHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""
    def __init__(
        self,
        actor: Actor,
        max_range: int,
        callback: Callable, # Callable[[Tuple[int, int]], int, Optional[Action]]
        item_cancel_callback: Callable = None,
    ):
        super().__init__(actor, max_range, callback, item_cancel_callback)

    @property
    def cursor_min_dist_toward_dxdy(self) -> int:
        """
        Return:
            Positive integer.

        . . . . *
        . . . . .
        @ + + + +

        (* - cursor, + - range)

        -> return 4 (since dy = 0, ignore cursor's dy distance)

        . . . . .
        . . + . *
        . + . . .
        @ . . . .

        -> return 2 (since dx & dy are both non-zero, min(4, 2) = 2)
        """
        cx, cy = self.engine.camera.rel_to_abs(*self.cursor_loc)
        cdx, cdy = abs(cx - self.actor.x), abs(cy - self.actor.y) # distance
        if self.cursor_dir[0] != 0 and self.cursor_dir[1] != 0:
            return min(cdx, cdy)
        elif self.cursor_dir[0] != 0:
            return cdx
        else:
            return cdy

    @property
    def throw_range(self):
        return min(self.max_range, self.cursor_min_dist_toward_dxdy)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        self.engine.refresh_screen()
        return self.callback((self.dx, self.dy), self.throw_range)



class RayDirInputHandler(SelectDirectionHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""
    def __init__(
        self,
        actor: Actor,
        max_range: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__()
        self.actor = actor
        self.max_range = max_range
        self.callback = callback
        self.target = None
        self.engine.message_log.add_message(
                "이동키 혹은 마우스:방향 선택 | 엔터:확인 | ESC:취소", color.help_msg
            )

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        dx, dy = self.cursor_dir
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
                rel_x, rel_y = self.engine.camera.abs_to_rel(abs_x=loc[0], abs_y=loc[1])
                console.tiles_rgb["bg"][rel_x, rel_y] = color.ray_path
            else:
                continue

        self.dx = dx
        self.dy = dy

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        self.engine.refresh_screen()
        return self.callback(self.dx, self.dy)


class QuitInputHandler(AskUserEventHandler):
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.draw_window(console, text="정말 현재 게임을 종료하시겠습니까? 모든 저장하지 않은 내역은 지워집니다. (Y/N)", title="Quit", frame_fg=color.lime, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        engine = self.engine

        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            self.engine.event_handler = MainGameEventHandler()
            save_game(player=player, engine=engine)
            quit_game()
            return None
        elif event.sym == tcod.event.K_n or event.sym == tcod.event.K_ESCAPE:
            self.engine.message_log.add_message(f"취소됨.", color.lime, stack=False)
        return super().ev_keydown(event)


class ForceAttackInputHandler(AskUserEventHandler):
    def __init__(self, melee_action: MeleeAction, item_cancel_callback: Callable = None, ):
        super().__init__(item_cancel_callback)
        self.melee_action = melee_action

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.draw_window(console, text="정말로 공격하시겠습니까? (Y/N)", title="공격 확인", frame_fg=color.red, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            return self.melee_action
        elif event.sym == tcod.event.K_n or event.sym == tcod.event.K_ESCAPE:
            pass
            #self.engine.message_log.add_message(f"취소됨.", color.lime, stack=False)
        return super().ev_keydown(event)


class PauseGameEventHandler(AskUserEventHandler):
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.draw_window(
            self.engine.console,
            text="(c):조작키 | (h):도움말 | (o):옵션 | ESC:취소",
            title="일시정지",
            frame_fg=color.white,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None
        key = event.sym
        player = self.engine.player

        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT): # Check Shift Modifier
            return None
        else:
            if key == tcod.event.K_c:
                self.engine.event_handler = DisplayControlEventHandler()
            elif key == tcod.event.K_h:
                self.engine.event_handler = GameHelpEventHandler()
            elif key == tcod.event.K_o:
                from option import Option
                Option.option_event_handler(console=self.engine.console, context=self.engine.context, game_started=False, sound_manager=self.engine.sound_manager)
            elif key == tcod.event.K_ESCAPE:
                self.engine.event_handler = MainGameEventHandler()

        # No valid key was pressed
        return None


class DisplayControlEventHandler(AskUserEventHandler):
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        console.draw_frame(5, 0, width=console.width - 10, height=console.height, fg=color.white, bg=color.black)
        x_start = 6
        y_start = 2
        xpad = 0
        ypad = 0
        console.print(x=x_start, y=y_start + ypad, string="가급적 키보드 조작을 권장합니다.", fg=color.yellow)
        ypad += 3
        console.print(x=x_start, y=y_start + ypad, string="<이동>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad+1, string="키패드 2468 1379 / 키보드 hjkl yubn / 마우스 좌클릭", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<턴 넘기기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad+1, string="키패드 5 / .(마침표)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<아이템 줍기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad+1, string="(g)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<계단 올라가기, 내려가기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad+1, string="(<, >)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<주위 살펴보기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(/)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<문 닫기,열기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(c), (o)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<인벤토리>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(i)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<인벤토리에서 여러 아이템 선택해 드랍하기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(d)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<능력>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(a)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<잠자기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(z)키", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<공중을 날기>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(f)키", fg=color.cyan)
        ypad += 4
        console.print(x=x_start, y=y_start + ypad, string="<게임 로그 확인>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(v)키. 이동키,마우스 휠로 스크롤 가능", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<도감 확인>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="TAB", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<게임 저장>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(S)키  (쉬프트 + (s)키)", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<게임 종료>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="(Q)키  (쉬프트 + (q)키)", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<스크린샷 저장>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="F12", fg=color.cyan)
        ypad += 2
        console.print(x=x_start, y=y_start + ypad, string="<게임 일시정지>", fg=color.white)
        console.print(x=x_start, y=y_start + ypad + 1, string="ESC", fg=color.cyan)
        ypad += 2


class GameHelpEventHandler(AskUserEventHandler):
    def __init__(self, item_cancel_callback=None):
        super().__init__(item_cancel_callback=item_cancel_callback)
        self.tips = [
            "당신의 가장 강력한 무기는 바로 당신의 머리입니다. 상황을 분석해 현명하게 위기를 헤쳐나가세요!",
            "위험한 상황에 빠졌다면 도망치는 것도 하나의 방법입니다.",
            "저장되지 않은 게임은 게임이 종료될 경우 완전히 삭제됩니다. 게임을 저장했더라도 플레이어가 죽거나, 새 게임을 시작하면 삭제됩니다.",
            "썩은 음식물에서는 구더기가 생겨날 수 있습니다.",
            "저주받은 장착품들은 한 번 장착하면 저주를 해제할 때 까지 자력으로 장착을 해제할 수 없습니다.",
            "감정되지 않은 아이템들은 꼭 감정하지 않더라도 다양한 방법으로 그 종류를 추측할 수 있습니다.",
            "상점에서는 아이템을 구매하거나 판매할 수 있습니다. 상점을 잘 활용하세요!",
            "(/)키로 몬스터를 선택해 몬스터의 자세한 정보를 볼 수 있습니다. 한 번 추가된 정보는 TAB키를 눌러 언제든지 다시 확인할 수 있습니다.",
            "몬스터들의 시야는 범위가 한정되어 있지만, 간혹 텔레파시와 같은 투시 능력을 가지고 있는 몬스터들도 존재합니다.",
            "항상 게임 로그를 주시하세요. 지금 어떤 일이 일어나는 지를 파악하는 것은 굉장히 중요합니다.",
            "수면 상태에서는 활력이 평소보다 증가하지만, 잠에서 깰 때 까지 아무 행동도 할 수 없습니다. 잠을 잘 때는 항상 주의하세요!",
            "음식물은 썩거나 상할 수 있습니다. 상한 음식물로부터는 영양분을 많이 얻을 수 없다는 점에 주의하세요.",
            "몬스터들간의 전투가 발생했다면 이를 유리한 방향으로 활용하세요!",
            "저장되지 않은 게임은 게임이 종료될 경우 삭제됩니다. 게임을 저장했더라도 플레이어가 죽거나, 새 게임을 시작하면 삭제됩니다.",
            "(/)키로 주변을 살펴보고 특정 타일을 선택해 그 타일에 있는 것들에 대한 자세한 설명을 볼 수 있습니다.",
            "인벤토리 -> 아이템 상호작용 -> (s)키를 눌러 아이템 한 세트를 여러 개의 작은 세트들로 분리할 수 있습니다.",
            "아이템의 투척 사거리는 플레이어의 수치들과 아이템의 무게, 공기저항 등에 의해 결정됩니다.",
            "투척, 마법 발사 등 모든 행동은 상하좌우와 대각선 총 8가지 방향으로만 할 수 있습니다. 적이 움직일 위치를 예측해 지능적으로 이동하세요!",
            "몬스터의 난이도 수치는 꼭 그 몬스터의 강함만을 나타내는 것이 아닙니다. 난이도가 낮은 몬스터라고 방심하는 것은 금물입니다.",
            "무기를 메인 핸드와 오프 핸드 양손에 쌍수로 장착하는 것은 경우에 따라 득이 될 수도, 실이 될 수도 있습니다. 잘 생각하고 장비하세요!",
            "일부 함정은 아이템 등을 던저 강제로 발동시켜 해제할 수 있습니다.",
            "전격 피해는 인접한 액터들을 따라 퍼져 나갈 수 있습니다.",
            "당신이 하는 대부분의 행동들은 당신의 능력치에 많은 영향을 받습니다.",
            "공중에 떠 있는 상태에서는 일부 함정이나 지형의 영향을 받지 않습니다.",
            "지나치게 어려운 마법서를 읽게 된다면 혼란 상태에 빠질 수도 있습니다. 지식을 길러 도전하세요!",
            "몬스터들은 지능에 따라 다르게 행동합니다. 상대를 잘 파악하세요.",
            "TAB키를 눌러 몬스터 도감을 볼 수 있습니다.",
            "포션은 마실 수도, 던질 수도 있습니다.",
            "물 속에 잠기게 되면 보유한 아이템이 부식될 수 있습니다. 물에 들어가는 것을 피하거나, 인벤토리를 방수 처리하세요!",
            "몬스터들간의 전투를 유리한 방향으로 활용하세요!",
            "아이템 뭉치를 (s)키를 사용해 나눌 수 있습니다. 아이템의 분배가 필요할 때 사용하세요.",
        ]
        self.curr_tip_index = random.randint(0,len(self.tips)-1)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None
        key = event.sym
        player = self.engine.player

        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT): # Check Shift Modifier
            return None
        else:
            if key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[key]
                self.curr_tip_index += dx
                if self.curr_tip_index < 0:
                    self.curr_tip_index = len(self.tips) - 1
                if self.curr_tip_index > len(self.tips) - 1:
                    self.curr_tip_index = 0
            elif key == tcod.event.K_SLASH:
                self.curr_tip_index = random.randint(0,len(self.tips)-1)
            elif key == tcod.event.K_ESCAPE:
                self.engine.event_handler = MainGameEventHandler()

        # No valid key was pressed
        return None

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        console.draw_frame(5, 0, width=console.width - 10, height=console.height, fg=color.white, bg=color.black)
        x_start = 6
        y_start = 2
        xpad = 0
        ypad = 0
        console.print(x=x_start, y=y_start + ypad, string="당신은 던전 가장 깊은 곳에 있는 '쿠가의 아뮬렛'을 찾아오라는 임무를 받고 끝이 보이지 않는 던전으로 발을 들였습니다.", fg=color.yellow)
        ypad += 1
        console.print(x=x_start, y=y_start + ypad, string="용감하게 던전을 헤쳐 나가 '쿠가의 아뮬렛'을 지상으로 가져오세요!", fg=color.yellow)
        ypad += 4
        console.print(x=x_start, y=y_start + ypad, string=self.tips[self.curr_tip_index], fg=color.white)
        ypad += 4
        console.print(x=x_start, y=y_start + ypad, string="(4),(h),(좌측 화살표):이전 도움말 살펴보기 | (6),(l),(우측 화살표):다음 도움말 살펴보기", fg=color.gray)
        ypad += 1
        console.print(x=x_start, y=y_start + ypad, string="(/)키:랜덤한 도움말 살펴보기 | ESC:나가기", fg=color.gray)


class MainGameEventHandler(EventHandler):
    def handle_events(self, event: tcod.event.Event) -> Optional[bool]:
        if self.engine.is_gameover:
            self.engine.event_handler = GameOverEventHandler()
            return False
        elif self.engine.has_won:
            self.engine.event_handler = GameClearInputHandler()
            return False
        else:
            return super().handle_events(event)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None
        key = event.sym
        player = self.engine.player

        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT): # Check Shift Modifier
            if key == tcod.event.K_PERIOD:
                action = DescendAction(player)
            elif key == tcod.event.K_COMMA:
                action = AscendAction(player)
            elif key == tcod.event.K_q:
                self.engine.event_handler = QuitInputHandler()
            elif key == tcod.event.K_s:
                self.engine.event_handler = SaveInputHandler()
        else:
            if key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[key]
                action = BumpAction(player, dx, dy)
            elif key in WAIT_KEYS:
                action = WaitAction(player)
            elif key == tcod.event.K_f:
                action = FlyAction(player)
            elif key == tcod.event.K_v:
                self.engine.event_handler = HistoryViewer()
            elif key == tcod.event.K_g:
                action = PickupAction(player)
            elif key == tcod.event.K_i:
                self.engine.event_handler = InventoryEventHandler(self.engine.player.inventory)
            elif key == tcod.event.K_d:
                self.engine.event_handler = InventoryDropHandler(self.engine.player.inventory)
            elif event.sym == tcod.event.K_SLASH or event.sym == tcod.event.K_KP_DIVIDE:
                self.engine.event_handler = LookHandler()
            elif key == tcod.event.K_c:
                self.engine.event_handler = RayDirInputHandler(
                    actor=player,
                    max_range=1,
                    callback=lambda dx, dy: DoorCloseAction(player, dx, dy)
                    )
            elif key == tcod.event.K_o:
                self.engine.event_handler = RayDirInputHandler(
                    actor=player,
                    max_range=1,
                    callback=lambda dx, dy: DoorOpenAction(player, dx, dy)
                    )
            elif key == tcod.event.K_a:
                self.engine.event_handler = AbilityActivateHandler()
            elif key == tcod.event.K_z:
                self.engine.event_handler = SleepTurnSelectHandler()
            elif key == tcod.event.K_TAB or key == tcod.event.K_KP_TAB:
                import book
                self.engine.event_handler = book.MonsterBookIndexHandler()
            elif key == tcod.event.K_ESCAPE:
                self.engine.event_handler = PauseGameEventHandler()
            elif key == tcod.event.K_F12:
                time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
                pic_name = time_str
                #pic_name = self.engine.player.name + "-" + time_str # bugs occur when using certain unicode chars.
                self.engine.context.save_screenshot(f"./screenshots/{pic_name}.png")
                self.engine.message_log.add_message(f"스크린샷 저장됨. {pic_name}.png", color.cyan)
            elif key == tcod.event.K_F11:
                if self.engine.easteregg > 50:
                    return None
                self.engine.easteregg += 1
                if self.engine.easteregg == 50:
                    self.engine.message_log.add_message(f"당신은 슬픈 기분이 든다.", color.white)
            #
            #
            #     ######### TODO FIXME DEBUG
            #     self.engine.change_entity_depth(
            #         self.engine.player,
            #         self.engine.depth + 1,
            #         self.engine.world.get_map(self.engine.depth + 1).ascend_loc[0],
            #         self.engine.world.get_map(self.engine.depth + 1).ascend_loc[1]
            #     )
            # elif key == tcod.event.K_F10:
            #     ######### TODO FIXME DEBUG
            #     self.engine.change_entity_depth(
            #         self.engine.player,
            #         self.engine.depth - 1,
            #         self.engine.world.get_map(self.engine.depth - 1).ascend_loc[0],
            #         self.engine.world.get_map(self.engine.depth - 1).ascend_loc[1] # NOTE: Chamber of Kugah has no descend loc
            #     )
            # elif key == tcod.event.K_F9:
            #     import procgen, actor_factories
            #     procgen.spawn_given_monster(
            #         x=self.engine.player.x,
            #         y=self.engine.player.y,
            #         monster=actor_factories.piranha,
            #         spawn_active=True,
            #         spawn_sleep=False,
            #         is_first_generation=False,
            #         dungeon=self.engine.game_map
            #     )
            # elif key == tcod.event.K_F8:
            #     import item_factories
            #     item_factories.scroll_of_magic_mapping.spawn(self.engine.game_map, self.engine.player.x, self.engine.player.y)
            #     item_factories.scroll_of_teleportation.spawn(self.engine.game_map, self.engine.player.x,self.engine.player.y)

        # No valid key was pressed
        return action

    #OVERRIDE
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> None:
        # Get the x, y coordinates of the mouse cursor.
        mouse_map_x, mouse_map_y = self.engine.camera.rel_to_abs(rel_x=event.tile.x, rel_y=event.tile.y)

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


class GameQuitHandler(EventHandler):
    def __init__(self, prev_event_handler):
        super().__init__(item_cancel_callback=None)
        self.prev_event_handler = prev_event_handler

    def on_render(self, console: tcod.Console) -> None:
        self.engine.draw_window(console, text="정말 게임을 종료하시겠습니까? (Y/N)", title="Quit", frame_fg=color.red, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        engine = self.engine

        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            quit_game()
            return None
        elif event.sym == tcod.event.K_n or event.sym == tcod.event.K_ESCAPE:
            self.engine.event_handler = self.prev_event_handler
        return None


class AscendToSurfaceHandler(AskUserEventHandler):
    def on_render(self, console: tcod.Console) -> None:
        self.engine.draw_window(console, text="정말 지상으로 나가시겠습니까? (Y/N)", title="던전 밖으로 나가기", frame_fg=color.lime, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        engine = self.engine

        if event.sym == tcod.event.K_y or event.sym == tcod.event.K_KP_ENTER:
            # TODO: Add upper dungeon contents
            self.engine.event_handler = GameQuitHandler(prev_event_handler=self)
            return None
        elif event.sym == tcod.event.K_n or event.sym == tcod.event.K_ESCAPE:
            self.engine.event_handler = MainGameEventHandler()
        return None


class GameOverEventHandler(EventHandler):
    """Renders Game Over Screen and wait for player to quit.
    TODO: Render player History"""
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        self.engine.draw_window(console, text="(v):로그 살펴보기 | (/):맵 둘러보기 | F12:스크린샷 | ESC:게임 종료", title="당신은 죽었습니다.", frame_fg=color.lime, frame_bg=color.gui_inventory_bg)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        key = event.sym
        if key == tcod.event.K_ESCAPE:
            self.engine.event_handler = GameQuitHandler(prev_event_handler=self)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer()
        elif key == tcod.event.K_SLASH or key == tcod.event.K_KP_DIVIDE:
            self.engine.event_handler = LookHandler()
        elif key == tcod.event.K_F12:
            time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            pic_name = time_str
            # pic_name = self.engine.player.name + "-" + time_str # bugs occur when using certain unicode chars.
            self.engine.context.save_screenshot(f"./screenshots/{pic_name}.png")
            self.engine.message_log.add_message(f"스크린샷 저장됨. {pic_name}.png", color.cyan)

    def ev_mousebuttondown(self, event: tcod.event.KeyDown) -> None:
        return None


CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_KP_8: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_KP_2: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_KP_4: -10,
    tcod.event.K_PAGEDOWN: 10,
    tcod.event.K_KP_6: 10,
}

class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self):
        super().__init__()
        self.log_length = len(self.engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.
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

    def ev_mousewheel(self, event: tcod.event.MouseWheel) -> None:
        if event.y > 0:
            adjust = -1
        else:
            adjust = 1
        self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))

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
            self.engine.event_handler = MainGameEventHandler()

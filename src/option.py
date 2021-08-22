from __future__ import annotations

import color
import tcod
import exceptions
import json
import configuration as modify
from typing import Optional

class OptionInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_d:
            return "display"
        elif event.sym == tcod.event.K_c:
            return "control"
        elif event.sym == tcod.event.K_l:
            return "language"
        elif event.sym == tcod.event.K_g:
            return "gameplay"
        elif event.sym == tcod.event.K_r:
            return "reset"
        elif event.sym == tcod.event.K_ESCAPE:
            return "escape"
        return None


class DisplayInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_PLUS or event.sym == tcod.event.K_KP_PLUS or event.sym == tcod.event.K_EQUALS:
            return "increase_res"
        elif event.sym == tcod.event.K_MINUS or event.sym == tcod.event.K_KP_MINUS:
            return "decrease_res"
        elif event.sym == tcod.event.K_f:
            return "toggle_fullscreen"
        elif event.sym == tcod.event.K_ESCAPE:
            return "escape"


class ControlInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_ESCAPE:
            return "escape"



class LanguageInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_ESCAPE:
            return "escape"



class GameplayInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_ESCAPE:
            return "escape"



class ResetInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_y:
            return "reset"
        elif event.sym == tcod.event.K_ESCAPE or event.sym == tcod.event.K_n:
            return "escape"


class Option():
    option_keys = ["(D) - 디스플레이 설정", "(C) - 컨트롤 설정", "(L) - 언어 설정", "(G) - 게임플레이 설정", "(R) - 설정 초기화"]
    display_option_keys = ["(+/-) - 디스플레이 해상도 증가/감소", "(F) - 전체 화면 모드, 창 모드 전환"]
    control_option_keys = []
    language_option_keys = []
    gameplay_option_keys = []
    reset_option_keys = ["(Y) - 초기화", "(N) - 취소"]
    opt_x = 0
    opt_y = 0

    @staticmethod
    def get_input_action(input_handler):
        """
        Get input from the player using Any given InputHandler, and return the coresspondent action in a string form.
        """
        # Get input
        while True:
            for event in tcod.event.wait():
                action = input_handler.dispatch(event)
                if action:
                    return action

    @staticmethod
    def render_gui_keys(console: tcod.Console, context: tcod.context.Context, type:str, initial_y: Optional[int]=0):
        """
                Renders GUI for the option screen.
                """
        width = tcod.console_get_width(console)
        height = tcod.console_get_height(console)
        x = 0
        y = 0
        from util import draw_thick_frame

        texts = None
        if type == 'option':
            texts = Option.option_keys
            opt_title = "설정"
        elif type == 'display':
            texts = Option.display_option_keys
            opt_title = "디스플레이 설정"
        elif type == 'control':
            texts = Option.control_option_keys
            opt_title = "컨트롤 설정"
        elif type == 'language':
            texts = Option.language_option_keys
            opt_title  = "언어 설정"
        elif type == 'gameplay':
            texts = Option.gameplay_option_keys
            opt_title = "게임플레이 설정"
        elif type == 'reset':
            texts = Option.reset_option_keys
            opt_title = "설정을 초기화하시겠습니까?"
        else:
            raise Exception("FATAL ERROR::option.render_gui - something went wrong.")

        draw_thick_frame(console, x, y, width=width, height=height, fg=color.option_bg, bg=color.option_fg, title=opt_title,
                         char_type=0) # reversed fg,bg
        ypad = 2
        for s in texts:
            console.print(x + 2, y + ypad + initial_y, string=s, fg=color.option_fg)
            ypad += 2
        context.present(console, keep_aspect=True)

    @staticmethod
    def display_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        Option.render_gui_keys(console, context, 'option')

    @staticmethod
    def render_display_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        fullscreen_str = lambda x : "전체화면" if x else "창 모드"
        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"<<---- 현재 디스플레이 설정 ---->>\
        \n디스플레이 관련 설정은 게임을 다시 시작해야 적용됩니다.\
        \n\n해상도: {cfg['screen_width'] * cfg['tile_width']} x {cfg['screen_height'] * cfg['tile_height']}\
        \n\n화면 모드: {fullscreen_str(cfg['fullscreen'])}", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'display', initial_y=10) # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_control_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"<<---- 현재 컨트롤 설정 ---->>\
                \n\n추가 예정", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'control', initial_y=5)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_language_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"<<---- 현재 언어 설정 ---->>\
                \n\nalpha v1.1에서는 한국어만을 지원합니다. 곧 영어가 추가될 예정입니다!", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'language', initial_y=5)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_gameplay_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"<<---- 현재 게임플레이 설정 ---->>\
                \n\n추가 예정", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'gameplay', initial_y=5)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_reset_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"설정 초기화는 게임을 다시 시작해야 적용됩니다.", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'reset', initial_y=5)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def handle_display_action(console: tcod.Console, context: tcod.context.Context, game_started: bool) -> bool:
        """
        Creates a display input handler, wait for any input, and apply the action.
        Returns:
            if return is False, the event handler that called this function will stop the loop.
        """
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        # remove any leftover messages on the screen from previous changes
        Option.render_display_option_gui(console, context)

        #  Set Input Handler
        display_action = Option.get_input_action(DisplayInputHandler())
        if display_action == "increase_res":
            try:
                modify.alter_resolution(cfg["tile_width"] + 1, cfg["tile_height"] + 1)
            except exceptions.ConfigException:
                pass
        elif display_action == "decrease_res":
            try:
                modify.alter_resolution(cfg["tile_width"] - 1, cfg["tile_height"] - 1)
            except exceptions.ConfigException:
                pass
        elif display_action == "toggle_fullscreen":
            modify.toggle_fullscreen()
        elif display_action == "escape":
            return False

        return True

    @staticmethod
    def handle_control_action(console: tcod.Console, context: tcod.context.Context, game_started: bool) -> bool:
        """
        Creates a display input handler, wait for any input, and apply the action.
        Returns:
            if return is False, the event handler that called this function will stop the loop.
        """
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        # remove any leftover messages on the screen from previous changes
        Option.render_control_option_gui(console, context)

        #  Set Input Handler
        display_action = Option.get_input_action(ControlInputHandler())
        if display_action == "escape":
            return False
        return True

    @staticmethod
    def handle_language_action(console: tcod.Console, context: tcod.context.Context, game_started: bool) -> bool:
        """
        Creates a display input handler, wait for any input, and apply the action.
        Returns:
            if return is False, the event handler that called this function will stop the loop.
        """
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        # remove any leftover messages on the screen from previous changes
        Option.render_control_option_gui(console, context)

        #  Set Input Handler
        display_action = Option.get_input_action(LanguageInputHandler())
        if display_action == "escape":
            return False
        return True

    @staticmethod
    def handle_gameplay_action(console: tcod.Console, context: tcod.context.Context, game_started: bool) -> bool:
        """
        Creates a display input handler, wait for any input, and apply the action.
        Returns:
            if return is False, the event handler that called this function will stop the loop.
        """
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        # remove any leftover messages on the screen from previous changes
        Option.render_gameplay_option_gui(console, context)

        #  Set Input Handler
        display_action = Option.get_input_action(GameplayInputHandler())
        if display_action == "escape":
            return False
        return True

    @staticmethod
    def handle_reset_action(console: tcod.Console, context: tcod.context.Context, game_started: bool) -> bool:
        """
        Creates a display input handler, wait for any input, and apply the action.
        Returns:
            if return is False, the event handler that called this function will stop the loop.
        """
        # remove any leftover messages on the screen from previous changes
        Option.render_reset_option_gui(console, context)

        #  Set Input Handler
        display_action = Option.get_input_action(ResetInputHandler())
        if display_action == "reset":
            try:
                with open("./config/config_default.json", "r") as f:
                    default_cfg = json.load(f)
                with open("./config/config.json", "w") as f2:
                    json.dump(default_cfg, f2, indent=4)
            except exceptions.ConfigException:
                pass
        elif display_action == "escape":
            return False

        return True

    @staticmethod
    def option_event_handler(console: tcod.Console, context: tcod.context.Context, game_started: bool):
        """
        Core function that handles most of the things related to the option screen.
        Option screen loop is handled here.

        Args:
            game_started:
                Whether the game has started or not (bool).
                If player opened the option window from the title, this value is false.
        """
        # Render Title Screen for the first time
        Option.display_option_gui(console=console, context=context)
        context.present(console, keep_aspect=True)

        # Option screen loop
        while True:
            # Render Title GUI
            Option.display_option_gui(console=console, context=context)
            context.present(console, keep_aspect=True)

            # Get Input from option screen
            option_action = Option.get_input_action(OptionInputHandler())

            # Get input from title screen
            if option_action == "display":
                Option.render_display_option_gui(console, context)
                context.present(console, keep_aspect=True)
                while Option.handle_display_action(console, context, game_started): # If false, finish session
                    pass
            elif option_action == "control":
                Option.render_control_option_gui(console, context)
                context.present(console, keep_aspect=True)
                while Option.handle_control_action(console, context, game_started): # If false, finish session
                    pass
            elif option_action == "language":
                Option.render_language_option_gui(console, context)
                context.present(console, keep_aspect=True)
                while Option.handle_language_action(console, context, game_started): # If false, finish session
                    pass
            elif option_action == "gameplay":
                Option.render_gameplay_option_gui(console, context)
                context.present(console, keep_aspect=True)
                while Option.handle_gameplay_action(console, context, game_started): # If false, finish session
                    pass
            elif option_action == "reset":
                Option.render_reset_option_gui(console, context)
                context.present(console, keep_aspect=True)
                while Option.handle_reset_action(console, context, game_started):
                    pass
            elif option_action == "escape":
                return None

from __future__ import annotations

import color
import tcod
import exceptions
import json
import configuration as modify
from sound import SoundManager
from typing import Optional
from game import Game

class OptionInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_d:
            return "display"
        elif event.sym == tcod.event.K_c:
            return "control"
        elif event.sym == tcod.event.K_s:
            return "sound"
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
        elif event.sym == tcod.event.K_i:
            return "toggle_safe_mouse_movement"


class SoundInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        shift = False
        if event.mod & (tcod.event.K_LSHIFT or tcod.event.K_RSHIFT):
            shift = True

        if event.sym == tcod.event.K_ESCAPE:
            return "escape"
        elif event.sym == tcod.event.K_KP_PLUS or event.sym == tcod.event.K_PLUS or event.sym == tcod.event.K_EQUALS or event.sym == tcod.event.K_KP_8 or event.sym == tcod.event.K_VOLUMEUP or event.sym == tcod.event.K_UP:
            if shift:
                return "volume10up"
            return "volumeup"
        elif event.sym == tcod.event.K_KP_MINUS or event.sym == tcod.event.K_MINUS or event.sym == tcod.event.K_KP_2 or event.sym == tcod.event.K_VOLUMEDOWN or event.sym == tcod.event.K_DOWN:
            if shift:
                return "volume10down"
            return "volumedown"


class GameplayInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_ESCAPE:
            return "escape"
        elif event.sym == tcod.event.K_a:
            return "toggle_animation"
        elif event.sym == tcod.event.K_s:
            return "toggle_autosave"


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
    option_keys = ["(d) 디스플레이 설정", "(c) 컨트롤 설정", "(s) 사운드 설정", "(g) 게임플레이 설정", "(r) 설정 초기화"]
    display_option_keys = ["(+/-) 디스플레이 해상도 증가/감소", "(f) 전체 화면 모드/창 모드 전환"]
    control_option_keys = ["(i) 안전한 마우스 이동 사용/사용 해제"]
    sound_option_keys = ["(+/-) 마스터 볼륨 증가/감소", "(쉬프트를 누른 채 +/-) 10% 단위로 조작"]
    gameplay_option_keys = ["(a) 애니메이션 효과 사용/사용 해제", "(s) 게임 종료 시 자동저장 사용/사용 해제"]
    reset_option_keys = ["(y) 초기화", "(n) 취소"]
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
        elif type == 'sound':
            texts = Option.sound_option_keys
            opt_title  = "사운드 설정"
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
        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"\n창 모드 사용이 권장됩니다.\n\n디스플레이 관련 설정은 게임을 다시 시작해야 적용됩니다.\
        \n\n\n\n해상도: {cfg['screen_width'] * cfg['tile_width']} x {cfg['screen_height'] * cfg['tile_height']}\
        \n\n화면 모드: {fullscreen_str(cfg['fullscreen'])}", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'display', initial_y=14) # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_control_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        string = lambda x: "활성화" if not x else "비활성화"
        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"\n\n안전한 마우스 이동: {string(cfg['ignore_enemy_spotted_during_mouse_movement'])}"
                                                                 f"\n활성화할 경우 마우스 클릭으로 이동하는 도중 새로운 액터가 시야에 들어오거나 시야에 있던 액터가 시야에서 사라지면 이동을 중지합니다", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'control', initial_y=6)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_sound_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"\n\n마스터 볼륨: {cfg['master_volume']}%", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'sound', initial_y=5)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_gameplay_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        string = lambda x : "활성화" if x else "비활성화"
        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"\n\n애니메이션 효과: {string(cfg['render_animation'])}"
                                                                 f"\n\n게임 종료 시 자동저장: {string(cfg['autosave'])}", fg=color.option_fg)
        Option.render_gui_keys(console, context, 'gameplay', initial_y=8)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_reset_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=f"\n\n설정 초기화는 게임을 다시 시작해야 적용됩니다.", fg=color.option_fg)
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
        elif display_action == "toggle_safe_mouse_movement":
            modify.toggle_mouse_enemy_ignore(not cfg['ignore_enemy_spotted_during_mouse_movement'])
        return True

    @staticmethod
    def handle_sound_action(console: tcod.Console, context: tcod.context.Context, game_started: bool, sound_manager: SoundManager) -> bool:
        """
        Creates a display input handler, wait for any input, and apply the action.
        Returns:
            if return is False, the event handler that called this function will stop the loop.
        """
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        # remove any leftover messages on the screen from previous changes
        Option.render_sound_option_gui(console, context)

        #  Set Input Handler
        display_action = Option.get_input_action(SoundInputHandler())
        if display_action == "volumeup":
            try:
                modify.change_master_volume(percent=1)
                sound_manager.update_volume_change()
            except exceptions.ConfigException:
                pass
        elif display_action == "volumedown":
            try:
                modify.change_master_volume(percent=-1)
                sound_manager.update_volume_change()
            except exceptions.ConfigException:
                pass
        elif display_action == "volume10up":
            try:
                modify.change_master_volume(percent=10)
                sound_manager.update_volume_change()
            except exceptions.ConfigException:
                pass
        elif display_action == "volume10down":
            try:
                modify.change_master_volume(percent=-10)
                sound_manager.update_volume_change()
            except exceptions.ConfigException:
                pass
        elif display_action == "escape":
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
        elif display_action == "toggle_animation":
            modify.toggle_animation(not cfg['render_animation'])
        elif display_action == "toggle_autosave":
            modify.toggle_autosave(not cfg['autosave'])
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
    def option_event_handler(console: tcod.Console, context: tcod.context.Context, game_started: bool, sound_manager:SoundManager):
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
            elif option_action == "sound":
                Option.render_sound_option_gui(console, context)
                context.present(console, keep_aspect=True)
                while Option.handle_sound_action(console, context, game_started, sound_manager): # If false, finish session
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

from __future__ import annotations

import color
import tcod
import exceptions
import json
import configuration as modify
from sound import SoundManager
from typing import Optional
from game import Game
from language import interpret as i

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
    def __init__(self, game_started: bool):
        self.game_started = game_started

    def ev_keydown(self, event):
        if event.sym == tcod.event.K_ESCAPE:
            return "escape"
        elif event.sym == tcod.event.K_a:
            return "toggle_animation"
        elif event.sym == tcod.event.K_l:
            if not self.game_started:
                return "change_language"
            else:
                return "fail_to_change_language"



class ResetInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def __init__(self, game_started: bool):
        self.game_started = game_started

    def ev_keydown(self, event):
        if event.sym == tcod.event.K_y:
            if not self.game_started:
                return "reset"
            else:
                return "fail_to_reset"
        elif event.sym == tcod.event.K_ESCAPE or event.sym == tcod.event.K_n:
            return "escape"


class Option():
    opt_x = 0
    opt_y = 0

    @staticmethod
    def update_lang():
        Option.option_keys = [i("(d) 디스플레이 설정", "(d) Display settings"),
                               i("(c) 컨트롤 설정", "(c) Control settings"),
                               i("(s) 사운드 설정", "(s) Sound settings"),
                               i("(g) 게임플레이 설정/Gameplay settings", "(g) Gameplay settings/게임플레이 설정"),
                               i("(r) 설정 초기화", "(r) Reset settings")]
        Option.display_option_keys = [i("(+/-) 디스플레이 해상도 증가/감소", "(+/-) Increase/Decrease display resolution"),
                               i("(f) 전체 화면 모드/창 모드 전환", "(f) Fullscreen/Windowed mode")]
        Option.control_option_keys = [i("(i) 안전한 마우스 이동 사용/사용 해제", "(i) Enable/Disable safe mouse movement")]
        Option.sound_option_keys = [i("(+/-) 마스터 볼륨 증가/감소", "(+/-) Increase/Decrease master volume"),
                             i("(쉬프트를 누른 채 +/-) 10% 단위로 조작", "(+/- while pressing shift) Adjust by 10%")]
        Option.gameplay_option_keys = [i("(a) 애니메이션 효과 사용/사용 해제", "(a) Enable/Disable animation"),
                                i("(l) 언어 변경/Change language", "(l) Change language/언어 변경")]
        Option.reset_option_keys = [i("(y) 초기화", "(y) Reset"),
                             i("(n) 취소", "(n) Cancel")]

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
            opt_title = i("설정", "Option")
        elif type == 'display':
            texts = Option.display_option_keys
            opt_title = i("디스플레이 설정", "Display settings")
        elif type == 'control':
            texts = Option.control_option_keys
            opt_title = i("컨트롤 설정", "Control settings")
        elif type == 'sound':
            texts = Option.sound_option_keys
            opt_title  = i("사운드 설정", "Sound settings")
        elif type == 'gameplay':
            texts = Option.gameplay_option_keys
            opt_title = i("게임플레이 설정", "Gameplay settings")
        elif type == 'reset':
            texts = Option.reset_option_keys
            opt_title = i("설정을 초기화하시겠습니까?", "Do you really want to reset your settings?")
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

        fullscreen_str = lambda x : i("전체화면","fullscreen") if x else i("창 모드","windowed")
        console.print(Option.opt_x + 2, Option.opt_y + 2, string=i(f"\n창 모드 사용이 권장됩니다.\n\n디스플레이 관련 설정은 게임을 다시 시작해야 적용됩니다.\
        \n\n\n\n해상도: {cfg['screen_width'] * cfg['tile_width']} x {cfg['screen_height'] * cfg['tile_height']}\
        \n\n화면 모드: {fullscreen_str(cfg['fullscreen'])}",
                                                                   f"\nWindowed mode is recommended.\n\nRestart the game to apply new display settings.\
        \n\n\n\nResolution: {cfg['screen_width'] * cfg['tile_width']} x {cfg['screen_height'] * cfg['tile_height']}\
        \n\nScreen mode: {fullscreen_str(cfg['fullscreen'])}"), fg=color.option_fg)
        Option.render_gui_keys(console, context, 'display', initial_y=14) # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_control_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        string = lambda x: i("활성화","enabled") if not x else i("비활성화","disabled")
        console.print(Option.opt_x + 2, Option.opt_y + 2, string=i(f"\n\n안전한 마우스 이동: {string(cfg['ignore_enemy_spotted_during_mouse_movement'])}"
                                                                 f"\n\n활성화할 경우 마우스 클릭으로 이동하는 도중 새로운 액터가 시야에 들어오거나 시야에 있던 액터가 시야에서 사라지면 이동을 중지합니다.",
                                                                   f"\n\nSafe mouse movement: {string(cfg['ignore_enemy_spotted_during_mouse_movement'])}"
                                                                 f"\n\nWhen enabled, you will stop moving when a new actor appears/disappears in your sight."), fg=color.option_fg)
        Option.render_gui_keys(console, context, 'control', initial_y=7)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_sound_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=i(f"\n\n마스터 볼륨: {cfg['master_volume']}%",
                                                                   f"\n\nMaster volume: {cfg['master_volume']}%"), fg=color.option_fg)
        Option.render_gui_keys(console, context, 'sound', initial_y=5)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_gameplay_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        string = lambda x : i("활성화","enabled") if x else i("비활성화","disabled")
        stringlang = lambda x : "한국어/Korean" if x == "KR" else ("English/영어" if x == "EN" else "Unknown language. Using English instead.")
        console.print(Option.opt_x + 2, Option.opt_y + 2, string=i(f"\n\n애니메이션 효과: {string(cfg['render_animation'])}"
                                                                   f"\n\n현재 언어: {stringlang(cfg['lang'])}"
                                                                   f"\n\n게임 플레이 중에는 언어를 변경할 수 없습니다.",
                                                                   f"\n\nAnimation: {string(cfg['render_animation'])}"
                                                                   f"\n\nCurrent language: {stringlang(cfg['lang'])}"
                                                                   f"\n\nYou can't change the language during the game."), fg=color.option_fg)
        Option.render_gui_keys(console, context, 'gameplay', initial_y=9)  # TODO Hard-coded
        context.present(console, keep_aspect=True)

    @staticmethod
    def render_reset_option_gui(console: tcod.Console, context: tcod.context.Context):
        console.clear(fg=color.option_bg, bg=color.option_bg)
        with open("./config/config.json", "r") as f:
            cfg = json.load(f)

        console.print(Option.opt_x + 2, Option.opt_y + 2, string=i(f"\n\n설정 초기화는 게임을 다시 시작해야 적용됩니다."
                                                                   "\n\n게임 플레이 중에는 설정을 초기화할 수 없습니다.",
                                                                   f"\n\nRestart the game after resetting the settings."
                                                                   "\n\nYou can't reset the settings during the game."), fg=color.option_fg)
        Option.render_gui_keys(console, context, 'reset', initial_y=8)  # TODO Hard-coded
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
        Option.update_lang()
        Option.render_gameplay_option_gui(console, context)

        #  Set Input Handler
        display_action = Option.get_input_action(GameplayInputHandler(game_started))
        if display_action == "escape":
            return False
        elif display_action == "toggle_animation":
            modify.toggle_animation(not cfg['render_animation'])
        elif display_action == "change_language":
            modify.change_language()
        elif display_action == "fail_to_change_language":
            pass
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
        display_action = Option.get_input_action(ResetInputHandler(game_started))
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
        elif display_action == "fail_to_reset":
            pass

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

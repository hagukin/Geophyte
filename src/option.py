import color
import tcod
import exceptions
import json
import configuration as modify


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

class ResetInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def ev_keydown(self, event):
        if event.sym == tcod.event.K_y:
            return "reset"
        elif event.sym == tcod.event.K_ESCAPE or event.sym == tcod.event.K_n:
            return "escape"


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


def render_option_gui(console: tcod.Console, context: tcod.context.Context):
    """
    Renders GUI for the option screen.
    """
    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    x = 0
    y = 0
    # render
    from util import draw_thick_frame
    console.clear(fg=color.black, bg=color.black)
    draw_thick_frame(console, x, y, width=width, height=height, fg=color.black, bg=color.green, title="설정", char_type=1)
    console.print(x+2, y+1, string="\n(D) - 디스플레이 설정\n\n(C) - 조작 설정\n\n(L) - 언어 설정\n\n(G) - 게임플레이 설정\n\n(R) - 설정 초기화", fg=color.green)


def fullscreen_str(is_full: bool) -> str:
    if is_full:
        return "전체화면"
    return "창 모드"


def render_display_option_gui(console: tcod.Console, context: tcod.context.Context):
    """
    Renders GUI for the display option screen.
    """
    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    x = 0
    y = 0
    with open("./config/config.json", "r") as f:
        cfg = json.load(f)
    
    # render
    from util import draw_thick_frame
    console.clear(fg=color.black, bg=color.black)
    draw_thick_frame(console, x, y, width=width, height=height, fg=color.black, bg=color.green, title="디스플레이 설정", char_type=1)
    console.print(x+2, y+2, string=f"<<---- 현재 디스플레이 정보 ---->>\n\
    \n\n해상도: {cfg['screen_width'] * cfg['tile_width']} x {cfg['screen_height'] * cfg['tile_height']}\
    \n\n화면 모드: {fullscreen_str(cfg['fullscreen'])}\
    \n\n\n\n\n\n<<---- 변경 ---->>\n\
    \n\n(+/-) - 디스플레이 해상도 증가/감소\
    \n\n(F) - 전체 화면 모드, 창 모드 전환\
    \n\n\n\n\n\n디스플레이 관련 설정은 게임을 다시 시작해야 적용됩니다.", fg=color.green)
    context.present(console, keep_aspect=True)


def render_control_option_gui(console: tcod.Console, context: tcod.context.Context):
    """
    Renders GUI for the display option screen.
    """
    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    x = 0
    y = 0
    with open("./config/config.json", "r") as f:
        cfg = json.load(f)

    # render
    from util import draw_thick_frame
    console.clear(fg=color.black, bg=color.black)
    draw_thick_frame(console, x, y, width=width, height=height, fg=color.black, bg=color.green, title="조작 설정",
                     char_type=1)
    console.print(x + 2, y + 2, string=f"<<---- 현재 조작 설정 ---->>\n\
    \n\nTODO\
    \n\n\n\n\n\n<<---- 변경 ---->>\n\
    \n\nTODO\
    \n\n\n\n\n\n", fg=color.green)
    context.present(console, keep_aspect=True)


def render_language_option_gui(console: tcod.Console, context: tcod.context.Context):
    """
    Renders GUI for the display option screen.
    """
    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    x = 0
    y = 0
    with open("./config/config.json", "r") as f:
        cfg = json.load(f)

    # render
    from util import draw_thick_frame
    console.clear(fg=color.black, bg=color.black)
    draw_thick_frame(console, x, y, width=width, height=height, fg=color.black, bg=color.green, title="언어 설정",
                     char_type=1)
    console.print(x + 2, y + 2, string=f"<<---- 현재 언어 설정 ---->>\n\
    \n\nTODO\
    \n\n\n\n\n\n<<---- 변경 ---->>\n\
    \n\nTODO\
    \n\n\n\n\n\n", fg=color.green)
    context.present(console, keep_aspect=True)


def render_gameplay_option_gui(console: tcod.Console, context: tcod.context.Context):
    """
    Renders GUI for the display option screen.
    """
    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    x = 0
    y = 0
    with open("./config/config.json", "r") as f:
        cfg = json.load(f)

    # render
    from util import draw_thick_frame
    console.clear(fg=color.black, bg=color.black)
    draw_thick_frame(console, x, y, width=width, height=height, fg=color.black, bg=color.green, title="게임플레이 설정",
                     char_type=1)
    console.print(x + 2, y + 2, string=f"<<---- 현재 게임플레이 설정 ---->>\n\
    \n\nTODO\
    \n\n\n\n\n\n<<---- 변경 ---->>\n\
    \n\nTODO\
    \n\n\n\n\n\n", fg=color.green)
    context.present(console, keep_aspect=True)


def render_reset_option_gui(console: tcod.Console, context: tcod.context.Context):
    """
    Renders GUI for the display option screen.
    """
    width = tcod.console_get_width(console)
    height = tcod.console_get_height(console)
    x = 0
    y = 0

    # render
    from util import draw_thick_frame
    console.clear(fg=color.black, bg=color.black)
    draw_thick_frame(console, x, y, width=width, height=height, fg=color.black, bg=color.green, title="설정을 초기화하시겠습니까?",
                     char_type=1)
    console.print(x + 2, y + 2, string=f"초기화는 게임을 다시 시작해야 적용됩니다.\n\
    \n\n\n\n(Y) - 초기화\n\n(N) - 취소", fg=color.green)
    context.present(console, keep_aspect=True)


def handle_display_action(console: tcod.Console, context: tcod.context.Context, game_started: bool) -> bool:
    """
    Creates a display input handler, wait for any input, and apply the action.
    Returns:
        if return is False, the event handler that called this function will stop the loop.
    """
    with open("./config/config.json", "r") as f:
        cfg = json.load(f)

    # remove any leftover messages on the screen from previous changes
    render_display_option_gui(console, context)
    
    #  Set Input Handler
    display_action = get_input_action(DisplayInputHandler())
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


def handle_reset_action(console: tcod.Console, context: tcod.context.Context, game_started: bool) -> bool:
    """
    Creates a display input handler, wait for any input, and apply the action.
    Returns:
        if return is False, the event handler that called this function will stop the loop.
    """
    # remove any leftover messages on the screen from previous changes
    render_reset_option_gui(console, context)

    #  Set Input Handler
    display_action = get_input_action(ResetInputHandler())
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
    render_option_gui(console=console, context=context)
    context.present(console, keep_aspect=True)

    # Option screen loop
    while True:
        # Render Title GUI
        render_option_gui(console=console, context=context)
        context.present(console, keep_aspect=True)

        # Get Input from option screen
        option_action = get_input_action(OptionInputHandler())
    
        # Get input from title screen
        if option_action == "display":
            render_display_option_gui(console, context)
            context.present(console, keep_aspect=True)
            while handle_display_action(console, context, game_started): # If false, finish session
                pass
        elif option_action == "reset":
            render_reset_option_gui(console, context)
            context.present(console, keep_aspect=True)
            while handle_reset_action(console, context, game_started):
                pass
        elif option_action == "escape":
            return None


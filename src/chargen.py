from render import render_img, draw_thick_frame

import actor_factories
import color
import tcod
import time
import copy
from typing import Optional, Callable
from sound import SoundManager

class CharGenInputHandler(tcod.event.EventDispatch[None]):
    """
    Handles every inputs that are made in the title screen.
    """
    def __init__(self):
        self.help_msg = "엔터:확인 | ESC:이전으로"
        self.should_render_pts = False # if True, render current usable points

    def render_gui(self, console) -> None:
        """
        Renders GUI for the title screen.
        """
        width = tcod.console_get_width(console)
        height = tcod.console_get_height(console)
        console.print(0, height-1, string=self.help_msg, fg=color.white)
        page_str = f"{CharGen.curr_order+1}/{len(CharGen.chargen_order)}"
        console.print(width - len(page_str), height-1, string=page_str, fg=color.yellow)
        if self.should_render_pts:
            console.print(0, height - 3, string=f"{CharGen.points} 포인트 사용 가능", fg=color.green)


class NameGenInputHandler(CharGenInputHandler):
    def ev_textinput(self, event):
        CharGen.player_name += event.text
        CharGen.player_name = CharGen.player_name[:20] # 20 letters max (unicode)
        return None

    def ev_keydown(self, event) -> str:
        if event.sym == tcod.event.K_BACKSPACE:
            CharGen.player_name = CharGen.player_name[:-1]
            return ""
        elif event.sym == tcod.event.K_KP_ENTER or event.sym == tcod.event.K_RETURN:
            return "to_next"
        elif event.sym == tcod.event.K_ESCAPE:
            return "to_prev"
        return ""

    def render_gui(self, console) -> None:
        """
        Renders GUI for the title screen.
        """
        super().render_gui(console)
        width = tcod.console_get_width(console)
        height = tcod.console_get_height(console)
        x = int(width / 2) - 5
        y = int(height / 2) - 5
        console.print(x, y, string=f"이름을 입력하세요:", fg=color.white)
        console.print(x + 5 - int(len(CharGen.player_name)/2), y + 3, string=CharGen.player_name, fg=color.white)


class StatusGenInputHandler(CharGenInputHandler):
    DEFAULT_STAT = 15
    MAX_SUB_POINT = 5
    MAX_ADD_POINT = 3

    def __init__(self):
        super().__init__()
        self.help_msg += " | 알파뱃:스테이터스 선택 | +,-키:포인트 사용/차감 | (r)-스테이터스 초기화"
        self.selected = None
        self.should_render_pts = True

    def add_one_point(self, stat: str) -> None:
        if not stat:
            return None
        if CharGen.points < 1:
            CharGen.show_warning("포인트가 부족합니다.")
            return None
        if CharGen.status_points_used[stat] >= StatusGenInputHandler.MAX_ADD_POINT:
            CharGen.show_warning("더 이상 포인트를 사용할 수 없습니다.")
            return None
        CharGen.status_points_used[stat] += 1
        CharGen.points -= 1

    def subtract_one_point(self, stat: str) -> None:
        if not stat:
            return None
        if CharGen.status_points_used[stat] <= -1 * StatusGenInputHandler.MAX_SUB_POINT:
            CharGen.show_warning("더 이상 포인트를 차감할 수 없습니다.")
            return None
        CharGen.status_points_used[stat] -= 1
        CharGen.points += 1

    def ev_keydown(self, event) -> str:
        key = event.sym
        if key == tcod.event.K_BACKSPACE:
            CharGen.player_name = CharGen.player_name[:-1]
            return ""
        elif key == tcod.event.K_KP_ENTER or key == tcod.event.K_RETURN:
            return "to_next"
        elif key == tcod.event.K_ESCAPE:
            return "to_prev"
        elif key == tcod.event.K_PLUS or key == tcod.event.K_KP_PLUS or key == tcod.event.K_EQUALS:
            self.add_one_point(self.selected)
        elif key == tcod.event.K_MINUS or key == tcod.event.K_KP_MINUS:
            self.subtract_one_point(self.selected)
        elif key == tcod.event.K_s:
            self.selected = "strength"
        elif key == tcod.event.K_d:
            self.selected = "dexterity"
        elif key == tcod.event.K_c:
            self.selected = "constitution"
        elif key == tcod.event.K_a:
            self.selected = "agility"
        elif key == tcod.event.K_i:
            self.selected = "intelligence"
        elif key == tcod.event.K_h:
            self.selected = "charm"
        elif key == tcod.event.K_r:
            for v in CharGen.status_points_used.values():
                CharGen.points += v
            for k in CharGen.status_points_used.keys():
                CharGen.status_points_used[k] = 0
        return ""

    def render_status(self, console, xpos: int, ypos: int):
        """
        Args:
            xpos, ypos:
                position of status window.
        """
        x = xpos + 2
        ypad = 0
        y = lambda: ypos + 2 + ypad

        str_fg = color.gui_chargen_status_name_fg
        if self.selected == "strength":
            str_fg = color.gui_selected_item
        console.print(string="(s) 힘", x=x, y=y(), fg=str_fg)
        ypad += 2
        console.print(string=f"{CharGen.player.status.origin_status['strength'] + CharGen.status_points_used['strength']} ({CharGen.status_points_used['strength']:+d}pt)", x=x, y=y(), fg=color.white)
        ypad += 5

        dex_fg = color.gui_chargen_status_name_fg
        if self.selected == "dexterity":
            dex_fg = color.gui_selected_item
        console.print(string="(d) 재주", x=x, y=y(), fg=dex_fg)
        ypad += 2
        console.print(
            string=f"{CharGen.player.status.origin_status['dexterity'] + CharGen.status_points_used['dexterity']} ({CharGen.status_points_used['dexterity']:+d}pt)",
            x=x, y=y(), fg=color.white)
        ypad += 5

        con_fg = color.gui_chargen_status_name_fg
        if self.selected == "constitution":
            con_fg = color.gui_selected_item
        console.print(string="(c) 활력", x=x, y=y(), fg=con_fg)
        ypad += 2
        console.print(
            string=f"{CharGen.player.status.origin_status['constitution'] + CharGen.status_points_used['constitution']} ({CharGen.status_points_used['constitution']:+d}pt)",
            x=x, y=y(), fg=color.white)
        ypad += 5

        agi_fg = color.gui_chargen_status_name_fg
        if self.selected == "agility":
            agi_fg = color.gui_selected_item
        console.print(string="(a) 민첩", x=x, y=y(), fg=agi_fg)
        ypad += 2
        console.print(
            string=f"{CharGen.player.status.origin_status['agility'] + CharGen.status_points_used['agility']} ({CharGen.status_points_used['agility']:+d}pt)",
            x=x, y=y(), fg=color.white)
        ypad += 5

        int_fg = color.gui_chargen_status_name_fg
        if self.selected == "intelligence":
            int_fg = color.gui_selected_item
        console.print(string="(i) 지능", x=x, y=y(), fg=int_fg)
        ypad += 2
        console.print(
            string=f"{CharGen.player.status.origin_status['intelligence'] + CharGen.status_points_used['intelligence']} ({CharGen.status_points_used['intelligence']:+d}pt)",
            x=x, y=y(), fg=color.white)
        ypad += 5

        char_fg = color.gui_chargen_status_name_fg
        if self.selected == "charm":
            char_fg = color.gui_selected_item
        console.print(string="(h) 매력", x=x, y=y(), fg=char_fg)
        ypad += 2
        console.print(
            string=f"{CharGen.player.status.origin_status['charm'] + CharGen.status_points_used['charm']} ({CharGen.status_points_used['charm']:+d}pt)",
            x=x, y=y(), fg=color.white)
        ypad += 5

    def render_status_desc(self, console, x:int, y:int) -> None:
        """
        Args:
            x, y:
                position to render
        """
        string = ""
        if self.selected == "strength":
            string = "육체적인 완력을 나타냅니다."
        elif self.selected == "dexterity":
            string = "물건을 원하는 대로 다룰 수 있는 능력을 나타냅니다."
        elif self.selected == "constitution":
            string = "신체의 강인함 및 건강을 나타냅니다."
        elif self.selected == "agility":
            string = "얼마나 민첩하게 행동할 수 있는지를 나타냅니다."
        elif self.selected == "intelligence":
            string = "두뇌 능력 및 마법에 대한 이해도를 포괄적으로 나타냅니다."
        elif self.selected == "charm":
            string = "얼마나 외적으로 매력적으로 느껴지는가, 혹은 얼마나 상대방에게 위압감을 줄 수 있는가를 나타냅니다."
        console.print(string=string, x=x, y=y, fg=color.white)

    def render_gui(self, console) -> None:
        """
        Renders GUI for the title screen.
        """
        width = tcod.console_get_width(console)
        height = tcod.console_get_height(console)
        x = 2
        y = 2
        f_width = 31
        f_height = 43
        draw_thick_frame(console, x, y, f_width, f_height, title="스테이터스", bg=color.gui_chargen_status_frame_bg,fg=color.gui_chargen_status_frame_fg, char_type=0)
        super().render_gui(console)
        self.render_status(console, x, y)
        self.render_status_desc(console, x + f_width + 2, y + 2)


class CharGen():
    player = None
    player_name = ""
    curr_order = 0
    chargen_order = None
    warning_msg = ""
    is_first_input = False # prevent titlehandler input stacking
    points = 0 # usable points
    status_points_used = {
        "strength": 0,
        "dexterity": 0,
        "constitution": 0,
        "agility": 0,
        "intelligence": 0,
        "charm": 0,
    }

    def __init__(self):
        CharGen.chargen_order = (NameGenInputHandler(),StatusGenInputHandler())
        CharGen.player = copy.deepcopy(actor_factories.player)  # Cannot use entity.copy() yet
        # NOTE: player.initialize_actor() is called from procgen.generate_entities()

    @staticmethod
    def show_warning(string: str) -> None:
        CharGen.warning_msg = string

    def clear_all_changes(self) -> None:
        CharGen.player = copy.deepcopy(actor_factories.player)
        CharGen.player_name = ""
        CharGen.curr_order = 0
        CharGen.warning_msg = ""
        CharGen.is_first_input = False

    def render_warning_msg(self, console) -> None:
        console.print(0, 0, string=CharGen.warning_msg, fg=color.red)

    def move_next_gen(self) -> bool:
        """
        Return:
            if reached end of the order, return True.
            return False instead.
        """
        if CharGen.curr_order == len(CharGen.chargen_order) - 1:
            return True
        CharGen.curr_order = min(len(CharGen.chargen_order)-1, CharGen.curr_order + 1)
        return False

    def move_prev_gen(self) -> bool:
        """
        Return:
            if tried to move out of the order, return True.
            return False instead.
        """
        if CharGen.curr_order == 0:
            return True
        CharGen.curr_order = max(0, CharGen.curr_order - 1)
        return False

    def get_chargen_action(self, sec_per_frame, input_handler):
        """
        Get input from the player using TitleInputHandler, and return the coresspondent action in a string form.
        """
        # Set Input Handler
        start_time = time.time()
        is_time_over = False

        # Get input
        while True:
            end_time = time.time()
            if end_time - start_time >= sec_per_frame:
                #print(end_time - start_time) #NOTE: time consumed for each loop
                is_time_over = True
                return None

            for event in tcod.event.wait(timeout=0.01):#NOTE: increasing the timeout value might cause each loop to consume longer time.
                if not CharGen.is_first_input:
                    CharGen.is_first_input = True
                    continue
                chargen_action = input_handler.dispatch(event)

                if chargen_action:
                    return chargen_action

            if is_time_over:
                return None

    def chargen_sound(self, sound_manager: SoundManager) -> None:
        sound_manager.change_bgm("bgm_title_screen")

    def chargen_event_handler(self, console, context, cfg, sound_manager: SoundManager) -> Optional:
        """
        Core function that handles most of the things related to the title screen.
        Title screen loop is handled here.
        """
        sec_per_frame = 0.1
        self.chargen_sound(sound_manager)

        # CharGen screen loop
        while True:
            console.clear()
            render_img(console=console, dest_x=8, dest_y=0, img=tcod.image_load("resources\\title_img.png"))
            chargen_input_handler = CharGen.chargen_order[self.curr_order]
            chargen_action = self.get_chargen_action(sec_per_frame=sec_per_frame, input_handler=chargen_input_handler)
            chargen_input_handler.render_gui(console)
            self.render_warning_msg(console)
            context.present(console, keep_aspect=True)

            # Get input from title screen
            if chargen_action == "to_prev":
                if self.move_prev_gen():
                    chargen_action = "exit_chargen"
            elif chargen_action == "to_next":
                if self.move_next_gen():
                    chargen_action = "end_chargen"

            if chargen_action == "end_chargen":
                return self.generate_player()
            elif chargen_action == "exit_chargen":
                return None # Exit and go back to the main menu

    def generate_player(self) -> None:
        CharGen.player.change_name(self.player_name.strip())

        CharGen.player.status.gain_strength(CharGen.status_points_used["strength"])
        CharGen.player.status.gain_dexterity(CharGen.status_points_used["dexterity"])
        CharGen.player.status.gain_constitution(CharGen.status_points_used["constitution"])
        CharGen.player.status.gain_agility(CharGen.status_points_used["agility"])
        CharGen.player.status.gain_intelligence(CharGen.status_points_used["intelligence"])
        CharGen.player.status.gain_charm(CharGen.status_points_used["charm"])
        CharGen.player.status.experience.init_experience() # update initial exp

        return CharGen.player
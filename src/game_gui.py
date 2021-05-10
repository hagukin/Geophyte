import textwrap
import copy
import color
import pygame

from typing import Iterable, List, Reversible, Tuple
from entity import Actor

class GameGui:
    def __init__(self, engine) -> None:
        """
        NOTE: MessageLog must use square fonts. (fonts with same width and height)

        Vars:
            curr_char:
                currently selected character to display.
        """
        self.engine = engine
        self.curr_char = engine.player
        self.fonts = {
            "character_name" : ("default-bold", 16),
            "character_health" : ("default-bold", 16),
            "character_mana" : ("default-bold", 16),
            "character_status" : ("default-bold", 16),
            "character_state": ("default-bold", 16),
            "mouse_render": ("default-bold", 16),
            "game_status": ("default-bold", 12),
        }
        self.display_pos = {
            "character_name" : (engine.config["camera_display_x"] + engine.config["camera_width"] + self.fonts["character_name"][1],
                                engine.config["camera_display_y"] + self.fonts["character_name"][1]),
            "character_health" : (engine.config["camera_display_x"] + engine.config["camera_width"] + self.fonts["character_name"][1],
                                  engine.config["camera_display_y"] + self.fonts["character_name"][1]+ self.fonts["character_name"][1]*2),
            "character_mana": (engine.config["camera_display_x"] + engine.config["camera_width"] + self.fonts["character_name"][1],
                                 engine.config["camera_display_y"] + self.fonts["character_name"][1] + self.fonts["character_name"][1]*3),
            "character_status": (engine.config["camera_display_x"] + engine.config["camera_width"] + self.fonts["character_name"][1],
                                 engine.config["camera_display_y"] + self.fonts["character_name"][1] + self.fonts["character_name"][1]*4),
            "character_state": (engine.config["camera_display_x"] + engine.config["camera_width"] + self.fonts["character_name"][1],
                                 engine.config["camera_display_y"] + self.fonts["character_name"][1] + self.fonts["character_name"][1]*5),
            "mouse_render" : (engine.config["camera_display_x"],
                              engine.config["camera_display_y"] + engine.config["camera_height"] - self.fonts["mouse_render"][1]*2),
            "game_status" : (engine.config["camera_display_x"],
                             engine.config["camera_display_y"])

        }

    def __deepcopy__(self, memo):
        # Backup pygame surfaces
        tmp = self.font
        self.font = None

        # deepcopy rest
        new_obj = GameGui(self.engine)
        for name, attr in self.__dict__.items():
            if name == "font":
                continue
            else:
                new_obj.__dict__[name] = copy.deepcopy(attr)

        self.font = tmp
        new_obj.font = tmp
        return new_obj

    @property
    def player(self):
        return self.engine.player

    @property
    def screen(self):
        return self.engine.screen

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """Return a wrapped text message."""
        for line in string.splitlines():  # Handle newlines in messages.
            yield from textwrap.wrap(
                line, width, expand_tabs=True,
            )

    def render_character_name(self, x: int, y: int, character: Actor, font_id: str="default-bold", font_size: int=16) -> None:
        self.engine.print_str(string=f"{character.name}", x=x, y=y, fg=color.yellow, font_id=font_id, font_size=font_size)

    def render_character_health(
            self, x: int, y: int, character: Actor, font_id: str="default-bold", font_size: int=16
    ) -> None:
        self.engine.print_str(string=f"체력: {character.status.hp}/{character.status.changed_status['max_hp']}",
                              x=x, y=y, fg=color.white, font_id=font_id, font_size=font_size)

    def render_character_mana(
            self, x: int, y: int, character: Actor, font_id: str="default-bold", font_size: int=16
    ) -> None:
        self.engine.print_str(string=f"마나: {character.status.mp}/{character.status.changed_status['max_mp']}",
                              x=x, y=y, fg=color.white, font_id=font_id, font_size=font_size)

    def render_character_status(
            self, x: int, y: int, character: Actor,
            font_id: str="default-bold", font_size: int=16
    ) -> int:
        """
        NOTE: x, y coordinates is the position of the letter S of the word Str(strength)
        Returns:
            Integer, the height of this function's rendering area. (pixels)
        """
        stat = character.status.changed_status
        x_span = 13 * font_size

        # Status
        self.engine.print_str(x=x, y=y, string=f"힘: {stat['strength']}", fg=color.light_gray,
                              font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x + x_span, y=y, string=f"손재주: {stat['dexterity']}", fg=color.light_gray,
                              font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x, y=y+font_size, string=f"활력: {stat['constitution']}", fg=color.light_gray,
                              font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x + x_span, y=y+font_size, string=f"민첩: {stat['agility']}", fg=color.light_gray,
                              font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x, y=y+2*font_size, string=f"지능: {stat['intelligence']}", fg=color.light_gray,
                              font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x + x_span, y=y+2*font_size, string=f"매력: {stat['charm']}", fg=color.light_gray,
                              font_id=font_id, font_size=font_size)

        # Armor
        self.engine.print_str(x=x, y=y+4*font_size, string=f"보호도: {stat['protection']}", fg=color.white,
                              font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x, y=y+6*font_size, string=f"기본 공격력: {stat['base_melee']}", fg=color.white,
                              font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x, y=y+7*font_size, string=f"추가 공격력: 0 ~ {stat['additional_melee']}", fg=color.white,
                              font_id=font_id, font_size=font_size)

        return y+7*font_size

    def render_character_state(
            self, x: int, y: int, tile_height: int, character: Actor, font_id: str="default-bold", font_size: int=16
    ) -> None:
        """
        NOTE: Status effects' string length should be shorter than 13 characters. (including blanks)
        NOTE: This function can display any actor's status. This can be used as checking player's pet status, etc.
        """

        num1 = 0  # y position of the leftside lane
        num2 = 0  # y position of the rightside lane
        lane1_x = x  # x pos of the leftside lane
        lane2_x = x + 13  # x pos of the rightside lane #NOTE hard-coded
        window_height = tile_height  # This graphic ui's frame height (frame border spaces(2 tiles) are ignored)
        # Maximum amount of status effects that can be displayed at once is (window_height * 2).
        hunger_text = character.actor_state.hunger_state

        #### Hunger ####
        if character.actor_state.hunger_state == "hungry":
            hunger_color = color.player_damaged
            if self.engine.config["lang"] == "ko":
                hunger_text = "배고픔"
        elif character.actor_state.hunger_state == "overeaten":
            hunger_color = color.player_damaged
            if self.engine.config["lang"] == "ko":
                hunger_text = "과식"
        elif character.actor_state.hunger_state == "starving":
            hunger_color = color.red
            if self.engine.config["lang"] == "ko":
                hunger_text = "굶주림"
        elif character.actor_state.hunger_state == "fainting":
            hunger_color = color.red
            if self.engine.config["lang"] == "ko":
                hunger_text = "배고픔에 허덕임"
        elif character.actor_state.hunger_state == "satiated":
            hunger_color = color.yellow
            if self.engine.config["lang"] == "ko":
                hunger_text = "배부름"
        else:
            hunger_color = color.white

        if character.actor_state.hunger_state != "":
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string=hunger_text, x=lane2_x, y=y + num2, fg=hunger_color, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string=hunger_text, x=lane1_x, y=y + num1, fg=hunger_color, font_id=font_id, font_size=font_size)

        #### Others ####
        if character.actor_state.is_burning != [0, 0, 0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string="불 붙음", x=lane2_x, y=y + num2, fg=color.red, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string="불 붙음", x=lane1_x, y=y + num1, fg=color.red, font_id=font_id, font_size=font_size)
        if character.actor_state.is_freezing != [0, 0, 0, 0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string="얼고 있음", x=lane2_x, y=y + num2, fg=color.ice, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string="얼고 있음", x=lane1_x, y=y + num1, fg=color.ice, font_id=font_id, font_size=font_size)
        if character.actor_state.is_frozen != [0, 0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string="얼어붙음", x=lane2_x, y=y + num2, fg=color.blue_ice, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string="얼어붙음", x=lane1_x, y=y + num1, fg=color.blue_ice, font_id=font_id, font_size=font_size)
        if character.actor_state.is_paralyzing != [0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string="마비됨", x=lane2_x, y=y + num2, fg=color.yellow, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string="마비됨", x=lane1_x, y=y + num1, fg=color.yellow, font_id=font_id, font_size=font_size)
        if character.actor_state.is_confused != [0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string="혼란", x=lane2_x, y=y + num2, fg=color.yellow, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string="혼란", x=lane1_x, y=y + num1, fg=color.yellow, font_id=font_id, font_size=font_size)
        if character.actor_state.is_bleeding != [0, 0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string="출혈", x=lane2_x, y=y + num2, fg=color.blood, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string="출혈", x=lane1_x, y=y + num1, fg=color.blood, font_id=font_id, font_size=font_size)
        if character.actor_state.is_melting != [0, 0, 0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(string="산에 뒤덮임", x=lane2_x, y=y + num2, fg=color.lime, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(string="산에 뒤덮임", x=lane1_x, y=y + num1, fg=color.lime, font_id=font_id, font_size=font_size)
        if character.actor_state.is_poisoned != [0, 0, 0, 0]:
            if num1 > window_height:
                num2 += 1
                self.engine.print_str(x=lane2_x, y=y + num2, string="중독", fg=color.purple, font_id=font_id, font_size=font_size)
            else:
                num1 += 1
                self.engine.print_str(x=lane1_x, y=y + num1, string="중독", fg=color.purple, font_id=font_id, font_size=font_size)
        if character.actor_state.is_submerged:
            if character.actor_state.is_underwater:
                if num1 > window_height:
                    num2 += 1
                    self.engine.print_str(x=lane2_x, y=y + num2, string="완전히 물에 잠김", fg=color.water_blue, font_id=font_id, font_size=font_size)
                else:
                    num1 += 1
                    self.engine.print_str(x=lane1_x, y=y + num1, string="완전히 물에 잠김", fg=color.water_blue, font_id=font_id, font_size=font_size)
            else:
                if num1 > window_height:
                    num2 += 1
                    self.engine.print_str(x=lane2_x, y=y + num2, string="일부분 물에 잠김", fg=color.water_blue, font_id=font_id, font_size=font_size)
                else:
                    num1 += 1
                    self.engine.print_str(x=lane1_x, y=y + num1, string="일부분 물에 잠김", fg=color.water_blue, font_id=font_id, font_size=font_size)
        if character.actor_state.is_drowning != [0, 0]:
            # Display turns left until drowning
            if character.actor_state.is_drowning[0] >= character.actor_state.is_drowning[1] * 0.75:  # 75% drowning
                if num1 > window_height:
                    num2 += 1
                    self.engine.print_str(x=lane2_x, y=y + num2,
                                     string=f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                                     fg=color.red, font_id=font_id, font_size=font_size)
                else:
                    num1 += 1
                    self.engine.print_str(x=lane1_x, y=y + num1,
                                     string=f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                                     fg=color.red, font_id=font_id, font_size=font_size)
            elif character.actor_state.is_drowning[0] >= character.actor_state.is_drowning[1] * 0.5:  # 50% drowning
                if num1 > window_height:
                    num2 += 1
                    self.engine.print_str(x=lane2_x, y=y + num2,
                                     string=f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                                     fg=color.player_damaged, font_id=font_id, font_size=font_size)
                else:
                    num1 += 1
                    self.engine.print_str(x=lane1_x, y=y + num1,
                                     string=f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                                     fg=color.player_damaged, font_id=font_id, font_size=font_size)

        # Display "None" if there is no status effects
        if not num1 and not num2:
            num1 = 1
            self.engine.print_str(x=lane1_x, y=y + num1, string="(없음)", fg=color.gray, font_id=font_id, font_size=font_size)

    def render_character_equipments(
            self, x: int, y: int, character: Actor,
    ) -> None:
        """
        NOTE: Function currently unused(ver27), under development
        NOTE: This function can display any actor's status.
        """

        self.engine.print_str(x=x, y=y, string=f"메인 핸드: {character.equipments.equipments['main_hand']}",
                         fg=color.gui_status_text)
        # TODO: Display item name instead of memory address
        # TODO: Do not display unequipped body parts

    def render_character_info(self, character: Actor):
        self.render_character_name(self.display_pos["character_name"][0], self.display_pos["character_name"][1], character,
                                   self.fonts["character_name"][0], self.fonts["character_name"][1])
        self.render_character_health(self.display_pos["character_health"][0], self.display_pos["character_health"][1], character,
                                     self.fonts["character_health"][0], self.fonts["character_health"][1])
        self.render_character_mana(self.display_pos["character_mana"][0], self.display_pos["character_mana"][1], character,
                                     self.fonts["character_mana"][0], self.fonts["character_mana"][1])
        y_begin = self.render_character_status(self.display_pos["character_status"][0], self.display_pos["character_status"][1], character,
                                     self.fonts["character_status"][0], self.fonts["character_status"][1])
        self.render_character_state(self.display_pos["character_state"][0], self.display_pos["character_state"][1] + y_begin, 10, character,
                                    self.fonts["character_state"][0], self.fonts["character_state"][1]) #TODO: tile_height hard-coded to 10


    def render_game_status(self, x: int, y: int, font_id: str="default-bold", font_size: int=16) -> None:
        """print dungeon depth, game turn, etc."""
        self.engine.print_str(f"층: {self.engine.depth}", x, y, fg=color.white, font_id=font_id, font_size=font_size)
        self.engine.print_str(f"턴수: {self.engine.game_turn}", x + font_size*7, y, fg=color.white, font_id=font_id, font_size=font_size)

    def render_names_at_mouse_location(self, x: int, y: int, font_id: str="default-bold", font_size: int=16) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x, mouse_y = self.engine.camera.diplay_abs_cor(mouse_x, mouse_y)

        names_at_mouse_location = self.engine.game_map.get_names_at_location(tile_x=mouse_x, tile_y=mouse_y, display_id=False)
        tile_name_at_location = self.engine.game_map.get_tile_name_at_location(tile_x=mouse_x, tile_y=mouse_y)

        self.engine.print_str(x=x, y=y, string=tile_name_at_location, fg=color.gui_mouse_tile, font_id=font_id, font_size=font_size)
        self.engine.print_str(x=x, y=y+font_size, string=names_at_mouse_location, fg=color.gui_mouse_entity, font_id=font_id, font_size=font_size)

    def render(self) -> None:
        """Render the message log over the given area."""
        self.render_names_at_mouse_location(self.display_pos["mouse_render"][0], self.display_pos["mouse_render"][1],
                                            self.fonts["mouse_render"][0], self.fonts["mouse_render"][1])
        self.render_character_info(self.curr_char)
        self.render_game_status(self.display_pos["game_status"][0], self.display_pos["game_status"][1],
                                self.fonts["game_status"][0], self.fonts["game_status"][1])

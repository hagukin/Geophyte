import textwrap
import copy
import color

from util import draw_thick_frame
from typing import Iterable, List, Reversible, Tuple
from entity import Entity, Actor


class Message:
    def __init__(self, text: str, fg: Tuple[int, int, int]):
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """The full text of this message, including the count if necessary."""
        if self.count > 1:
            return f"({self.count}x) {self.plain_text}"
        return self.plain_text


class MessageLog:
    def __init__(self, engine, font_id: str="default-bold", font_size: int=16) -> None:
        """
        NOTE: MessageLog must use square fonts. (fonts with same width and height)
        """
        self.engine = engine
        self.font_id = font_id
        self.font_size = font_size
        self.font = engine.get_font(font_id, font_size)
        self.width = int(engine.config["camera_width"] * engine.config["msg_log_width_ratio_to_camera_width"])
        self.height = engine.config["screen_height"] - engine.config["camera_height"] - self.font_size * 2
        self.display_x = engine.config["camera_display_x"] + self.font_size
        self.display_y = engine.config["camera_display_y"] + engine.config["camera_height"] + self.font_size
        self.messages: List[Message] = []

    def __deepcopy__(self, memo):
        # Backup pygame surfaces
        tmp = self.font
        self.font = None

        # deepcopy rest
        new_obj = MessageLog(self.engine, self.font_id, self.font_size)
        for name, attr in self.__dict__.items():
            if name == "font":
                continue
            else:
                new_obj.__dict__[name] = copy.deepcopy(attr)

        self.font = tmp
        new_obj.font = tmp
        return new_obj

    @property
    def letter_height(self):
        """returns how many letters can fit in this message log's height."""
        return int(self.height / self.font_size)

    @property
    def letter_width(self):
        """returns how many letters can fit in this message log's width."""
        return int(self.width / self.font_size)

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

    def add_message(
        self, text: str, fg: Tuple[int, int, int] = color.white, *, target: Entity = None, stack: bool = True, show_once: bool = False,
    ) -> None:
        """
        Adds a message to this log.

        Args:
            stack:
                Boolean. It indicates whether the message should be stacked(if the message is same as before) or not.
            target:
                When printing out the message on the log, the game decides whether to show the message or not by checking the location of the target.
                If target is in player's sight, the game will print out the message.
                If target is set to None, the message will always get printed.
            show_once:
                Boolean. It indicates whether the message should be shown once.
        """
        if target:
            if not self.engine.game_map.visible[target.x, target.y]:
                return None

        if show_once == False:
            if stack and self.messages and text == self.messages[-1].plain_text:
                self.messages[-1].count += 1
            else:
                self.messages.append(Message(text, fg))
        else:
            if text == self.messages[-1].plain_text:
                pass
            else:
                self.messages.append(Message(text, fg))

    def add_speech(
        self, text: str, fg: Tuple[int, int, int] = color.msg_log_speech, *, speaker: Actor = None, stack: bool = True, show_once: bool = False,
    ) -> None:
        """Print a actor speaking."""
        if speaker.actor_state.can_talk:
            self.add_message(f"{speaker.name}({speaker.char}): ", speaker.fg, target=speaker, stack=stack, show_once=show_once)
            self.add_message(text, fg, target=speaker, stack=stack, show_once=show_once)
        else:
            self.add_message(f"{speaker.name}({speaker.char}): " + "(알아들을 수 없음)", fg, target=speaker, stack=stack, show_once=show_once)

    def render(self) -> None:
        """Render the message log over the given area."""
        self.render_messages()

    def render_messages(self) -> None:
        """Render messages."""
        y_offset = self.height - self.font_size

        for message in reversed(self.messages):
            for line in reversed(list(self.wrap(message.full_text, self.letter_width))):
                self.screen.blit(self.font.render(line, True, message.fg), (self.display_x, self.display_y + y_offset))
                y_offset -= self.font_size
                if y_offset < 0:
                    return  # No more space to print messages.

import random
import textwrap
from util import draw_thick_frame
import tcod
import color

from game import Game
from language import interpret
from util import get_distance
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
    def __init__(self, engine) -> None:
        self.messages: List[Message] = []
        self.engine = engine

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
        if text == '':
            return None
        if Game.language == "EN":
            text = text[0].upper() + text[1:] # .capitalize() will make other letters lowercase

        if target:
            if not self.engine.game_map.visible[target.x, target.y]:
                return None #TODO: Maybe let player get every information on the dungeon under certain condition?

        if show_once == False:
            if stack and self.messages and text == self.messages[-1].plain_text:
                self.messages[-1].count += 1
            else:
                self.messages.append(Message(text, fg))
        else:
            if text == self.messages[-1].plain_text:
                return None
            else:
                self.messages.append(Message(text, fg))

    def add_speech(
        self, text: str, fg: Tuple[int, int, int] = color.msg_log_speech, *, speaker: Actor = None, stack: bool = True, show_once: bool = False,
    ) -> None:
        """Print a actor speaking."""
        # Cannot listen to a speech from a far enough distance.
        if self.engine.player.status.changed_status["hearing"] < get_distance(self.engine.player.x, self.engine.player.y, speaker.x, speaker.y):
            return None #TODO: Maybe let player get every information on the dungeon under certain condition?

        speaker_name = f"{speaker.name}({speaker.char})"
        speak_text = text
        speaker_fg = speaker.fg
        if not self.engine.game_map.visible[speaker.x, speaker.y]:
            speaker_name = interpret("(시야에 없음)", "(out of sight)")
            speaker_fg = color.white

            # Will change some characters of the text to "?" to give a effect of not clearly hearing things that arew too far or out of sight.
            cant_hear_letters_count = min(len(speak_text), max(0, int(20 / self.engine.player.status.changed_status["hearing"] - get_distance(
                self.engine.player.x, self.engine.player.y, speaker.x, speaker.y))))
            for i in range(max(0, len(speak_text)-2)): # ignore last letter to avoid confusion with the question marks in sentences.
                if random.random() <= cant_hear_letters_count / len(speak_text): # Chance of changing the character: Total size / cant_hear_letters_count
                    speak_text[i] = '?'

        if not speaker.actor_state.can_talk:
            speak_text = interpret("(알아들을 수 없음)", "(unrecognizable)")

        self.add_message(f"{speaker_name}: ", speaker_fg, target=speaker, stack=stack, show_once=show_once)
        self.add_message(speak_text, fg, target=speaker, stack=stack, show_once=show_once)

    def render(
        self, console: tcod.Console, x: int, y: int, width: int, height: int, draw_frame: bool=False
    ) -> None:
        """
        Render the message log over the given area.
        """
        self.render_messages(console, x, y, width, height, self.messages)

        if draw_frame:
            draw_thick_frame(console, x=x-1, y=y-1, width=width+2, height=height+2, fg=color.gui_frame_fg, bg=color.gui_frame_bg)
            console.draw_frame(x=x-1, y=y-1, width=width+2, height=height+2, clear=False, fg=color.gui_frame_fg, bg=color.gui_frame_bg)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """Return a wrapped text message."""
        for line in string.splitlines():  # Handle newlines in messages.
            yield from textwrap.wrap(
                line, width, expand_tabs=True,
            )

    @classmethod
    def render_messages(
        cls,
        console: tcod.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        """
        Render the messages provided.
        The `messages` are rendered starting at the last message and working backwards.
        """
        y_offset = height - 1

        for message in reversed(messages):
            for line in reversed(list(cls.wrap(message.full_text, width))):
                console.print(x=x, y=y + y_offset, string=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return  # No more space to print messages.

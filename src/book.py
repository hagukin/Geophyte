from __future__ import annotations
from input_handlers import AskUserEventHandler
from entity import Actor, Item, SemiActor
from base.data_loader import load_book, save_actor_book
from typing import Optional
from actions import Action
from util import multiline
from korean import grammar as g
from language import interpret as i
import actor_factories
import tcod
import color

monchar = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@"
actor_db = {}

class MonsterBookIndexHandler(AskUserEventHandler):
    def __init__(self, page: Optional[int]=None):
        """
        Vars:
            db:
                { monster_char : { press_key : monster_actor }}
        """
        super().__init__()
        load_book()
        if page == None:
            self.page = 0
        else:
            self.page = page

    def next_page(self):
        self.page = self.page + 1
        self.engine.sound_manager.add_sound_queue("fx_book")
        if self.page >= len(monchar):
            self.page = 0

    def prev_page(self):
        self.page = self.page - 1
        self.engine.sound_manager.add_sound_queue("fx_book")
        if self.page < 0:
            self.page = len(monchar) - 1

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym == tcod.event.K_ESCAPE or event.sym == tcod.event.K_TAB or event.sym == tcod.event.K_KP_TAB:
            return self.on_exit()

        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        if event.sym in (tcod.event.K_KP_6, tcod.event.K_RIGHT):
            self.next_page()
            return None
        elif event.sym in (tcod.event.K_KP_4, tcod.event.K_LEFT):
            self.prev_page()
            return None

        # Alphabets
        if event.mod & tcod.event.K_LSHIFT:
            alphabet = {
                tcod.event.K_a:"A",tcod.event.K_b:"B",tcod.event.K_c:"C",tcod.event.K_d:"D",tcod.event.K_e:"E",tcod.event.K_f:"F",tcod.event.K_g:"G",tcod.event.K_h:"H",tcod.event.K_i:"I",tcod.event.K_j:"J",tcod.event.K_k:"K",tcod.event.K_l:"L",tcod.event.K_m:"M",tcod.event.K_n:"N",tcod.event.K_o:"O",tcod.event.K_p:"P",tcod.event.K_q:"Q",tcod.event.K_r:"R",tcod.event.K_s:"S",tcod.event.K_t:"T",tcod.event.K_u:"U",tcod.event.K_v:"V",tcod.event.K_w:"W",tcod.event.K_x:"X",tcod.event.K_y:"Y",tcod.event.K_z:"Z",
            }
        else:
            alphabet = {
                tcod.event.K_a:"a",tcod.event.K_b:"b",tcod.event.K_c:"c",tcod.event.K_d:"d",tcod.event.K_e:"e",tcod.event.K_f:"f",tcod.event.K_g:"g",tcod.event.K_h:"h",tcod.event.K_i:"i",tcod.event.K_j:"j",tcod.event.K_k:"k",tcod.event.K_l:"l",tcod.event.K_m:"m",tcod.event.K_n:"n",tcod.event.K_o:"o",tcod.event.K_p:"p",tcod.event.K_q:"q",tcod.event.K_r:"r",tcod.event.K_s:"s",tcod.event.K_t:"t",tcod.event.K_u:"u",tcod.event.K_v:"v",tcod.event.K_w:"w",tcod.event.K_x:"x",tcod.event.K_y:"y",tcod.event.K_z:"z",
            }
        try:
            monster = actor_factories.ActorDB.get_actor_by_id(entity_id=actor_db[monchar[self.page]][alphabet[event.sym]])
            if monster == None:
                raise KeyError()
            self.engine.event_handler = MonsterInfoHandler(monster, self.page)
            return None
        except KeyError:
            self.engine.message_log.add_message(i("잘못된 입력입니다.",
                                                  f"Invalid input."), color.invalid)
            return self.on_exit()
        except:
            import traceback
            traceback.print_exc()

        return self.on_exit()

    def on_render(self, console: tcod.Console) -> None:
        """Render current page"""
        console.draw_frame(0, 0, console.width, console.height, i("던전 몬스터 도감",f"Monster Encyclopedia"), fg=color.book_fg, bg=color.book_bg)
        console.draw_frame(1, 1, console.width - 2, console.height - 2, f"{monchar[self.page]}", fg=color.book_fg, bg=color.book_bg)

        start_x = 3
        start_y = 3
        xpad = 0
        ypad = 0

        for presskey, mon_id in actor_db[monchar[self.page]].items():
            if mon_id == None:
                continue
            m = actor_factories.ActorDB.get_actor_by_id(entity_id=mon_id)

            key = f"({presskey})"
            console.print(start_x + xpad, start_y+ypad, key, fg=color.white)
            xpad += len(key)

            charstr = f" {m.char}"
            console.print(start_x + xpad, start_y+ypad, charstr, fg=m.fg)
            xpad += len(charstr)
            console.print(start_x + xpad, start_y+ypad, " |", fg=color.white)
            xpad += 2

            diffstr = i(f" 위험도 {m.status.difficulty}",
                        f" Difficulty {m.status.difficulty}")
            console.print(start_x + xpad, start_y + ypad, diffstr, fg=color.white)
            xpad += len(diffstr)
            console.print(start_x + xpad, start_y + ypad, " |", fg=color.white)
            xpad += 2

            namestr = f" {m.name}"
            console.print(start_x + xpad, start_y + ypad, namestr, fg=color.white)
            xpad += len(namestr)

            # newline
            xpad = 0
            ypad += 1


class MonsterInfoHandler(AskUserEventHandler):
    width: int = 70
    def __init__(self, monster: Actor, page: int=None):
        super().__init__()
        self.monster = monster
        self.page = page # If this input handler is called from MonsterBookIndexHandler, pass in the page number so it could callback the indexhandler when cancelled.
        if not self.engine._is_gameover:
            if save_actor_book(actor=self.monster): # Try save actor info to the book
                # succeded
                self.engine.sound_manager.add_sound_queue("fx_ui_positive")
                self.engine.message_log.add_message(text=i(f"{g(self.monster.name, '이')} 몬스터 도감에 추가되었습니다.",
                                                           f"{self.monster.name} is now added to the encyclopedia."), fg=color.add_to_book)

    def on_render(self, console: tcod.Console) -> None:
        console.draw_frame(0, 0, console.width, console.height, bg=color.book_bg)
        console.draw_frame(1, 1, console.width - 2, console.height - 2, f"{self.monster.name}", fg=color.book_fg,
                           bg=color.book_bg)

        start_x = 3
        start_y = 3
        xpad = 0
        ypad = 0

        # Name
        console.print(start_x, start_y, self.monster.name, fg=color.cyan)
        ypad += 4

        # Type Description
        if self.monster.actor_type_desc != "":
            text, line_cnt = multiline(self.monster.actor_type_desc, self.width, 2)
            console.print(start_x, start_y + ypad, text, fg=color.white)
            ypad += line_cnt
            ypad += 4

        # Entity Description
        if self.monster.entity_desc != "":
            text, line_cnt = multiline(self.monster.entity_desc, self.width, 2)
            console.print(start_x, start_y + ypad, text, fg=color.white)
            ypad += line_cnt
            ypad += 4

        # Actor quote
        if self.monster.actor_quote != "":
            text, line_cnt = multiline(self.monster.actor_quote, self.width)
            console.print(start_x, start_y + ypad, "\""+text+"\"", fg=color.white)
            ypad += line_cnt

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym == tcod.event.K_ESCAPE:
            if self.page != None:
                self.engine.event_handler = MonsterBookIndexHandler(page=self.page)
                return None
            else:
                return self.on_exit()
        return self.on_exit()


class ItemInfoHandler(AskUserEventHandler):
    width: int = 70
    def __init__(self, item: Item, page: int=None):
        super().__init__()
        self.item = item
        self.page = page # If this input handler is called from MonsterBookIndexHandler, pass in the page number so it could callback the indexhandler when cancelled.
        # NOTE: page value currently(20210821) unused.

    def on_render(self, console: tcod.Console) -> None:
        console.draw_frame(0, 0, console.width, console.height, bg=color.book_bg)
        console.draw_frame(1, 1, console.width - 2, console.height - 2, f"{self.item.name}", fg=color.book_fg,
                           bg=color.book_bg)

        start_x = 3
        start_y = 3
        xpad = 0
        ypad = 0

        # Name
        console.print(start_x, start_y, self.item.name, fg=color.cyan)
        ypad += 4

        # Type Description
        if self.item.item_type_desc != "":
            text, line_cnt = multiline(self.item.item_type_desc, self.width, 2)
            console.print(start_x, start_y + ypad, text, fg=color.white)
            ypad += line_cnt
            ypad += 4

        # Entity Description
        if self.item.entity_desc != "":
            text, line_cnt = multiline(self.item.entity_desc, self.width, 2)
            console.print(start_x, start_y + ypad, text, fg=color.white)
            ypad += line_cnt
            ypad += 4

        # Item quote
        if self.item.item_quote != "":
            text, line_cnt = multiline(self.item.item_quote, self.width)
            console.print(start_x, start_y + ypad, "\""+text+"\"", fg=color.white)
            ypad += line_cnt

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym == tcod.event.K_ESCAPE:
            return self.on_exit()
        return self.on_exit()


class SemiActorInfoHandler(AskUserEventHandler):
    width: int = 70
    def __init__(self, semiactor: SemiActor, page: int=None):
        super().__init__()
        self.semiactor = semiactor
        self.page = page # If this input handler is called from MonsterBookIndexHandler, pass in the page number so it could callback the indexhandler when cancelled.

    def on_render(self, console: tcod.Console) -> None:
        console.draw_frame(0, 0, console.width, console.height, bg=color.book_bg)
        console.draw_frame(1, 1, console.width - 2, console.height - 2, f"{self.semiactor.name}", fg=color.book_fg,
                           bg=color.book_bg)

        start_x = 3
        start_y = 3
        xpad = 0
        ypad = 0

        # Name
        console.print(start_x, start_y, self.semiactor.name, fg=color.cyan)
        ypad += 4

        # Type Description
        if self.semiactor.semiactor_type_desc != "":
            text, line_cnt = multiline(self.semiactor.semiactor_type_desc, self.width, 2)
            console.print(start_x, start_y + ypad, text, fg=color.white)
            ypad += line_cnt
            ypad += 4

        # Entity Description
        if self.semiactor.entity_desc != "":
            text, line_cnt = multiline(self.semiactor.entity_desc, self.width, 2)
            console.print(start_x, start_y + ypad, text, fg=color.white)
            ypad += line_cnt
            ypad += 4

        # Item quote
        if self.semiactor.semiactor_quote != "":
            text, line_cnt = multiline(self.semiactor.semiactor_quote, self.width)
            console.print(start_x, start_y + ypad, "\""+text+"\"", fg=color.white)
            ypad += line_cnt

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym == tcod.event.K_ESCAPE:
            return self.on_exit()
        return self.on_exit()
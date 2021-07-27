from __future__ import annotations
from input_handlers import AskUserEventHandler
from entity import Actor
from render import randomized_screen_paint
from loader.data_loader import load_book
from typing import Optional
from actions import Action
import actor_factories
import copy
import tcod
import color

monchar = "@abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
actor_db = {}

class MonsterBookIndexHandler(AskUserEventHandler):
    def __init__(self, page: Optional[int]=None):
        """
        Vars:
            db:
                { monster_char : { press_key : monster_actor }}
        """
        super().__init__()



        from loader.data_loader import save_actor_book #DEBUG TODO
        save_actor_book(get_all_monsters=True) # TODO
        load_book()
        if page == None:
            self.page = 1
        else:
            self.page = page

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym == tcod.event.K_ESCAPE:
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
        if event.sym in (tcod.event.K_KP_6. tcod.event.K_RIGHT):
            self.page += 1
        elif event.sym in (tcod.event.K_KP_4, tcod.event.K_LEFT):
            self.page -= 1

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
            monster = db[monchar[self.page]][alphabet[event.sym]]
            self.engine.event_handler = MonsterInfoHandler(self.page, monster)
            return None
        except KeyError:
            self.engine.message_log.add_message("잘못된 입력입니다.", color.invalid)
            return None
        except:
            import traceback
            traceback.print_exc()

        return self.on_exit()

    def on_render(self, console: tcod.Console) -> None:
        """Render current page"""
        randomized_screen_paint(console, self.engine.context, main_color=color.old_paper_yellow, diversity=2)
        console.draw_frame(1, 1, console.width, console.height, "몬스터 도감", fg=color.black, bg=None)

        start_x = 3
        start_y = 3
        xpad = 0
        ypad = 0

        for presskey, m in db[monchar[self.page]].items():
            key = f"({presskey})"
            xpad += len(key)
            diffstr = f" 위험도 {m.status.difficulty} |"
            console.print(start_x + xpad, start_y+ypad, diffstr, fg=color.white)
            xpad += len(diffstr)
            charstr = f" {m.char} |"
            console.print(start_x + xpad, start_y+ypad, charstr, fg=m.fg)
            xpad += len(charstr)
            console.print(start_x + xpad, start_y+ypad, f" {m.name}", fg=color.white)
            ypad += 1
            xpad = 0


class MonsterInfoHandler(AskUserEventHandler):
    def __init__(self, page: int, monster: Actor):
        super().__init__()
        self.monster = monster
        self.page = page

    def on_render(self, console: tcod.Console) -> None:
        randomized_screen_paint(console, self.engine.context, main_color=color.old_paper_yellow, diversity=2)
        console.draw_frame(1, 1, console.width, console.height, f"{self.monster.name}", fg=color.black, bg=None)

        start_x = 3
        start_y = 3
        xpad = 0
        ypad = 0

        console.print(start_x, start_y, self.monster.name, fg=color.black)
        ypad += 2
        if self.monster.actor_type_desc == None or self.monster.actor_type_desc == "":
            pass
        else:
            console.print(start_x, start_y + ypad, self.monster.actor_type_desc, fg=color.black)
            ypad += 1
        console.print(start_x, start_y + ypad, self.monster.entity_desc, fg=color.black)
        ypad += 4
        console.print(start_x, start_y + ypad, self.monster.actor_quote, fg=color.black)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        """By default any key exits this input handler."""
        if event.sym == tcod.event.K_ESCAPE:
            self.engine.event_handler = MonsterBookIndexHandler(page=self.page)
        return None
from __future__ import annotations
import random

from typing import Optional, Tuple, TYPE_CHECKING
from util import draw_thick_frame
from entity import Actor, Item
from language import interpret as i
from game import Game

import tcod
import color

if TYPE_CHECKING:
    from game_map import GameMap
    from tcod import Console
    from tcod.context import Context
    from engine import Engine
    
def randomized_screen_paint(console: Console, context: Context, main_color: Tuple, diversity: int = 10) -> None:
    """
    Clear entire console and display graphics that are going to be shown during descending(dungeon generating) process.

    Args:
        diversity:
            value used for shifting rgb value slightly.
            Lower number = smoother screen
    """
    console.clear(bg=color.black)
    for y in range(console.height):
        for x in range(console.width):
            console.print(
                x=x,
                y=y,
                string=" ",
                bg=( 
                    max(0, min(255, main_color[0] + random.randint(-diversity, diversity))),
                    max(0, min(255, main_color[1] + random.randint(-diversity, diversity))),
                    max(0, min(255, main_color[2] + random.randint(-diversity, diversity)))
                )
            )
    context.present(console, keep_aspect=True)

def get_names_at_location(x: int, y: int, game_map: GameMap, display_id: bool=False) -> str:
    """
    Display entity's name that are at the mouse cursor location. (Only when the location is visible)
    """
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = []

    for entity in reversed(game_map.entities):
        if entity.x == x and entity.y == y:
            if display_id:
                names.append(f"{id(entity)}:{entity.name}")
                continue
            name = Game.engine.modify_entity_name_to_render(entity)
            names.append(name)

    names = ", ".join(names)
    names = names[0:game_map.engine.config["camera_width"] - 7]

    return names.capitalize()


def get_tile_name_at_location(x: int, y: int, game_map: GameMap) -> str:
    """
    Display tile's name that are at the mouse cursor location. (Only when the location is explored)
    """
    if not game_map.in_bounds(x, y) or not game_map.explored[x, y]:
        return ""

    return game_map.tiles[x, y]["tile_name"].capitalize()


def render_character_name(
    console: Console, x: int, y: int, character: Actor,
) -> None:
    console.print(x=x, y=y, string=f"{character.name}", fg=color.yellow)


def render_gameinfo(
    console: Console, x: int, y: int, depth: int, game_turn: int,
) -> None:
    """print dungeon depth, game turn, etc."""
    depth_ = depth
    if depth <= 0:
        depth_ = i(f"{depth*-1 + 1} (지상)",
                   f"{depth*-1 + 1} (Overground)")
    tmp = i(f"층: {depth_}",f"Depth: {depth_}")
    console.print(x=x, y=y, string=tmp, fg=color.cyan)
    console.print(x=x+len(tmp)+3, y=y, string=i(f"턴수: {game_turn}",
                                              f"Turns: {game_turn}"), fg=color.white)



def render_health_bar(
    console: Console, x: int, y: int, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=0, bg=color.health_bar_empty)

    if bar_width > 0:
        console.draw_rect(x=x, y=y, width=bar_width, height=1, ch=0, bg=color.health_bar_filled)

    console.print(x=x, y=y, string=i(f"체력: {current_value}/{maximum_value}",
                                     f"Health: {current_value}/{maximum_value}"), fg=color.white)


def render_mana_bar(
    console: Console, x: int, y: int, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=0, bg=color.mana_bar_empty)

    if bar_width > 0:
        console.draw_rect(x=x, y=y, width=bar_width, height=1, ch=0, bg=color.mana_bar_filled)

    console.print(x=x, y=y, string=i(f"마나: {current_value}/{maximum_value}",
                                     f"Mana  : {current_value}/{maximum_value}"), fg=color.white)


def sign(num: int):
    if num < 0:
        return f"{num}"
    else:
        return f"+{num}"


def get_stats_string_and_fg(changed_stat: int, origin_stat: int, change_fg: bool=True) -> Tuple[str, Tuple[int,int,int]]:
    string = f"{changed_stat}"
    fg = color.light_gray
    diff = changed_stat - origin_stat
    if diff != 0:
        string += f"({origin_stat}{(changed_stat - origin_stat):+d})"
        if change_fg:
            if diff < 0:
                fg = color.player_damaged
            else:
                fg = color.health_recovered
    return string, fg

def render_character_status(
    console: Console, x: int, y: int, width: int, height: int, character: Actor, draw_frame:bool = True,
) -> None:
    """NOTE: x, y coordinates is the position of the letter S of the word Str(strength)"""

    render_character_name(console=console, x=x, y=y, character=character)

    render_health_bar(
        console=console,
        x=x,
        y=y+2,
        current_value=character.status.hp,
        maximum_value=character.status.max_hp,
        total_width=26,
    )

    render_mana_bar(
        console=console,
        x=x,
        y=y+3,
        current_value=character.status.mp,
        maximum_value=character.status.max_mp,
        total_width=26,
    )

    stat = character.status.changed_status
    origin = character.status.origin_status
    y_span = 5

    # Status
    str, fg = get_stats_string_and_fg(stat["strength"], origin["strength"])
    console.print(x=x, y=y+y_span, string=i("힘: ","Str: ")+str, fg=fg)
    str, fg = get_stats_string_and_fg(stat["dexterity"], origin["dexterity"])
    console.print(x=x+13, y=y+y_span, string=i("재주: ","Dex: ")+str, fg=fg)
    str, fg = get_stats_string_and_fg(stat["constitution"], origin["constitution"])
    console.print(x=x, y=y+y_span+1, string=i("활력: ","Con: ")+str, fg=fg)
    str, fg = get_stats_string_and_fg(stat["agility"], origin["agility"])
    console.print(x=x+13, y=y+y_span+1, string=i("민첩: ","Agi: ")+str, fg=fg)
    str, fg = get_stats_string_and_fg(stat["intelligence"], origin["intelligence"])
    console.print(x=x, y=y+y_span+2, string=i("지능: ","Int: ")+str, fg=fg)
    str, fg = get_stats_string_and_fg(stat["charm"], origin["charm"])
    console.print(x=x+13, y=y+y_span+2, string=i("매력: ","Cha: ")+str, fg=fg)

    # Armor
    console.print(x=x, y=y+y_span+4, string=i(f"보호도: {stat['protection']}",
                                              f"Protection: {stat['protection']}"), fg=color.white)
    console.print(x=x, y=y+y_span+6, string=i(f"기본 공격력: {stat['base_melee']}",
                                              f"Base Atk: {stat['base_melee']}"), fg=color.white)
    console.print(x=x, y=y+y_span+7, string=i(f"추가 공격력: 0 ~ {stat['additional_melee']}",
                                              f"Add. Atk: {stat['additional_melee']}"), fg=color.white)

    # border for status gui
    if draw_frame:
        console.draw_frame(x=x-1, y=y-1, width=width, height=height, title=i("스테이터스","Status"), clear=False, fg=color.gui_frame_fg, bg=color.gui_frame_bg)


def render_character_state(
    console: Console, engine: Engine, x: int, y: int, height: int, character: Actor, draw_frame: bool=True,
) -> None:
    """
    NOTE: Status effects' string length should be shorter than 13 characters. (including blanks)
    NOTE: This function can display any actor's status. This can be used as checking player's pet status, etc.
    """
    
    num1 = 0 # y position of the leftside lane
    num2 = 0 # y position of the rightside lane
    lane1_x = x #  x pos of the leftside lane
    lane2_x = x+13 # x pos of the rightside lane #NOTE hard-coded
    window_height = height # This graphic ui's frame height (frame border spaces(2 tiles) are ignored)
    # Maximum amount of status effects that can be displayed at once is (window_height * 2).
    hunger_text = character.actor_state.hunger_state

    #### Hunger ####
    if character.actor_state.hunger_state == "hungry":
        hunger_color = color.player_not_good
        hunger_text = i("배고픔","hungry")
    elif character.actor_state.hunger_state == "overeaten":
        hunger_color = color.player_bad
        hunger_text = i("과식","overeaten")
    elif character.actor_state.hunger_state == "starving":
        hunger_color = color.player_bad
        hunger_text = i("굶주림","starving")
    elif character.actor_state.hunger_state == "fainting":
        hunger_color = color.player_severe
        hunger_text = i("배고픔에 허덕임","fainting")
    elif character.actor_state.hunger_state == "satiated":
        hunger_color = color.player_not_good
        hunger_text = i("배부름","satiated")
    elif character.actor_state.hunger_state == "choked by food":
        hunger_color = color.player_severe
        hunger_text = i("끔찍하게 배부름","choked by food")
    else:
        hunger_color = color.white

    if character.actor_state.hunger_state != "":
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=hunger_text, fg=hunger_color)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=hunger_text, fg=hunger_color)

    #### Others ####
    if character.actor_state.is_burning != [0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("불 붙음", "on fire"), fg=color.red)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("불 붙음", "on fire"), fg=color.red)
    if character.actor_state.is_freezing != [0,0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("얼고 있음", "freezing"), fg=color.ice)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("얼고 있음", "freezing"), fg=color.ice)
    if character.actor_state.is_frozen != [0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("얼어붙음", "frozen"), fg=color.blue_ice)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("얼어붙음", "frozen"), fg=color.blue_ice)
    if character.actor_state.is_paralyzing != [0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("마비됨", "paralyzed"), fg=color.yellow)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("마비됨", "paralyzed"), fg=color.yellow)
    if character.actor_state.is_sleeping != [0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("잠이 듬", "sleeping"), fg=color.pink)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("잠이 듬", "sleeping"), fg=color.pink)
    if character.actor_state.is_confused != [0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("혼란", "confused"), fg=color.yellow)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("혼란", "confused"), fg=color.yellow)
    if character.actor_state.is_bleeding != [0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("출혈", "bleeding"), fg=color.blood)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("출혈", "bleeding"), fg=color.blood)
    if character.actor_state.is_angry != [0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("분노", "rage"), fg=color.red)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("분노", "rage"), fg=color.red)
    if character.actor_state.is_melting != [0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("산에 뒤덮임", "dissolving"), fg=color.lime)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("산에 뒤덮임", "dissolving"), fg=color.lime)
    if character.actor_state.is_poisoned != [0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("중독", "poisoned"), fg=color.purple)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("중독", "poisoned"), fg=color.purple)
    if character.is_on_air:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("공중에 떠 있음","airborne"), fg=color.white)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("공중에 떠 있음","airborne"), fg=color.white)
    if character.actor_state.encumbrance == 1:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("약간의 중량 초과", "burdened"), fg=color.burdened)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("약간의 중량 초과", "burdened"), fg=color.burdened)
    if character.actor_state.encumbrance == 2:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("중량 초과", "stressed"), fg=color.stressed)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("중량 초과", "stressed"), fg=color.stressed)
    if character.actor_state.encumbrance == 3:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("심각한 중량 초과", "overloaded"), fg=color.overloaded)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("심각한 중량 초과", "overloaded"), fg=color.overloaded)
    if character.actor_state.encumbrance == 4:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=i("치명적인 중량 초과", "fatal overload"), fg=color.overloaded)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=i("치명적인 중량 초과", "fatal overload"), fg=color.overloaded)
    for detecting in character.actor_state.is_detecting_obj[2]:
        if detecting == "actor":
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string=i("생명체 감지", "detect creatures"), fg=color.actor_detection)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string=i("생명체 감지", "detect creatures"), fg=color.actor_detection)
        #TODO Make rest
    if character.actor_state.is_submerged:
        if character.actor_state.is_underwater:
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string=i("완전히 물에 잠김", "submerged"), fg=color.water_blue)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string=i("완전히 물에 잠김", "submerged"), fg=color.water_blue)
        else:
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string=i("일부분 물에 잠김", "soaked"), fg=color.water_blue)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string=i("일부분 물에 잠김", "soaked"), fg=color.water_blue)
    if character.actor_state.is_drowning != [0,0]:
        # Display turns left until drowning
        if character.actor_state.is_drowning[0] >= character.actor_state.is_drowning[1] * 0.75:# 75% drowning
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string=i(f"익사까지 {character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}턴",
                                                            f"drown:{character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}"), fg=color.player_severe)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string=i(f"익사까지 {character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}턴",
                                                            f"drown:{character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}"), fg=color.player_severe)
        elif character.actor_state.is_drowning[0] >= character.actor_state.is_drowning[1] * 0.5:# 50% drowning
            if num1 > window_height:
                num2 += 1
                console.print(x=lane1_x, y=y + num1, string=i(
                    f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                    f"drown:{character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}"),
                              fg=color.player_bad)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y + num1, string=i(
                    f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                    f"drown:{character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}"),
                              fg=color.player_bad)
        else:
            if num1 > window_height:
                num2 += 1
                console.print(x=lane1_x, y=y + num1, string=i(
                    f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                    f"drown:{character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}"),
                              fg=color.player_not_good)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y + num1, string=i(
                    f"익사까지 {character.actor_state.is_drowning[1] - character.actor_state.is_drowning[0]}턴",
                    f"drown:{character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]}"),
                              fg=color.player_not_good)
    if character.actor_state.is_suffocating != [0,0]:
        # Display turns left until drowning
        if character.actor_state.is_suffocating[0] >= character.actor_state.is_suffocating[1] * 0.75:# 75% drowning
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string=i(f"질식사까지 {character.actor_state.is_suffocating[1]-character.actor_state.is_suffocating[0]}턴",
                                                            f"suffocation:{character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}"), fg=color.player_severe)
            else:
                num1 += 1
                console.print(x=lane2_x, y=y + num2, string=i(
                    f"질식사까지 {character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}턴",
                    f"suffocation:{character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}"),
                              fg=color.player_severe)
        elif character.actor_state.is_suffocating[0] >= character.actor_state.is_suffocating[1] * 0.5:# 50% drowning
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y + num2, string=i(
                    f"질식사까지 {character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}턴",
                    f"suffocation:{character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}"),
                              fg=color.player_bad)
            else:
                num1 += 1
                console.print(x=lane2_x, y=y + num2, string=i(
                    f"질식사까지 {character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}턴",
                    f"suffocation:{character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}"),
                              fg=color.player_bad)
        else:
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y + num2, string=i(
                    f"질식사까지 {character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}턴",
                    f"suffocation:{character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}"),
                              fg=color.player_not_good)
            else:
                num1 += 1
                console.print(x=lane2_x, y=y + num2, string=i(
                    f"질식사까지 {character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}턴",
                    f"suffocation:{character.actor_state.is_suffocating[1] - character.actor_state.is_suffocating[0]}"),
                              fg=color.player_not_good)
        
    # Display "None" if there is no status effects
    if not num1 and not num2:
        num1 = 1
        console.print(x=lane1_x, y=y+num1, string=i("(없음)","(None)"), fg=color.gray)

    # border for state gui
    if draw_frame:
        console.draw_frame(x=x-1, y=y, width=28, height=window_height+2, title=i("상태 이상","State"), clear=False,  fg=color.gui_frame_fg, bg=color.gui_frame_bg)


def render_character_equipments(
    console: Console, x: int, y: int, character: Actor,
) -> None:
    """
    NOTE: Function currently unused(ver27), under development
    NOTE: This function can display any actor's status.
    """

    console.print(x=x, y=y, string=i(f"메인 핸드: {character.equipments.equipments['main_hand'].name}",
                                     f"Main hand: {character.equipments.equipments['main_hand'].name}"), fg=color.gui_status_text)
    #TODO: Display item name instead of memory address
    #TODO: Do not display unequipped body parts


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.camera.rel_to_abs(*engine.mouse_location)

    names_at_mouse_location = get_names_at_location(x=mouse_x, y=mouse_y, game_map=engine.game_map, display_id=False)
    tile_name_at_location = get_tile_name_at_location(x=mouse_x, y=mouse_y, game_map=engine.game_map)

    console.print(x=x, y=y, string=tile_name_at_location, fg=color.gui_mouse_tile)
    console.print(x=x, y=y+engine.config["camera_height"]+1, string=names_at_mouse_location, fg=color.gui_mouse_entity)


def insert_string(origin: str, insert: str, insert_loc: int) -> str:
    return origin[:insert_loc] + insert + origin[insert_loc:]


def render_message_window(
    console: Console, 
    engine: Engine, 
    text: str,
    fixed_width: bool = False,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    title: Optional[str] = "",
    frame_fg: Optional[Tuple[int, int, int]] = (218, 196, 0),
    frame_bg: Optional[Tuple[int, int, int]] = (0, 0, 0),
    text_fg: Optional[Tuple[int, int, int]] = (255, 255, 255),
) -> None:
    """
    Text should be given as a single line.
    The function will automatically divide it into multiple lines if necessary.
    Args:
        x, y:
            top-left position of the window.
            if set to None(default), the function will assign a position between (5,5) ~ (width/2, 5).
        width, height:
            if set to None(default), the function will assign a size between 5 ~ screen_width - 14.
    """
    # values
    screen_width, screen_height = engine.config["screen_width"], engine.config["screen_height"]
    msg = text
    msg_length = len(text)

    # constants
    DEFAULT_X_PADDING = 4
    DEFAULT_Y_PADDING = 4 # Fixed
    MAX_FRAME_WIDTH = screen_width - (DEFAULT_X_PADDING * 2)
    DEFAULT_FRAME_WIDTH = MAX_FRAME_WIDTH
    MAX_FRAME_HEIGHT = screen_height - (DEFAULT_Y_PADDING * 2)

    if fixed_width:
        msg_width = DEFAULT_FRAME_WIDTH - 2
        msg_height = min(int(msg_length / msg_width) + 1, MAX_FRAME_HEIGHT - 2)
        
        # Set frame width, height, x, y
        width, height = msg_width + 2, msg_height + 2
        if not x and not y:
            x, y = DEFAULT_X_PADDING, DEFAULT_Y_PADDING
        msg_x, msg_y = x+1, y+1

        # divide string into multiple parts
        loc = msg_width
        for i in range(0, msg_height):
            msg = insert_string(msg, "\n", loc * (i+1) + i) # adding i because the string gradually gets longer becuase "\n" is being added.
    else:
        if msg_length > MAX_FRAME_WIDTH - 2:
            msg_width = MAX_FRAME_WIDTH - 2
            msg_height = min(int(msg_length / msg_width) + 1, MAX_FRAME_HEIGHT - 2)

            # Set frame width, height, x, y
            if not width and not height:
                width, height = msg_width + 2, msg_height + 2
            if not x and not y:
                x, y = DEFAULT_X_PADDING, DEFAULT_Y_PADDING
            msg_x, msg_y = x+1, y+1

            # divide string into multiple parts
            loc = msg_width
            for i in range(0, msg_height):
                msg = insert_string(msg, "\n", loc * (i+1) + i) # adding i because the string gradually gets longer becuase "\n" is being added.
        else:
            msg_width = max(msg_length, len(title) + 2)
            msg_height = 1

            # Set frame width, height, x, y
            if not width and not height:
                width, height = msg_width + 2, msg_height + 2
            if not x and not y:
                x = int((screen_width - msg_width + 2) / 2)
                y = DEFAULT_Y_PADDING
            msg_x, msg_y = x+1, y+1

    # draw frame
    #draw_thick_frame(console, x, y, width, height, title=title, fg=frame_fg, bg=frame_bg)
    console.draw_frame(x, y, width, height, title=title, clear=True, fg=frame_fg, bg=frame_bg)

    # print msg
    console.print(msg_x, msg_y, msg, fg=text_fg)

def render_img(
    console, 
    img,
    dest_x:int = 0, 
    dest_y:int = 0, 
    img_x: int = 0, 
    img_y: int = 0,
    img_width: int = -1,
    img_height: int = -1,
    ):
    """
    Args:
        https://python-tcod.readthedocs.io/en/latest/tcod/image.html?highlight=blit_2x#tcod.image.Image.blit_2x

        console (Console):
            Blit destination Console.
        dest_x (int):
            Console tile X position starting from the left at 0.
        dest_y (int):
            Console tile Y position starting from the top at 0.
        img_x (int):
            Left corner pixel of the Image to blit
        img_y (int):
            Top corner pixel of the Image to blit
        img_width (int):
            Width of the Image to blit. Use -1 for the full Image width.
        img_height (int):
            Height of the Image to blit. Use -1 for the full Image height.
    """
    # tcod.image_blit(image=img, console=console, x=dest_x, y=dest_y, bkgnd_flag=1, scalex=0.7, scaley=0.7, angle=0)
    tcod.image_blit_2x(image=img, console=console, dx=dest_x, dy=dest_y, sx=img_x, sy=img_y, w=img_width, h=img_height)
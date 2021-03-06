from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from numpy.core.numeric import Inf
from entity import Actor, Item

import color

if TYPE_CHECKING:
    from game_map import GameMap
    from tcod import Console
    from engine import Engine
    


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    """
    Display entity's name that are at the mouse cursor location. (Only when the location is visible)
    """
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = []

    for entity in reversed(game_map.entities):
        if entity.x == x and entity.y == y:
            if isinstance(entity, Item):
                # If entity is a item, display stack_count as well
                if entity.stack_count > 1:
                    names.append(f"{entity.name} x{entity.stack_count}")
                else:
                    names.append(entity.name)
            elif isinstance(entity, Actor):
                if entity.ai:
                    if entity.ai.owner == game_map.engine.player:
                        names.append(f"Pet {entity.name}")
                    else:
                        names.append(entity.name)
                else:
                    names.append(entity.name)
            else:
                names.append(entity.name)

    names = ", ".join(names)

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
    console.print(x=x, y=y, string=f"Depth: {depth}", fg=color.white)
    console.print(x=x+11, y=y, string=f"Turn: {game_turn}", fg=color.gray)


def render_health_bar(
    console: Console, x: int, y: int, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=1, bg=color.health_bar_empty)

    if bar_width > 0:
        console.draw_rect(x=x, y=y, width=bar_width, height=1, ch=1, bg=color.health_bar_filled)

    console.print(x=x, y=y, string=f"HP: {current_value}/{maximum_value}", fg=color.white)


def render_mana_bar(
    console: Console, x: int, y: int, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=1, bg=color.mana_bar_empty)

    if bar_width > 0:
        console.draw_rect(x=x, y=y, width=bar_width, height=1, ch=1, bg=color.mana_bar_filled)

    console.print(x=x, y=y, string=f"MP: {current_value}/{maximum_value}", fg=color.white)


def sign(num: int):
    if num < 0:
        return f"{num}"
    else:
        return f"+{num}"


def render_character_status(
    console: Console, x: int, y: int, character: Actor, draw_frame:bool = True,
) -> None:
    """NOTE: x, y coordinates is the position of the letter S of the word Str(strength)"""
    stat = character.status.changed_status

    # Status
    console.print(x=x, y=y, string=f"Str: {stat['strength']}", fg=color.light_gray)
    console.print(x=x+13, y=y, string=f"Dex: {stat['dexterity']}", fg=color.light_gray)
    console.print(x=x, y=y+1, string=f"Con: {stat['constitution']}", fg=color.light_gray)
    console.print(x=x+13, y=y+1, string=f"Agi: {stat['agility']}", fg=color.light_gray)
    console.print(x=x, y=y+2, string=f"Int: {stat['intelligence']}", fg=color.light_gray)
    console.print(x=x+13, y=y+2, string=f"Cha: {stat['charm']}", fg=color.light_gray)

    # Armor
    console.print(x=x, y=y+4, string=f"Protection level: {stat['protection']}", fg=color.white)
    console.print(x=x, y=y+6, string=f"Base Atk: {stat['base_melee']}", fg=color.white)
    console.print(x=x, y=y+7, string=f"Add. Atk: 0 ~ {stat['additional_melee']}", fg=color.white)

    # border for status gui
    if draw_frame:
        console.draw_frame(x=x-1, y=y-6, width=28, height=15, title="Player Status", clear=False, fg=(255,255,255), bg=(0,0,0))


def render_character_state(
    console: Console, x: int, y: int, height: int, character: Actor, draw_frame: bool=True,
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

    #### Hunger ####
    if character.actor_state.hunger_state == "hungry":
        hunger_color = color.player_damaged
    elif character.actor_state.hunger_state == "overeaten":
        hunger_color = color.player_damaged
    elif character.actor_state.hunger_state == "starving":
        hunger_color = color.red
    elif character.actor_state.hunger_state == "fainting":
        hunger_color = color.red
    elif character.actor_state.hunger_state == "satiated":
        hunger_color = color.yellow
    else:
        hunger_color = color.white

    if character.actor_state.hunger_state != "":
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string=character.actor_state.hunger_state, fg=hunger_color)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string=character.actor_state.hunger_state, fg=hunger_color)

    #### Others ####
    if character.actor_state.is_burning != [0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="on fire", fg=color.red)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="on fire", fg=color.red)
    if character.actor_state.is_freezing != [0,0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="freezing", fg=color.ice)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="freezing", fg=color.ice)
    if character.actor_state.is_frozen != [0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="frozen", fg=color.blue_ice)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="frozen", fg=color.blue_ice)
    if character.actor_state.is_paralyzing != [0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="paralyzed", fg=color.yellow)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="paralyzed", fg=color.yellow)
    if character.actor_state.is_confused != [0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="confused", fg=color.yellow)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="confused", fg=color.yellow)
    if character.actor_state.is_bleeding != [0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="bleeding", fg=color.blood)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="bleeding", fg=color.blood)
    if character.actor_state.is_melting != [0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="covered in acid", fg=color.lime)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="covered in acid", fg=color.lime)
    if character.actor_state.is_poisoned != [0,0,0,0]:
        if num1 > window_height:
            num2 += 1
            console.print(x=lane2_x, y=y+num2, string="poisoned", fg=color.purple)
        else:
            num1 += 1
            console.print(x=lane1_x, y=y+num1, string="poisoned", fg=color.purple)
    if character.actor_state.is_submerged:
        if character.actor_state.is_underwater:
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string="fully submerged", fg=color.water_blue)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string="fully submerged", fg=color.water_blue)
        else:
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string="partially submerged", fg=color.water_blue)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string="partially submerged", fg=color.water_blue)
    if character.actor_state.is_drowning != [0,0]:
        # Display turns left until drowning
        if character.actor_state.is_drowning[0] >= character.actor_state.is_drowning[1] * 0.75:# 75% drowning
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string=f"drowning ({character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]})", fg=color.red)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string=f"drowning ({character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]})", fg=color.red)
        elif character.actor_state.is_drowning[0] >= character.actor_state.is_drowning[1] * 0.5:# 50% drowning
            if num1 > window_height:
                num2 += 1
                console.print(x=lane2_x, y=y+num2, string=f"drowning ({character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]})", fg=color.player_damaged)
            else:
                num1 += 1
                console.print(x=lane1_x, y=y+num1, string=f"drowning ({character.actor_state.is_drowning[1]-character.actor_state.is_drowning[0]})", fg=color.player_damaged)
        
    # Display "None" if there is no status effects
    if not num1 and not num2:
        num1 = 1
        console.print(x=lane1_x, y=y+num1, string="None", fg=color.gray)

    # border for state gui
    if draw_frame:
        console.draw_frame(x=x-1, y=y, width=28, height=window_height+2, title="Status Effects", clear=False, fg=(255,255,255), bg=(0,0,0))


def render_character_equipments(
    console: Console, x: int, y: int, character: Actor,
) -> None:
    """
    NOTE: Function currently unused(ver27), under development
    NOTE: This function can display any actor's status.
    """

    console.print(x=x, y=y, string=f"Main-hand: {character.equipments.equipments['main_hand']}", fg=color.gui_status_text)
    #TODO: Display item name instead of memory address
    #TODO: Do not display unequipped body parts


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(x=mouse_x, y=mouse_y, game_map=engine.game_map)

    tile_name_at_location = get_tile_name_at_location(x=mouse_x, y=mouse_y, game_map=engine.game_map)

    console.print(x=x, y=y, string=tile_name_at_location, fg=color.white)
    console.print(x=x, y=y+1, string=names_at_mouse_location, fg=color.yellow)

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
    console.draw_frame(x, y, width, height, title=title, fg=frame_fg, bg=frame_bg, clear=True)

    # print msg
    console.print(msg_x, msg_y, msg, fg=text_fg)

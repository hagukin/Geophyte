import random

from typing import TYPE_CHECKING
from room_factories import Room
from game_map import GameMap
import random

if TYPE_CHECKING:
    from entity import Item


def grow_shop_item(gamemap: GameMap, x: int, y: int, item_dict: dict) -> None:
    random.choices(tuple(item_dict.keys()), tuple(item_dict.values()), k=1)[0].spawn(gamemap, x, y)


def generate_shop_item(gamemap: GameMap, room: Room) -> None:
    if len(room.doors) != 1:
        print(f"WARNING::There should be 1 door, instead the room {room.terrain.terrain_id} has {len(room.doors)} door(s).\
            \nIf there is 0 door attached to this room, the game might have canceled the door spawning if it collided with protected area of the gamemap.\
            \nIf there are more than 1 doors attached to this room, something might have gone wrong.")
        return None
    door_dir = room.get_door_dir(room.doors[0][0], room.doors[0][1])

    # keep one line as blank tile. (Nethack style shop)
    tmp = room.inner_tiles
    for tile in tmp:
        if (door_dir == 'u' and tile[1] <= room.y1 + 1):
            continue
        elif (door_dir == 'd' and tile[1] >= room.y2 - 1):
            continue
        elif (door_dir == 'l' and tile[0] <= room.x1 + 1):
            continue
        elif (door_dir == 'r' and tile[0] >= room.x2 - 1):
            continue
        else:
            # Spawn item
            grow_shop_item(gamemap=gamemap, x=tile[0], y=tile[1], item_dict=room.terrain.sell_items)


def generate_shop(gamemap: GameMap, room: Room) -> None:
    """
    Custom function for generating shops.
    """
    generate_shop_item(gamemap, room)
    # TODO Add shopkeeper


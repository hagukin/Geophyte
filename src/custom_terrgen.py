import random

from typing import TYPE_CHECKING
from unique_terrains.shop import ShopTerrain
from room_factories import Room
from game_map import GameMap
from entity import Actor
import random

if TYPE_CHECKING:
    pass


def grow_shop_item(gamemap: GameMap, x: int, y: int, room: Room) -> None:
    item = random.choices(tuple(room.terrain.sell_items.keys()), tuple(room.terrain.sell_items.values()), k=1)[0]
    tmp = item.spawn(gamemap, x, y)
    tmp.stackable = False # Items in shops are spawned as nonstackable to prevent glitches and to clarify each item's indivisual prices.
    # After purchasing it, the items becomes stackable again. (shopkeeper.remove_item_from_shop())
    room.terrain.items_on_stock.append(tmp)


def generate_shop_item(gamemap: GameMap, room: Room) -> None:
    if len(room.doors) != 1:
        print(f"WARNING::There should be 1 door, instead the room {room.terrain.terrain_id} has {len(room.doors)} door(s).\
            \nIf there is 0 door attached to this room, the game might have canceled the door spawning if it collided with protected area of the gamemap.\
            \nIf there are more than 1 doors attached to this room, something might have gone wrong.")
        return None
    door_dir = room.get_door_dir(room.doors[0][0], room.doors[0][1])

    # keep one line as blank tile. (Nethack style shop)
    tmp = room.inner_tiles
    idle_tile = room.doors[0] # tile where shopkeeper idles.
    for tile in tmp:
        if (door_dir == 'u' and tile[1] <= room.y1 + 1):
            if tile[0] != room.doors[0][0]: # preventing shopkeeper blocking the passage
                idle_tile = tile
            continue
        elif (door_dir == 'd' and tile[1] >= room.y2 - 1):
            if tile[0] != room.doors[0][0]: # preventing shopkeeper blocking the passage
                idle_tile = tile
            continue
        elif (door_dir == 'l' and tile[0] <= room.x1 + 1):
            if tile[1] != room.doors[0][1]: # preventing shopkeeper blocking the passage
                idle_tile = tile
            continue
        elif (door_dir == 'r' and tile[0] >= room.x2 - 1):
            if tile[1] != room.doors[0][1]: # preventing shopkeeper blocking the passage
                idle_tile = tile
            continue
        else:
            # Spawn item
            grow_shop_item(gamemap=gamemap, x=tile[0], y=tile[1], room=room)

    if idle_tile == room.doors[0]:
        print("ERROR::Couldn't find a valid location for shopkeeper to idle. Using door location instead. - custom_terrgen.generate_shop_item()")
    room.terrain.shopkeeper_loc = idle_tile


def spawn_shopkeeper(gamemap: GameMap, room: Room) -> None:
    """
    Spawn shopkeeper for the given shop.
    """
    tmp = room.terrain.shopkeeper_type.spawn(gamemap, room.terrain.shopkeeper_loc[0], room.terrain.shopkeeper_loc[1])
    tmp.ai.room = room
    return tmp

def adjust_items(shopkeeper: Actor, room: Room) -> None:
    """
    Set shop items' item_state.is_being_sold_from to shopkeeper.
    """
    for item in room.terrain.items_on_stock:
        item.item_state.is_being_sold_from = id(shopkeeper) #NOTE: Since this value is copied during deep copying an item entity, you should use integer instead of directly referencing the actor.

def generate_shop(gamemap: GameMap, room: Room) -> None:
    """
    Custom function for generating shops.
    """
    try:
        generate_shop_item(gamemap, room)
        shopkeeper = spawn_shopkeeper(gamemap, room)
        adjust_items(shopkeeper, room)
    except AttributeError:
        print("ERROR::Tried to generate a shop onto a non-shop-terrain room. - custom_terrgen.generate_shop()")


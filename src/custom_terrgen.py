import random

from typing import TYPE_CHECKING
from unique_terrains.guarded_treasure import GuardedTreasureTerrain
from rooms import Room
from game_map import GameMap
from entity import Actor
import random

if TYPE_CHECKING:
    pass

class ShopTerrGen:
    @staticmethod
    def grow_shop_item(gamemap: GameMap, x: int, y: int, room: Room) -> None:
        item = random.choices(tuple(room.terrain.sell_items.keys()), tuple(room.terrain.sell_items.values()), k=1)[0]
        tmp = item.spawn(gamemap, x, y)
        tmp.stackable = False # Items in shops are spawned as nonstackable to prevent glitches and to clarify each item's indivisual prices.
        # After purchasing it, the items becomes stackable again. (shopkeeper.remove_item_from_shop())
        room.terrain.items_on_stock.append(tmp)

    @staticmethod
    def generate_shop_item(gamemap: GameMap, room: Room) -> None:
        door_dir = list(room.doors_rel.keys())[0]
        if len(room.doors_rel.keys()) != 1:
            print(f"WARNING::Shop generation cancelled - There should be 1 door, instead the room {room.terrain.terrain_id} has {len(door_dir)} door(s).")

        # keep 2 line as blank tile. (Nethack style shop)
        tmp = room.inner_tiles
        idle_tile = room.doors[door_dir] # tile where shopkeeper idles.
        for tile in tmp:
            if (door_dir == 'u' and tile[1] <= room.y1 + 1):
                if tile[0] != room.doors[door_dir][0]: # preventing shopkeeper blocking the passage
                    idle_tile = tile
                continue
            elif (door_dir == 'd' and tile[1] >= room.y2 - 1):
                if tile[0] != room.doors[door_dir][0]: # preventing shopkeeper blocking the passage
                    idle_tile = tile
                continue
            elif (door_dir == 'l' and tile[0] <= room.x1 + 1):
                if tile[1] != room.doors[door_dir][1]: # preventing shopkeeper blocking the passage
                    idle_tile = tile
                continue
            elif (door_dir == 'r' and tile[0] >= room.x2 - 1):
                if tile[1] != room.doors[door_dir][1]: # preventing shopkeeper blocking the passage
                    idle_tile = tile
                continue
            else:
                # Spawn item
                ShopTerrGen.grow_shop_item(gamemap=gamemap, x=tile[0], y=tile[1], room=room)

        if idle_tile == room.doors[door_dir]:
            print("WARNING::Couldn't find a valid location for shopkeeper to idle. Using random indoor location instead. - custom_terrgen.generate_shop_item()", end=' ')
            for tile in tmp:
                if tile[0] != room.single_door[0] and tile[1] != room.single_door[1]:
                    idle_tile = tile
                    print("Random tile found.")
                    break
        room.terrain.shopkeeper_loc = idle_tile

    @staticmethod
    def spawn_shopkeeper(gamemap: GameMap, room: Room) -> None:
        """
        Spawn shopkeeper for the given shop.
        """
        tmp = room.terrain.shopkeeper_type.spawn(gamemap, room.terrain.shopkeeper_loc[0], room.terrain.shopkeeper_loc[1])
        tmp.ai.room = room
        return tmp

    @staticmethod
    def adjust_items(shopkeeper: Actor, room: Room) -> None:
        """
        Set shop items' item_state.is_being_sold_from to shopkeeper.
        """
        for item in room.terrain.items_on_stock:
            item.item_state.is_being_sold_from = id(shopkeeper) #NOTE: Since this value is copied during deep copying an item entity, you should use integer instead of directly referencing the actor.

    @staticmethod
    def generate_shop(gamemap: GameMap, room: Room) -> None:
        """
        Custom function for generating shops.
        """
        ShopTerrGen.generate_shop_item(gamemap, room)
        shopkeeper = ShopTerrGen.spawn_shopkeeper(gamemap, room)
        ShopTerrGen.adjust_items(shopkeeper, room)
        # except AttributeError as e:
        #     print(e)
        #     print("ERROR::Tried to randomize a shop onto a non-shop-terrain room. - custom_terrgen.generate_shop()")


class ChamberOfKugahTerrGen:
    @staticmethod
    def generate_amulet_of_kugah(gamemap: GameMap, room: Room) -> None:
        from item_factories import amulet_of_kugah
        coors = room.center
        tmp = amulet_of_kugah.spawn(gamemap, coors[0], coors[1])

    @staticmethod
    def generate_chamber_of_kugah(gamemap: GameMap, room: Room) -> None:
        """
        Custom function for generating chamber of kugah.
        """
        ChamberOfKugahTerrGen.generate_amulet_of_kugah(gamemap, room)


class GuardedTreasureTerrGen:
    @staticmethod
    def spawn_guardians(gamemap: GameMap, room: Room) -> None:
        """Spawn 4 guardian onto 4 corners."""
        if isinstance(room.terrain, GuardedTreasureTerrain):
            for x,y in ((room.x1+2,room.y1+2),(room.x1+2,room.y2-2),(room.x2-2,room.y1+2),(room.x2-2,room.y2-2)):
                monster = room.terrain.guardian_type.spawn(gamemap=gamemap, x=x, y=y)
                monster.actor_state.apply_sleeping(value=[0,-1], forced=True) # Infinite sleeping
                room.terrain.guardians.append(monster)
        return None

    @staticmethod
    def generate_treasure_chest(gamemap: GameMap, room: Room) -> None:
        """Spawn 1 chest on the center of the room
        NOTE: To specify the chest type, modify terrain.gen_chest parameter."""
        if not isinstance(room.terrain, GuardedTreasureTerrain):
            return None

        checklist = room.terrain.gen_treasure_chests["checklist"]
        chest_id_chosen = random.choices(list(checklist.keys()), weights=list(checklist.values()), k=1)[0]
        chest_num = 1

        from terrain_generation import grow_chest
        chest = grow_chest(gamemap=gamemap, x=room.center[0], y=room.center[1], chest_id=chest_id_chosen,
                   initial_items=room.terrain.gen_treasure_chests["initial_items"])

        chest.trigger_when_take = room.terrain.guardians

    @staticmethod
    def generate_guarded_treasure(gamemap: GameMap, room: Room) -> None:
        """Custom function for generating guarded treasure terain."""
        GuardedTreasureTerrGen.spawn_guardians(gamemap, room)
        GuardedTreasureTerrGen.generate_treasure_chest(gamemap, room)
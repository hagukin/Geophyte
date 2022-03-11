from terrain import Terrain
from typing import TYPE_CHECKING, Tuple, Optional
from entity import Actor
from actor_factories import shopkeeper
from order import InventoryOrder
from game_map import GameMap
from rooms import Room
import random


class ShopTerrain(Terrain):
    """
    Shop terrain component.
    """
    def __init__(
        self,
        name: str = "shop",
        terrain_id: str = "shop",
        terrain_desc: str = "",
        rarity: int = 1,
        min_width: int = 6, # min 6
        max_width: int = 10,
        min_height: int = 6, # min 6
        max_height: int = 10,
        shape: dict = None,
        spawn_item: bool = False,
        spawn_monster: bool = False,
        has_wall: bool = True, #TODO: need to add feature
        protected: bool = True,
        has_door: bool = True,
        can_have_stair: bool = False,
        door_num_range = (1,),
        door_num_weight = (1,),
        gen_grass = None,
        gen_holes=None,
        gen_water = None,
        gen_pits = None,
        gen_traps = None,
        gen_chests = None,
        custom_gen = None, # Must have one
        sell_items = None,
        sell_items_type_limit: Optional[Tuple[InventoryOrder, ...]] = None,
        items_on_stock = None,
        shopkeeper_type: Actor = shopkeeper,
    ):
        super().__init__(
            name=name,
            terrain_id=terrain_id,
            terrain_desc=terrain_desc,
            rarity=rarity,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            shape=shape,
            spawn_item=spawn_item,
            spawn_monster=spawn_monster,
            has_wall=has_wall,
            protected=protected,
            has_door=has_door,
            can_have_stair=can_have_stair,
            door_num_range=door_num_range,
            door_num_weight=door_num_weight,
            gen_grass=gen_grass,
            gen_holes=gen_holes,
            gen_water=gen_water,
            gen_pits=gen_pits,
            gen_traps=gen_traps,
            gen_chests=gen_chests,
            custom_gen=custom_gen,
        )
        """
        Vars:
            shopkeeper_loc:
                Tuple(int, int).
                Location where shopkeeper idles when there are no money to collect. (no customers / customer hasn't purchased anything yet)
            sell_items:
                {
                    item object : chance of spawning(weight)
                }
            items_on_stock:
                List of item objects that currently belongs to the shop.
                
        NOTE: Shop should always sell items that has stack count as 1.
        This is to prevent unwanted behaviour when player broke(or used/consumed) an item in the shop, and tries to pay the bill.
        (Shopkeeper asks the fee for its price * stack_count, but if items gets removed via consume, its stack_count is 0 so shopkeeper will ask for 0 shine, which could break the shop system.
        See item.price_of_all_stack() for details.)
        """
        if shape == None:
            self.shape = {
            "rectangular":1 #Shops can be in any shape, but rectangular is most stable
            }
        else:
            self.shape = shape

        self.shopkeeper_loc = None # initialized during ShopTerrGen.generate_shop_item()
        self.shopkeeper_type = shopkeeper_type
        self.shopkeeper = None

        self.sell_items_type_limit = sell_items_type_limit
        if sell_items == None:
            self.sell_items = {} # Spawn all items
            from item_factories import item_rarity, temp_items_lists
            for i in range(len(temp_items_lists)):
                if temp_items_lists[i].spawnable and not temp_items_lists[i].is_artifact: # Does not spawn artifact.
                    # NOTE: Since shop items are initialized early on, shop can techinically generate non-artifact item that is in item_manager._block_spawn_id_set
                    if self.sell_items_type_limit:
                        tmp = [x.value for x in sell_items_type_limit]
                        if temp_items_lists[i].item_type.value in tmp:
                            self.sell_items[temp_items_lists[i]] = item_rarity[i]
                    else:
                        self.sell_items[temp_items_lists[i]] = item_rarity[i]
        else:
            self.sell_items = sell_items

        if items_on_stock == None:
            self.items_on_stock = []
        else:
            self.items_on_stock = items_on_stock


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
            print("WARNING::Couldn't find a valid location for shopkeeper to idle. Using random indoor location instead. - ShopTerrGen.generate_shop_item()", end=' ')
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
        #     print("ERROR::Tried to randomize a shop onto a non-shop-terrain room. - ShopTerrGen.generate_shop()")





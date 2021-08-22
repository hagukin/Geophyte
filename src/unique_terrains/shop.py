from terrain import Terrain
from typing import TYPE_CHECKING, Tuple, Optional
from entity import Actor
from actor_factories import shopkeeper
from order import InventoryOrder

if TYPE_CHECKING:
    from room_factories import Room

class ShopTerrain(Terrain):
    """
    Shop terrain component.
    """
    def __init__(
        self,
        name: str = "Shop",
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
        """
        if shape == None:
            self.shape = {
            "rectangular":1 #Shops can be in any shape, but rectangular is most stable
            }
        else:
            self.shape = shape

        self.shopkeeper_loc = None # initialized during custom_terrgen.generate_shop_item()
        self.shopkeeper_type = shopkeeper_type
        self.shopkeeper = None

        self.sell_items_type_limit = sell_items_type_limit
        if sell_items == None:
            self.sell_items = {} # Spawn all items
            from item_factories import item_rarity, temp_items_lists
            for i in range(len(temp_items_lists)):
                if temp_items_lists[i].spawnable:
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



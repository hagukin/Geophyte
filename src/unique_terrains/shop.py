from terrain import Terrain
from typing import TYPE_CHECKING
from entity import Actor
from actor_factories import shopkeeper

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
        shape: dict = {
            "rectangular":1, #Shops can be in any shape, but rectangular is most stable
            "perpendicular":99,
        },
        spawn_item: bool = False,
        spawn_monster: bool = False,
        has_wall: bool = True, #TODO: need to add feature
        wall_protected: bool = True,
        has_door: bool = True,
        can_have_stair: bool = False,
        door_num_range = (1,),
        door_num_weight = (1,),
        gen_grass = None,
        gen_water = None,
        gen_traps = None,
        gen_chests = None,
        custom_gen = None, # Must have one
        sell_items = dict(),
        items_on_stock = list(),
        shopkeeper_type: Actor = shopkeeper,
    ):
        super().__init__(
            name,
            terrain_id,
            terrain_desc,
            rarity,
            min_width,
            max_width,
            min_height,
            max_height,
            shape,
            spawn_item,
            spawn_monster,
            has_wall,
            wall_protected,
            has_door,
            can_have_stair,
            door_num_range,
            door_num_weight,
            gen_grass,
            gen_water,
            gen_traps,
            gen_chests,
            custom_gen,
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
        self.shopkeeper_loc = None # initialized during custom_terrgen.generate_shop_item()
        self.shopkeeper_type = shopkeeper_type
        self.shopkeeper = None
        self.sell_items = sell_items
        self.items_on_stock = items_on_stock



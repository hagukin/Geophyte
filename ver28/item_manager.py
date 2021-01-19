from entity import Item
from order import InventoryOrder

import random
import copy

class ItemManager:
    def __init__(self):
        """
        Keep track of mutable data of item entities 
        that can affect the entire item type.

        e.g. identification, randomized color, randomized name, etc
        """
        self.engine = None
        self.items_lists = None
        self.item_rarity = None
        self.items_identified = {}
        self.items_fake_info = {} # key: item.entity_id, value: dice{"fg":(r,g,b), "bg":(r,g,b), "name":string, "char":string, "entity_desc":string}
        # if there is no data stored in items_fake_info, or if the data is set to None,
        # the item will use its default value instead.
        # e.g. if items_fake_info["potion_of_fire"] throws an error,
        # potion of fire will use its default color, name, etc.
        self.colors_for_potions = [
            ("bloodlike",(178,34,34), None),
            ("red",(255,0,0), None),
            ("pink",(255,0,127), None),
            ("violet",(199,21,133), None),
            ("orange",(255,69,0), None),
            ("fruity",(255,165,0), None),
            ("golden",(255,215,0), None),
            ("yellow",(255,255,0), None),
            ("shining",(255,255,224), None),
            ("mirky",(189,183,107), None),
            ("lavender",(230,230,250), None),
            ("magenta",(255,0,255), None),
            ("indigo",(75,0,130), None),
            ("lime",(0,255,0), None),
            ("glowing",(0,250,154), None),
            ("green",(34,139,34), None),
            ("olive",(128,128,0), None),
            ("cyan",(0,255,255), None),
            ("lightblue",(173,216,230), None),
            ("blue",(0,0,255), None),
            ("navy",(0,0,128), None),
            ("white",(255,250,250), None),
            ("silver",(192,192,192), None),
            ("gray",(128,128,128), None),
            ("black",(10,10,10), None),
        ] # NOTE: Currently 24 colors available
        self.colors_for_scrolls = copy.copy(self.colors_for_potions)

        # shuffle color
        random.shuffle(self.colors_for_potions)
        random.shuffle(self.colors_for_scrolls)

    def initialize_data(self):
        import item_factories

        # initialize items_lists
        if self.items_lists == None:
            self.items_lists = copy.copy(item_factories.temp_items_lists)
        
            for item in self.items_lists:
                # initialize items_fake_info (info is set to None if the item doesn't have any "fake information".)
                self.items_fake_info[item.entity_id] = {"fg":None, "bg":None, "name":None, "char":None, "entity_desc":None}

                #  Randomize items
                if item.should_randomize:
                    self.randomize_item(item)

                # initialize items_identified (decide whether item should start as identified or not)
                self.items_identified[item.entity_id] = item.item_state.is_identified

    def randomize_item(self, item: Item):
        if item.item_type == InventoryOrder.SCROLL:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.SCROLL)
            self.items_fake_info[item.entity_id]["name"] = "Scroll labeled " + self.gen_randomized_string(random.randint(4, 8))
            self.items_fake_info[item.entity_id]["entity_desc"] = "Scroll made out of thin paper. You are clueless about what this scroll could do."
            self.items_fake_info[item.entity_id]["fg"] = fg
        elif item.item_type == InventoryOrder.POTION:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.POTION)
            self.items_fake_info[item.entity_id]["name"] = color_name + " potion"
            self.items_fake_info[item.entity_id]["entity_desc"] = f"{color_name} colored potion. You are clueless about what this potion could do."
            self.items_fake_info[item.entity_id]["fg"] = fg
            self.items_fake_info[item.entity_id]["bg"] = bg
        else:
            print(f"ERROR::Cannot randomize {item.name} of {item.item_type} type.")
            return None

    def gen_randomized_string(self, string_length: int = 6) -> str:
        vowels = "aeiou"
        non_vowels = "bcdfghjklmnpqrstvwxyz"
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        
        word = ""
        for _ in range(string_length):
            word += alphabet[random.randint(0,25)]
        return word

    def gen_randomized_color(self, item_type):
        if item_type == InventoryOrder.POTION:
            return self.colors_for_potions.pop()
        elif item_type == InventoryOrder.SCROLL:
            return self.colors_for_scrolls.pop()


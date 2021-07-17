from entity import Item
from order import InventoryOrder
from korean import grammar as g
from game import Game

import random
import copy

class ItemManager:
    def __init__(self):
        """
        Keep track of mutable data of item entities 
        that can affect the entire item type.

        e.g. identification, randomized color, randomized name, etc
        """
        self.items_lists = None
        self.item_rarity = None
        self.items_identified = {}
        self.items_fake_info = {} # key: item.entity_id, value: dice{"fg":(r,g,b), "bg":(r,g,b), "name":string, "char":string, "entity_desc":string}
        # items_fake_info stores fake information(or the surface information) for EVERY items that exists in game.
        # However, if the data's values are set to None, they are unused, and the item will use its default value instead.
        # e.g. if items_fake_info["potion_of_fire"]["name"] == None,
        # potion of fire will use its default name.
        self.colors_for_potions = [
            ("적혈색",(178,34,34), None),
            ("빨간색",(255,0,0), None),
            ("핑크색",(255,0,127), None),
            ("자주색",(199,21,133), None),
            ("주황색",(255,69,0), None),
            ("백황색",(255,165,0), None),
            ("황금색",(255,215,0), None),
            ("노란색",(255,255,0), None),
            ("빛나는",(255,255,224), None),
            ("뿌연",(189,183,107), None),
            ("라벤더색",(230,230,250), None),
            ("마젠타색",(255,0,255), None),
            ("인디고색",(75,0,130), None),
            ("라임색",(0,255,0), None),
            ("반짝이는",(0,250,154), None),
            ("초록색",(34,139,34), None),
            ("올리브색",(128,128,0), None),
            ("시안색",(0,255,255), None),
            ("하늘색",(173,216,230), None),
            ("파란색",(0,0,255), None),
            ("군청색",(0,0,128), None),
            ("하얀색",(255,250,250), None),
            ("은색",(192,192,192), None),
            ("회색",(128,128,128), None),
            ("검정색",(10,10,10), None),
        ] # NOTE: Currently 24 colors available TODO: Multi lang support
        self.colors_for_scrolls = copy.copy(self.colors_for_potions)

        # shuffle color
        random.shuffle(self.colors_for_potions)
        random.shuffle(self.colors_for_scrolls)

    def engine(self):
        return Game.engine

    def identify_type(self, item_id:str, identify_level: int=1):
        """
        NOTE: When identifying an entire type, use item_manager.identify_type instead.
        NOTE: Normally, you should not "fully identify" the entire item type.
        Thus, identify_level should stay 1 in normal occasions.
        """
        self.items_identified[item_id] = identify_level

    def unidentify_type(self, item_id:str):
        self.items_identified[item_id] = 0

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
            self.items_fake_info[item.entity_id]["name"] = f"{self.gen_randomized_string(random.randint(4, 8))}이라고 적혀있는 주문서"
            self.items_fake_info[item.entity_id]["entity_desc"] = "얇은 종이로 만들어진 주문서이다. 주문서의 내용을 해독할 수 없다."
            self.items_fake_info[item.entity_id]["fg"] = fg
        elif item.item_type == InventoryOrder.POTION:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.POTION)
            self.items_fake_info[item.entity_id]["name"] = color_name + " 물약"
            self.items_fake_info[item.entity_id]["entity_desc"] = f"{color_name} 물약. 마시면 무슨 일이 일어날지 알 수 없다."
            self.items_fake_info[item.entity_id]["fg"] = fg
            self.items_fake_info[item.entity_id]["bg"] = bg
        else:
            print(f"ERROR::Cannot randomize {item.name} of {item.item_type} type.")
            return None

    def gen_randomized_string(self, string_length: int = 6, vowel_chance: float = 0.5, completely_random: bool = False) -> str:
        vowels = "aeiou"
        non_vowels = "bcdfghjklmnpqrstvwxyz"
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        
        word = ""
        for _ in range(string_length):
            if completely_random:
                word += alphabet[random.randint(0,len(alphabet) - 1)]
            else:
                if random.random() < vowel_chance:
                    word += vowels[random.randint(0,len(vowels) - 1)]
                else:
                    word += non_vowels[random.randint(0,len(non_vowels) - 1)]
        return word

    def gen_randomized_color(self, item_type):
        if item_type == InventoryOrder.POTION:
            return self.colors_for_potions.pop()
        elif item_type == InventoryOrder.SCROLL:
            return self.colors_for_scrolls.pop()


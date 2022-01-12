from entity import Item
from order import InventoryOrder
from korean import grammar as g
from game import Game
from typing import List
from language import interpret as i

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
        self.items_identified = {}
        self.items_fake_info = {} # key: item.entity_id, value: dice{"fg":(r,g,b), "bg":(r,g,b), "name":string, "char":string, "entity_desc":string}
        # items_fake_info stores fake information(or the surface information) for EVERY items that exists in game.
        # However, if the data's values are set to None, they are unused, and the item will use its default value instead.
        # e.g. if items_fake_info["potion_of_fire"]["name"] == None,
        # potion of fire will use its default name.

        self.generated_artifacts = set() # List of artifacts that have been spawned, and should not be spawned naturally again.

        self.colors_for_potions = [
            (i("적혈색","blood-red"),(178,34,34), None),
            (i("빨간색","red"),(255,0,0), None),
            (i("핑크색","pink"),(255,0,127), None),
            (i("자주색","amethyst"),(199,21,133), None),
            (i("주황색","orange"),(255,69,0), None),
            (i("백황색","pale-orange"),(255,165,0), None),
            (i("황금색","gold"),(255,215,0), None),
            (i("노란색","yellow"),(255,255,0), None),
            (i("빛나는","shining"),(255,255,224), None),
            (i("뿌연","cloudy"),(189,183,107), None),
            (i("라벤더색","lavender"),(230,230,250), None),
            (i("마젠타색","magenta"),(255,0,255), None),
            (i("인디고색","indigo"),(75,0,130), None),
            (i("라임색","lime"),(0,255,0), None),
            (i("반짝이는","flashing"),(0,250,154), None),
            (i("초록색","green"),(34,139,34), None),
            (i("올리브색","olive"),(128,128,0), None),
            (i("시안색","cyan"),(0,255,255), None),
            (i("하늘색","skyblue"),(173,216,230), None),
            (i("파란색","blue"),(0,0,255), None),
            (i("군청색","ultramarine"),(0,0,128), None),
            (i("하얀색","white"),(255,250,250), None),
            (i("은색","silver"),(192,192,192), None),
            (i("회색","gray"),(128,128,128), None),
            (i("검정색","black"),(10,10,10), None),
        ] # NOTE: Currently 24 colors available TODO: Multi lang support
        self.colors_for_scrolls = copy.copy(self.colors_for_potions)
        self.colors_for_amulets = copy.copy(self.colors_for_potions)
        self.colors_for_spellbooks = copy.copy(self.colors_for_potions)
        self.colors_for_rings = copy.copy(self.colors_for_potions)

        self.shapes_for_amulets = [
            i("오각형","pentagonal"),
            i("사각형","rectangular"),
            i("별 모양","star"),
            i("칠각형","heptagonal"),
            i("팔각형","octagonal"),
            i("구형","spherical"),
            i("원뿔형","cone"),
            i("피라미드 모양","pyramid"),
            i("눈송이 모양","snowflake-shaped"),
            i("십자가 모양","cross-shaped"),
            i("다이아몬드 모양","diamond-shaped"),
            i("역삼각형","inverted triangular"),
            i("삼각형","triangular"),
            i("반구형","semispherical"),
            ]

        self.shapes_for_rings = [
            i("황동","brass"),
            i("강철","steel"),
            i("백금","platinum"),
            i("가시달린","spiked"),
            i("타원형","oval"),
            i("뱀 문양","snake emblem"),
            i("사자 문양","lion emblem"),
            i("구부러진","bent"),
            i("황금","gold"),
            i("은제","silver"),
            i("구리","copper"),
            i("무쇠","iron"),
        ]

        # shuffle
        random.shuffle(self.colors_for_potions)
        random.shuffle(self.colors_for_scrolls)
        random.shuffle(self.colors_for_amulets)
        random.shuffle(self.shapes_for_amulets)
        random.shuffle(self.colors_for_spellbooks)
        random.shuffle(self.shapes_for_rings)
        random.shuffle(self.colors_for_rings)

    @property
    def items_rarity(self) -> List:
        tmp = []
        for item in self.items_lists:
            tmp.append(item.rarity)
        return tmp

    def engine(self):
        return Game.engine

    def check_artifact_id_generated(self, item_id: str) -> bool:
        """Check whether the artifact has been spawned on the world at least once."""
        if item_id in self.generated_artifacts:
            return True
        return False

    def disable_artifact_from_spawning(self, item_id: str) -> None:
        self.generated_artifacts.add(item_id)

    def reenable_artifact_from_spawning(self, item_id: str) -> None:
        self.generated_artifacts.remove(item_id)

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
        if item.item_type.value == InventoryOrder.SCROLL.value:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.SCROLL)
            self.items_fake_info[item.entity_id]["name"] = i(f"{self.gen_randomized_string(random.randint(4, 8))}이라고 적혀있는 주문서",
                                                             f"a scroll called {self.gen_randomized_string(random.randint(4, 8))}")
            self.items_fake_info[item.entity_id]["entity_desc"] = i("얇은 종이로 만들어진 주문서이다. 주문서의 내용을 해독할 수 없다.",
                                                                    "The scroll is made out of thin paper. You don't recognize the exact type.")
            self.items_fake_info[item.entity_id]["fg"] = fg
        elif item.item_type.value == InventoryOrder.POTION.value:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.POTION)
            self.items_fake_info[item.entity_id]["name"] = i(color_name + " 물약", color_name + " potion")
            self.items_fake_info[item.entity_id]["entity_desc"] = i(f"{color_name} 물약이다. 마시면 무슨 일이 일어날지 알 수 없다.",
                                                                    f"{color_name.capitalize()} potion. You don't know what's going to happen when you drink it.")
            self.items_fake_info[item.entity_id]["fg"] = fg
            self.items_fake_info[item.entity_id]["bg"] = bg
        elif item.item_type.value == InventoryOrder.GEM.value:
            self.items_fake_info[item.entity_id]["name"] = i("반짝거리는 돌맹이", "shiny rock")
            self.items_fake_info[item.entity_id]["entity_desc"] = i("투명하고 반짝거리는 돌맹이이다. 종류를 정확히 식별할 수 없다.",
                                                                    "The rock is transparent and shiny. You can't tell the exact type.")
        elif item.item_type.value == InventoryOrder.AMULET.value:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.AMULET)
            shape = self.gen_randomized_shape(item_type=InventoryOrder.AMULET)
            self.items_fake_info[item.entity_id]["name"] = i(f"{shape} 아뮬렛", f"{shape} amulet")
            self.items_fake_info[item.entity_id]["entity_desc"] = i(f"{shape} 아뮬렛이다. 종류를 정확히 식별할 수 없다.",
                                                                    f"{shape.capitalize()} amulet. You don't recognize the exact type.")
            self.items_fake_info[item.entity_id]["fg"] = fg
            self.items_fake_info[item.entity_id]["bg"] = bg
        elif item.item_type.value == InventoryOrder.SPELLBOOK.value:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.SPELLBOOK) # Skillbooks are not randomized.
            self.items_fake_info[item.entity_id]["name"] = i(color_name + " 마법서", color_name + " spellbook")
            self.items_fake_info[item.entity_id]["entity_desc"] = i(f"{color_name} 마법서이다. 복잡한 고대 문자들이 적혀 있다.",
                                                                    f"{color_name.capitalize()} spellbook. There are ancient glyphs written inside.")
            self.items_fake_info[item.entity_id]["fg"] = fg
            self.items_fake_info[item.entity_id]["bg"] = bg
        elif item.item_type.value == InventoryOrder.RING.value:
            color_name, fg, bg = self.gen_randomized_color(item_type=InventoryOrder.RING)
            shape = self.gen_randomized_shape(item_type=InventoryOrder.RING)
            self.items_fake_info[item.entity_id]["name"] = i(f"{shape} 반지", f"{shape} ring")
            self.items_fake_info[item.entity_id]["entity_desc"] = i(f"{shape} 반지이다. 종류를 정확히 식별할 수 없다.",
                                                                    f"{shape.capitalize()} ring. You don't recognize the exact type.")
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
        if item_type.value == InventoryOrder.POTION.value:
            return self.colors_for_potions.pop()
        elif item_type.value == InventoryOrder.SCROLL.value:
            return self.colors_for_scrolls.pop()
        elif item_type.value == InventoryOrder.AMULET.value:
            return self.colors_for_amulets.pop()
        elif item_type.value == InventoryOrder.SPELLBOOK.value:
            return self.colors_for_spellbooks.pop()
        elif item_type.value == InventoryOrder.RING.value:
            return self.colors_for_rings.pop()

    def gen_randomized_shape(self, item_type):
        if item_type.value == InventoryOrder.AMULET.value:
            return self.shapes_for_amulets.pop()
        elif item_type.value == InventoryOrder.RING.value:
            return self.shapes_for_rings.pop()
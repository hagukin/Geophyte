from __future__ import annotations
from typing import List, TYPE_CHECKING
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item
    from ability import Ability


class AbilityInventory(BaseComponent):
    """
    Inventory component that stores parent actor's skills and spells.
    """
    def __init__(self, capacity: int):
        super().__init__(None)
        self.capacity = capacity # max 52
        self.ability_hotkeys = {
            "a":None,"b":None,"c":None,"d":None,"e":None,"f":None,"g":None,"h":None,"i":None,"j":None,"k":None,"l":None,"m":None,"n":None,"o":None,"p":None,"q":None,"r":None,"s":None,"t":None,"u":None,"v":None,"w":None,"x":None,"y":None,"z":None,
            "A":None,"B":None,"C":None,"D":None,"E":None,"F":None,"G":None,"H":None,"I":None,"J":None,"K":None,"L":None,"M":None,"N":None,"O":None,"P":None,"Q":None,"R":None,"S":None,"T":None,"U":None,"V":None,"W":None,"X":None,"Y":None,"Z":None
        }

    @property
    def abilities(self):
        return [x for x in self.ability_hotkeys.values() if x is not None]

    def sort_ability_inventory(self) -> None:
        """
        Sort inventory by type.
        Using enum from order.InventoryOrder
        """
        def sort_hotkeys(ability):
            if ability[1]:
                try:
                    return ability[1].ability_type.value
                except:
                    print("DEBUG::ABILITY SORTING SOMETHING WENT WRONG")
                    return -1
            else:
                # If there is no ability stored, return -1.
                return -1
        
        self.ability_hotkeys = dict(sorted(self.ability_hotkeys.items(), key=sort_hotkeys))

        return None

    def get_ability_by_id(self, ability_id: str) -> Ability:
        """
        return ability object that has the matching id that was given to this function.
        """
        for ability in self.abilities:
            if ability.ability_id == ability_id:
                return ability

        return None

    def add_ability(self, ability: Ability) -> None:
        """
        Add ability to ability inventory.
        Using this function is recommended instead of using .append()
        """
        # Prevent duplicates
        if ability in self.abilities:
            return None

        ability.parent = self
        self.abilities.append(ability)

        # give alphabet key
        for key, value in self.ability_hotkeys.items():
            if value == None:
                self.ability_hotkeys[key] = ability
                break

    def remove_ability(self, item: Ability) -> None:
        """
        Remove ability from inventory.
        """
        # TODO
        pass
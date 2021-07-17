from __future__ import annotations

import copy
from order import AbilityOrder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.activatable import Activatable
    from components.ability_inventory import AbilityInventory

class Ability:
    """
    A generic object to represent magics, spells, skills, etc.
    """
    def __init__(
        self,
        parent: AbilityInventory = None,
        name: str = "<Unnamed>",
        ability_id: str = "<Undefined id>",
        ability_desc: str = "", # Recommendation: Max 110 letters per line, Max 5 Lines total.
        ability_type: AbilityOrder = None,
        activatable: Activatable = None,
    ):
        self.parent = parent
        self.name = name
        self.ability_id = ability_id
        self.ability_desc = ability_desc
        self.ability_type = ability_type
        
        if activatable:
            self.activatable = activatable
            self.activatable.parent = self
    
    @property
    def gamemap(self):
        return self.parent.parent.gamemap

    def copy(self):
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        copy.parent = self.parent
        return clone
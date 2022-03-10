from typing import Optional
from entity import Actor

### NOTE: Rarity can have value between 0 and 10 ###
class ActorDB:
    monster_difficulty = {  # Includes both surface and underwater
        0: [],
        1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
        11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [],
        21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [],
    }

    monster_rarity_for_each_difficulty = {
        0: [],
        1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
        11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [],
        21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [],
    }
    surface_monster_difficulty = {}
    underwater_monster_difficulty = {}  # Underwater monsters are also stored in monster_difficulty dictionary.

    # k, v = difficulty, actor

    def get_actor_by_id(entity_id: str) -> Optional[Actor]:
        for monslist in ActorDB.monster_difficulty.values():
            for mon in monslist:
                if mon.entity_id == entity_id:
                    return mon
        print(f"WARNING::Can't find {entity_id} from ActorDB.")
        return None

    def reset() -> None:
        """Delete all db. Is called when you change the ingame language."""
        ActorDB.monster_difficulty = {
            0: [],
            1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
            11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [],
            21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [],
        }
        ActorDB.monster_rarity_for_each_difficulty = {
            0: [],
            1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
            11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [],
            21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [],
        }
        ActorDB.surface_monster_difficulty = {}
        ActorDB.underwater_monster_difficulty = {}
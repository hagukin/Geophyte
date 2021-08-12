from typing import Dict, Optional

def get_dungeon_biome(depth: int) -> Optional[Dict]:
    if depth == 10:
        return {
            "ancient_ruins":1
        }
    return None
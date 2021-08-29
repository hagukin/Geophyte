from typing import Dict, Optional
import biome_factories

def get_dungeon_biome(depth: int) -> Optional[Dict]:
    if depth <= 0:
        return {
            biome_factories.forest:1
        }
    elif depth < 8:
        return {
            biome_factories.rocky_dungeon:1
        }
    elif depth < 12:
        return {
            biome_factories.forest:1
        }
    if depth == 13:
        return {
            biome_factories.ancient_ruins:1
        }
    return None
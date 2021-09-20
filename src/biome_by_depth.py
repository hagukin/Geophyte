from typing import Dict, Optional
import biome_factories

def get_dungeon_biome(depth: int) -> Optional[Dict]:
    if depth <= 0:
        return {
            biome_factories.forest:1
        }
    elif depth < 10:
        return {
            biome_factories.rocky_dungeon_small(round((depth+1) // 2 * 5)):1 # deeper you go larger it gets
        }
    elif depth < 13:
        return {
            biome_factories.forest:1
        }
    elif depth < 18:
        return {
            biome_factories.desert_dungeon: 1
        }
    elif depth < 23:
        return {
            biome_factories.crystal_cavern:1
        }
    elif depth == 24:
        return {
            biome_factories.ancient_ruins: 1
        }
    return None
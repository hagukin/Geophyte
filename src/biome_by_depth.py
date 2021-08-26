from typing import Dict, Optional
import biome_factories

def get_dungeon_biome(depth: int) -> Optional[Dict]:
    if depth <= 0:
        return {
            biome_factories.forest:1
        }
    elif depth < 20:
        return {
            biome_factories.rocky_dungeon:1
        }
    if depth == 20:
        return {
            biome_factories.ancient_ruins:1
        }
    return None
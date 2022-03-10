import numpy as np
import random

from typing import List, Tuple, TYPE_CHECKING, Optional

from entity import SemiActor
from order import TilemapOrder
from rooms import Room
from game_map import GameMap

import semiactor_factories
import chests
import chest_factories

if TYPE_CHECKING:
    from rooms import Room


def grow_grass(
    gamemap: GameMap, grass_tile, grass_core: Tuple[int, int], scale:int=2, density: float=0.6,
) -> None:
    """
    Create grass around nearby tiles from grass_core.
    4 of the newly created grass tiles becomes new grass_core, and repeat the process again.
    Reapeat for amount of scale value received.
    Args:
        scale:
            Integer. Indicates how many time will the grass generating loop repeats.
    """
    tilemap = gamemap.tilemap

    # Set directions
    spawn_core_dir = ((1,0), (-1,0), (0,1), (0,-1)) # duplicate core in cross-directions
    spawn_grass_dir = ((1,1), (1,-1), (-1,1), (-1,-1)) # randomize grass in X-directions

    # Create grass_core at given location
    # NOTE: You have to manually write what types of terrains that the grass can overwrite
    # Currently the grass only grows on ROON_INNER.
    if tilemap[grass_core[0]][grass_core[1]] == TilemapOrder.ROOM_INNER.value:
        tilemap[grass_core[0]][grass_core[1]] = TilemapOrder.GRASS_CORE.value
    else:# cannot spawn grass at given location
        return -1

    for _ in range(scale):
        core_locations = zip(*np.where(tilemap == TilemapOrder.GRASS_CORE.value))

        for loc in core_locations:
            # Spawn grass
            for direction in spawn_grass_dir:
                try:
                    if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value:#TODO terrain겹침
                        if random.random() < density:
                            tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.GRASS.value
                        else:
                            continue # density-1/density chance of not generating anything (NOTE: this feature will randomize and diversify grassfield shapes)
                except:
                    continue

            # Spawn new grass core
            for direction in spawn_core_dir:
                try:
                    if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value or tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.GRASS.value:#TODO terrain겹침
                        if random.random() < density:
                            tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.GRASS_CORE.value
                        else:
                            continue # density-1/density chance of not generating anything
                except:
                    continue

    # Change leftover grass_cores into regular grass
    leftcore_locations = zip(*np.where(tilemap == TilemapOrder.GRASS_CORE.value))
    for loc in leftcore_locations:
        tilemap[loc[0]][loc[1]] = TilemapOrder.GRASS.value

    # Make Grass tiles
    grass_locations = zip(*np.where(tilemap == TilemapOrder.GRASS.value))

    for loc in grass_locations:
        gamemap.tiles[loc[0], loc[1]] = grass_tile()


def generate_grass(gamemap: GameMap, room: Room) -> None:
    
    core_num_range = room.terrain.gen_grass["core_num_range"]
    core_count = random.randint(core_num_range[0], core_num_range[1])
        
    possible_gen_tiles = room.inner_tiles
    core_coordinates = random.choices(possible_gen_tiles, k=core_count)
    
    for loc in set(core_coordinates):
        scale_range = room.terrain.gen_grass["scale_range"]
        scale = random.randint(scale_range[0], scale_range[1])
        
        # For every single grass cores, run grass generating algorithm
        grow_grass(gamemap=gamemap, grass_tile=gamemap.tileset["t_dense_grass"], grass_core=loc, scale=scale, density=room.terrain.gen_grass["density"])


def grow_hole(
        gamemap: GameMap, hole_tile, hole_core: Tuple[int, int], scale: int = 2, density: float = 0.6,
) -> None:
    """
    Create hole around nearby tiles from hole_core.
    4 of the newly created hole tiles becomes new hole_core, and repeat the process again.
    Reapeat for amount of scale value received.
    Args:
        scale:
            Integer. Indicates how many time will the hole generating loop repeats.
    """
    tilemap = gamemap.tilemap

    # Set directions
    spawn_core_dir = ((1, 0), (-1, 0), (0, 1), (0, -1))  # duplicate core in cross-directions
    spawn_hole_dir = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # randomize hole in X-directions

    # Create hole_core at given location
    # NOTE: You have to manually write what types of terrains that the hole can overwrite
    # Currently the hole only grows on ROON_INNER.
    if tilemap[hole_core[0]][hole_core[1]] == TilemapOrder.ROOM_INNER.value:
        tilemap[hole_core[0]][hole_core[1]] = TilemapOrder.HOLE_CORE.value
    else:  # cannot spawn hole at given location
        return -1

    for _ in range(scale):
        core_locations = zip(*np.where(tilemap == TilemapOrder.HOLE_CORE.value))

        for loc in core_locations:
            # Spawn hole
            for direction in spawn_hole_dir:
                try:
                    if tilemap[loc[0] + direction[0]][
                        loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value:  # TODO terrain겹침
                        if random.random() < density:
                            tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.HOLE.value
                        else:
                            continue  # density-1/density chance of not generating anything (NOTE: this feature will randomize and diversify holefield shapes)
                except:
                    continue

            # Spawn new hole core
            for direction in spawn_core_dir:
                try:
                    if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value or \
                            tilemap[loc[0] + direction[0]][
                                loc[1] + direction[1]] == TilemapOrder.HOLE.value:  # TODO terrain겹침
                        if random.random() < density:
                            tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.HOLE_CORE.value
                        else:
                            continue  # density-1/density chance of not generating anything
                except:
                    continue

    # Change leftover hole_cores into regular hole
    leftcore_locations = zip(*np.where(tilemap == TilemapOrder.HOLE_CORE.value))
    for loc in leftcore_locations:
        tilemap[loc[0]][loc[1]] = TilemapOrder.HOLE.value

    # Make hole tiles
    hole_locations = zip(*np.where(tilemap == TilemapOrder.HOLE.value))

    for loc in hole_locations:
        gamemap.tiles[loc[0], loc[1]] = hole_tile()


def generate_hole(gamemap: GameMap, room: Room) -> None:
    core_num_range = room.terrain.gen_holes["core_num_range"]
    core_count = random.randint(core_num_range[0], core_num_range[1])

    possible_gen_tiles = room.inner_tiles
    core_coordinates = random.choices(possible_gen_tiles, k=core_count)

    for loc in set(core_coordinates):
        scale_range = room.terrain.gen_holes["scale_range"]
        scale = random.randint(scale_range[0], scale_range[1])

        # For every single hole cores, run hole generating algorithm
        grow_hole(gamemap=gamemap, hole_tile=gamemap.tileset["t_hole"], hole_core=loc, scale=scale,
                   density=room.terrain.gen_holes["density"])


def grow_trap(gamemap, x, y, trap_semiactor:SemiActor, lifetime=-1) -> None:
    """Spawn a SemiActor instance of a given name at given location."""

    tilemap = gamemap.tilemap

    # Check and change tilemap info
    # NOTE: You have to manually write what types of terrains that the traps can overwrite
    # Currently the trap only spawns on ROON_INNER.
    if tilemap[x][y] == TilemapOrder.ROOM_INNER.value:
        tilemap[x][y] = TilemapOrder.TRAP.value
    else:
        return None

    # Spawn
    trap_semiactor.spawn(gamemap=gamemap, x=x, y=y, lifetime=lifetime)


def generate_trap(gamemap: GameMap, room: Room) -> None:

    trap_count = 0
    checklist = room.terrain.gen_traps["checklist"]
    max_traps_per_room = room.terrain.gen_traps["max_traps_per_room"]
    spawn_chance = room.terrain.gen_traps["spawn_chance"]
    forced_traps_gen_number = room.terrain.gen_traps["forced_traps_gen_number"]
    gen_tiles = room.inner_tiles

    # 1. Generate force-generated traps first
    if forced_traps_gen_number: # if not 0
        trap_coordinates = None
        try:
            trap_coordinates = random.choices(gen_tiles, k=min(len(room.inner_tiles), forced_traps_gen_number)) # Prevents the trap num going higher than the available inner tiles num
        except Exception as e:
            print(f"ERROR::{e} - generate_trap()")

        if trap_coordinates: # If there is no trap_coordinates ignore the process
            for loc in set(trap_coordinates):
                # Choose trap type
                trap_chosen = random.choices(list(checklist.keys()), weights=list(checklist.values()), k=1)[0]

                # Spawn trap
                if trap_count <= max_traps_per_room:
                    grow_trap(gamemap=gamemap, x=loc[0], y=loc[1], trap_semiactor=trap_chosen)
                    trap_count += 1
                else:
                    break

    # 2. Spawn inside the given room
    # Shuffle the inner tiles to prevent traps getting crammed in specific location
    room_tile = room.inner_tiles
    random.shuffle(room_tile)

    for loc in room_tile:
        if trap_count >= max_traps_per_room:
            break
        
        # Chance of spawning a trap
        if random.random() > spawn_chance:
            continue
        
        # Spawn trap
        trap_chosen = random.choices(list(checklist.keys()), weights=list(checklist.values()), k=1)[0]
        grow_trap(gamemap=gamemap, x=loc[0], y=loc[1], trap_semiactor=trap_chosen)
        trap_count += 1


def make_shallow_water(
    gamemap: GameMap, water_core: Tuple[int, int], scale:int=2, density: float=0.6, no_border: bool=False, 
):
    """
    NOTE: This function was created based on the grow_grass function
    """
    tilemap = gamemap.tilemap

    # Set directions
    spawn_core_dir = ((1,0), (-1,0), (0,1), (0,-1)) # duplicate core in cross-directions
    spawn_water_dir = ((1,1), (1,-1), (-1,1), (-1,-1)) # randomize grass in X-directions

    # Create water_core at given location
    # NOTE: You have to manually write what types of terrains that the grass can overwrite
    # Currently the water only generates on ROON_INNER, unless it has no_border parameter set to True.
    if not no_border:
        if tilemap[water_core[0]][water_core[1]] == TilemapOrder.ROOM_INNER.value:
            tilemap[water_core[0]][water_core[1]] = TilemapOrder.WATER_CORE.value
        else:# cannot spawn water at given location
            return -1
    else:
        if tilemap[water_core[0]][water_core[1]] != TilemapOrder.MAP_BORDER.value\
            and not gamemap.protectmap[water_core[0]][water_core[1]]:
            tilemap[water_core[0]][water_core[1]] = TilemapOrder.WATER_CORE.value
        else:
            return -1

    for _ in range(scale):
        core_locations = zip(*np.where(tilemap == TilemapOrder.WATER_CORE.value))

        for loc in core_locations:
            # Spawn water
            for direction in spawn_water_dir:
                try:
                    if no_border:
                        if random.random() < density:
                            if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] != TilemapOrder.MAP_BORDER.value\
                                and not gamemap.protectmap[loc[0] + direction[0]][loc[1] + direction[1]]:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.WATER.value
                        else:
                            continue # density-1/density chance of not generating
                    else:
                        if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value\
                            and not gamemap.protectmap[loc[0] + direction[0]][loc[1] + direction[1]]:#TODO terrain collided
                            if random.random() < density:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.WATER.value
                            else:
                                continue # density-1/density chance of not generating
                except:
                    continue

            # Spawn new water core
            for direction in spawn_core_dir:
                try:
                    if no_border:
                        if random.random() < density:
                            if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] != TilemapOrder.MAP_BORDER.value\
                            and not gamemap.protectmap[loc[0] + direction[0]][loc[1] + direction[1]]:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.WATER_CORE.value
                        else:
                            continue # density-1/density chance of not generating
                    else:
                        if (tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value or tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.WATER.value)\
                            and not gamemap.protectmap[loc[0] + direction[0]][loc[1] + direction[1]]:#TODO terrain collided
                            if random.random() < density:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.WATER_CORE.value
                            else:
                                continue # density-1/density chance of not generating
                except:
                    continue

    # Change leftover water_cores into regular water
    leftcore_locations = zip(*np.where(tilemap == TilemapOrder.WATER_CORE.value))
    for loc in leftcore_locations:
        tilemap[loc[0], loc[1]] = TilemapOrder.WATER.value
        
    # Make shallow_pit tile at every TilemapORder.WATER locations 
    water_locations = zip(*np.where(tilemap == TilemapOrder.WATER.value))

    for loc in water_locations:
        gamemap.tiles[loc[0], loc[1]] = gamemap.tileset["t_shallow_water"]()
        #gamemap.tiles[loc[0], loc[1]] = gamemap.tileset["t_DEBUG"]()


def make_deep_water(
    gamemap: GameMap,
) -> None:
    # Search for locations where deep water needs to be placed
    water_locations = zip(*np.where(gamemap.tilemap == TilemapOrder.WATER.value))
    deep_water_locations = []

    for cor in water_locations:
        nearby_water_count = 0
        for x_add in range(3):
            for y_add in range(3):
                try:
                    if gamemap.tilemap[cor[0]-1+x_add, cor[1]-1+y_add] == TilemapOrder.WATER.value:
                        nearby_water_count += 1
                except IndexError: # Out of map border (TODO: Find a better way of dealing this)
                    continue
        if nearby_water_count >= 8:# Generate deep water if there are 8 surrounding water tiles nearby
            deep_water_locations.append(cor)

    for loc in deep_water_locations:
        gamemap.tiles[loc[0], loc[1]] = gamemap.tileset["t_deep_water"]()


def generate_water(gamemap: GameMap, room: Room) -> None:
    core_num_range = room.terrain.gen_water["core_num_range"]
    core_count = random.randint(core_num_range[0], core_num_range[1])
        
    possible_gen_tiles = room.inner_tiles
    core_coordinates = random.choices(possible_gen_tiles, k=core_count)
    
    # Generate shallow water
    for loc in set(core_coordinates):
        scale_range = room.terrain.gen_water["scale_range"]
        scale = random.randint(scale_range[0], scale_range[1])

        # For each core run water gen algorithm
        make_shallow_water(gamemap=gamemap, water_core=loc, scale=scale, density=room.terrain.gen_water["density"], no_border=room.terrain.gen_water["no_border"])

    # Generate deep water (change all shallow water to deep water except for water pool boundaries
    make_deep_water(gamemap=gamemap)


def make_shallow_pit(
        gamemap: GameMap, pit_core: Tuple[int, int], scale: int = 2, density: float = 0.6, no_border: bool = False,
):
    """
    NOTE: This function was created based on the grow_grass function
    """
    tilemap = gamemap.tilemap

    # Set directions
    spawn_core_dir = ((1, 0), (-1, 0), (0, 1), (0, -1))  # duplicate core in cross-directions
    spawn_pit_dir = ((1, 1), (1, -1), (-1, 1), (-1, -1))  # randomize grass in X-directions

    # Create pit_core at given location
    # NOTE: You have to manually write what types of terrains that pits can overwrite
    # Currently the pit only generates on ROON_INNER, unless it has no_border parameter set to True.
    if not no_border:
        if tilemap[pit_core[0]][pit_core[1]] == TilemapOrder.ROOM_INNER.value:
            tilemap[pit_core[0]][pit_core[1]] = TilemapOrder.PIT_CORE.value
        else:  # cannot spawn pit at given location
            return -1
    else:
        if tilemap[pit_core[0]][pit_core[1]] != TilemapOrder.MAP_BORDER.value \
                and not gamemap.protectmap[pit_core[0]][pit_core[1]]:
            tilemap[pit_core[0]][pit_core[1]] = TilemapOrder.PIT_CORE.value
        else:
            return -1

    for _ in range(scale):
        core_locations = zip(*np.where(tilemap == TilemapOrder.PIT_CORE.value))

        for loc in core_locations:
            # Spawn pit
            for direction in spawn_pit_dir:
                try:
                    if no_border:
                        if random.random() < density:
                            if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] != TilemapOrder.MAP_BORDER.value \
                                    and not gamemap.protectmap[loc[0] + direction[0]][loc[1] + direction[1]]:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.PIT.value
                        else:
                            continue  # density-1/density chance of not generating
                    else:
                        if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value \
                                and not gamemap.protectmap[loc[0] + direction[0]][
                            loc[1] + direction[1]]:  # TODO terrain collided
                            if random.random() < density:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.PIT.value
                            else:
                                continue  # density-1/density chance of not generating
                except:
                    continue

            # Spawn new pit core
            for direction in spawn_core_dir:
                try:
                    if no_border:
                        if random.random() < density:
                            if tilemap[loc[0] + direction[0]][loc[1] + direction[1]] != TilemapOrder.MAP_BORDER.value \
                                    and not gamemap.protectmap[loc[0] + direction[0]][loc[1] + direction[1]]:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.PIT_CORE.value
                        else:
                            continue  # density-1/density chance of not generating
                    else:
                        if (tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.ROOM_INNER.value or
                            tilemap[loc[0] + direction[0]][loc[1] + direction[1]] == TilemapOrder.PIT.value) \
                                and not gamemap.protectmap[loc[0] + direction[0]][
                            loc[1] + direction[1]]:  # TODO terrain collided
                            if random.random() < density:
                                tilemap[loc[0] + direction[0]][loc[1] + direction[1]] = TilemapOrder.PIT_CORE.value
                            else:
                                continue  # density-1/density chance of not generating
                except:
                    continue

    # Change leftover pit_cores into regular pit
    leftcore_locations = zip(*np.where(tilemap == TilemapOrder.PIT_CORE.value))
    for loc in leftcore_locations:
        tilemap[loc[0], loc[1]] = TilemapOrder.PIT.value

    # Make shallow_pit tile at every TilemapORder.PIT locations
    pit_locations = zip(*np.where(tilemap == TilemapOrder.PIT.value))

    for loc in pit_locations:
        gamemap.tiles[loc[0], loc[1]] = gamemap.tileset["t_shallow_pit"]()
        # gamemap.tiles[loc[0], loc[1]] = gamemap.tileset["t_DEBUG"]()


def make_deep_pit(
        gamemap: GameMap,
) -> None:
    # Search for locations where deep pit needs to be placed
    pit_locations = zip(*np.where(gamemap.tilemap == TilemapOrder.PIT.value))
    deep_pit_locations = []

    for cor in pit_locations:
        nearby_pit_count = 0
        for x_add in range(3):
            for y_add in range(3):
                try:
                    if gamemap.tilemap[cor[0] - 1 + x_add, cor[1] - 1 + y_add] == TilemapOrder.PIT.value:
                        nearby_pit_count += 1
                except IndexError:  # Out of map border (TODO: Find a better way of dealing this)
                    continue
        if nearby_pit_count >= 8:  # Generate deep pit if there are 8 surrounding pit tiles nearby
            deep_pit_locations.append(cor)

    for loc in deep_pit_locations:
        gamemap.tiles[loc[0], loc[1]] = gamemap.tileset["t_deep_pit"]()


def generate_pits(gamemap: GameMap, room: Room) -> None:
    core_num_range = room.terrain.gen_pits["core_num_range"]
    core_count = random.randint(core_num_range[0], core_num_range[1])

    possible_gen_tiles = room.inner_tiles
    core_coordinates = random.choices(possible_gen_tiles, k=core_count)

    # Generate shallow pits
    for loc in set(core_coordinates):
        scale_range = room.terrain.gen_pits["scale_range"]
        scale = random.randint(scale_range[0], scale_range[1])

        # For each core run pit gen algorithm
        make_shallow_pit(gamemap=gamemap, pit_core=loc, scale=scale, density=room.terrain.gen_pits["density"],
                           no_border=room.terrain.gen_pits["no_border"])

    # Generate deep pit (change all shallow pit to deep pit except for pit pool boundaries
    make_deep_pit(gamemap=gamemap)



def grow_chest(gamemap, x, y, chest_id:str, lifetime=-1, initial_items: List=None) -> chests.ChestSemiactor:
    """
    Spawn a chest type SemiActor instance of given name at given location.
    NOTE: This function is based on grow_traps() function

    Args:
        initial_items:
            A list that consists of tuples.
            Each tuple consists of 
            (
                Item, 
                Chance of having this Item when generated, 
                Item amount
            )
            NOTE: if the terrain has specific gen_chests["initial_items"] value, use it.
            If it's set to None, the chest will randomize items based on the default values. (default values are set in chest_factories.)
    """
    tilemap = gamemap.tilemap
    if chest_id:
        return chest_factories.chest_id_to_chest[chest_id].spawn(gamemap=gamemap, x=x, y=y, lifetime=lifetime, initial_items=initial_items)


def generate_chest(gamemap: GameMap, room: Room) -> None:

    possible_gen_tiles = room.inner_tiles
    checklist = room.terrain.gen_chests["checklist"]
    chest_id_chosen = random.choices(list(checklist.keys()), weights=list(checklist.values()), k=1)[0]
    chest_num = random.randint(room.terrain.gen_chests["chest_num_range"][0], room.terrain.gen_chests["chest_num_range"][1])
    chest_coordinates = random.choices(possible_gen_tiles, k=chest_num)

    for loc in set(chest_coordinates):
        if not gamemap.get_any_entity_at_location(location_x=loc[0], location_y=loc[1]):
            grow_chest(gamemap=gamemap, x=loc[0], y=loc[1], chest_id=chest_id_chosen, initial_items=room.terrain.gen_chests["initial_items"])


def generate_on_empty_convex(gamemap: GameMap, x:int, y:int) -> None:
    """
    Generate a random terrain to the given empty convex location.
    """
    tmp = random.random()
    if tmp <= 0.05:
        from chest_factories import choose_random_chest_id
        grow_chest(gamemap=gamemap, x=x, y=y, chest_id=choose_random_chest_id(k=1)[0], initial_items=None)
        # gamemap.tiles[x, y] = gamemap.tileset["t_DEBUG"]()
    elif tmp <= 0.5:
        from procgen import spawn_monster_of_appropriate_difficulty
        spawn_monster_of_appropriate_difficulty(x=x, y=y, dungeon=gamemap)
    else:
        return None


def grow_plant(gamemap, x, y, plant_semiactor: SemiActor, lifetime=-1) -> None:
    """Spawn a SemiActor instance of a given name at given location."""

    tilemap = gamemap.tilemap

    # Check and change tilemap info
    # NOTE: You have to manually write what types of terrains that the plants can overwrite
    # Currently the plant only spawns on ROON_INNER.
    if tilemap[x][y] == TilemapOrder.ROOM_INNER.value\
            or tilemap[x][y] == TilemapOrder.GRASS.value\
            or tilemap[x][y] == TilemapOrder.GRASS_CORE.value:
        tilemap[x][y] = TilemapOrder.PLANT.value
    else:
        return None

    # Spawn
    plant_semiactor.spawn(gamemap=gamemap, x=x, y=y, lifetime=lifetime)


def generate_plant(gamemap: GameMap, room: Room) -> None:
    plant_count = 0
    checklist = room.terrain.gen_plants["checklist"]
    max_plants_per_room = room.terrain.gen_plants["max_plants_per_room"]
    spawn_chance = room.terrain.gen_plants["spawn_chance"]
    forced_plants_gen_number = room.terrain.gen_plants["forced_plants_gen_number"]
    gen_tiles = room.inner_tiles

    # 1. Generate force-generated plants first
    if forced_plants_gen_number:  # if not 0
        plant_coordinates = random.choices(gen_tiles, k=min(len(room.inner_tiles),
                                                           forced_plants_gen_number))  # Prevents the plant num going higher than the available inner tiles num

        for loc in set(plant_coordinates):
            # Choose plant type
            plant_chosen = random.choices(list(checklist.keys()), weights=list(checklist.values()), k=1)[0]

            # Spawn plant
            if plant_count <= max_plants_per_room:
                grow_plant(gamemap=gamemap, x=loc[0], y=loc[1], plant_semiactor=plant_chosen)
                plant_count += 1
            else:
                break

    # 2. Spawn inside the given room
    # Shuffle the inner tiles to prevent plants getting crammed in specific location
    room_tile = room.inner_tiles
    random.shuffle(room_tile)

    for loc in room_tile:
        if plant_count >= max_plants_per_room:
            break

        # Chance of spawning a plant
        if random.random() > spawn_chance:
            continue

        # Spawn plant
        plant_chosen = random.choices(list(checklist.keys()), weights=list(checklist.values()), k=1)[0]
        grow_plant(gamemap=gamemap, x=loc[0], y=loc[1], plant_semiactor=plant_chosen)
        plant_count += 1
from __future__ import annotations
from tcod.console import Console
from tcod.context import Context, new

from entity import SemiActor, Actor
from terrain import Terrain
from biome import Biome
from biome_by_depth import get_dungeon_biome

import numpy as np
import copy
import time
import random
import tcod
import color
import actor_factories, item_factories, semiactor_factories
import terrain_factories
import biome_factories
import terrain_generation

from order import TilemapOrder
from typing import Iterator, List, Tuple, TYPE_CHECKING, Optional
from room_factories import Room, RectangularRoom, CircularRoom, BlobRoom
from game_map import GameMap
from render import randomized_screen_paint

if TYPE_CHECKING:
    from engine import Engine


def choose_biome(
    biome_dicts: dict=None #if value is given, use it as population and weights
) -> Biome:
    if biome_dicts == None:
        biome = random.choices(
            population=list(biome_factories.biome_dict.values()),
            weights=biome_factories.biome_rarity,
            k=1
            )[0]
    else:
        biome = random.choices(
            population=list(biome_dicts.keys()),
            weights=list(biome_dicts.values()),
            k=1
            )[0]

    return copy.deepcopy(biome)


def choose_terrain(
    terrain_dicts: dict=None #if value is given, use it as population and weights
) -> Terrain:
    if terrain_dicts == None:
        terrain = random.choices(
            population=list(terrain_factories.terrain_dict.keys()),
            weights=list(terrain_factories.terrain_dict.values()),
            k=1
            )[0]
    else:
        terrain = random.choices(
            population=list(terrain_dicts.keys()),
            weights=list(terrain_dicts.values()),
            k=1
            )[0]

    return copy.deepcopy(terrain)


def choose_monster_difficulty(gamemap: GameMap, toughness: int=0) -> int:
    """
    Input: the depth of the floor to randomize new monsters
    Output: an integer value that indicates the difficulty of the monster to randomize
    
    Args:
        toughness:
            Higher toughness value will result in a higher difficulty output.

    NOTE: If the gamemap's biome has specified monster difficulty, toughness is totally ignored.

    TODO: Make this function affected by the player's status?
    """
    if gamemap.depth < 0:
        depth_ = -gamemap.depth
    else:
        depth_ = gamemap.depth

    if gamemap.biome.monster_difficulty:
        difficulty_chosen = random.choices(list(gamemap.biome.monster_difficulty.keys()),
                                           list(gamemap.biome.monster_difficulty.values()),
                                                k=1)[0] # Toughness is ignored.
    else:
        avg_diff = depth_ + toughness + 1
        max_diff = avg_diff + 2 # Technically the max difficulty of a spawned monster is avg_diff + 3, since choose_monster_by_difficulty().radius is (-1,1)

        # Choose the monster difficulty (Using normal distribution; but there are limits to maximum and minimum values)
        difficulty_chosen = min(max_diff, max(1, round(np.random.normal(avg_diff, 1.5, 1)[0])))

    return difficulty_chosen


def choose_monster_by_difficulty(difficulty: int, radius: (0,0)) -> Optional[Actor]:
    """
    Args:
        radius:
            if (0,0), function will return monster that exactly matches the given difficulty.
            if (-1,3) and difficulty is 4, function will generate a list of monsters that has difficulty between 3,7 and will choose one randomly.
    """
    select_radius = (max(difficulty + radius[0], 1) , max(radius[0], radius[1]) + difficulty)

    population_list = []
    for i in select_radius:
        population_list.extend(actor_factories.ActorDB.monster_difficulty[difficulty])

    rarity_list = []
    for i in select_radius:
        rarity_list.extend(actor_factories.ActorDB.monster_rarity_for_each_difficulty[difficulty])

    try:
        monster_to_spawn = random.choices(
            population=population_list,
            weights=rarity_list,
            k=1
        )[0]
        return monster_to_spawn
    except IndexError as e:
        print(f"ERROR::Cannot spawn monster of difficulty {difficulty}, radius {radius}.")
        return None # FIXME


def spawn_given_monster(
    x: int, y: int, monster: Actor, dungeon: GameMap, spawn_active=False, spawn_sleep=False, is_first_generation=False,
) -> None:
    """
    Spawns a given monster to given location from given gamemap.
    This is the only function you should use during procgen process to directly spawn an actor entity.
    Args:
        spawn_active:
            Boolean, Will the monster become active right after they are spawned?
        spawn_sleep:
            Boolean. If True, monster will sleep indefinitely.
        is_first_generation:
            Boolean, Is this function called by the gamemap generation function?
            (=is this the first time that the monster is being generated to this dungeon?)
    """
    if monster is None or not monster.spawnable:
        return None

    # Spawn new monster
    new_monster = monster.spawn(dungeon, x, y)

    # DEBUG
    # print(new_monster.entity_id)

    if spawn_active:
        if new_monster.ai:
            new_monster.ai.activate()
    if spawn_sleep:
        new_monster.actor_state.apply_sleeping(value=[0,-1], forced=True) # Infinite sleeping
    if is_first_generation:
        dungeon.starting_monster_num += 1


def spawn_monster_of_appropriate_difficulty(x: int, y: int, dungeon: GameMap, spawn_active=False, spawn_sleep=False, is_first_generation=False) -> None:
    """Wrapper funciton."""
    spawn_given_monster(
        x=x,
        y=y,
        monster=choose_monster_by_difficulty(
            difficulty=choose_monster_difficulty(
                dungeon,
                dungeon.engine.toughness
            ),
            radius=(-1, 1)
        ),
        dungeon=dungeon,
        spawn_active=spawn_active,
        spawn_sleep=spawn_sleep,
        is_first_generation=is_first_generation
    )


def spawn_monsters(
    room: Room, dungeon: GameMap, depth: int
) -> None:
    """
    Spawn monsters to given room.
    Sole purpose of this function is to use it in procgen.
    """
    mon_num = random.choices(
        list(room.terrain.monsters_cnt.keys()),
        list(room.terrain.monsters_cnt.values()),
        k=1)[0]

    if room.terrain.monster_to_spawn:
        monsters_to_spawn = random.choices(
            population=list(room.terrain.monster_to_spawn.keys()),
            weights=list(room.terrain.monster_to_spawn.values()),
            k=mon_num
        )
    else:
        monsters_to_spawn = []
        for _ in range(mon_num):
            # Choose difficulty
            difficulty_chosen = choose_monster_difficulty(gamemap=dungeon, toughness=max(dungeon.engine.toughness + room.terrain.adjust_monster_difficulty, 0))
            if room.terrain.spawn_monster_of_difficulty:
                difficulty_chosen = room.terrain.spawn_monster_of_difficulty

            while not actor_factories.ActorDB.monster_difficulty[difficulty_chosen]:
                print(f"WARNING::Difficulty {difficulty_chosen} missing. Choosing a new difficulty...")
                difficulty_chosen = choose_monster_difficulty(gamemap=dungeon, toughness=max(dungeon.engine.toughness + room.terrain.adjust_monster_difficulty, 0))

            monsters_to_spawn.append(choose_monster_by_difficulty(difficulty_chosen, radius=(-1, 1)))

    for monster_to_spawn in monsters_to_spawn:
        # Spawn location
        tile_coordinates = room.inner_tiles
        place_tile = random.choice(tile_coordinates)

        # Prevent entities clipping
        if any(entity.x == place_tile[0] and entity.y == place_tile[1] for entity in dungeon.entities) \
                or dungeon.tilemap[place_tile[0], place_tile[1]] == TilemapOrder.ASCEND_STAIR.value \
                or dungeon.tilemap[place_tile[0], place_tile[1]] == TilemapOrder.DESCEND_STAIR.value:
            continue
        else:
            # Spawn
            spawn_given_monster(x=place_tile[0], y=place_tile[1], monster=monster_to_spawn, dungeon=dungeon,
                                         spawn_active=False, spawn_sleep=room.terrain.make_monster_sleep, is_first_generation=True)


def spawn_items(
    room: Room, dungeon: GameMap
) -> None:
    """
    Spawn items to given room.
    Sole purpose of this function is to use it in procgen.
    """
    number_of_items = random.choices(
        list(room.terrain.items_cnt.keys()),
        list(room.terrain.items_cnt.values()),
        k=1)[0]
    tile_coordinates = room.inner_tiles

    if room.terrain.item_to_spawn:
        item_candidates = room.terrain.item_to_spawn
    else:
        item_candidates = {}
        from item_factories import item_rarity, temp_items_lists
        for i in range(len(temp_items_lists)):
            if temp_items_lists[i].spawnable and not dungeon.engine.item_manager.check_artifact_id_generated(temp_items_lists[i].entity_id):
                item_candidates[temp_items_lists[i]] = item_rarity[i]

    # Choose items to spawn
    spawn_list = random.choices(
        population=list(item_candidates.keys()),
        weights=list(item_candidates.values()),
        k=number_of_items
        )

    # Spawn items
    for item_to_spawn in spawn_list:
        place_tile = random.choice(tile_coordinates)
        
        if not any(entity.x == place_tile[0] and entity.y == place_tile[1] for entity in dungeon.entities) \
                and item_to_spawn.spawnable \
                and not dungeon.engine.item_manager.check_artifact_id_generated(item_to_spawn.entity_id)\
                and dungeon.tilemap[place_tile[0], place_tile[1]] != TilemapOrder.ASCEND_STAIR.value\
                and dungeon.tilemap[place_tile[0], place_tile[1]] != TilemapOrder.DESCEND_STAIR.value:
            # Do not remove artifact checking line. If you remove this line, artifacts be spawned multiple times during this function call.
            item_to_spawn.spawn(dungeon, place_tile[0], place_tile[1])


def get_path_to(
    tilemap, start_x: int, start_y: int, dest_x: int, dest_y: int, heuristic: int=1,
) -> List[Tuple[int, int]]:
    """
    Compute and return a path to the target position.
    If there is no valid path then returns an empty list.
    """
    # Copy the walkable array.
    cost = np.array(tilemap, dtype=np.int8)

    # Create a graph from the cost array and pass that graph to a new pathfinder.
    # diagonal cost is set to 1000, so the path isn't too narrow.
    graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=1000, greed=heuristic)
    pathfinder = tcod.path.Pathfinder(graph)

    pathfinder.add_root((start_x, start_y))  # Start position.

    # Compute the path to the destination and remove the starting point.
    path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

    # Convert from List[List[int]] to List[Tuple[int, int]].
    return [(index[0], index[1]) for index in path]


def path_between(
    cost, start: Tuple[int, int], end: Tuple[int, int], heuristic: int=1,
) -> Iterator[Tuple[int, int]]:
    """
    Yield the path between two points.

    Args:
        cost:
            Cost can have different types of values depending on the situation.
            Regardless, cost is used for generating path, and tiles with lower costs are more likely to be part of the path.
            e.g. If you are generating the tunnel, you should pass tunnelmap information to cost.
            But If you are using this function for pathfinding, you should pass tiles["walkable"] to cost.
    
    NOTE: DO NOT use this function for player/AI pathfinding, since this function ignores any type of entities such as actors.
    """
    x1, y1 = start
    x2, y2 = end

    paths = get_path_to(cost, x1, y1, x2, y2, heuristic=heuristic)

    if paths:
        for path in paths:
            x, y = path
            yield x, y



def search_empty_convex(
    dungeon: GameMap
) -> List:
    convex_coordinates = zip(*np.where(dungeon.tilemap[:,:] == TilemapOrder.DOOR_CONVEX.value))
    empty_convex = []

    for cor in convex_coordinates:
        wall_count = 0
        covered_by_door = False
        for dx, dy in ((1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            nx = cor[0]+dx
            ny = cor[1]+dy
            if nx < dungeon.width and nx >= 0 and ny < dungeon.height and ny >= 0:
                if dungeon.tilemap[cor[0]+dx, cor[1]+dy] == TilemapOrder.VOID.value or dungeon.tilemap[cor[0]+dx, cor[1]+dy] == TilemapOrder.ROOM_WALL.value:
                    wall_count += 1
                if dungeon.tilemap[cor[0]+dx, cor[1]+dy] == TilemapOrder.DOOR.value:
                    covered_by_door = True
            else:
                continue
        if wall_count >= 7 and covered_by_door:# If there is more than 7 walls surrounding the door convex, it is considered as an "empty convex".
            empty_convex.append(cor)
    
    return empty_convex


def adjust_convex(
    dungeon: GameMap,
    rooms: List,
) -> None:
    """
    This function will connect empty convexes with tunnels, or randomize something in the convex.
    ###
    # #
    #+# -> an example of an empty convex
    """

    # Search
    empty_convex = search_empty_convex(dungeon=dungeon)

    # Connect convexes 
    while len(empty_convex) >= 2:
        con1 = empty_convex.pop()
        con2 = empty_convex.pop()

        for x, y in path_between(dungeon.tunnelmap, (con1[0], con1[1]), (con2[0], con2[1])):
            if dungeon.tilemap[x, y] == TilemapOrder.VOID.value:
                dungeon.tiles[x, y] = dungeon.tileset["t_floor"]()
                dungeon.tilemap[x, y] = TilemapOrder.TUNNEL.value
                dungeon.tunnelmap[x, y] = True
            else:
                continue

    # Search for leftover, and use it as something else
    empty_convex = search_empty_convex(dungeon=dungeon)
    for cor in empty_convex:
        terrain_generation.generate_on_empty_convex(dungeon, cor[0], cor[1])


def remove_awkward_entities(
    gamemap: GameMap
) -> None:
    # Check 0,0
    check_spawn_err = gamemap.get_any_entity_at_location(location_x=0, location_y=0)
    if check_spawn_err != None:
        print(f"WARNING::{check_spawn_err.name} spawned at (0,0)")

    trash = []
    for e in gamemap.entities:
        if isinstance(e, SemiActor): # Delete semiactors that are generated on water (both opened/closed)
            if e.entity_id[-4:] == "door" or e.entity_id[-4:] == "trap" or e.entity_id[-5:] == "chest" or e.entity_id[-4:] == "tree":
                if gamemap.tiles[e.x, e.y]["tile_id"] == "deep_water"\
                    or gamemap.tiles[e.x, e.y]["tile_id"] == "shallow_water"\
                    or gamemap.tiles[e.x, e.y]["tile_id"] == "hole"\
                    or gamemap.tiles[e.x, e.y]["tile_id"] == "deep_pit"\
                    or gamemap.tiles[e.x, e.y]["tile_id"] == "shallow_pit"\
                    or gamemap.tiles[e.x, e.y]["tile_id"] == "ascending_stair"\
                    or gamemap.tiles[e.x, e.y]["tile_id"] == "descending_stair"\
                    or gamemap.tilemap[e.x, e.y] == TilemapOrder.MAP_BORDER.value:
                    trash.append(e)
    for e in trash: # 별도의 루프에서 처리해줘야함
        print(f"DEBUG::Removed awkwardly placed entity {e.entity_id}.")
        e.remove_self()

def generate_earth(
    dungeon: GameMap,
    map_width: int,
    map_height: int,
    engine: Engine
    ) -> None:
    # Generate color-randomized walls
    for x in range(len(dungeon.tiles)):
        for y in range(len(dungeon.tiles[x])):
            dungeon.tiles[x, y] = dungeon.tileset["t_wall"]()

    # Generate unbreakable outer walls
    for x in range(len(dungeon.tiles)):
        dungeon.tiles[x, 0] = dungeon.tileset["t_border"]()
        dungeon.tilemap[x, 0] = TilemapOrder.MAP_BORDER.value
        dungeon.tiles[x, -1] = dungeon.tileset["t_border"]()
        dungeon.tilemap[x, -1] = TilemapOrder.MAP_BORDER.value
    for y in range(len(dungeon.tiles[0])):
        dungeon.tiles[0, y] = dungeon.tileset["t_border"]()
        dungeon.tilemap[0, y] = TilemapOrder.MAP_BORDER.value
        dungeon.tiles[-1, y] = dungeon.tileset["t_border"]()
        dungeon.tilemap[-1, y] = TilemapOrder.MAP_BORDER.value

    # TODO : Add metals and ores and gems?


def create_room(
        dungeon: GameMap,
        x: int,
        y: int,
        room_width: int,
        room_height: int,
        room_shape: str,
        room_terrain: Terrain,
) -> Room:
    # Actual generation of the room
    if room_shape == "rectangular":
        new_room = RectangularRoom(x, y, room_width, room_height, parent=dungeon, terrain=room_terrain)
    elif room_shape == "circular":
        new_room = CircularRoom(x, y, room_width, room_height, parent=dungeon, terrain=room_terrain)
    elif room_shape == "blob":
        min_dense = 0.2
        max_dense = 0.5
        new_room = BlobRoom(x, y, 8, 8, parent=dungeon, terrain=room_terrain, area_min_density=min_dense,
                            area_max_density=max_dense)
        # FIXME
        # new_room.terrain.has_door = False
    else:
        new_room = RectangularRoom(x, y, room_width, room_height, parent=dungeon, terrain=room_terrain)
        print("WARNING::PROCGEN - GENERATE_ROOMS - FAILED TO SET THE ROOM SHAPE")

    return new_room

def spawn_room(
        dungeon: GameMap,
        room: Room
) -> None:
    """Actually spawn the tiles on the gamemap."""
    # Fill room's outer area on tilemap.
    for outer_slice in room.outer:
        dungeon.tilemap[outer_slice] = TilemapOrder.ROOM_WALL.value
        dungeon.tunnelmap[outer_slice] = False
        if room.terrain.protected:
            dungeon.protectmap[outer_slice] = True
        # dungeon.tiles[outer_slice] = dungeon.tileset["t_DEBUG"]()

    # Dig out this rooms inner area.
    for inner_slice in room.inner:
        dungeon.tiles[inner_slice] = dungeon.tileset["t_floor"]()
        dungeon.tilemap[inner_slice] = TilemapOrder.ROOM_INNER.value
        dungeon.tunnelmap[inner_slice] = True
        if room.terrain.protected:
            dungeon.protectmap[inner_slice] = True


def spawn_doors(
        dungeon: GameMap,
        room: Room
) -> None:
    """Actually spawn the door on the gamemap.
    Will use room.doors to get the door locations."""
    # Convex
    for convex_pos in room.door_convexes.values():
        dungeon.tilemap[convex_pos] = TilemapOrder.DOOR_CONVEX.value
        dungeon.tunnelmap[convex_pos] = True
        if room.terrain.protected:
            dungeon.protectmap[convex_pos] = True
        dungeon.tiles[convex_pos] = dungeon.tileset["t_floor"]()
        # dungeon.tiles[convex_pos] = dungeon.tileset["t_DEBUG"]()

    # Door
    for door_pos in room.doors.values():
        dungeon.tilemap[door_pos] = TilemapOrder.DOOR.value
        dungeon.tunnelmap[door_pos] = True
        if room.terrain.protected:
            dungeon.protectmap[door_pos] = True
        dungeon.tiles[door_pos] = dungeon.tileset["t_floor"]()

        if room.terrain.spawn_door and dungeon.get_semiactor_at_location(x=door_pos[0], y=door_pos[1], semiactor_id="door") == None:
            if random.random() <= room.terrain.locked_door_chance:
                semiactor_factories.locked_door.spawn(gamemap=dungeon, x=door_pos[0], y=door_pos[1], lifetime=-1)
            else:
                semiactor_factories.closed_door.spawn(gamemap=dungeon, x=door_pos[0], y=door_pos[1], lifetime=-1)
        else:
            print(f"WARNING::Door already exists on {door_pos}. Cancelled Spawning.")

def generate_rooms(
    dungeon: GameMap,
    rooms: List,
    max_rooms: int,
    engine: Engine,
) -> Tuple[GameMap, list]:
    """Generate rooms, stairs, and doors."""
    # Generate rooms
    nx, ny = 0, 0
    for r in range(max_rooms):
        # Choose the terrain of the room
        if dungeon.biome.terrain == None:
            room_terrain = choose_terrain()
        else:
            room_terrain = choose_terrain(terrain_dicts=dungeon.biome.terrain)

        # Choose the size of the room
        room_width = random.randint(room_terrain.min_width, room_terrain.max_width)
        room_height = random.randint(room_terrain.min_height, room_terrain.max_height)

        # Start location of the room
        # NOTE: There should be at least 4 tiles of free space each sides, so that every room can be connected.
        # It is recommeded to keep the free space as minimum as possible.
        x, y = 4, 4

        # Choose the shape of the room
        shape = list(room_terrain.shape.keys())
        shape_weights = list(room_terrain.shape.values())
        room_shape = random.choices(population=shape, weights=shape_weights, cum_weights=None, k=1)[0]
        new_room = create_room(dungeon, x, y, room_width, room_height, room_shape, room_terrain) # Generated door locations as well

        # Run through the other rooms and see if they intersect with this one.
        found = False
        for x in range(nx, dungeon.tiles.shape[0]):
            for y in range(ny, dungeon.tiles.shape[1]): # Map border colliding handled in room.move()
                if any(new_room.intersects(other_room) for other_room in rooms):
                    new_room.move(x, y)
                    continue  # This room intersects, so go to the next attempt.
                # If there are no intersections then the room is valid.
                else:
                    found = True
                    nx = x
                    ny = 0
                    break
            if found:
                break
        if not found:
            break # Made every available rooms

        # Actual entity, tile spawning
        spawn_room(dungeon, new_room)
        spawn_doors(dungeon, new_room)

        # Finally, append the new room to the list.
        rooms.append(new_room)
        # debug(dungeon, save_as_txt=True)
    # NOTE: You can save the room data on GameMap by adding something here like "dungeon.rooms = rooms"
    return dungeon, rooms


def generate_terrain(
    dungeon: GameMap,
    map_width: int,
    map_height: int,
    rooms: List,
) -> None:
    """Generate a new dungeon map."""

    for room in rooms:
        # Generate water
        if room.terrain.gen_water:
            terrain_generation.generate_water(gamemap=dungeon, room=room)

        # Generate pits
        if room.terrain.gen_pits:
            terrain_generation.generate_pits(gamemap=dungeon, room=room)

        # Generate Holes
        if room.terrain.gen_holes:
            terrain_generation.generate_hole(gamemap=dungeon, room=room)

        # Generate grass
        if room.terrain.gen_grass:
            terrain_generation.generate_grass(gamemap=dungeon, room=room)

        # Generate trap
        if room.terrain.gen_traps:
            terrain_generation.generate_trap(gamemap=dungeon, room=room)

        # Generate plant
        if room.terrain.gen_plants:
            terrain_generation.generate_plant(gamemap=dungeon, room=room)

        # Generate chests/storages
        if room.terrain.gen_chests:
            terrain_generation.generate_chest(gamemap=dungeon, room=room)

        # Call custom function if it has one
        if room.terrain.custom_gen:
            room.terrain.custom_gen(gamemap=dungeon, room=room)

    return None


def generate_tunnels(
    dungeon: GameMap,
    rooms: List,
) -> None:
    """Generate a new dungeon map."""

    # Sort rooms by the distance between one another
    dist_order_rooms = []
    temp = copy.deepcopy(rooms)
    new = None

    while len(temp) != 0:

        if len(dist_order_rooms) == 0:
            base_room = temp.pop()
            dist_order_rooms.append(base_room)
        else:
            base_room = new[0]
            dist_order_rooms.append(new[0])
            temp.remove(new[0])
            new = None
        
        for room in temp:
            dist_square = pow(base_room.x1 - room.x1, 2) + pow(base_room.y1 - room.y1, 2)
            if new == None:
                new = (room, dist_square)
            elif new[1] > dist_square:
                new = (room, dist_square)

    # Choose two rooms and make a tunnel
    while len(dist_order_rooms) >= 2:
        room1 = dist_order_rooms.pop(0)
        room2 = dist_order_rooms[0]

        # The path starts at the center of the room
        start_x = room1.center[0]
        start_y = room1.center[1]
        
        end_x = room2.center[0]
        end_y = room2.center[1]

        for x, y in path_between(dungeon.tunnelmap, (start_x, start_y), (end_x, end_y)):
            if dungeon.tilemap[x, y] == TilemapOrder.VOID.value:
                dungeon.tiles[x, y] = dungeon.tileset["t_floor"]()
                #dungeon.tiles[x, y] = dungeon.tileset["t_DEBUG"]()
                dungeon.tilemap[x, y] = TilemapOrder.TUNNEL.value
                dungeon.tunnelmap[x, y] = True
            else:
                continue

    return None


def stair_generation(
    dungeon: GameMap,
    rooms: List[Room],
    direction: int, #0 - up, 1 - down
    ):
    """
    Choose a random room, check if the room is suitable, choose a random tile, check if the tile is suitable, then return the tile.
    """
    if direction == 0:
        while True:
            ascend_room = random.choice(rooms)
            if not ascend_room.terrain.can_have_stair:
                continue
            ascend_tile = random.choice(ascend_room.inner_tiles)
            if dungeon.get_any_entity_at_location(ascend_tile[0], ascend_tile[1]) or not dungeon.tiles[ascend_tile]["walkable"] or not dungeon.tiles[ascend_tile]["safe_to_walk"]:
                continue
            else:
                return ascend_tile
    elif direction == 1:
        while True:
            descend_room = random.choice(rooms)
            if not descend_room.terrain.can_have_stair:
                continue
            descend_tile = random.choice(descend_room.inner_tiles)
            if dungeon.get_any_entity_at_location(descend_tile[0], descend_tile[1]) or not dungeon.tiles[descend_tile]["walkable"] or not dungeon.tiles[descend_tile]["safe_to_walk"]:
                continue
            else:
                return descend_tile


def generate_stair(
    dungeon: GameMap,
    rooms: List,
    stair_type: str = "pair", # pair : ascending, descending stair pair / up : ascending stair / down : descending stair
) -> None:
    """Generate a given type of stair."""
    ascend_tile, descend_tile = None, None

    if stair_type == "pair":
        while True:
            # Generate stairs
            ascend_tile = stair_generation(dungeon, rooms, 0)
            descend_tile = stair_generation(dungeon, rooms, 1)
            
            # Check if both stairs are connected to one another
            connected = False
            cost = np.array(dungeon.tiles["walkable"], dtype=np.int8) # tunnelmap includes "void" tiles as a valid path, so create a new cost grid and pass it to pathfinder

            # Avoid dangerous tiles
            dangerous_coordinates = zip(*np.where(dungeon.tiles["safe_to_walk"][:,:] == False))
            for cor in dangerous_coordinates:
                cost[cor] = 0
            
            for x, y in path_between(cost, ascend_tile, descend_tile):
                if x != descend_tile[0] or y != descend_tile[1]:
                    continue
                else:
                    connected = True
                    break

            if connected:
                break
            else:
                print("WARNING::Path not found, Regenerating Staircases...") # Search for new locations
                continue
    elif stair_type == "ascend": # Generate single stair
        ascend_tile = stair_generation(dungeon, rooms, 0)
    elif stair_type == "descend": # Generate single stair
        descend_tile = stair_generation(dungeon, rooms, 1)

    if ascend_tile:
        dungeon.tilemap[ascend_tile] = TilemapOrder.ASCEND_STAIR.value
        dungeon.tiles[ascend_tile] = dungeon.tileset["t_ascending_stair"]()
        dungeon.ascend_loc = ascend_tile
    if descend_tile:
        dungeon.tilemap[descend_tile] = TilemapOrder.DESCEND_STAIR.value
        dungeon.tiles[descend_tile] = dungeon.tileset["t_descending_stair"]()
        dungeon.descend_loc = descend_tile

    return None


def generate_entities(
    dungeon: GameMap,
    rooms: List,
    depth: int,
    ) -> None:
    for room in rooms:
        ### Spawning Monsters ###
        if room.terrain.spawn_monster:
            spawn_monsters(
                room,
                dungeon,
                depth
            )

        ### Spawning Items ###
        if room.terrain.spawn_item:
            spawn_items(
                room,
                dungeon,
            )


def debug(dungeon, save_as_txt: bool = False):
    """
    prints out tilemap
    """
    import sys
    if save_as_txt:
        sys.stdout = open('storage/procgen_debug.txt', 'a')
    
    print("\n")
    
    for i in dungeon.tilemap:
        for k in i:
            if k == TilemapOrder.VOID.value:
                print(" ", end=" ")
            elif k == TilemapOrder.ROOM_WALL.value:
                print("#", end=" ")
            elif k == TilemapOrder.ROOM_INNER.value or k == TilemapOrder.TUNNEL.value:
                print(".", end=" ")
            elif k == TilemapOrder.DOOR_CONVEX.value:
                print("d", end=" ")
            elif k == TilemapOrder.DOOR.value:
                print("+", end=" ")
            elif k == TilemapOrder.GRASS_CORE.value or k == TilemapOrder.GRASS.value:
                print("\"", end=" ")
            elif k == TilemapOrder.ASCEND_STAIR.value:
                print("<", end=" ")
            elif k == TilemapOrder.DESCEND_STAIR.value:
                print(">", end=" ")
            else:
                print(" ", end=" ")
        print(end="\n")

    for i in dungeon.protectmap:
        for k in i:
            if k:
                print("P", end=" ")
            else:
                print(".", end=" ")
        print(end='\n')
    
    sys.stdout = sys.__stdout__ #stdout back to normal


def generate_dungeon(
    console: Console,
    context: Context,
    depth: int,
    display_process: bool,
    debugmode: bool = True,
    txt_log: bool = False,
) -> GameMap:
    """
    Args:
        display_process:
            Whether to display current procgen process on the screen or not.
    """
    from game import Game
    engine = Game.engine
    rooms: List[Room] = []
    biome = choose_biome(get_dungeon_biome(depth))# If there is certain list of biomes specified for certain depth, choose one from the specified biome list.

    dungeon = GameMap(depth=depth, biome=biome) #NOTE: tilemap initialization happens during  gamemap.__init__()

    screen_center_x = int(engine.config["screen_width"] / 2)
    screen_center_y = int(engine.config["screen_height"] / 2)

    t = time.time()
    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=0)
        console.print(screen_center_x - 5, screen_center_y, "던전 생성 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "토양 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Earth...")
    generate_earth(
        dungeon=dungeon,
        map_width=biome.map_width,
        map_height=biome.map_height,
        engine=engine
    )
    if debugmode:
        print(f"Generating Earth - {time.time() - t}s")
        t = time.time()

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=10)
        console.print(screen_center_x - 5, screen_center_y, "던전 생성 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "던전 공간 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Dungeon Rooms...")
    generate_rooms(
        dungeon=dungeon,
        rooms=rooms,
        max_rooms=biome.max_rooms,
        engine=engine
    )
    if debugmode:
        print(f"Generating Dungeon Rooms - {time.time() - t}s")
        t = time.time()

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=15)
        console.print(screen_center_x - 5, screen_center_y, "던전 생성 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "터널 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Tunnels...")
    generate_tunnels(
        dungeon=dungeon,
        rooms=rooms,
    )
    if debugmode:
        print(f"Generating Tunnels - {time.time() - t}s")
        t = time.time()

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=25)
        console.print(screen_center_x - 5, screen_center_y, "던전 생성 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "지형 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Terrains...")
    generate_terrain(
        dungeon=dungeon,
        rooms=rooms,
        map_width=biome.map_width,
        map_height=biome.map_height,
    )
    if debugmode:
        print(f"Generating Terrains - {time.time() - t}s")
        t = time.time()

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=30)
        console.print(screen_center_x - 5, screen_center_y, "던전 생성 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "계단 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Staircases...")
    if not biome.generate_descending_stair:
        generate_stair(
            dungeon=dungeon,
            rooms=rooms,
            stair_type="ascend"
        )
    else:
        generate_stair(
            dungeon=dungeon,
            rooms=rooms,
            stair_type="pair"
        )
    if debugmode:
        print(f"Generating Staircases - {time.time() - t}s")
        t = time.time()

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=35)
        console.print(screen_center_x - 5, screen_center_y, "던전 생성 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "엔티티 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Spawning Entities...")
    generate_entities(
        dungeon=dungeon,
        rooms=rooms,
        depth=depth,
    )
    if debugmode:
        print(f"Spawning Entities - {time.time() - t}s")
        t = time.time()

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=20)
        console.print(screen_center_x - 5, screen_center_y, "던전 생성 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "던전 다듬는 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Adjusting Dungeon...")
    adjust_convex(
        dungeon=dungeon,
        rooms=rooms,
        )
    remove_awkward_entities(
        gamemap=dungeon
    )
    if debugmode:
        print(f"Adjusting Tunnels - {time.time() - t}s")
        t = time.time()


    if txt_log:
        debug(dungeon=dungeon, save_as_txt=True)

    return dungeon
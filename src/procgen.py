from __future__ import annotations
from tcod.console import Console
from tcod.context import Context, new
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
from typing import Iterator, List, Tuple, TYPE_CHECKING
from room_factories import Room, RectangularRoom, CircularRoom, PerpendicularRoom
from game_map import GameMap
from render import randomized_screen_paint

if TYPE_CHECKING:
    from engine import Engine


def choose_biome(
    biome_dicts: dict=None #if value is given, use it as population and weights
) -> Biome:
    if biome_dicts == None:
        biome_id = random.choices(
            population=list(biome_factories.biome_dict.keys()),
            weights=biome_factories.biome_rarity,
            k=1
            )[0]
    else:
        biome_id = random.choices(
            population=list(biome_dicts.keys()),
            weights=list(biome_dicts.values()),
            k=1
            )[0]

    return biome_factories.biome_dict[biome_id]


def choose_terrain(
    terrain_dicts: dict=None #if value is given, use it as population and weights
) -> None:
    if terrain_dicts == None:
        terrain_id = random.choices(
            population=list(terrain_factories.terrain_dict.keys()),
            weights=terrain_factories.terrain_rarity,
            k=1
            )[0]
    else:
        terrain_id = random.choices(
            population=list(terrain_dicts.keys()),
            weights=list(terrain_dicts.values()),
            k=1
            )[0]

    return copy.deepcopy(terrain_factories.terrain_dict[terrain_id])


def choose_monster_difficulty(depth: int, toughness: int=0) -> int:
    """
    Input: the depth of the floor to generate new monsters
    Output: an integer value that indicates the difficulty of the monster to generate
    
    Args:
        toughness:
            Higher toughness value will result in a higher difficulty output.

    TODO: Make this function affected by the player's status?
    NOTE: This whole function may need some minor adjustments
    """
    avg_diff = depth + toughness + 1
    min_diff = max(1, avg_diff - 3)
    max_diff = avg_diff + 3
        
    # Choose the monster difficulty (Using normal distribution; but there are limits to maximum and minimum values)
    difficulty_chosen = min(max_diff, max(min_diff, round(np.random.normal(avg_diff, 2, 1)[0])))

    return difficulty_chosen


def spawn_monsters_by_difficulty(
    x: int, y: int, difficulty: int, dungeon: GameMap, spawn_awake=False, is_first_generation=False,
) -> None:
    """
    Spawn a random monster of a given difficulty.

    Args:
        spawn_awake:
            Boolean, Will the monster become active right after they are spawned?
        is_first_generation:
            Boolean, Is this function called by the gamemap generation function?
            (=is this the first time that the monster is being generated to this dungeon?)
    """
    rarity_list = actor_factories.ActorDB.monster_rarity_for_each_difficulty[difficulty]
    monster_to_spawn = random.choices(
        population=actor_factories.ActorDB.monster_difficulty[difficulty],
        weights=rarity_list,
        k=1
        )[0]

    # Spawn new monster
    new_monster = monster_to_spawn.spawn(dungeon, x, y)

    if spawn_awake:
        if new_monster.ai:
            new_monster.ai.activate()
    if is_first_generation:
        dungeon.starting_monster_num += 1


def spawn_items(
    room: Room, dungeon: GameMap, max_item_per_room: int, min_item_per_room: int=0,
) -> None:
    number_of_items = random.randint(min_item_per_room, max_item_per_room)
    tile_coordinates = room.inner_tiles

    # Choose items to spawn
    spawn_list = random.choices(
        population=dungeon.engine.item_manager.items_lists,
        weights=item_factories.item_rarity,
        k=number_of_items
        )

    # Spawn items
    for item_to_spawn in spawn_list:
        place_tile = random.choice(tile_coordinates)
        
        if not any(entity.x == place_tile[0] and entity.y == place_tile[1] for entity in dungeon.entities) and item_to_spawn.spawnable:
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
        for x_add in range(3):
            for y_add in range(3):
                if dungeon.tilemap[cor[0]-1+x_add, cor[1]-1+y_add] == TilemapOrder.VOID.value or dungeon.tilemap[cor[0]-1+x_add, cor[1]-1+y_add] == TilemapOrder.ROOM_WALL.value:
                    wall_count += 1
        if wall_count >= 7:# If there is more than 7 walls surrounding the door convex, it is considered as an "empty convex".
            empty_convex.append(cor)
    
    return empty_convex


def adjust_convex(
    dungeon: GameMap,
    rooms: List,
) -> None:
    """
    This function will connect empty convexes with tunnels, or generate something in the convex.
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
           

def door_generation(
    dungeon: GameMap,
    room: Room,
    door_dir: str
) -> None:
    if door_dir == 'u':
        dx = 0
        dy = 1
        door_slices = room.door_up()
    elif door_dir == 'd':
        dx = 0
        dy = -1
        door_slices = room.door_down()
    elif door_dir == 'l':
        dx = 1
        dy = 0
        door_slices = room.door_left()
    elif door_dir == 'r':
        dx = -1
        dy = 0
        door_slices = room.door_right()

    for door_slice in door_slices:
        # Get door location
        door_loc = door_slice[0].start + dx, door_slice[1].start + dy
        room.doors.append(door_loc)

        # Check if door convex collides with protected areas.
        if 1 in dungeon.protectmap[door_slice]:
            continue # NOTE: Warning - Because of this line of code, the actual number of door being spawned can be smaller than the user-defined amount.
        
        # Check if door collides with protected areas.
        if dungeon.protectmap[door_loc] == 1 and room.room_protectmap[door_loc] != 1:
            print("SOMETHING WENT WRONG::DOOR COLLIDED WITH PROTECTED AREA(PROCGEN.PY)")
            continue

        # generate door convex
        dungeon.tilemap[door_slice] = TilemapOrder.DOOR_CONVEX.value
        dungeon.tunnelmap[door_slice] = True
        if room.terrain.protected:
            dungeon.protectmap[door_slice] = True
            room.room_protectmap[door_slice] = True
        dungeon.tiles[door_slice] = dungeon.tileset["t_floor"]()
        #dungeon.tiles[door_slice] = dungeon.tileset["t_DEBUG"]()

        # generate door
        dungeon.tilemap[door_loc] = TilemapOrder.DOOR.value
        dungeon.tunnelmap[door_loc] = True
        if room.terrain.protected:
            dungeon.protectmap[door_loc] = True
            room.room_protectmap[door_loc] = True
        dungeon.tiles[door_loc] = dungeon.tileset["t_floor"]()

        # spawn door unless there is nothing on the location
        if not dungeon.get_any_entity_at_location(door_loc[0], door_loc[1]):
            semiactor_factories.closed_door.spawn(gamemap=dungeon, x=door_loc[0], y=door_loc[1], lifetime=-1)
            #semiactor_factories.locked_door.spawn(gamemap=dungeon, x=door_loc[0], y=door_loc[1], lifetime=-1)


def generate_rooms(
    dungeon: GameMap,
    rooms: List,
    max_rooms: int,
    engine: Engine,
) -> Tuple[GameMap, list]:
    """Generate rooms, stairs, and doors."""
    # Generate rooms
    for r in range(max_rooms):
        # Choose the terrain of the room
        if dungeon.biome.terrain == None:
            room_terrain = choose_terrain()
        else:
            room_terrain = choose_terrain(terrain_dicts=dungeon.biome.terrain)

        # Choose the size of the room
        room_width = random.randint(room_terrain.min_width, room_terrain.max_width)
        room_height = random.randint(room_terrain.min_height, room_terrain.max_height)

        # Choose the location of the room
        # NOTE: There should be at least 4 tiles of free space each sides, so that every room can be connected.
        # It is recommeded to keep the free space as minimum as possible.
        x = random.randint(3, dungeon.width - room_width - 4)
        y = random.randint(3, dungeon.height - room_height - 4)

        # Choose the shape of the room
        shape = list(room_terrain.shape.keys())
        shape_weights = list(room_terrain.shape.values())
        room_shape = random.choices(population=shape, weights=shape_weights, cum_weights=None, k=1)[0]

        # Actual generation of the room
        if room_shape == "rectangular":
            new_room = RectangularRoom(x, y, room_width, room_height, parent=dungeon, terrain=room_terrain)
        elif room_shape == "circular":
            new_room = CircularRoom(x, y, room_width, room_height, parent=dungeon, terrain=room_terrain)
        elif room_shape == "perpendicular":
            new_room = PerpendicularRoom(x, y, room_width, room_height, parent=dungeon, terrain=room_terrain)
        else:
            new_room = RectangularRoom(x, y, room_width, room_height, parent=dungeon, terrain=room_terrain)
            print("WARNING::PROCGEN - GENERATE_ROOMS - FAILED TO SET THE ROOM SHAPE")

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Fill room's outer area on tilemap.
        for outer_slice in new_room.outer:
            dungeon.tilemap[outer_slice] = TilemapOrder.ROOM_WALL.value
            dungeon.tunnelmap[outer_slice] = False
            if new_room.terrain.protected:
                dungeon.protectmap[outer_slice] = True
                new_room.room_protectmap[outer_slice] = True

        # Dig out this rooms inner area.
        for inner_slice in new_room.inner:
            dungeon.tiles[inner_slice] = dungeon.tileset["t_floor"]()
            dungeon.tilemap[inner_slice] = TilemapOrder.ROOM_INNER.value
            dungeon.tunnelmap[inner_slice] = True
            if new_room.terrain.protected:
                dungeon.protectmap[inner_slice] = True
                new_room.room_protectmap[inner_slice] = True

        # choose the direction of the door
        doordir = []
        tempdir = ["u","d","l","r"]
        random.shuffle(tempdir)
        door_num = random.choices(new_room.terrain.door_num_range, new_room.terrain.door_num_weight, k=1)[0]
        for i in range(door_num):
            doordir.append(tempdir[i%4]) # udlr 1234

        # generate doors and door convexes
        if new_room.terrain.has_door:
            for direction in doordir:
                door_generation(dungeon=dungeon, room=new_room, door_dir=direction)

        # Finally, append the new room to the list.
        rooms.append(new_room)

        #debug(dungeon, save_as_txt=True)

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

        # Generate chests/storages
        if room.terrain.gen_chests:
            terrain_generation.generate_chest(gamemap=dungeon, room=room)

        # Call custom function if it has one
        if room.terrain.custom_gen:
            room.terrain.custom_gen(gamemap=dungeon, room=room)

        # Adjust map (delete awkwardly placed semiactors)
        terrain_generation.adjust_obstacles(gamemap=dungeon)

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
    max_monsters_per_room: int,
    max_items_per_room: int,
    ) -> None:
    for room in rooms:
        ### Spawning Monsters ###
        if room.terrain.spawn_monster:

            # Each loop can generates one monster
            mon_num = random.randint(0, max_monsters_per_room)
            for _ in range(mon_num):

                # Spawn location
                tile_coordinates = room.inner_tiles
                place_tile = random.choice(tile_coordinates)

                # Prevent entities clipping
                if any(entity.x == place_tile[0] and entity.y == place_tile[1] for entity in dungeon.entities):
                    continue
        
                # Choose difficulty
                difficulty_chosen = choose_monster_difficulty(depth=depth, toughness=0)#TODO: Adjust toughness?

                while not actor_factories.ActorDB.monster_difficulty[difficulty_chosen]:
                    difficulty_chosen = choose_monster_difficulty(depth=depth, toughness=0)

                # Spawn
                spawn_monsters_by_difficulty(x=place_tile[0], y=place_tile[1], difficulty=difficulty_chosen, dungeon=dungeon, spawn_awake=False, is_first_generation=True)


        ### Spawning Items ###
        if room.terrain.spawn_item:
            spawn_items(room, dungeon, max_items_per_room)


def debug(dungeon, save_as_txt: bool = False):
    """
    prints out tilemap
    """
    import sys
    if save_as_txt:
        sys.stdout = open('./procgen_debug.txt', 'a')
    
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
    depth,
    display_process: bool,
    min_display_time: int = 2,
) -> GameMap:
    """
    Args:
        display_process:
            Whether to display current procgen process on the screen or not.
        min_display_time:
            Minimum length(seconds) of how long the game will display procgen process to the screen.
            This argument does nothing if display_process is set to False.
    """
    from game import Game
    engine = Game.engine
    rooms: List[Room] = []
    possible_biome = get_dungeon_biome(depth) # If there is certain list of biomes specified for certain depth, choose one from the specified biome list.
    if possible_biome:
        biome = choose_biome(possible_biome)
    else:
        biome = choose_biome()

    dungeon = GameMap(depth=depth, biome=biome) #NOTE: tilemap initialization happens during  gamemap.__init__()

    screen_center_x = int(engine.config["screen_width"] / 2)
    screen_center_y = int(engine.config["screen_height"] / 2)

    render_start_time = time.time()

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=0)
        console.print(screen_center_x - 5, screen_center_y, "던전을 내려가는 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "토양 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Earth...")
    generate_earth(
        dungeon=dungeon,
        map_width=biome.map_width,
        map_height=biome.map_height,
        engine=engine
    )

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=10)
        console.print(screen_center_x - 5, screen_center_y, "던전을 내려가는 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "던전 공간 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Dungeon Rooms...")
    generate_rooms(
        dungeon=dungeon,
        rooms=rooms,
        max_rooms=biome.max_rooms,
        engine=engine
    )

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=15)
        console.print(screen_center_x - 5, screen_center_y, "던전을 내려가는 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "터널 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Tunnels...")
    generate_tunnels(
        dungeon=dungeon,
        rooms=rooms,
    )

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=20)
        console.print(screen_center_x - 5, screen_center_y, "던전을 내려가는 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "터널 다듬는 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Adjusting Tunnels...")
    adjust_convex(
        dungeon=dungeon,
        rooms=rooms,
        )

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=25)
        console.print(screen_center_x - 5, screen_center_y, "던전을 내려가는 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "지형 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Generating Terrains...")
    generate_terrain(
        dungeon=dungeon,
        rooms=rooms,
        map_width=biome.map_width,
        map_height=biome.map_height,
    )


    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=30)
        console.print(screen_center_x - 5, screen_center_y, "던전을 내려가는 중", fg=color.procgen_fg, bg=color.procgen_bg)
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

    if display_process:
        randomized_screen_paint(console, context, color.black, diversity=35)
        console.print(screen_center_x - 5, screen_center_y, "던전을 내려가는 중", fg=color.procgen_fg, bg=color.procgen_bg)
        console.print(screen_center_x - 6, screen_center_y + 2, "엔티티 생성 중...", fg=color.procgen_fg)
        context.present(console=console, keep_aspect=True)
    print("Spawning Entities...")
    generate_entities(
        dungeon=dungeon,
        rooms=rooms,
        depth=depth,
        max_monsters_per_room=biome.max_monsters_per_room,
        max_items_per_room=biome.max_items_per_room,
    )

    # Error check
    check_spawn_err = dungeon.get_any_entity_at_location(location_x=0, location_y=0)
    if check_spawn_err != None:
        print(f"WARNING::{check_spawn_err.name} spawned at (0,0)")

    # debug(dungeon=dungeon, save_as_txt=True)

    if display_process:
        time.sleep(max(0.0, min_display_time - (time.time() - render_start_time)))

    return dungeon
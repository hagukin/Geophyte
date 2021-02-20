from typing import Tuple

import numpy as np  # type: ignore
import random


# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("safe_to_walk", np.bool), # boolean that indicates if this tile is safe to walk on. 
        # This value us used when deciding whether to include this tile when pathfinding or not.
        # NOTE: if the tile is unwalkable, this value indicates if this tile is safe to phase into instead.
        ("flammable", np.float16), # chance of this tile catching on fire
        ("phaseable", np.bool), # whether the tile is phasable or not
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
        ("tile_name", np.unicode_, 16), # Tile name (under 16 letters)
        ("tile_id", np.unicode_, 16) # Tile id (under 16 letters)
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: bool,
    safe_to_walk: bool,
    flammable: float,
    phaseable: bool,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    tile_name: str,
    tile_id: str,
    ) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, safe_to_walk, flammable, phaseable, transparent, dark, light, tile_name, tile_id), dtype=tile_dt)


def new_tile_randomized(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: bool,
    safe_to_walk: bool,
    flammable: float,
    phaseable: bool,
    transparent: bool,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    darkest_fg_color: Tuple[int, int, int]=None, # None 일 경우 randomize color 하지 않음.
    brightest_fg_color: Tuple[int, int, int]=None,
    darkest_bg_color: Tuple[int, int, int]=None,
    brightest_bg_color: Tuple[int, int, int]=None,
    tile_name: str,
    tile_id: str,
    ) -> np.ndarray:
    """Helper function for defining individual tile types """

    # fg color randomize
    if darkest_fg_color and brightest_fg_color:

        r_diff = abs(brightest_fg_color[0] - darkest_fg_color[0])
        g_diff = abs(brightest_fg_color[1] - darkest_fg_color[1])
        b_diff = abs(brightest_fg_color[2] - darkest_fg_color[2])

        min_diff = min(r_diff, g_diff, b_diff)

        r_inc = round(r_diff / min_diff) #increment
        g_inc = round(g_diff / min_diff)
        b_inc = round(b_diff / min_diff)

        strength = random.randint(0, min_diff)

        fg = (
            min(brightest_fg_color[0], darkest_fg_color[0]) + r_inc * strength,
            min(brightest_fg_color[1], darkest_fg_color[1]) + g_inc * strength,
            min(brightest_fg_color[2], darkest_fg_color[2]) + b_inc * strength,
        )
    else:
        fg = light[1]

    # bg color randomize
    if darkest_bg_color and brightest_bg_color:

        r_diff = abs(brightest_bg_color[0] - darkest_bg_color[0])
        g_diff = abs(brightest_bg_color[1] - darkest_bg_color[1])
        b_diff = abs(brightest_bg_color[2] - darkest_bg_color[2])

        min_diff = min(r_diff, g_diff, b_diff)

        r_inc = round(r_diff / min_diff) #increment
        g_inc = round(g_diff / min_diff)
        b_inc = round(b_diff / min_diff)

        strength = random.randint(0, min_diff)

        bg = (
            min(brightest_bg_color[0], darkest_bg_color[0]) + r_inc * strength,
            min(brightest_bg_color[1], darkest_bg_color[1]) + g_inc * strength,
            min(brightest_bg_color[2], darkest_bg_color[2]) + b_inc * strength,
        )
    else:
        bg = light[2]
    
    randomized_light = (light[0], fg, bg)

    return np.array((walkable, safe_to_walk, flammable, phaseable, transparent, dark, randomized_light, tile_name, tile_id), dtype=tile_dt)

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

###############################################################
# NOTE:
# Tiles should have a function form.
# And each function should only indicate a single type of tile.
# The function name should have the following form:
#     "tile types"_"biome"
#     e.g. wall_desert
################################################################


### Debug Tile
def DEBUG():
    return new_tile(
    walkable=True,
    safe_to_walk=True,
    flammable=1,
    phaseable=True,
    transparent=True,
    dark=(
        ord("?"),
        (255, 0, 0),
        (255, 0, 0)
    ),
    light=(
        ord("?"),
        (255, 0, 0),
        (255, 0, 0)
    ),
    tile_name="DEBUG TILE",
    tile_id="debug",
    )


### Vintronium (Map border)
def vintronium():
    return new_tile_randomized(
        walkable=False,
        safe_to_walk=False,
        flammable=0,
        phaseable=False,
        transparent=False,
        dark=(
            ord("#"),
            (0, 0, 0),
            (15, 15, 15)
        ),
        light=(
            ord("#"),
            (0, 40, 40),
            (25, 25, 25)
        ),
        darkest_fg_color=(39, 11, 59),
        brightest_fg_color=(60, 0, 106),
        darkest_bg_color=(15, 15, 15),
        brightest_bg_color=(35, 35, 35),
        tile_name="vintronium",
        tile_id="vintronium",
    )


### Floor
def floor():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord("·"),
            (60, 60, 60),
            (15, 15, 15)
        ),
        light=(
            ord("·"),
            (150, 150, 150),
            (47, 47, 47)
        ),
        tile_name="stone floor",
        tile_id="floor",
    )
def floor_desert():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        dark=(
            ord("·"),
            (60, 60, 60),
            (15, 15, 15)
        ),
        light=(
            ord("·"),
            (254, 207, 71),
            (209, 199, 155),
        ),
        tile_name="sand",
        tile_id="floor",
    )
def floor_ancient_ruins():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        dark=(
            ord("·"),
            (60, 60, 60),
            (15, 15, 15)
        ),
        light=(
            ord("·"),
            (70, 65, 89),
            (47, 47, 47),
        ),
        tile_name="ancient tiles",
        tile_id="floor",
    )

### Wall
def wall():
    return new_tile_randomized(
        walkable=False,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=False,
        dark=(
            ord("#"),
            (20, 20, 20),
            (20, 20, 50)
        ),
        light=(
            ord("#"),
            (40, 40, 40),
            (130, 90, 60)
        ),
        darkest_bg_color=(90, 60, 30),
        brightest_bg_color=(210, 110, 40),
        tile_name="wall",
        tile_id="wall",
    )
def wall_desert():
    return new_tile_randomized(
        walkable=False,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=False,
        dark=(
            ord("#"),
            (20, 20, 20),
            (20, 20, 50)
        ),
        light=(
            ord("#"),
            (194, 168, 99),
            (227, 216, 148)
        ),
        darkest_bg_color=(227, 216, 148),
        brightest_bg_color=(254, 207, 71),
        tile_name="sand wall",
        tile_id="wall",
    )
def wall_ancient_ruins():
    return new_tile_randomized(
        walkable=False,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=False,
        dark=(
            ord("#"),
            (20, 20, 20),
            (20, 20, 50)
        ),
        light=(
            ord("#"),
            (199, 240, 219),
            (227, 216, 148)
        ),
        darkest_bg_color=(108, 123, 149),
        brightest_bg_color=(139, 186, 187),
        tile_name="ancient wall",
        tile_id="wall",
    )

### Dense Grass
def dense_grass():
    return new_tile_randomized(
        walkable=True,
        safe_to_walk=True,
        flammable=1,
        phaseable=True,
        transparent=True,
        dark=(
            ord("\""),
            (30, 35, 30),
            (15, 15, 15)
        ),
        light=(
            ord("\""),
            (85, 200, 55),
            (47, 47, 47)
        ),
        darkest_fg_color=(150, 190, 50),
        brightest_fg_color=(15, 255, 0),
        tile_name="dense grass",
        tile_id="dense_grass",
    )
def dense_grass_desert():
    return new_tile_randomized(
        walkable=True,
        safe_to_walk=True,
        flammable=1,
        phaseable=True,
        transparent=True,
        dark=(
            ord("\""),
            (30, 35, 30),
            (15, 15, 15)
        ),
        light=(
            ord("\""),
            (150, 190, 50),
            (209, 199, 155),
        ),
        darkest_fg_color=(150, 190, 50),
        brightest_fg_color=(15, 255, 0),
        tile_name="dense grass",
        tile_id="dense_grass",
    )


### Sparse Grass
def sparse_grass():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=0.9,
        phaseable=True,
        transparent=True,
        dark=(
            ord("\'"),
            (30, 35, 30),
            (15, 15, 15)
        ), # TODO : If floor tile's bg change, doors' bg should change dynamically as well
        light=(
            ord("\'"),
            (85, 200, 55),
            (47, 47, 47)
        ),
        tile_name="sparse grass",
        tile_id="sparse_grass",
    )
def sparse_grass_desert():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=0.9,
        phaseable=True,
        transparent=True,
        dark=(
            ord("\'"),
            (30, 35, 30),
            (15, 15, 15)
        ), # TODO : If floor tile's bg change, doors' bg should change dynamically as well
        light=(
            ord("\'"),
            (150, 190, 50),
            (209, 199, 155),
        ),
        tile_name="sparse grass",
        tile_id="sparse_grass",
    )


### Burnt Floor
def burnt_floor():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord("·"),
            (20, 20, 20),
            (10, 10, 10)
        ), # TODO : If floor tile's bg change, doors' bg should change dynamically as well
        light=(
            ord("·"),
            (250, 10, 0),
            (35, 25, 25)
        ),
        tile_name="burnt floor",
        tile_id="burnt_floor",
    )


### Ascending Stair
def ascending_stair():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord("<"),
            (255, 255, 0),
            (10, 10, 10)
        ), # TODO : If floor tile's bg change, stairs' bg should change dynamically as well
        light=(
            ord("<"),
            (255, 255, 0),
            (80, 80, 80)
        ),
        tile_name="ascending stair",
        tile_id="ascending_stair",
    )


### Descending Stair
def descending_stair():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord(">"),
            (255, 255, 0),
            (10, 10, 10)
        ), # TODO : If floor tile's bg change, stairs' bg should change dynamically as well
        light=(
            ord(">"),
            (255, 255, 0),
            (80, 80, 80)
        ),
        tile_name="descending stair",
        tile_id="descending_stair",
    )


### Hole
def hole():
    return new_tile(
        walkable=True,
        safe_to_walk=False,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord(" "),
            (0, 0, 0),
            (0, 0, 0)
        ),
        light=(
            ord(" "),
            (0, 0, 0),
            (0, 0, 0)
        ),
        tile_name="hole",
        tile_id="hole",
    )


### Deep Pit
def deep_pit():
    return new_tile(
        walkable=True,
        safe_to_walk=False,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord(" "),
            (0, 0, 0),
            (0, 0, 0)
        ),
        light=(
            ord(" "),
            (0, 0, 0),
            (15, 15, 15)
        ),
        tile_name="deep pit",
        tile_id="deep_pit",
    )


### Shallow Pit
def shallow_pit():
    return new_tile(
        walkable=True,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord(" "),
            (0, 0, 0),
            (10, 10, 10)
        ),
        light=(
            ord(" "),
            (0, 0, 0),
            (36, 36, 36)
        ),
        tile_name="shallow pit",
        tile_id="shallow_pit",
    )


### Deep Water
def deep_water():
    return new_tile_randomized(
        walkable=True,
        safe_to_walk=False,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord("~"),
            (0, 0, 0),
            (5, 5, 10)
        ),
        light=(
            ord("~"),
            (32, 24, 145),
            (16, 48, 156)
        ),
        darkest_bg_color=(75, 68, 182),
        brightest_bg_color=(32, 24, 145),
        tile_name="deep water",
        tile_id="deep_water",
    )


### Shallow Water
def shallow_water():
    return new_tile_randomized(
        walkable=True,
        safe_to_walk=True,
        flammable=0,
        phaseable=True,
        transparent=True,
        dark=(
            ord("·"),
            (0, 0, 0),
            (10, 10, 20)
        ),
        light=(
            ord("·"),
            (106, 107, 250),
            (16, 48, 156)
        ),
        darkest_bg_color=(75, 68, 182),
        brightest_bg_color=(106, 107, 250),
        tile_name="shallow water",
        tile_id="shallow_water",
    )


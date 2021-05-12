from tile import Tile
import skin_factories

def shroud(randomize=False):
    """NOTE: Cannot be randomized"""
    tile = Tile(
        skin=skin_factories.skin_shroud(randomize),
        walkable=True,
        safe_to_walk=False,
        flammable=False,
        phaseable=False,
        transparent=True,
        tile_name="",
        tile_id="shroud",
    )
    return tile


def debug_tile(randomize=True):
    """NOTE: Cannot be randomized"""
    tile = Tile(
        skin=skin_factories.skin_debug_tile(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="debug tile",
        tile_id="debug_tile",
    )
    return tile


def epithelium(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_epithelium(randomize),
        walkable=False,
        safe_to_walk=False,
        flammable=False,
        phaseable=False,
        transparent=False,
        tile_name="에피데리움",
        tile_id="epithelium",
    )
    return tile


###########################################
################ FLOORS ###################
###########################################

def stone_floor(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_stone_floor(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=True,
        phaseable=True,
        transparent=True,
        tile_name="석재 바닥",
        tile_id="stone_floor",
    )
    return tile


def stone_floor_burnt(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_stone_floor_burnt(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="그을린 석재 바닥",
        tile_id="stone_floor_burnt",
    )
    return tile


def sand_floor(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_sand_floor(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=True,
        phaseable=True,
        transparent=True,
        tile_name="모래 바닥",
        tile_id="sand_floor",
    )
    return tile


def sand_floor_burnt(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_sand_floor_burnt(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="모래 바닥",
        tile_id="stone_floor_burnt",
    )
    return tile


def quartz_floor(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_quartz_floor(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="대리석 바닥",
        tile_id="quartz_floor",
    )
    return tile

###########################################
################# WALLS ###################
###########################################

def cave_wall(randomize=True):
    tile = Tile(
        skin=skin_factories.skin_cave_wall(randomize),
        walkable=False,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=False,
        tile_name="동굴 벽",
        tile_id="cave_wall",
    )
    return tile

def sandstone_wall(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_sandstone_wall(randomize),
        walkable=False,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=False,
        tile_name="사암 벽",
        tile_id="sandstone_wall",
    )
    return tile


def quartz_wall(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_quartz_wall(randomize),
        walkable=False,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=False,
        tile_name="대리석 벽",
        tile_id="quartz_wall",
    )
    return tile



###########################################
############### GRASSES ###################
###########################################

def dense_grass(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_dense_grass(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=True,
        phaseable=True,
        transparent=True,
        tile_name="풀숲",
        tile_id="dense_grass",
    )
    return tile

def dense_grass_desert(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_dense_grass_desert(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=True,
        phaseable=True,
        transparent=True,
        tile_name="풀숲",
        tile_id="dense_grass",
    )
    return tile

def sparse_grass(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_sparse_grass(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=True,
        phaseable=True,
        transparent=True,
        tile_name="잔디밭",
        tile_id="sparse_grass",
    )
    return tile

def sparse_grass_desert(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_sparse_grass_desert(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=True,
        phaseable=True,
        transparent=True,
        tile_name="잔디밭",
        tile_id="sparse_grass_desert",
    )
    return tile



###########################################
################ STAIRS ###################
###########################################

def ascending_stair(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_ascending_stair(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="위로 향하는 계단",
        tile_id="ascending_stair",
    )
    return tile

def descending_stair(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_descending_stair(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="아래로 향하는 계단",
        tile_id="descending_stair",
    )
    return tile



###########################################
################ HOLES ####################
###########################################

def hole(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_hole(randomize),
        walkable=True,
        safe_to_walk=False,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="구멍",
        tile_id="hole",
    )
    return tile

def deep_pit(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_deep_pit(randomize),
        walkable=True,
        safe_to_walk=False,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="깊은 구덩이",
        tile_id="deep_pit",
    )
    return tile

def shallow_pit(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_shallow_pit(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="얕은 구덩이",
        tile_id="shallow_pit",
    )
    return tile



###########################################
################ WATER ####################
###########################################

def deep_water(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_deep_water(randomize),
        walkable=True,
        safe_to_walk=False,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="깊은 물",
        tile_id="deep_water",
    )
    return tile


def shallow_water(randomize=False):
    tile = Tile(
        skin=skin_factories.skin_shallow_water(randomize),
        walkable=True,
        safe_to_walk=True,
        flammable=False,
        phaseable=True,
        transparent=True,
        tile_name="얕은 물",
        tile_id="shallow_water",
    )
    return tile


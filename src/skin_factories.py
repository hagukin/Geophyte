from components.skin import Skin, TileSkin, EntitySkin
import sprite_factories


############################################
############### TILE SKINS #################
############################################

def skin_shroud(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_shroud_light,
            "dark":sprite_factories.t_shroud_dark
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_debug_tile(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_debug_tile_light,
            "dark":sprite_factories.t_debug_tile_dark,
        },{
            "light":sprite_factories.t_stone_floor_burnt_light,
            "dark":sprite_factories.t_stone_floor_burnt_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_epithelium(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_epithelium_light,
            "dark":sprite_factories.t_epithelium_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################ FLOORS ###################
def skin_stone_floor(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_stone_floor_light,
            "dark":sprite_factories.t_stone_floor_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_stone_floor_burnt(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_stone_floor_burnt_light,
            "dark":sprite_factories.t_stone_floor_burnt_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_sand_floor(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_sand_floor_light,
            "dark":sprite_factories.t_sand_floor_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin

def skin_sand_floor_burnt(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_sand_floor_burnt_light,
            "dark":sprite_factories.t_sand_floor_burnt_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_quartz_floor(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_quartz_floor_light,
            "dark":sprite_factories.t_quartz_floor_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################# WALLS ###################
def skin_cave_wall(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_cave_wall_light,
            "dark":sprite_factories.t_cave_wall_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_sandstone_wall(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_sandstone_wall_light,
            "dark":sprite_factories.t_sandstone_wall_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_quartz_wall(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_quartz_wall_light,
            "dark":sprite_factories.t_quartz_wall_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


############### GRASSES ###################
def skin_dense_grass(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_dense_grass_light,
            "dark":sprite_factories.t_dense_grass_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_dense_grass_desert(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_dense_grass_desert_light,
            "dark":sprite_factories.t_dense_grass_desert_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_sparse_grass(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_sparse_grass_light,
            "dark":sprite_factories.t_sparse_grass_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_sparse_grass_desert(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_sparse_grass_desert_light,
            "dark":sprite_factories.t_sparse_grass_desert_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################ STAIRS ###################
def skin_ascending_stair(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_ascending_stair_light,
            "dark":sprite_factories.t_ascending_stair_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_descending_stair(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_descending_stair_light,
            "dark":sprite_factories.t_descending_stair_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################ HOLES ####################
def skin_hole(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_hole_light,
            "dark":sprite_factories.t_hole_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_deep_pit(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_deep_pit_light,
            "dark":sprite_factories.t_deep_pit_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_shallow_pit(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_shallow_pit_light,
            "dark":sprite_factories.t_shallow_pit_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################ WATER ####################
def skin_deep_water(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_deep_water_light,
            "dark":sprite_factories.t_deep_water_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_shallow_water(randomize: bool):
    skin = TileSkin(
        sprites_set=[{
            "light":sprite_factories.t_shallow_water_light,
            "dark":sprite_factories.t_shallow_water_dark,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin



############################################
############## ENTITY SKINS ################
############################################

def skin_transparent(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_transparent_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin

### 1. Actor Skins
def skin_player(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_player_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin

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
            "light0000":sprite_factories.t_stone_floor_light0000,
            "light0001": sprite_factories.t_stone_floor_light0001,
            "light0010": sprite_factories.t_stone_floor_light0010,
            "light0011": sprite_factories.t_stone_floor_light0011,
            "light0100": sprite_factories.t_stone_floor_light0100,
            "light0101": sprite_factories.t_stone_floor_light0101,
            "light0110": sprite_factories.t_stone_floor_light0110,
            "light0111": sprite_factories.t_stone_floor_light0111,
            "light1000": sprite_factories.t_stone_floor_light1000,
            "light1001": sprite_factories.t_stone_floor_light1001,
            "light1010": sprite_factories.t_stone_floor_light1010,
            "light1011": sprite_factories.t_stone_floor_light1011,
            "light1100": sprite_factories.t_stone_floor_light1100,
            "light1101": sprite_factories.t_stone_floor_light1101,
            "light1110": sprite_factories.t_stone_floor_light1110,
            "light1111": sprite_factories.t_stone_floor_light1111,
            "dark0000": sprite_factories.t_stone_floor_dark0000,
            "dark0001": sprite_factories.t_stone_floor_dark0001,
            "dark0010": sprite_factories.t_stone_floor_dark0010,
            "dark0011": sprite_factories.t_stone_floor_dark0011,
            "dark0100": sprite_factories.t_stone_floor_dark0100,
            "dark0101": sprite_factories.t_stone_floor_dark0101,
            "dark0110": sprite_factories.t_stone_floor_dark0110,
            "dark0111": sprite_factories.t_stone_floor_dark0111,
            "dark1000": sprite_factories.t_stone_floor_dark1000,
            "dark1001": sprite_factories.t_stone_floor_dark1001,
            "dark1010": sprite_factories.t_stone_floor_dark1010,
            "dark1011": sprite_factories.t_stone_floor_dark1011,
            "dark1100": sprite_factories.t_stone_floor_dark1100,
            "dark1101": sprite_factories.t_stone_floor_dark1101,
            "dark1110": sprite_factories.t_stone_floor_dark1110,
            "dark1111": sprite_factories.t_stone_floor_dark1111,
        }],
        is_dynamic=True,#TODO
        bitmap_true_when_not_walkable=True,
        bitmap_true_when_water=True,
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
            "light":sprite_factories.t_cave_wall_light1,
            "dark":sprite_factories.t_cave_wall_dark,
        }, {
            "light":sprite_factories.t_cave_wall_light2,
            "dark":sprite_factories.t_cave_wall_dark,
        }, {
            "light":sprite_factories.t_cave_wall_light3,
            "dark":sprite_factories.t_cave_wall_dark,
        }, {
            "light":sprite_factories.t_cave_wall_light4,
            "dark":sprite_factories.t_cave_wall_dark,
        }, {
            "light":sprite_factories.t_cave_wall_light5,
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

"""
############################### Actor Skins ############################
"""
################## @ - Humanoids  ##################
def skin_player(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_player_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin

def skin_shopkeeper(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_shopkeeper_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin



###################### a - ants  ###################
def skin_ant(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_ant_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_fire_ant(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_fire_ant_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_volt_ant(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_volt_ant_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin



#################  b- bats / birds  ################
def skin_bat(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_bat_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


#####################  c- cats  ####################
def skin_kitten(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_kitten_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_cat(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_cat_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_large_cat(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_large_cat_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin



####################  d - dogs  ####################
def skin_puppy(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_puppy_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_dog(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_dog_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_large_dog(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_large_dog_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################  e - eyes & brains  ###############
def skin_floating_eye(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_floating_eye_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


############### i = flying insects  ################
def skin_fly(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_fly_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_giant_bee(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_giant_bee_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


############### j - jellies / slimes  ##############
def skin_black_jelly(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_black_jelly_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


#################### n - nymphs  ###################
def skin_nymph(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_nymph_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


#################### o - spheres ###################
def skin_sphere_of_acid(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_sphere_of_acid_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


############# s - spiders & scorpions  #############
def skin_jumping_spider(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_jumping_spider_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


#####################  w - worms  ##################
def skin_earthworm(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_earthworm_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_maggot(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_maggot_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################## E - ELEMENTALS  #################
def skin_ice_elemental(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_ice_elemental_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################### I - IMPOSTERS  #################
def skin_chatterbox(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_chatterbox_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


################ T - GIANTS & TITANS  ##############
def skin_giant(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_giant_default,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


"""
############################### Semiactor Skins ############################
"""
########################## SEMIACTORS WITH AI ############################

################################ CHESTS ##################################
def skin_wooden_chest(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_wooden_chest_closed,
            "opened":sprite_factories.e_wooden_chest_opened,
            "closed":sprite_factories.e_wooden_chest_closed
        }]
    )
    skin.curr_sprite_state = "closed"
    if randomize:
        skin = skin.randomize()
    return skin


def skin_large_wooden_chest(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_large_wooden_chest_closed,
            "opened":sprite_factories.e_large_wooden_chest_opened,
            "closed":sprite_factories.e_large_wooden_chest_closed
        }]
    )
    skin.curr_sprite_state = "closed"
    if randomize:
        skin = skin.randomize()
    return skin

################################# TRAPS ##################################

################ INTERACTABLE SEMIACTORS WITH NO AI ######################
def skin_wooden_door_opened(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_wooden_door_opened,
        }]
    ) #NOTE: Since closed doors and opened doors are two entire different entities, we seperate the skin components as well.
    if randomize:
        skin = skin.randomize()
    return skin


def skin_wooden_door_closed(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.e_wooden_door_closed,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin




############################################
###############VISUAL SKINS ################
############################################

def skin_magic_missile(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.v_magic_missile,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_piercing_flame(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.v_piercing_flame,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_explosion(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.v_explosion,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin


def skin_acid_explosion(randomize: bool):
    skin = EntitySkin(
        sprites_set=[{
            "default":sprite_factories.v_acid_explosion,
        }]
    )
    if randomize:
        skin = skin.randomize()
    return skin



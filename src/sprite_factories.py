from sprite import GameSprite
import copy
import pygame
import json



def dynamic_tile_constructor(sprite_id_no_bit: str, is_animating: bool, frame_len: int):
    b0000 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0000",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b0001 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0001",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b0010 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0010",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b0011 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0011",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b0100 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0100",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b0101 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0101",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b0110 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0110",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b0111 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/0111",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1000 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1000",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1001 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1001",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1010 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1010",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1011 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1011",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1100 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1100",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1101 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1101",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1110 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1110",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    b1111 = GameSprite(
        sprite_category="tiles",
        sprite_id=f"{sprite_id_no_bit}/1111",
        is_animating=is_animating,
        frame_len=frame_len,
    )
    return b0000, b0001, b0010, b0011, b0100, b0101, b0110, b0111, b1000, b1001, b1010, b1011, b1100, b1101, b1110, b1111




############################################
############### TILE SPRITES ###############
############################################

# shroud
t_shroud_light = GameSprite(
    sprite_category="tiles",
    sprite_id="shroud/light",
    is_animating=False,
    frame_len=1,
)
t_shroud_dark = copy.copy(t_shroud_light)
t_shroud_dark.sprite_id = "shroud/dark"

# debug tile
t_debug_tile_light = GameSprite(
    sprite_category="tiles",
    sprite_id="debug_tile/light",
    is_animating=True,
    frame_len=4,
)
t_debug_tile_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="debug_tile/dark",
    is_animating=True,
    frame_len=4,
)

# epithelium
t_epithelium_light = GameSprite(
    sprite_category="tiles",
    sprite_id="epithelium/light",
    is_animating=False,
    frame_len=1,
)
t_epithelium_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="epithelium/dark",
    is_animating=False,
    frame_len=1,
)

################ FLOORS ###################
# stone floor
t_stone_floor_light = GameSprite(
    sprite_category="tiles",
    sprite_id="stone_floor/light",
    is_animating=False,
    frame_len=1,
)
t_stone_floor_light0000,\
t_stone_floor_light0001,\
t_stone_floor_light0010,\
t_stone_floor_light0011,\
t_stone_floor_light0100,\
t_stone_floor_light0101,\
t_stone_floor_light0110,\
t_stone_floor_light0111,\
t_stone_floor_light1000,\
t_stone_floor_light1001,\
t_stone_floor_light1010,\
t_stone_floor_light1011,\
t_stone_floor_light1100,\
t_stone_floor_light1101,\
t_stone_floor_light1110,\
t_stone_floor_light1111 = dynamic_tile_constructor("stone_floor/light", False, 1)
t_stone_floor_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="stone_floor/dark",
    is_animating=False,
    frame_len=1,
)
t_stone_floor_dark0000,\
t_stone_floor_dark0001,\
t_stone_floor_dark0010,\
t_stone_floor_dark0011,\
t_stone_floor_dark0100,\
t_stone_floor_dark0101,\
t_stone_floor_dark0110,\
t_stone_floor_dark0111,\
t_stone_floor_dark1000,\
t_stone_floor_dark1001,\
t_stone_floor_dark1010,\
t_stone_floor_dark1011,\
t_stone_floor_dark1100,\
t_stone_floor_dark1101,\
t_stone_floor_dark1110,\
t_stone_floor_dark1111 = dynamic_tile_constructor("stone_floor/dark", False, 1)


# stone floor burnt
t_stone_floor_burnt_light = GameSprite(
    sprite_category="tiles",
    sprite_id="stone_floor_burnt/light",
    is_animating=False,
    frame_len=1,
)
t_stone_floor_burnt_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="stone_floor_burnt/dark",
    is_animating=False,
    frame_len=1,
)


# sand floor
t_sand_floor_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor/light",
    is_animating=False,
    frame_len=1,
)
t_sand_floor_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor/dark",
    is_animating=False,
    frame_len=1,
)


# sand floor burnt
t_sand_floor_burnt_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor_burnt/light",
    is_animating=False,
    frame_len=1,
)
t_sand_floor_burnt_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor_burnt/dark",
    is_animating=False,
    frame_len=1,
)


# quartz floor
t_quartz_floor_light = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_floor/light",
    is_animating=False,
    frame_len=1,
)
t_quartz_floor_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_floor/dark",
    is_animating=False,
    frame_len=1,
)




################# WALLS ###################
# cave wall
t_cave_wall_light1 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light1",
    is_animating=False,
    frame_len=1,
)
t_cave_wall_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/dark",
    is_animating=False,
    frame_len=1,
)

t_cave_wall_light2 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light2",
    is_animating=False,
    frame_len=1,
)
t_cave_wall_light3 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light3",
    is_animating=False,
    frame_len=1,
)
t_cave_wall_light4 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light4",
    is_animating=False,
    frame_len=1,
)
t_cave_wall_light5 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light5",
    is_animating=False,
    frame_len=1,
)


#sandstone wall
t_sandstone_wall_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sandstone_wall/light",
    is_animating=False,
    frame_len=1,
)
t_sandstone_wall_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sandstone_wall/dark",
    is_animating=False,
    frame_len=1,
)


#quartz wall
t_quartz_wall_light = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_wall/light",
    is_animating=False,
    frame_len=1,
)
t_quartz_wall_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_wall/dark",
    is_animating=False,
    frame_len=1,
)




############### GRASSES ###################
t_dense_grass_light = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass/light",
    is_animating=False,
    frame_len=1,
)
t_dense_grass_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass/dark",
    is_animating=False,
    frame_len=1,
)


t_dense_grass_desert_light = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass_desert/light",
    is_animating=False,
    frame_len=1,
)
t_dense_grass_desert_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass_desert/dark",
    is_animating=False,
    frame_len=1,
)


t_sparse_grass_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass/light",
    is_animating=False,
    frame_len=1,
)
t_sparse_grass_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass/dark",
    is_animating=False,
    frame_len=1,
)


t_sparse_grass_desert_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass_desert/light",
    is_animating=False,
    frame_len=1,
)
t_sparse_grass_desert_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass_desert/dark",
    is_animating=False,
    frame_len=1,
)




################ STAIRS ###################
t_ascending_stair_light = GameSprite(
    sprite_category="tiles",
    sprite_id="ascending_stair/light",
    is_animating=False,
    frame_len=1,
)
t_ascending_stair_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="ascending_stair/dark",
    is_animating=False,
    frame_len=1,
)


t_descending_stair_light = GameSprite(
    sprite_category="tiles",
    sprite_id="descending_stair/light",
    is_animating=False,
    frame_len=1,
)
t_descending_stair_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="descending_stair/dark",
    is_animating=False,
    frame_len=1,
)




################ HOLES ####################
t_hole_light = GameSprite(
    sprite_category="tiles",
    sprite_id="hole/light",
    is_animating=False,
    frame_len=1,
)
t_hole_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="hole/dark",
    is_animating=False,
    frame_len=1,
)


t_deep_pit_light = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_pit/light",
    is_animating=False,
    frame_len=1,
)
t_deep_pit_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_pit/dark",
    is_animating=False,
    frame_len=1,
)


t_shallow_pit_light = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_pit/light",
    is_animating=False,
    frame_len=1,
)
t_shallow_pit_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_pit/dark",
    is_animating=False,
    frame_len=1,
)




################ WATER ####################
t_deep_water_light = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_water/light",
    is_animating=True,
    frame_len=5,
)
t_deep_water_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_water/dark",
    is_animating=False,
    frame_len=1,
)


t_shallow_water_light = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_water/light",
    is_animating=True,
    frame_len=5,
)
t_shallow_water_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_water/dark",
    is_animating=False,
    frame_len=1,
)




############################################
############## ENTITY SKINS ################
############################################

e_transparent_default = GameSprite(
    sprite_category="miscs",
    sprite_id="transparent/default",
    is_animating=False,
    frame_len=1,
)

e_debug_entity_default = GameSprite(
    sprite_category="miscs",
    sprite_id="debug_entity/default",
    is_animating=True,
    frame_len=4,
)


e_debug_actor_default = GameSprite(
    sprite_category="miscs",
    sprite_id="debug_actor/default",
    is_animating=False,
    frame_len=1,
)

"""
#############  ACTORS ################
"""
################## @ - Humanoids  ##################
e_player_default = GameSprite(
    sprite_category="actors",
    sprite_id="player/default",
    is_animating=True,
    frame_len=2,
)


e_shopkeeper_default = GameSprite(
    sprite_category="actors",
    sprite_id="shopkeeper/default",
    is_animating=True,
    frame_len=2,
)



###################### a - ants  ###################
e_ant_default = GameSprite(
    sprite_category="actors",
    sprite_id="ant/default",
    is_animating=True,
    frame_len=2,
)

e_fire_ant_default = GameSprite(
    sprite_category="actors",
    sprite_id="fire_ant/default",
    is_animating=True,
    frame_len=2,
)


e_volt_ant_default = GameSprite(
    sprite_category="actors",
    sprite_id="volt_ant/default",
    is_animating=True,
    frame_len=2,
)



#################  b- bats / birds  ################
e_bat_default = GameSprite(
    sprite_category="actors",
    sprite_id="bat/default",
    is_animating=True,
    frame_len=2,
)



#####################  c- cats  ####################
e_kitten_default = GameSprite(
    sprite_category="actors",
    sprite_id="kitten/default",
    is_animating=True,
    frame_len=2,
)


e_cat_default = GameSprite(
    sprite_category="actors",
    sprite_id="cat/default",
    is_animating=True,
    frame_len=2,
)

e_large_cat_default = GameSprite(
    sprite_category="actors",
    sprite_id="large_cat/default",
    is_animating=True,
    frame_len=2,
)


####################  d - dogs  ####################
e_puppy_default = GameSprite(
    sprite_category="actors",
    sprite_id="puppy/default",
    is_animating=True,
    frame_len=2,
)


e_dog_default = GameSprite(
    sprite_category="actors",
    sprite_id="dog/default",
    is_animating=True,
    frame_len=2,
)


e_large_dog_default = GameSprite(
    sprite_category="actors",
    sprite_id="large_dog/default",
    is_animating=True,
    frame_len=2,
)



################  e - eyes & brains  ###############
e_floating_eye_default = GameSprite(
    sprite_category="actors",
    sprite_id="floating_eye/default",
    is_animating=True,
    frame_len=2,
)



############### i = flying insects  ################
e_fly_default = GameSprite(
    sprite_category="actors",
    sprite_id="fly/default",
    is_animating=True,
    frame_len=2,
)


e_giant_bee_default = GameSprite(
    sprite_category="actors",
    sprite_id="giant_bee/default",
    is_animating=True,
    frame_len=2,
)



############### j - jellies / slimes  ##############
e_black_jelly_default = GameSprite(
    sprite_category="actors",
    sprite_id="black_jelly/default",
    is_animating=True,
    frame_len=2,
)



#################### n - nymphs  ###################
e_nymph_default = GameSprite(
    sprite_category="actors",
    sprite_id="nymph/default",
    is_animating=True,
    frame_len=2,
)



#################### o - spheres ###################
e_sphere_of_acid_default = GameSprite(
    sprite_category="actors",
    sprite_id="sphere_of_acid/default",
    is_animating=True,
    frame_len=2,
)



############# s - spiders & scorpions  #############
e_jumping_spider_default = GameSprite(
    sprite_category="actors",
    sprite_id="jumping_spider/default",
    is_animating=True,
    frame_len=2,
)



#####################  w - worms  ##################
e_earthworm_default = GameSprite(
    sprite_category="actors",
    sprite_id="earthworm/default",
    is_animating=True,
    frame_len=2,
)


e_maggot_default = GameSprite(
    sprite_category="actors",
    sprite_id="maggot/default",
    is_animating=True,
    frame_len=2,
)



################## E - ELEMENTALS  #################
e_ice_elemental_default = GameSprite(
    sprite_category="actors",
    sprite_id="ice_elemental/default",
    is_animating=True,
    frame_len=2,
)


################### I - IMPOSTERS  #################
e_chatterbox_default = GameSprite(
    sprite_category="actors",
    sprite_id="chatterbox/default",
    is_animating=True,
    frame_len=2,
)


################ T - GIANTS & TITANS  ##############
e_giant_default = GameSprite(
    sprite_category="actors",
    sprite_id="giant/default",
    is_animating=True,
    frame_len=2,
)



"""
#############  SEMIACTORS ################
"""
########################## SEMIACTORS WITH AI ############################

################################# TRAPS ##################################

################################ CHESTS ##################################
e_wooden_chest_closed = GameSprite(
    sprite_category="semiactors",
    sprite_id="wooden_chest/closed",
    is_animating=False,
    frame_len=1,
)

e_wooden_chest_opened = GameSprite(
    sprite_category="semiactors",
    sprite_id="wooden_chest/opened",
    is_animating=False,
    frame_len=1,
)


e_large_wooden_chest_closed = GameSprite(
    sprite_category="semiactors",
    sprite_id="large_wooden_chest/closed",
    is_animating=False,
    frame_len=1,
)

e_large_wooden_chest_opened = GameSprite(
    sprite_category="semiactors",
    sprite_id="large_wooden_chest/opened",
    is_animating=False,
    frame_len=1,
)


################ INTERACTABLE SEMIACTORS WITH NO AI ######################
e_wooden_door_opened = GameSprite(
    sprite_category="semiactors",
    sprite_id="wooden_door/opened",
    is_animating=False,
    frame_len=1,
)


e_wooden_door_closed = GameSprite(
    sprite_category="semiactors",
    sprite_id="wooden_door/closed",
    is_animating=False,
    frame_len=1,
)



############################################
################### VISUALS ################
############################################

v_magic_missile = GameSprite(
    sprite_category="visuals",
    sprite_id="magic_missile/default",
    is_animating=False,
    frame_len=1,
)


v_piercing_flame = GameSprite(
    sprite_category="visuals",
    sprite_id="piercing_flame/default",
    is_animating=False,
    frame_len=1,
)


v_explosion = GameSprite(
    sprite_category="visuals",
    sprite_id="explosion/default",
    is_animating=False,
    frame_len=1,
)


v_acid_explosion = GameSprite(
    sprite_category="visuals",
    sprite_id="acid_explosion/default",
    is_animating=False,
    frame_len=1,
)

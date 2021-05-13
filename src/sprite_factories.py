from sprite import GameSprite
import copy
import pygame
import json

tile_sprites = []
entity_sprites = []

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
tile_sprites.append(t_shroud_light)
t_shroud_dark = copy.copy(t_shroud_light)
t_shroud_dark.sprite_id = "shroud/dark"
tile_sprites.append(t_shroud_dark)

# debug tile
t_debug_tile_light = GameSprite(
    sprite_category="tiles",
    sprite_id="debug_tile/light",
    is_animating=True,
    frame_len=4,
)
tile_sprites.append(t_debug_tile_light)
t_debug_tile_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="debug_tile/dark",
    is_animating=True,
    frame_len=4,
)
tile_sprites.append(t_debug_tile_dark)

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
tile_sprites.append(t_stone_floor_light)
t_stone_floor_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="stone_floor/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_stone_floor_dark)


# stone floor burnt
t_stone_floor_burnt_light = GameSprite(
    sprite_category="tiles",
    sprite_id="stone_floor_burnt/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_stone_floor_burnt_light)
t_stone_floor_burnt_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="stone_floor_burnt/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_stone_floor_burnt_dark)


# sand floor
t_sand_floor_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sand_floor_light)
t_sand_floor_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sand_floor_dark)


# sand floor burnt
t_sand_floor_burnt_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor_burnt/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sand_floor_burnt_light)
t_sand_floor_burnt_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sand_floor_burnt/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sand_floor_burnt_dark)


# quartz floor
t_quartz_floor_light = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_floor/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_quartz_floor_light)
t_quartz_floor_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_floor/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_quartz_floor_dark)




################# WALLS ###################
# cave wall
t_cave_wall_light1 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light1",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_light1)
t_cave_wall_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_dark)

t_cave_wall_light2 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light2",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_light2)
t_cave_wall_light3 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light3",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_light3)
t_cave_wall_light4 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light4",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_light4)
t_cave_wall_light5 = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light5",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_light5)


#sandstone wall
t_sandstone_wall_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sandstone_wall/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sandstone_wall_light)
t_sandstone_wall_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sandstone_wall/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sandstone_wall_dark)


#quartz wall
t_quartz_wall_light = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_wall/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_quartz_wall_light)
t_quartz_wall_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="quartz_wall/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_quartz_wall_dark)




############### GRASSES ###################
t_dense_grass_light = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_dense_grass_light)
t_dense_grass_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_dense_grass_dark)


t_dense_grass_desert_light = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass_desert/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_dense_grass_desert_light)
t_dense_grass_desert_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="dense_grass_desert/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_dense_grass_desert_dark)


t_sparse_grass_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sparse_grass_light)
t_sparse_grass_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sparse_grass_dark)


t_sparse_grass_desert_light = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass_desert/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sparse_grass_desert_light)
t_sparse_grass_desert_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="sparse_grass_desert/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_sparse_grass_desert_dark)




################ STAIRS ###################
t_ascending_stair_light = GameSprite(
    sprite_category="tiles",
    sprite_id="ascending_stair/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_ascending_stair_light)
t_ascending_stair_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="ascending_stair/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_ascending_stair_dark)


t_descending_stair_light = GameSprite(
    sprite_category="tiles",
    sprite_id="descending_stair/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_descending_stair_light)
t_descending_stair_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="descending_stair/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_descending_stair_dark)




################ HOLES ####################
t_hole_light = GameSprite(
    sprite_category="tiles",
    sprite_id="hole/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_hole_light)
t_hole_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="hole/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_hole_dark)


t_deep_pit_light = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_pit/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_deep_pit_light)
t_deep_pit_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_pit/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_deep_pit_dark)


t_shallow_pit_light = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_pit/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_shallow_pit_light)
t_shallow_pit_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_pit/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_shallow_pit_dark)




################ WATER ####################
t_deep_water_light = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_water/light",
    is_animating=True,
    frame_len=5,
)
tile_sprites.append(t_deep_water_light)
t_deep_water_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="deep_water/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_deep_water_dark)


t_shallow_water_light = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_water/light",
    is_animating=True,
    frame_len=5,
)
tile_sprites.append(t_shallow_water_light)
t_shallow_water_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="shallow_water/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_shallow_water_dark)




############################################
############## ENTITY SKINS ################
############################################

e_transparent_default = GameSprite(
    sprite_category="miscs",
    sprite_id="transparent/default",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(e_transparent_default)

e_debug_entity_default = GameSprite(
    sprite_category="miscs",
    sprite_id="debug_entity/default",
    is_animating=True,
    frame_len=4,
)
entity_sprites.append(e_debug_entity_default)


e_debug_actor_default = GameSprite(
    sprite_category="miscs",
    sprite_id="debug_actor/default",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(e_debug_actor_default)

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
entity_sprites.append(e_player_default)


e_shopkeeper_default = GameSprite(
    sprite_category="actors",
    sprite_id="shopkeeper/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_shopkeeper_default)



###################### a - ants  ###################
e_ant_default = GameSprite(
    sprite_category="actors",
    sprite_id="ant/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_ant_default)


e_fire_ant_default = GameSprite(
    sprite_category="actors",
    sprite_id="fire_ant/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_fire_ant_default)


e_volt_ant_default = GameSprite(
    sprite_category="actors",
    sprite_id="volt_ant/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_volt_ant_default)



#################  b- bats / birds  ################
e_bat_default = GameSprite(
    sprite_category="actors",
    sprite_id="bat/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_bat_default)



#####################  c- cats  ####################
e_kitten_default = GameSprite(
    sprite_category="actors",
    sprite_id="kitten/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_kitten_default)


e_cat_default = GameSprite(
    sprite_category="actors",
    sprite_id="cat/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_cat_default)


e_large_cat_default = GameSprite(
    sprite_category="actors",
    sprite_id="large_cat/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_large_cat_default)


####################  d - dogs  ####################
e_puppy_default = GameSprite(
    sprite_category="actors",
    sprite_id="puppy/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_kitten_default)


e_dog_default = GameSprite(
    sprite_category="actors",
    sprite_id="dog/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_dog_default)


e_large_dog_default = GameSprite(
    sprite_category="actors",
    sprite_id="large_dog/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_large_dog_default)



################  e - eyes & brains  ###############
e_floating_eye_default = GameSprite(
    sprite_category="actors",
    sprite_id="floating_eye/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_floating_eye_default)



############### i = flying insects  ################
e_fly_default = GameSprite(
    sprite_category="actors",
    sprite_id="fly/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_fly_default)


e_giant_bee_default = GameSprite(
    sprite_category="actors",
    sprite_id="giant_bee/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_giant_bee_default)



############### j - jellies / slimes  ##############
e_black_jelly_default = GameSprite(
    sprite_category="actors",
    sprite_id="black_jelly/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_black_jelly_default)



#################### n - nymphs  ###################
e_nymph_default = GameSprite(
    sprite_category="actors",
    sprite_id="nymph/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_nymph_default)



#################### o - spheres ###################
e_sphere_of_acid_default = GameSprite(
    sprite_category="actors",
    sprite_id="sphere_of_acid/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_sphere_of_acid_default)



############# s - spiders & scorpions  #############
e_jumping_spider_default = GameSprite(
    sprite_category="actors",
    sprite_id="jumping_spider/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_jumping_spider_default)



#####################  w - worms  ##################
e_earthworm_default = GameSprite(
    sprite_category="actors",
    sprite_id="earthworm/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_earthworm_default)


e_maggot_default = GameSprite(
    sprite_category="actors",
    sprite_id="maggot/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_maggot_default)



################## E - ELEMENTALS  #################
e_ice_elemental_default = GameSprite(
    sprite_category="actors",
    sprite_id="ice_elemental/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_ice_elemental_default)


################### I - IMPOSTERS  #################
e_chatterbox_default = GameSprite(
    sprite_category="actors",
    sprite_id="chatterbox/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_chatterbox_default)


################ T - GIANTS & TITANS  ##############
e_giant_default = GameSprite(
    sprite_category="actors",
    sprite_id="giant/default",
    is_animating=True,
    frame_len=2,
)
entity_sprites.append(e_giant_default)



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
entity_sprites.append(e_wooden_chest_closed)

e_wooden_chest_opened = GameSprite(
    sprite_category="semiactors",
    sprite_id="wooden_chest/opened",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(e_wooden_chest_opened)


e_large_wooden_chest_closed = GameSprite(
    sprite_category="semiactors",
    sprite_id="large_wooden_chest/closed",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(e_large_wooden_chest_closed)

e_large_wooden_chest_opened = GameSprite(
    sprite_category="semiactors",
    sprite_id="large_wooden_chest/opened",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(e_large_wooden_chest_opened)


################ INTERACTABLE SEMIACTORS WITH NO AI ######################
e_wooden_door_opened = GameSprite(
    sprite_category="semiactors",
    sprite_id="wooden_door/opened",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(e_wooden_door_opened)


e_wooden_door_closed = GameSprite(
    sprite_category="semiactors",
    sprite_id="wooden_door/closed",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(e_wooden_door_closed)



############################################
################### VISUALS ################
############################################

v_magic_missile = GameSprite(
    sprite_category="visuals",
    sprite_id="magic_missile/default",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(v_magic_missile)


v_piercing_flame = GameSprite(
    sprite_category="visuals",
    sprite_id="piercing_flame/default",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(v_piercing_flame)


v_explosion = GameSprite(
    sprite_category="visuals",
    sprite_id="explosion/default",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(v_explosion)


v_acid_explosion = GameSprite(
    sprite_category="visuals",
    sprite_id="acid_explosion/default",
    is_animating=False,
    frame_len=1,
)
entity_sprites.append(v_acid_explosion)
from sprite import GameSprite
import copy

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
t_cave_wall_light = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/light",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_light)
t_cave_wall_dark = GameSprite(
    sprite_category="tiles",
    sprite_id="cave_wall/dark",
    is_animating=False,
    frame_len=1,
)
tile_sprites.append(t_cave_wall_dark)


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
    is_animating=False,
    frame_len=1,
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
    is_animating=False,
    frame_len=1,
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


#############  ACTORS ################
e_player_default =GameSprite(
    sprite_category="actors",
    sprite_id="player/default",
    is_animating=True,
    frame_len=4,
)
entity_sprites.append(e_player_default)


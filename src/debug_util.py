# Memory debug
#print(" ################################################")
# print("+++++++++++메모리++++++++")
# for k, v in engine.world.mem_world.items():
#     print(k, v)
# print("++++++++++++데이터+++++++++++++")
# for k in engine.world.saved_maps:
#     try:
#         tmp = engine.world.load_map_from_seriallized_data(k)
#         if tmp:
#             print(k)
#     except Exception as e:
#         print(f"{k}없음")
#         raise e

# Player count debug
# print("###############################")
# for k, v in engine.world.mem_world.items():
#     if v == None:
#         continue
#     cnt = 0
#     for e in v.entities:
#         if e.entity_id == "player":
#             cnt += 1
#     print(f"depth {k} - player cnt - {cnt}")
#
# def physical_dmg_calc(dmg, protection, strength):
#     import math
#     import random
#     penetration = 1 + math.log10(strength / 10 + 1)
#     dmg_absorbed = int(protection * 0.7 / penetration)
#     dmg_reduced = 1 + protection * math.log2(protection / 2000 + 1)
#     dmg = (dmg - dmg_absorbed) / dmg_reduced
#     print(dmg)
#     return
#
# for i in range(10, 80):
#     print(i)
#     physical_dmg_calc(100, i, 15)


# Check for duplicate player (serialization error)
# has_player = False
# for e in engine.game_map.entities:
#     if e.gamemap is not None and e.gamemap != engine.game_map:
#         print(f"{e.entity_id} has wrong gamemap.")
#     if e.entity_id == "player":
#         if has_player:
#             print(f"{engine.depth} depth has multiple player.")
#         else:
#             has_player = True
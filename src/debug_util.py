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
import vk_api
from pprint import pprint

vk_session = vk_api.VkApi(
    token="ed52a625ed52a625ed52a6252eee461ffbeed52ed52a62589c8f057c4ad4cf28e7d8a73"
)
vk_session.auth()

vk = vk_session.get_api()

tools = vk_api.VkTools(vk_session)
# print(vk.wall.post(message="Hello world!"))

# wall = tools.get_all("wall.get", 1000, {"domain": "repouiii"})
wall = tools.get_all("wall.get", 1000, {"owner_id": -121568313})

pprint(wall["count"])
print("\n")

wall_items = wall["items"]

wall_items = sorted(wall_items, key=lambda x: x["likes"]["count"], reverse=True)

print([item["likes"]["count"] for item in wall_items])

# if wall["count"]:
#     pprint(wall_items[0])
#     print("\n")

if wall["count"] > 1:
    pprint(wall_items[-1])

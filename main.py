import vk_api
from pprint import pprint
import requests
from backend.constants import APP_ACCESS_KEY, VKAPI_VERSION, VKAPI_URL

# if False:
#     params = {
#         "v": VKAPI_VERSION,
#         "access_token": APP_ACCESS_KEY,
#         "domain": "repouiii",
#     }
#     response = requests.get(VKAPI_URL + "wall.get?", params=params)
#     pprint(response.json())

vkscript_code = (
    'var posts = API.wall.get({"count": 10, "offset": 0, "domain": "repouiii"});'
)
vkscript_code = """
var count = 0;
var i = 0; 
var offset = 0;
var items = [];
while (i != 26) { 
    i = i + 1; 
    var get_data = API.wall.get({"count": 100, "offset": offset, "domain": "repouiii"}); 
    items = items + get_data["items"];
    count = get_data["count"]; 
    offset = offset + 100;
}; 
return {
"count": count, 
"items": items};
"""
params = {
    "v": VKAPI_VERSION,
    "access_token": APP_ACCESS_KEY,
    "code": vkscript_code,
}

response = requests.get(VKAPI_URL + "execute", params=params)
json_data = response.json()["response"]
pprint(json_data)
print(len(json_data["items"]))

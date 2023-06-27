"""
Contains things connected with VK script.
These scripts can be used as "code" parameters
for URL /execute in VK API.
"""

from string import Template

# Gets 2500 posts using cycle, 100 posts * 25 iterations.
# 25 is maximum iterations API allows.
GET_2500_POSTS_TEMPLATE = Template(
    """
    var offset_global = $offset;
    var offset_cycle = 0;
    var items = [];
    var count = 0;

    var i = 0; 
    while (i != 25) { 
        var data = API.wall.get({
            "count": 100,
            "offset": offset_global + offset_cycle, 
            "domain": "$domain"
        }); 
        items = items + data["items"];
        count = data["count"];
        offset_cycle = offset_cycle + 100;
        i = i + 1; 
    }; 

    return {
    "count": count, 
    "items": items
    };
    """
)

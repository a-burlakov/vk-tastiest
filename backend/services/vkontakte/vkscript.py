"""
Contains things connected with VK script.
These scripts can be used as "code" parameters
for URL /execute in VK API.
"""

from string import Template

# Gets posts from VK domain using cycle with.
# 25 is maximum iterations API allows.
get_wall_post_template = Template(
    """
    var offset_global = $offset;
    var offset_cycle = 0;
    var items = [];
    var count = 0;

    var i = 0; 
    while (i != $execution_times) { 
        var data = API.wall.get({
            "count": $posts_per_portion,
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

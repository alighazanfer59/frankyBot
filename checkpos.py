# from in_pos import pos

# pos['btc4h'] = True
import json

from main_functions import update_dict_value
update_dict_value('pos.json', 'btc4h', False)


# Load the JSON data from the file
with open('pos.json', 'r') as f:
    json_pos = f.read()

# Convert the JSON data back to a dictionary
pos = json.loads(json_pos)

in_position = pos['btc4h']
print(in_position)
update_dict_value('qty.json', 'btc4h', 0)

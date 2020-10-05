# Abdullah Mahmood, aam2vp
# Flood Warning Systems 20-21

import json, re


file_name = "test_data.json"
with open(file_name, "r") as read_file:
    data = json.load(read_file)

transformed_data = []

# TODO: Make map patterns for the other ways its ordered OR just make it more robust
map_pattern = re.compile(r"map\[displayName:.*unit:.*value:.*]")
for reading in data:
    transformed_reading = {}

    for field in reading:
        value = reading[field]
        if isinstance(value, str) and re.match(map_pattern, value):
            unit_idx = value.index("unit:")
            value_idx = value.index("value:")
            unit_value = value[unit_idx+5:value_idx-1]
            value_value = value[value_idx+6:-1]
            try:
                value_value = float(value_value)
            except ValueError:
                pass
            transformed_reading[field] = value_value
            transformed_reading["{}_unit".format(field)] = unit_value
        else:
            transformed_reading[field] = value
        # end if
    transformed_data.append(transformed_reading)
    # end for

# end for

# # Test output
# for item in transformed_data:
#     print(item)
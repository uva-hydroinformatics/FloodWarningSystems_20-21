# Abdullah Mahmood, aam2vp
# Flood Warning Systems 20-21

import json, re, sqlite3


file_name = "test_data.json"
with open(file_name, "r") as read_file:
    data = json.load(read_file)

transformed_data = []

# map_pattern = re.compile(r"map\[displayName:.*unit:.*value:.*]")
map_pattern = re.compile(r"map\[.*:.*:.*:.*]")
for reading in data:
    transformed_reading = {}

    for field in reading:
        value = reading[field]
        
        if isinstance(value, str) and re.match(map_pattern, value):
            line_split = value[4:-1].split(":")
            len_line_split = len(line_split)

            for i in range(1, len_line_split):
                if (i == 1):
                    subfield = line_split[0]

                # Converting the subfields in fields like battery voltage, temperature, pressure, etc.
                if (i < len_line_split-1):
                    subvalue_split = line_split[i].split()
                    subvalue = " ".join(subvalue_split[:-1])
                    next_subfield = subvalue_split[-1]
                else:
                    subvalue = line_split[i]

                if subfield != "displayName": # Skipping displayName as a field, redundant?
                    if subfield == "value":
                        subfield = field
                    else:
                        subfield = field + "_" + subfield
                    
                    try:
                        subvalue = float(subvalue)
                    except ValueError:
                        pass

                    transformed_reading[subfield] = subvalue
                # end if
                
                subfield = next_subfield
            # end for
        else:
            transformed_reading[field] = value
        # end if
    transformed_data.append(transformed_reading)
    # end for
# end for

# # Test output
# for item in transformed_data:
#     print(item)

##################################################
##################################################

# TODO: Check for all the fields that and see if they exist in the table, 
# if not, for loop and add new column. Might be faster to do try/except and check for the 
# col
# SQLite3 Connectivity
# conn = sqlite3.connect("C:/Users/Shoikut/OneDrive/Documents/2020 Fall/SYS 4053/TestDataDB.db")
# c = conn.cursor()

# table = "test"
# row1 = transformed_data[0]
# # c.execute("INSERT INTO {}".format(table,))
# c.execute("INSERT INTO test(battery_voltage_unit, battery_voltage) VALUES ('mV', 2479);")

# conn.commit()
# conn.close()

##################################################
##################################################

# print("done!")
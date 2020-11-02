import json, re


def parse_data(data):
    """ Parse and transform the incoming JSON data

    Parameters
    ----------
    data : JSON formatted str
        JSON formatted list data

    Returns
    -------
    returns dictionary of transformed records (can change to return JSON in future with dump/s)
    """
    data = json.loads(data)
    transformed_data = []

    subfield_pattern = re.compile(r"map\[.*:.*:.*:.*]")
    for reading in data:
        transformed_reading = {}

        for field in reading:
            value = reading[field]

            if isinstance(value, str) and re.match(subfield_pattern, value):
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

                    if subfield != "displayName": # Skipping displayName as a field, redundant value?
                        if subfield == "value":
                            subfield = field
                        else:
                            subfield = field + "_" + subfield
                        
                        try:
                            subvalue = float(subvalue)
                        except ValueError:
                            pass

                        transformed_reading[subfield] = subvalue
                    
                    subfield = next_subfield
            else:
                transformed_reading[field] = value

        transformed_data.append(transformed_reading)

    return transformed_data    

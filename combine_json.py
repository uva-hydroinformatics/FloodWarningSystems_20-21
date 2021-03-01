from datetime import datetime, date, timezone, timedelta
import json
from glob import glob
import os


seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
strfmt = {'year_month':'%Y-%m', 'day':"%d", 'time': '%H_%M_%S'}

def convert_to_seconds(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]]

def combine_json(device, last='1h', start_date=None, end_date=None, file=None):
    """ combine json file readings for specific device 

    Parameters
    ----------
    device : str
        device ID 

    time : str (optional)
        Duration on which we want to get the data (default 1h). 
        Past 30s for the last 30 seconds, 1h for the last hour, 
        2d for the last 48 hours, etc
    
    file : str (optional)
        optional parameter to write combined json to file. Leave
        blank to not write to file

    Returns
    -------
    returns the JSON formated list sensor readings  

    NOTE
    ----
    -   units return as ASCII characters, regular print(combine_json(stuff)) will throw UnicodeEncodeError, 
        instead use print(json.dumps(combine_json(stuff)), be sure to 'import json' first
    """
    # TODO: check if device/directory exists
    
    next = True
    readings = []
    reading_jsons = []

    time_now = datetime.now(timezone.utc)
    # time_now = datetime(year=2021, month=1, day=20, hour=23)
    time_last = time_now - timedelta(seconds=convert_to_seconds(last))
    temp_day = time_now

    if start_date is not None:
        time_last = datetime.fromisoformat(start_date)
    if end_date is not None:
        temp_day = datetime.fromisoformat(end_date)

    # starts with most recent reading and works backwards to find last reading
    while(next):
        dir_readings = glob("SensorData/"+device+"/"+temp_day.strftime('%Y-%m')+"/" + temp_day.strftime('%d' + "/*"))

        if temp_day.date() == time_last.date(): 
            for i, r in enumerate(dir_readings):
                time_str = r[-13:-5]
                temp_time = datetime.strptime(time_str, '%H_%M_%S').time()
                if temp_time >= time_last.time():
                    reading_jsons.extend(dir_readings[i:])
                    break
            next = False
        else:
            reading_jsons.extend(dir_readings)

        temp_day -= timedelta(days=1)

    # print(reading_jsons)

    for reading in reading_jsons:
        with open(reading, 'r') as f:
            json_file = json.load(f)
            readings.append(json_file)
    
    # print(json.dumps(readings, indent=4))

    if file is not None:
        with open(file, 'w') as f:
            json.dump(readings, f, indent=4)
    return readings

if __name__ == "__main__":
    combine1 = combine_json('dl-atm41_5245')  # last hour of readings for device 
    combine2 = combine_json('dl-atm41_5245', '2h')  # last 2 hours of readings for device, no json file created
    combine3 = combine_json('dl-atm41_5245', '3h', file='combined.json')  # last 3 hours of readings for device, json file created

    print(json.dumps(combine3, indent=4))

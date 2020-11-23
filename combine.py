import http_get, payload_parser, update_db
import json

# see http_get for full documentation 
"""
get_data() has 2 parameters
the first is required: device type 'pressure' or 'weather'
the second is optional: time '3h', '4d', default if not specified is '1hr'
""" 

pressure_data_1h = http_get.get_data('pressure')  # returns 1 hour of data from pressure sensor
pressure_data_3d = http_get.get_data('pressure', '3d')  # returns 3 days of of data from pressure sensor
weather_data_2h = http_get.get_data('weather', '2h')  # returns 2 hours of data from pressure sensor

# TODO: new/updated payload parser to work for weather data
# NOTE: current payload parser will still process weather data without throwing
#       an error, it just fails to process a few fields
transformed_pressure_data = payload_parser.parse_data(pressure_data_1h)
transformed_weather_data = payload_parser.parse_data(weather_data_2h)


"""
due to the measurement units in the weather response, running just print(weather_data_2h)
will produce UnicodeEncodeError, so wrap in json.dumps(weather_data_2h) first before printing
* not needed for pressure data
"""
print("Pressure Data")  # NOTE: can print regularly
print("raw json: ", pressure_data_1h)
print("transformed: ", transformed_pressure_data)
update_db.upload_pressure(transformed_pressure_data)

print("\nWeather Data")
print("raw json: ", json.dumps(weather_data_2h))
print("transformed: ", json.dumps(transformed_weather_data))


print("done")

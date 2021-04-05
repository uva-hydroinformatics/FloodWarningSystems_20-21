import http_get, payload_parser, upload, get_from_db
import json
from datetime import datetime, date, timezone, timedelta


# see http_get for full documentation 
"""
get_data() has 2 parameters
the first is required: device type 'pressure' or 'weather'
the second is optional: time '3h', '4d', default if not specified is '1hr'
""" 

##### Current Commands
# device_list = [
#         'dl-pr-26_5100',
#         'dl-atm41_5245',
#         'dl-mbx_5248',
#         'dl-mbx_5249'
#     ]

###
# print('Downloading data for the sensors from TTN...')
# pressure_data = http_get.get_data('dl-pr-26_5100', '3d')
# weather_data = http_get.get_data('dl-atm41_5245', '3d')
# ultrasonic1_data = http_get.get_data('dl-mbx_5248', '3d')
# ultrasonic2_data = http_get.get_data('dl-mbx_5249', '3d')

# print('Transforming sensor data payload...')
# transformed_pressure_data = payload_parser.parse_data(pressure_data)
# transformed_weather_data = payload_parser.parse_data(weather_data)
# transformed_ultrasonic1_data = payload_parser.parse_data(ultrasonic1_data)
# transformed_ultrasonic2_data = payload_parser.parse_data(ultrasonic2_data)
###

# print('Uploading sensor data to update database...')
# upload.update_db(device='dl-pr-26_5100', data=transformed_pressure_data, ssh_connection=True)
# upload.update_db(device='dl-atm41_5245', data=transformed_weather_data, ssh_connection=True)
# upload.update_db(device='dl-mbx_5248', data=transformed_ultrasonic1_data, ssh_connection=True)
# upload.update_db(device='dl-mbx_5249', data=transformed_ultrasonic2_data, ssh_connection=True)
# print('Database update finished!')

# To download EVERYTHING from S3, use get_from_S3.py

print('Downloading data for the sensors from DB...')
# pressure_data = get_from_db.db_read('dl-pr-26_5100', start_date='2020-12-01', end_date='2021-03-31')
# weather_data = get_from_db.db_read('dl-atm41_5245', start_date='2020-12-01', end_date='2021-03-31')
ultrasonic1_data = get_from_db.db_read('dl-mbx_5248', start_date='2020-12-01', end_date='2021-03-31')
# ultrasonic2_data = get_from_db.db_read('dl-mbx_5249', start_date='2020-12-01', end_date='2021-03-31')

sensor_data_file = 'testing.json'
with open(sensor_data_file, 'w') as f:
    json.dump(ultrasonic1_data, f, indent=4)


##### Old commands/examples, will clean up soon
# pressure_data_1h = http_get.get_data('pressure')  # returns 1 hour of data from pressure sensor
# pressure_data_3d = http_get.get_data('pressure', '3d')  # returns 3 days of of data from pressure sensor
# weather_data_2h = http_get.get_data('weather', '2h')  # returns 2 hours of data from pressure sensor

# transformed_pressure_data = payload_parser.parse_data(pressure_data_1h)
# transformed_weather_data = payload_parser.parse_data(weather_data_2h)

# """
# due to the measurement units in the weather response, running just print(weather_data_2h)
# will produce UnicodeEncodeError, so wrap in json.dumps(weather_data_2h) first before printing
# * not needed for pressure data
# """
# print("Pressure Data")  # NOTE: can print regularly
# print("raw json: ", pressure_data_1h)
# print("transformed: ", transformed_pressure_data)
# update_db.upload_pressure(transformed_pressure_data)

# print("\nWeather Data")
# print("raw json: ", json.dumps(weather_data_2h))
# print("transformed: ", json.dumps(transformed_weather_data))

# print("done")


##### Upload backup data from S3 to new/clean Database (now deprecated)
# start_date = '2020-12-15'
# end_date = '2021-03-15'

# while start_date <= end_date:
#     next_day = datetime.fromisoformat(start_date) + timedelta(days=1)
#     next_day = datetime.strftime(next_day, '%Y-%m-%d')
#     upload.upload_backup_to_db(device='dl-pr-26_5100', start_date=start_date, end_date=next_day)
#     upload.upload_backup_to_db(device='dl-atm41_5245', start_date=start_date, end_date=next_day)
#     upload.upload_backup_to_db(device='dl-mbx_5248', start_date=start_date, end_date=next_day)
#     upload.upload_backup_to_db(device='dl-mbx_5249', start_date=start_date, end_date=next_day)
#     print("Date {} completed...".format(start_date))
#     start_date = next_day

# print("Finished uploading backup data to the database!")


##### Testing download from S3 and upload backup to db (get_from_s3 + upload) (now deprecated)
# device_list = [
#         'dl-pr-26_5100',
#         'dl-atm41_5245',
#         'dl-mbx_5248',
#         'dl-mbx_5249'
#     ]

# for device in device_list:
#     sensor_data_file = '{}.json'.format(device)
#     with open(sensor_data_file) as f:
#         sensor_data = json.load(f)
#     upload.upload_backup_to_db(device, data=sensor_data) # now deprecated

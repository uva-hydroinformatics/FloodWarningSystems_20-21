from datetime import datetime, date, timezone, timedelta
from queue import Queue
from combine_json import combine_json
import os, boto3


##### USE CASE EXAMPLES:
# - For returning a json list of readings for a device:
#       sensor_readings = combined_readings('dl-pr-26_5100')
# - For returning a json list of readings from a certain date (Feb 1, 2021) til now:
#       sensor_readings = combined_readings('dl-pr-26_5100', start_date='2021-02-01')
# - For returning a json list of readings from a certain date (Feb 1, 2021) to another date (Feb 8, 2021):
#       sensor_readings = combined_readings('dl-pr-26_5100', start_date='2021-02-01', end_date='2021-02-08)
# - For creating a local json file of readings (can combine with timerange arguments as well):
#       combined_readings('dl-pr-26_5100', file='pressure_sensor_readings.json')
# - For assigning a json list AND creating a local file
#       sensor_readings = combined_readings('dl-pr-26_5100', file='pressure_sensor_readings.json')

# Note: start_date and end_date are going to be read as UTC timezone (EST is UTC-5, EDT is UTC-4)
# start_date overrides "last" parameter
# by default, return readings for past day since midnight UTC
def download_from_S3(device, last=None, start_date=None, end_date=None):

    bucket_name = 'floodwarningsystem'
    
    # Convert start_date into type datetime
    if start_date is None:
        datetime_start_date = datetime.now(timezone.utc)
        if last is not None:
            number_of_days = int(last[:-1])
            datetime_start_date -= timedelta(days=number_of_days)
        start_date = datetime.strftime(datetime_start_date, '%Y-%m-%d')
    datetime_start_date = datetime.fromisoformat(start_date)

    # Convert end_date into type datetime
    if end_date is None:
        datetime_end_date = datetime.now(timezone.utc)
        end_date = datetime.strftime(datetime_end_date, '%Y-%m-%d')
    datetime_end_date = datetime.fromisoformat(end_date)
    
    # Create queue for parallel S3 downloads for each day's readings
    object_prefix = 'SensorData/{}/'.format(device)
    object_prefix_queue = Queue()

    current_date = datetime_start_date
    
    while current_date <= datetime_end_date:
        current_date_prefix = datetime.strftime(current_date, '%Y-%m/%d')
        current_date_object_prefix = object_prefix + current_date_prefix
        object_prefix_queue.put(current_date_object_prefix)
        current_date += timedelta(days=1)
    
    # s3 = boto3.resource('s3', aws_access_key_id = 'ENTER YOUR ACCESS KEY', 
    #                           aws_secret_access_key= 'ENTER YOUR SECRET KEY')
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(bucket_name)

    while not object_prefix_queue.empty():

        reading_object_prefix = object_prefix_queue.get()
        print('Downloading readings from \'{}\' directory...'.format(reading_object_prefix))

        for s3_object in s3_bucket.objects.filter(Prefix=reading_object_prefix):
            path, filename = os.path.split(s3_object.key)
            if not os.path.exists(path):
                os.makedirs(path)

            s3_bucket.download_file(s3_object.key, s3_object.key)
    
    print('Finished downloading selected readings!')


def combined_readings(device, last='1d', start_date=None, end_date=None, file=''):
    download_from_S3(device, last=last, start_date=start_date, end_date=end_date)
    return combine_json(device, last=last, start_date=start_date, end_date=end_date, file=file)

##### TEST CASES
# download_from_S3('dl-pr-26_5100', start_date='2021-02-23', end_date='2021-03-01')
# download_from_S3('dl-pr-26_5100', start_date='2021-02-20', end_date='2021-02-21')
# download_from_S3('dl-pr-26_5100')
# download_from_S3('dl-pr-26_5100', last='1d')
# download_from_S3('dl-pr-26_5100', last='3d', start_date='2021-02-20')

# combined_readings('dl-pr-26_5100', file='combinedpressure.json')
# print(combined_readings('dl-pr-26_5100'))
# print(combined_readings('dl-pr-26_5100', start_date='2021-01-31', end_date='2021-02-01'))
# print(combined_readings('dl-mbx_5248', start_date='2021-01-31', end_date='2021-02-01'))
# combined_readings('dl-atm41_5245', start_date='2021-01-31', end_date='2021-02-01')

from datetime import datetime, date, timezone, timedelta
from queue import Queue
import os, boto3


# Note: start_date and end_date are going to be read as UTC timezone (EST is UTC-5, EDT is UTC-4)
# start_date overrides "last" parameter
# by default, return readings for past day since midnight UTC
def download_from_S3(device, last=None, start_date=None, end_date=None):

    bucket_name = 'floodwarningsystem'
    
    if start_date is None:
        datetime_start_date = datetime.now(timezone.utc)
        if last is not None:
            number_of_days = int(last[:-1])
            datetime_start_date -= timedelta(days=number_of_days)
        start_date = datetime.strftime(datetime_start_date, '%Y-%m-%d')
    datetime_start_date = datetime.fromisoformat(start_date)

    if end_date is None:
        datetime_end_date = datetime.now(timezone.utc)
        end_date = datetime.strftime(datetime_end_date, '%Y-%m-%d')
    datetime_end_date = datetime.fromisoformat(end_date)
    
    object_prefix = 'SensorData/{}/'.format(device)
    object_prefix_queue = Queue()

    current_date = datetime_start_date
    current_date_prefix = datetime.strftime(current_date, '%Y-%m/%d')
    current_date_object_prefix = object_prefix + current_date_prefix
    object_prefix_queue.put(current_date_object_prefix)
    
    while current_date < datetime_end_date:
        current_date += timedelta(days=1)
        current_date_prefix = datetime.strftime(current_date, '%Y-%m/%d')
        current_date_object_prefix = object_prefix + current_date_prefix
        object_prefix_queue.put(current_date_object_prefix)
    

    s3 = boto3.resource('s3')
    # s3 = boto3.resource('s3', aws_access_key_id = 'ENTER YOUR ACCESS KEY', 
    #                           aws_secret_access_key= 'ENTER YOUR SECRET KEY')
    s3_bucket = s3.Bucket(bucket_name)

    while not object_prefix_queue.empty():

        reading_object_prefix = object_prefix_queue.get()
        print('Downloading readings from \'{}\' directory'.format(reading_object_prefix))

        for s3_object in s3_bucket.objects.filter(Prefix=reading_object_prefix):
            path, filename = os.path.split(s3_object.key)
            if not os.path.exists(path):
                os.makedirs(path)

            s3_bucket.download_file(s3_object.key, s3_object.key)
    
    print('Finished downloading selected readings')


# TEST
# download_from_S3('dl-pr-26_5100', start_date="2021-02-23", end_date="2021-03-01")
# download_from_S3('dl-pr-26_5100', start_date="2021-02-20")
# download_from_S3('dl-pr-26_5100')
# download_from_S3('dl-pr-26_5100', last='1d')
# download_from_S3('dl-pr-26_5100', last='3d', start_date="2021-02-20")

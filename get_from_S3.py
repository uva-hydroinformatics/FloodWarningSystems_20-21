from datetime import datetime, date, timezone, timedelta
from queue import Queue
import boto3, json, multiprocessing


# Note: start_date and end_date are going to be read as UTC timezone (EST is UTC-5, EDT is UTC-4)
# start_date overrides "last" parameter
# by default, return readings for past day since midnight UTC
def get_object_prefixes(device, last=None, start_date=None, end_date=None):
    
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
    # object_prefix = 'SensorData/{}/'.format(device)
    # object_prefix_queue = Queue()

    # current_date = datetime_start_date
    
    # while current_date <= datetime_end_date:
    #     current_date_prefix = datetime.strftime(current_date, '%Y-%m/%d')
    #     current_date_object_prefix = object_prefix + current_date_prefix
    #     object_prefix_queue.put(current_date_object_prefix)
    #     current_date += timedelta(days=1)
    
    # return object_prefix_queue

    object_prefix = 'SensorData/{}/'.format(device)
    object_prefix_list = []

    current_date = datetime_start_date
    
    while current_date <= datetime_end_date:
        current_date_prefix = datetime.strftime(current_date, '%Y-%m/%d')
        current_date_object_prefix = object_prefix + current_date_prefix
        object_prefix_list.append(current_date_object_prefix)
        current_date += timedelta(days=1)
    
    return object_prefix_list


def combined_readings(device, object_list, json_object=False):
    
    bucket_name = 'floodwarningsystem'
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(bucket_name)
    readings = []

    while not object_list.empty():

        reading_object_prefix = object_list.get()

        for s3_object in s3_bucket.objects.filter(Prefix=reading_object_prefix):
            
            file_content = s3_object.get()['Body'].read().decode('utf-8')
            json_content = json.loads(file_content)
            readings.append(json_content)
    
    if json_object is True:
        file = '{}.json'.format(device)
        if file is not None:
            with open(file, 'w') as f:
                json.dump(readings, f, indent=4)
        return readings
    else:
        readings_json = json.dumps(readings, indent=4)
        return readings_json


def get_combined_readings(device, last='1d', start_date=None, end_date=None, json_object=False):
    object_prefix_queue = get_object_prefixes(device, last=last, start_date=start_date, end_date=end_date)
    device_readings = combined_readings(device, object_prefix_queue, json_object=json_object)
    return device_readings

global s3_bucket
s3 = None
bucket_name = 'floodwarningsystem'
s3 = boto3.resource('s3')
s3_bucket = s3.Bucket(bucket_name)
global readings
readings = []

def download(job):

    print(job)
    for s3_object in s3_bucket.objects.filter(Prefix=job):
        file_content = s3_object.get()['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        readings.append(json_content)
    return readings

if __name__ == '__main__':

    device_list = [
        'dl-pr-26_5100',
        'dl-atm41_5245',
        'dl-mbx_5248',
        'dl-mbx_5249'
    ]

    start_date='2020-12-15'
    end_date='2021-03-15'

    for device in device_list:

        jobs = get_object_prefixes(device, last=None, start_date=start_date, end_date=end_date)
        pool = multiprocessing.Pool(min(multiprocessing.cpu_count(), len(jobs)))
        readings = pool.map(download, jobs)
        pool.close()
        pool.join()

        seen = set()
        readings_flattened = []
        for daily_reading in readings:
            for hourly_reading in daily_reading:
                time = hourly_reading['time']
                if time not in seen:
                    readings_flattened.append(hourly_reading)
                    seen.add(time)
        
        file = '{}.json'.format(device)
        with open(file, 'w') as f:
            json.dump(readings_flattened, f, indent=4)

##### TEST CASES
# device1 = 'dl-pr-26_5100'
# device_readings = get_combined_readings(device1, start_date='2020-12-15', end_date='2021-03-15', json_object=True)

# device1 = 'dl-atm41_5245'
# device_readings = get_combined_readings(device1, start_date='2020-12-15', end_date='2021-03-15', json_object=True)

# device1 = 'dl-mbx_5248'
# device_readings = get_combined_readings(device1, start_date='2020-12-15', end_date='2021-03-15', json_object=True)

# device1 = 'dl-mbx_5249'
# device_readings = get_combined_readings(device1, start_date='2020-12-15', end_date='2021-03-15', json_object=True)

# device = 'dl-pr-26_5100'
# run(device, start_date='2021-03-10', end_date='2021-03-15')

### For local testing purposes, uncomment to print out to a local file
# file_name = 'test_data_{}.json'.format(device1)
# with open(file_name, 'w') as f:
#     json.dump(device_readings, '', indent=4)
#     f.write("\n")

# device_readings = get_combined_readings(device1, start_date='2021-02-14', end_date='2021-02-14')
# test = json.dumps(device_readings, indent=4)
# print(test)

### For testing API Query Strings
# device=dl-pr-26_5100&start_date=2021-03-01&end_date=2021-03-01 <- ~8-9 seconds to run
# device=dl-atm41_5245&start_date=2021-03-01&end_date=2021-03-01 <- ~8-9 seconds to run

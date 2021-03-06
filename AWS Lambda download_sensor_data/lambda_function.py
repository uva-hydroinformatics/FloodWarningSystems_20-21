import json
from get_from_S3 import get_combined_readings


def lambda_handler(event, context):
    
    # Default Parameters
    device = None
    last = '1d'
    start_date = None
    end_date = None
    
    # Test Parameters
    device = 'dl-pr-26_5100'
    last = '1d'
    start_date = '2021-01-31'
    end_date = '2021-01-31'
    
    if device is not None:
        sensor_readings = get_combined_readings(device, last=last, start_date=start_date, end_date=end_date)
        
        return {
            'statusCode': 200,
            'body': json.dumps(sensor_readings)
        }
    elif device is None:
        return {
            'statusCode': 200,
            'body': 'No device ID entered'
        }
    elif start_date is None and end_date is not None:
        return {
            'statusCode': 200,
            'body': 'Invalid start_date and end_date'
        }

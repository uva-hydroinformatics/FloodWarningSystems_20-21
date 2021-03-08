import json
from get_from_S3 import get_combined_readings


def lambda_handler(event, context):
    
    # Default Parameters
    device = None
    last = '1d'
    start_date = None
    end_date = None
    
    # From queryStringParameters
    query_parameters = event['queryStringParameters']
    device = query_parameters['device']
    if 'last' in query_parameters:
        last = query_parameters['last']
    if 'start_date' in query_parameters:
        start_date = query_parameters['start_date']
    if 'end_date' in query_parameters:
        end_date = query_parameters['end_date']
    
    # # Test Parameters
    # device = 'dl-pr-26_5100'
    # last = '1d'
    # start_date = '2021-01-31'
    # end_date = '2021-01-31'
    
    if start_date is None and end_date is not None:
        return {
            'statusCode': 200,
            'body': 'Invalid values for parameters start_date and end_date'
        }
    # else:
    #     return {
    #         'statusCode': 200,
    #         'body': 'Invalid parameters, please check input and try again'
    #     }
    
    sensor_readings = get_combined_readings(device, last=last, start_date=start_date, end_date=end_date)
    return {
            'statusCode': 200,
            'body': json.dump(sensor_readings)
        }

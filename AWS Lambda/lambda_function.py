import json, http_get, payload_parser

def lambda_handler(event, context):
    
    data = http_get.get_data()
    transformed_data = payload_parser.parse_data(data)
    
    for reading in transformed_data:
        print(reading)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(transformed_data)
    }

import http_get, payload_parser, upload
import json


def lambda_handler(event, context):

    # latest readings period in hours (h), minutes (m), or seconds (s)
    reading_period = '90m'

    device_list = [
        'dl-pr-26_5100',
        'dl-atm41_5245',
        'dl-mbx_5248',
        'dl-mbx_5249'
    ]
    
    for device in device_list:
        device_payload = http_get.get_data(device, reading_period)
        transformed_sensor_data = payload_parser.parse_data(device_payload)
        try:
            upload.update_db(device=device, data=transformed_sensor_data, ssh_connection=True)
        except:
            print("Could not update database for device: {}".format(device))
        upload.json_to_s3(transformed_sensor_data)
        

    return {
        'statusCode': 200,
        'body': ''
    }

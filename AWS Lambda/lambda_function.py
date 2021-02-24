import http_get, payload_parser, upload
import json


def lambda_handler(event, context):

    # latest readings period in hours (h), minutes (m), or seconds (s)
    reading_period = '90m'

    print("Pressure Start")
    pressure_data_1h = http_get.get_data('pressure', reading_period)  # returns data from pressure sensor
    transformed_pressure_data = payload_parser.parse_data(pressure_data_1h)
    upload.json_to_s3(transformed_pressure_data)
    upload.update_db(transformed_pressure_data)
    print("Pressure Done")
    
    print("Weather Start")
    weather_data_1h = http_get.get_data('weather', reading_period)  # returns data from weather sensor
    transformed_weather_data = payload_parser.parse_data(weather_data_1h)
    upload.json_to_s3(transformed_weather_data)
    upload.update_db(transformed_weather_data)
    print("Weather Done")
    
    print("Ultrasonic Start")
    ultrasonic1_data_1h = http_get.get_data('ultrasonic1', reading_period)  # returns data from ultrasonic sensor 1 (bradywine bridge)
    transformed_ultrasonic1_data = payload_parser.parse_data(ultrasonic1_data_1h)
    upload.json_to_s3(transformed_ultrasonic1_data)
    upload.update_db(transformed_ultrasonic1_data)
    
    ultrasonic2_data_1h = http_get.get_data('ultrasonic2', reading_period)  # returns data from ultrasonic sensor 2 (greenbrier bridge)
    transformed_ultrasonic2_data = payload_parser.parse_data(ultrasonic2_data_1h)
    upload.json_to_s3(transformed_ultrasonic2_data)
    upload.update_db(transformed_ultrasonic2_data)
    print("Ultrasonic Done")

    return {
        'statusCode': 200,
        'body': ''
    }

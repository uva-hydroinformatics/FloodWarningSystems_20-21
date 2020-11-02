import http_get, payload_parser

data = http_get.get_data()
transformed_data = payload_parser.parse_data(data)

for reading in transformed_data:
    print(reading)

import requests
import json
from requests.exceptions import HTTPError

url = 'https://ruchir_dl-pr-26_5100.data.thethingsnetwork.org/api/v2/query'
key = ''  # add key
headers = {
    'Accept': 'application/json',
    'Authorization': 'key ' + key,
}


response = requests.get(url, headers=headers)
response_json = []

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if (response.status_code == 200):
        response_text = response.text  # 
        response_json = json.loads(response_text)  # list of dicts
    
        print(json.dumps(response_json, indent = 2))  # printing json.loads for nice formatting
        # NOTE: Temperature unit is °C but json.dump converts to ASCII \u00b0C

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')
import requests
import json
from requests.exceptions import HTTPError
from http_config import *


device_urls = {
    'pressure' : pressure_url,
    'ultrasonic1' : ultrasonic1_url,
    'ultrasonic2' : ultrasonic2_url,
    'weather' : weather_url,
}

device_keys = {
    'pressure'  : pressure_key,
    'ultrasonic1' : ultrasonic1_key,
    'ultrasonic2' : ultrasonic2_key,
    'weather' :  weather_key,
}


def get_headers(key):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'key ' + key,
    }
    return headers


def get_devices_ids_by_type(dev_type):
    """ Gets the JSON list of devices for which data has been stored
    Parameters
    ----------
    device type 'pressure' or 'weather'

    Returns
    -------
    list of devices ids of all devices accross types

    TODO
    ----
    clean output currently returns with brackets and quotes

    """ 
    url = device_urls[dev_type] + 'devices'
    headers = get_headers(device_keys[dev_type])
    return get_response(url, headers)


def get_all_device_ids():
    """ Gets the JSON list of devices for which data has been stored
    Parameters
    ----------
    None

    Returns
    -------
    list of devices ids of all devices accross types

    TODO
    ----
    clean output currently returns with brackets and quotes

    """ 
    device_ids = []
    for dev_type, url_base in device_urls.items():
        url = url_base + 'devices'
        headers = get_headers(device_keys[dev_type])
        device_ids.append(get_response(url, headers))

    return device_ids

def get_data(dev_type, time='1h'):
    """ Query the data for all devices

    Parameters
    ----------
    time : str
        Duration on which we want to get the data (default 1h). 
        Pass 30s for the last 30 seconds, 1h for the last hour, 
        2d for the last 48 hours, etc

    Returns
    -------
    returns the JSON formated list data for all devices 

    NOTE
    ----
    -   units return as ASCII characters, regular print(get_data(stuff)) will throw UnicodeEncodeError, 
        instead use print(json.dumps(get_data(stuff)), be sure to 'import json' first
    """

    url = device_urls[dev_type] + 'query'
    headers = get_headers(device_keys[dev_type])
    params = {'last':time}

    return get_response(url, headers , params)

def get_response(url, headers={}, params={}):   
    """
    Parameters
    ----------
    url : str
        URL to TTN endpoint to query

    params : dict
        parameters for url

    Returns
    -------
    JSON response for url if successfull else None


    Raises
    ------
    HTTPError:
        If HTTP error occurs on TNN server side

    NOTE
    ----
    -   units return as ASCII characters, regular print(get_response(stuff)) will throw UnicodeEncodeError, 
        instead use print(json.dumps(get_response(stuff)), be sure to 'import json' first 
    """ 
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        if (response.status_code == 200):
            response_json = response.text  # list of dicts
        
            # print(json.dumps(response_json, indent = 2))  # printing json.loads for nice formatting
            return response_json
        else:
            return None

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


if __name__ == "__main__":
    print(json.dumps(get_data('weather')))
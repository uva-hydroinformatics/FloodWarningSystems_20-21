# import requests
import requests
import json
from requests.exceptions import HTTPError

# TODO: parameterize for sepcific device
# DONE: Parameterize time range queried
# DONE: function for most recent measurment
# DONE: modularize into functions 

url_base = 'https://ruchir_dl-pr-26_5100.data.thethingsnetwork.org/api/v2/'
key = 'ttn-account-v2.cYFVGyYQf-6sbt6WNsoi42RDgD4CCECPF5ElP3Ztrks'  # add key
headers = {
    'Accept': 'application/json',
    'Authorization': 'key ' + key,
}

def get_devices():
    """ Gets the JSON list of devices for which data has been stored
    Parameters
    ----------
    None

    Returns
    -------
    list of devices ids

    """ 
    url = url_base + 'devices'
    return get_response(url)

def get_data(time='1h'):
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
    """

    url = url_base + 'query'
    params = {'last':time}
    return get_response(url, params)


def get_response(url, params={}):   
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
    """ 
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        if (response.status_code == 200):
            response_json = response.text  # list of dicts
        
            # print(json.dumps(response_json, indent = 2))  # printing json.loads for nice formatting
            # NOTE: Temperature unit is °C but json.dump converts to ASCII \u00b0C
            return response_json
        else:
            return None

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


if __name__ == "__main__":
    get_data('2h')
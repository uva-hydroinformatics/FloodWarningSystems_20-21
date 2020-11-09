import requests

device_urls = {
    # TODO: Get the integration url and fix the URLs below for proper HTTP calls for downlink
    'pressure': 'https://bad17136f2a19347c38adc89286ada12.m.pipedream.net',
    'weather': 'https://bad17136f2a19347c38adc89286ada12.m.pipedream.net'
    # 'pressure' : 'https://ruchir_dl-pr-26_5100.data.thethingsnetwork.org/',
    # 'weather' : 'https://ruchir_dl-atm-41_5245.data.thethingsnetwork.org/'
    # 'pressure': 'https://ruchir_dl-pr-26_5100.data.thethingsnetwork.org/api/v2/devices/=ttn-account-v2._mPeoCyPkrWW0v5IQZXCOIkHMItGVAM3oQ2saSr_0-4'
}

sampling_rate = {
    # Sampling rate in seconds, encoded in hex
    # 60: '0002003CF5A1',
    # 300: '0002012CA9A1',
    # 900: '0002038477A1'

    # Sampling rate in seconds, encoded in base64 from hex
    60: 'AAIAPPWh==',
    300: 'AAIBLKmh==',
    900: 'AAIDhHeh=='
}

# TODO: Change function definition to take in device ID instead
def update_sampling_period(device_url, seconds):

    message = '{{"dev_id":"{}","payload_raw":"{}"}}'.format("dl-pr26_5100",sampling_rate[60])

    downlink_command = requests.post(device_url, data=message)

    print(downlink_command.text)

update_sampling_period(device_urls['pressure'], 60)
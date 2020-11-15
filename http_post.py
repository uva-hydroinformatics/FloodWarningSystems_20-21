import requests


device_ids = {
    'pressure': 'dl-pr-26_5100',
    'weather': ''
}

# TODO: Cleanup device urls (ask Abdullah for pressure device url)
device_urls = {
    'pressure': '',
    'weather': ''
}

# Command set period + save
sampling_rate = {
    # Sampling rate in seconds, encoded in hex
    # Command generated from https://htmlpreview.github.io/?https://github.com/decentlab/decentlab-decoders/blob/master/downlink-command-encoder.html 
    # 60: '0002003CF5A1',
    # 300: '0002012CA9A1',
    # 900: '0002038477A1'

    # Sampling rate in seconds, encoded in base64 from hex
    60: 'AAIAPPWh',
    300: 'AAIBLKmh',
    600: 'AAICWH6h',
    900: 'AAIDhHeh'
}

# TODO: Change function definition to take in device IDs instead?
def update_sampling_period(device_url, seconds):

    message = '{{"dev_id":"{}","payload_raw":"{}"}}'.format(device_ids['pressure'], sampling_rate[seconds])

    downlink_command = requests.post(device_url, data=message)

    print(downlink_command.text)

# 1 minute sampling period
# update_sampling_period(device_urls['pressure'], 60)

# 5 minute sampling period
# update_sampling_period(device_urls['pressure'], 300)

# 10 minute sampling period
update_sampling_period(device_urls['pressure'], 600)

# 15 minute sampling period
# update_sampling_period(device_urls['pressure'], 900)

# FloodWarningSystems_20-21
Repository for the Flood Warning Systems 2020-2021 capstone group

## Getting Started
Clone this repo 
```
https://github.com/uva-hydroinformatics/FloodWarningSystems_20-21.git
```
Install Dependencies
```
pip install -r requirements.txt
```
Obtain local copies of `http_config.py` and `rds_config`

## Usage

### Read Sensor Data and Update Database
Read past 3 days of data from the pressure sensor
```
import http_get, payload_parser, update_db
pressure_data = http_get.get_data('pressure', '3d')  
transformed_pressure_data = payload_parser.parse_data(pressure_data)
update_db.upload_pressure(transformed_pressure_data)
```

### Update Sensor Sampling Period
Update sampling period of pressure sensor to 600 seconds
```
import http_post
http_post.update_sampling_period(downlink_urls['pressure'], 600)
```

### Download Data from S3
Download device readings over date range (requires aws access keys)
```
import downloadS3
downloadS3.download_from_S3('dl-pr-26_5100', start_date='2021-02-23', end_date='2021-03-01')
```
Download last day of device readings
```
downloadS3.download_from_S3('dl-pr-26_5100', last='1d')
```
Combine device readings into single JSON, assuming local SensorData directory already exists
```
import combine_json.py
combine_json.combine_json('dl-mbx_5248', start_date='2021-01-31', end_date='2021-02-01', file='pressuredata.json')
```

Download and Combine
```
import downloadS3
downloadS3.combined_readings('dl-pr-26_5100', start_date='2021-01-31', end_date='2021-02-01')
```
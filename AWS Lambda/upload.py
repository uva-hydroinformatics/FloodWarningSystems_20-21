import boto3, rds_config, pymysql, json


# Takes in transformed JSON data
def json_to_s3(data):
    
    if data == None:
        return None
    
    bucket_name = 'floodwarningsystem'
    s3_bucket = boto3.resource('s3').Bucket(bucket_name)
    
    for reading in data:
        time_of_reading = reading['time']
        serial_ID = reading['device_id_1']
            
        # Check if sensor folder exists
        year_month = time_of_reading[:7]
        day = time_of_reading[8:10]
        # '_' because ':' might require special handling for future applications
        time = time_of_reading[11:19].replace(':', '_') 
        reading_filename = '{}/{}/{}/{}/{}.json'.format('SensorData', serial_ID, year_month, day, time)

        if len(list(s3_bucket.objects.filter(Prefix=reading_filename))) > 0:
            continue
        else:
            s3_bucket.Object(reading_filename).put(Body=bytes(json.dumps(reading).encode('UTF-8')))


# Takes in transformed JSON data
def update_db(data):
    
    if data == None:
        return None
    
    # Config for Flood DB Cluster
    db_host = rds_config.floodDBcluster_endpoint
    db_user = rds_config.floodDBcluster_username
    db_pass = rds_config.floodDBcluster_password
    db_name = rds_config.floodDB_name
    # db_name = rds_config.testDB_name
    char_set = 'utf8mb4'
    
    # Create connection
    connection = pymysql.connect(host=db_host,
                             user=db_user,
                             password=db_pass,
                             db=db_name,
                             charset=char_set,
                             cursorclass=pymysql.cursors.DictCursor)
    
    try:
        common_values = ['battery_voltage', 'device_id', 'device_id_1', 'protocol_version', 'raw', 'time']
        for reading in data:        
            with connection.cursor() as cursor:
                time_of_reading = reading['time'][:19] # Cutting off millisecond values and offset Z for comparison simplicity
                serial_ID = reading['device_id_1']
                device_ID = reading['device_id']
                # device_type = 'pressure_sensor'
                device_battery = reading['battery_voltage']

                # TODO: Handle if serial_ID not found
                sql_SELECT_device_type = "SELECT type FROM `{}`.Devices WHERE serial_ID='{}';".format(db_name, serial_ID)
                cursor.execute(sql_SELECT_device_type)
                device_type = cursor.fetchone()
                if device_type is not None:
                    device_type = device_type['type']

                SELECT_as_iso_utc = 'DATE_FORMAT(latest_query, "%Y-%m-%dT%T")'
                sql_SELECT_device_last_queried = "SELECT {} FROM `{}`.Devices;".format(SELECT_as_iso_utc, db_name)
                cursor.execute(sql_SELECT_device_last_queried)
                last_queried = cursor.fetchone()
                if last_queried is not None:
                    last_queried = last_queried[SELECT_as_iso_utc]

                # if last_queried is None or last_queried < time_of_reading:
                if last_queried < time_of_reading:
                    sql_UPDATE_Devices = """UPDATE `{}`.Devices 
                                            SET battery = '{}', latest_query = '{}'
                                            WHERE serial_ID = '{}';""".format(db_name, device_battery, time_of_reading, serial_ID)
                    cursor.execute(sql_UPDATE_Devices)

                    for value in reading:
                        if value not in common_values and value[-5:] != "_unit":
                            variable_ID = "{}_{}".format(device_type, value)
                            sql_INSERT_Values = """INSERT INTO {}.`Values` (`datetime`, `serial_ID`, `variable_ID`, `value`) 
                                                    VALUES ('{}', '{}', '{}', '{}');
                                                """.format(db_name, time_of_reading, serial_ID, variable_ID, reading[value])
                            cursor.execute(sql_INSERT_Values)

            connection.commit()

    except Exception as e:
        print("Exception occurred: {}".format(e))

    finally:
        connection.close()

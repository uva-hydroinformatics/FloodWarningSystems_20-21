import boto3, rds_config, pymysql, json
from sshtunnel import SSHTunnelForwarder


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


# Upload backup data from S3 to new/clean database on EC2 instance
def update_db(device, data=None, start_date=None, end_date=None, is_backup=False, ssh_connection=False):
    
    device_data = data
    
    if ssh_connection == True:
        SSH_host = rds_config.floodDBcluster_endpoint
        SSH_user = rds_config.SSH_user
        SSH_password = rds_config.SSH_password
        SSH_private_key = rds_config.SSH_private_key

        with SSHTunnelForwarder(
            (SSH_host, 22),
            ssh_username=SSH_user,
            ssh_password=SSH_password,
            ssh_pkey=SSH_private_key,
            remote_bind_address=('127.0.0.1', 3306)) as server:
                db_command_runner(device_data, SSH_server=server)
                
    else:
        db_command_runner(device_data)
    
    print("Finished uploading data for device: {}".format(device))


# Takes in transformed JSON data
def db_command_runner(data, SSH_server=None):
    
    if data == None:
        return None
    
    # Config for Flood DB Cluster
    db_host = rds_config.floodDBcluster_endpoint
    db_user = rds_config.floodDBcluster_username
    db_pass = rds_config.floodDBcluster_password
    db_name = rds_config.floodDB_name
    char_set = 'utf8mb4'

    # Create connection
    if SSH_server is not None:
        connection = pymysql.connect(host='127.0.0.1',
                                user=db_user,
                                password=db_pass,
                                port=SSH_server.local_bind_port,
                                db=db_name,
                                charset=char_set,
                                cursorclass=pymysql.cursors.DictCursor)
    else:
        connection = pymysql.connect(host=db_host,
                                user=db_user,
                                password=db_pass,
                                db=db_name,
                                charset=char_set,
                                cursorclass=pymysql.cursors.DictCursor)
    
    try:
        common_values = ['device_id', 'device_id_1', 'protocol_version', 'raw', 'time']
        last_queried = None
        last_record_battery = None
        last_record_time = None
        device_data_to_INSERT = []
        sql_INSERT_Values = """INSERT INTO {}.`Values` (`datetime`, `serial_ID`, `variable_ID`, `value`) 
                                                    VALUES (%s, %s, %s, %s)""".format(db_name)
        
        # Dict to check for special cases (e.g. ultrasonic sensor 0 valid readings -> distance value change to null)
        # Key: device (by serial ID) with special case
        # Value: List (special case variable, special case value, variable to update, updated variable value, variable to update...)
        # Can be modified in future to include more variables to check by making a list of lists instead of single list
        # Can also read this in from separate file (of which can be easily modified by users)
        variable_special_cases = {
            'dl-mbx_5248' : ['number_of_valid_samples', 0, 'distance', None],
            'dl-mbx_5249' : ['number_of_valid_samples', 0, 'distance', None]
        }
        
        with connection.cursor() as cursor:
            for reading in data:
                time_of_reading = reading['time'][:19] # Cutting off millisecond values and offset Z for comparison simplicity
                serial_ID = reading['device_id_1']
                device_ID = reading['device_id']
                device_battery = reading['battery_voltage']

                # TODO: Handle if null values found
                # Assumes if device_id value is null, the other values are null -> skip reading
                if device_ID is None:
                    continue

                # Get datetime when device was last updated
                if last_queried is None:
                    SELECT_as_iso_utc = 'DATE_FORMAT(latest_query, "%Y-%m-%dT%T")'
                    sql_SELECT_device_last_queried = "SELECT {} FROM `{}`.Devices WHERE serial_ID='{}';".format(SELECT_as_iso_utc, db_name, serial_ID)
                    cursor.execute(sql_SELECT_device_last_queried)
                    last_queried_command = cursor.fetchone()
                    last_queried = last_queried_command[SELECT_as_iso_utc]

                if last_queried is not None and last_queried >= time_of_reading:
                    continue
                
                # TODO: Handle if serial_ID not found
                sql_SELECT_device_type = "SELECT type FROM `{}`.Devices WHERE serial_ID='{}';".format(db_name, serial_ID)
                cursor.execute(sql_SELECT_device_type)
                device_type = cursor.fetchone()
                if device_type is not None:
                    device_type = device_type['type']
                
                if last_queried < time_of_reading:
                    # Check and handle for special cases first (modifies reading for next step)
                    if serial_ID in variable_special_cases:
                        variable_to_check = variable_special_cases[serial_ID][0]
                        value_to_check = variable_special_cases[serial_ID][1]
                        if reading[variable_to_check] == value_to_check:
                            list_to_modify = variable_special_cases[serial_ID][2:]
                            while len(list_to_modify) >= 2:
                                variable_to_modify = list_to_modify.pop(0)
                                variable_new_value = list_to_modify.pop(0)
                                reading[variable_to_modify] = variable_new_value

                    for value in reading:
                        if value not in common_values and value[-5:] != "_unit":
                            variable_ID = "{}_{}".format(device_type, value)
                            reading_value = reading[value]
                            data_tuple = (time_of_reading, serial_ID, variable_ID, reading_value) # row in table Values
                            device_data_to_INSERT.append(data_tuple)
                            last_record_battery = device_battery
                            last_record_time = time_of_reading

            if last_record_time is not None:
                cursor.executemany(sql_INSERT_Values, device_data_to_INSERT) 
                
                sql_UPDATE_Devices = """UPDATE `{}`.Devices 
                                        SET battery = '{}', latest_query = '{}'
                                        WHERE serial_ID = '{}';""".format(db_name, last_record_battery, last_record_time, serial_ID)
                cursor.execute(sql_UPDATE_Devices)

        connection.commit()

    except Exception as e:
        print("Exception occurred: {}".format(e))

    finally:
        connection.close()

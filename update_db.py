import rds_config, pymysql


# Config for Flood DB Cluster
db_host = rds_config.floodDBcluster_endpoint
db_user = rds_config.floodDBcluster_username
db_pass = rds_config.floodDBcluster_password
# db_name = rds_config.floodDB_name
db_name = rds_config.testDB_name
char_set = 'utf8mb4'

# TODO: Finish function to create tables if they don't exist in db and fill in devices/variables tables
def initialize():
    pass

# TODO: Finish function to upload transformed pressure sensor data (for loops through all data)
def upload_pressure(data):
    # Create connection
    connection = pymysql.connect(host=db_host,
                             user=db_user,
                             password=db_pass,
                             db=db_name,
                             charset=char_set,
                             cursorclass=pymysql.cursors.DictCursor)
    
    try:
        
        for reading in data:        
            with connection.cursor() as cursor:

                datetime = reading['time']
                serial_id = reading['device_id_1']
                device_id = reading['device_id']
                device_type = 'pressure sensor'
                device_battery = reading['battery_voltage']

                Values_list = ['battery_voltage', 'pressure', 'protocol_version', 'temperature', 'time']

                # Should inserting devices only be reserved for creation upon db formation?
                sql_INSERT_Devices = """INSERT INTO {}.`Devices` VALUES ('{}', '{}', '{}', {}, '{}')
                                            ON DUPLICATE KEY UPDATE battery = {}, latest_query = '{}';""".format(db_name, serial_id, device_id, device_type, device_battery, datetime, device_battery, datetime)
                cursor.execute(sql_INSERT_Devices)

                for value in Values_list:
                    
                    sql_INSERT_Values = """INSERT INTO {}.`Values` (`datetime`, `serial_ID`, `variable_ID`, `value`) 
                                            VALUES ('{}', '{}', '{}', '{}');
                                        """.format(db_name, datetime, serial_id, 'placeholder variable_ID', reading[value])
                    cursor.execute(sql_INSERT_Values)

                # # Should this be reserved for creation upon db formation?
                # sql_INSERT_Variables = ""
                # cursor.execute(sql_INSERT_Variables)

                
            connection.commit()

    except Exception as e:
        print("Exception occurred: {}".format(e))

    finally:
        connection.close()

# TODO: Finish function to upload transformed weather sensor data
def upload_weather(data):
    pass

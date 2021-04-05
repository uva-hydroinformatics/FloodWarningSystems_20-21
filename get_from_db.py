import rds_config, pymysql, json
import pandas as pd
from datetime import datetime, date, timezone, timedelta
from sshtunnel import SSHTunnelForwarder


# Config for SSH Tunnel
SSH_host = rds_config.floodDBcluster_endpoint
SSH_user = rds_config.SSH_user
SSH_password = rds_config.SSH_password
SSH_private_key = rds_config.SSH_private_key

# Config for Flood DB Cluster
db_host = rds_config.floodDBcluster_endpoint
db_user = rds_config.floodDBcluster_username
db_pass = rds_config.floodDBcluster_password
db_name = rds_config.floodDB_name
char_set = 'utf8mb4'

def format_variable(var):
    var_as_list = var.split('_')
    var_part = var_as_list[2:] # assumes first 2 words in variable name are sensor type i.e. sensor_name_variable
    return "_".join([str(x) for x in var_part])

# TODO: make 'last' parameter work for hour and week i.e '2h' or '3w'
# Now returns payload as JSON (previously was JSON formatted string)
def db_read(device, last='1d', start_date=None, end_date=None):

    # Convert start_date into type datetime
    if start_date is None:
        datetime_start_date = datetime.now(timezone.utc)
        if last is not None:
            number_of_days = int(last[:-1])
            datetime_start_date -= timedelta(days=number_of_days)
        start_date = datetime.strftime(datetime_start_date, '%Y-%m-%d')
    datetime_start_date = datetime.fromisoformat(start_date)

    # Convert end_date into type datetime
    if end_date is None:
        datetime_end_date = datetime.now(timezone.utc)
        end_date = datetime.strftime(datetime_end_date, '%Y-%m-%d')
    datetime_end_date = datetime.fromisoformat(end_date)

    # Create connection
    with SSHTunnelForwarder(
                            (SSH_host, 22),
                            ssh_username=SSH_user,
                            ssh_password=SSH_password,
                            ssh_pkey=SSH_private_key,
                            remote_bind_address=('127.0.0.1', 3306)) as SSH_server:
        
        connection = pymysql.connect(host='127.0.0.1',
                            user=db_user,
                            password=db_pass,
                            port=SSH_server.local_bind_port,
                            db=db_name,
                            charset=char_set,
                            cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `{}`.Values WHERE serial_ID='{}' AND datetime between '{}' and '{}'".format(db_name, device, str(datetime_start_date), str(datetime_end_date))
                cursor.execute(sql)
                result = cursor.fetchall()
                
                if len(result) == 0:
                    return []
                
                
                
                df = pd.DataFrame(result)
                df['variable_ID'] = df.apply(lambda x: format_variable(x['variable_ID']), axis=1)

                dates = df['datetime'].unique()
                variables = df['variable_ID'].unique()
                dfx = pd.DataFrame(index=dates, columns=variables)
                
                for index, x in df.iterrows():
                    dfx.at[x['datetime'],  x['variable_ID']] = x['value']

                dfx.reset_index(inplace=True)
                dfx.rename(columns={"index":"time"}, inplace=True)
       
 
                payload = json.loads(dfx.to_json(orient='records', date_format='iso'))
                return payload
                

        except Exception as e:
            print("Exception occured: {}".format(e))

        finally:
            connection.close()     


# print(db_read('dl-mbx_5248', start_date='2020-12-01', end_date='2021-02-01'))

# data = db_read('dl-mbx_5248', start_date='2021-03-29', end_date='2021-04-05')
# sensor_data_file = 'download_values_test.json'
# with open(sensor_data_file, 'w') as f:
#     json.dump(data, f, indent=4)
import influxdb
import requests
import pandas as pd
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

client_db = influxdb.InfluxDBClient('54.212.39.89', 8086,

                    
client_db.query("show databases;")

# def req(user,field)
a = client_db.query('SELECT * FROM "invt_bpd_b".."bpd";')

d = pd.DataFrame(a.raw['series'][0]['values'])

client_db.close()
import pandas as pd
from datetime import datetime
from influxdb import InfluxDBClient



# esult = client.query('select value from outputCurrent;')#voltage_PV #temperature#outputCurrent


class iot_db:

    def get_client(self):
        client_db = InfluxDBClient(self.host, 8086, self.name, self.passw, self.db)

        return client_db

    def get_serie(self, serie):
        client_db = self.get_client()
        result = client_db.query('select value from ' + serie + ';')  # voltage_PV #temperature#outputCurrent
        d = pd.DataFrame(result.raw['series'][0]['values'])
         #client_db.close()

        return d

    def get_last(self,serie):

        client_db = self.get_client()
        result = client_db.query('select value from ' +serie+';')#voltage_PV #temperature#outputCurrent
        d = pd.DataFrame(result.raw['series'][0]['values'])
        num = d.tail(1).iloc[0][1]
        #client_db.close()

        return float(num)

    def __init__(self, host_in, name_in, passw_in, dBin):
        self.host = host_in
        self.name = name_in
        self.passw = passw_in
        self.db = dBin



import mysql.connector
import json
from datetime import datetime

class Database:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.database = 'test'
        with open('variable.json', 'r') as f:
            self.json_data = json.load(f)
            f.close()

    def connect(self):
        try:
            mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                database=self.database)
        except mysql.connector.errors.InterfaceError as e:
            print(e)
            return None
        else:
            return mydb

    def create_table(self):
        mydb = self.connect()
        tower = 'CREATE TABLE tower_{} (' \
                'tower_id INT AUTO_INCREMENT PRIMARY KEY, ' \
                'time_stamp DATETIME,' \
                'license_id VARCHAR(10),' \
                'company VARCHAR(15),' \
                'start_date DATE,' \
                'business_type VARCHAR(10),' \
                'expire_date DATE,' \
                'power INT,' \
                'tower_type VARCHAR(10),' \
                'city VARCHAR(10),' \
                'together VARCHAR(10),' \
                'statue VARCHAR(10),' \
                'row_county VARCHAR(10),' \
                'row_city VARCHAR(10),' \
                'row_street VARCHAR(10)) ' \
                'DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci'.format(self.json_data['nccDate'])
        freq = 'CREATE TABLE freq_{} (' \
               'tower_id INT,' \
               'license_id VARCHAR(10),' \
               'frequency VARCHAR(10),' \
               'bandwidth INT,' \
               'PRIMARY KEY (tower_id, frequency),' \
               'CONSTRAINT FK_tower_id_{} FOREIGN KEY (tower_id) REFERENCES tower_{}(tower_id)) ' \
               'DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci'.format(self.json_data['nccDate'], self.json_data['nccDate'], self.json_data['nccDate'])
        try:
            mydb.cursor().execute(tower)
            mydb.cursor().execute(freq)
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def insert_tower(self, data_dict):
        mydb = self.connect()
        data = list(data_dict.values())
        fix = self.json_data['nccDate']
        cmd = \
            f"INSERT INTO tower_{fix} (time_stamp, license_id, company, start_date, business_type, expire_date, power, tower_type, city, together, statue, row_county, row_city, row_street) " \
            f"VALUES (str_to_date('{data[0]}', '%Y-%m-%d %H:%i:%s %f'), '{data[1]}', '{data[2]}',str_to_date('{data[3]}', '%Y/%m/%d'), '{data[4]}', str_to_date('{data[5]}', '%Y/%m/%d')," \
            f"{int(data[6])}, '{data[7]}', '{data[8]}', '{data[9]}', '{data[10]}', '{data[11]}', '{data[12]}', '{data[13]}')"
        try:
            mydb.cursor().execute(cmd)
            mydb.cursor().execute('COMMIT')
        except Exception as e:
            print(e)
            with open('db.err.log', 'a') as f:
                time = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %f'))
                f.write(f'{data_dict}\n')
                f.write(f'{time}:{e}\n')
                f.close()
            return False
        else:
            return True

    def insert_freq(self, data_dict, time_stamp):
        mydb = self.connect()
        data = list(data_dict.values())
        fix = self.json_data['nccDate']
        cmd = f"INSERT INTO freq_{fix} (tower_id, license_id, frequency, bandwidth) " \
            f"VALUES ((SELECT tower_id FROM tower_{fix} WHERE tower_{fix}.license_id = '{data[0]}' AND str_to_date('{time_stamp}', '%Y-%m-%d %H:%i:%s %f')), " \
            f"'{data[0]}', '{data[1]}', {int(data[2])})"
        try:
            mydb.cursor().execute(cmd)
            mydb.cursor().execute('COMMIT')
        except Exception as e:
            print(e)
            with open('db.err.log', 'a') as f:
                time = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %f'))
                f.write(f'{data_dict}\n')
                f.write(f'{time}:{e}\n')
                f.close()
            return False
        else:
            return True

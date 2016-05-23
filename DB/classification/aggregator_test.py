import datetime
import pickle
import psycopg2
import uuid
import functools



database = 'seads'
user = 'seadapi'
def aggregate_data():
        con = psycopg2.connect(database=database, user=user)
        cursor = con.cursor()
        params = {'panel': 'Panel1',
                  'id': None}
        query = "select * from data_label"
        cursor.execute(query, params)
        results = cursor.fetchall()

        query = "select * from data_raw order by time asc limit 200;"
        cursor.execute(query)
        results = cursor.fetchall()
        print(results)

aggregate_data()

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
        labels = cursor.fetchall()

        query = "select * from data_raw order by time desc limit 100;"
        cursor.execute(query)
        dataraw = cursor.fetchall()
        
        result = []
        for datum in dataraw:
                for label in labels:
                        #datum[3] is the timestamp of the datum
                        #label 1, 2 are the limits of the label
                        #label 3 is the label
                        print("" + str(datum[3]) + " < " + str(label[2]) + " : " + str(datum[3]<label[2]) + " | " + str(datum[3]) + " > " + str(label[1]) + " : " + str(datum[3]>label[1]))
                        if(datum[3] < label[2] and datum[3] > label[1]):
                                result.append(datum + (label[3],))
                                print(datum)
#        result = [elem for elem in dataraw if len(elem) > 5]
        print(result)


aggregate_data()

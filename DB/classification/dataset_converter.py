import pandas
import numpy as np
import psycopg2

DATABASE = "seads"
USER = "ianlofgren"
TABLE = "data_raw"

store = pandas.io.pytables.HDFStore('store.h5')
con = psycopg2.connect(database = DATABASE, user = USER)
cursor = con.cursor()
cursor.execute("select * from data_raw where serial = 466419816 limit 50;")
records = cursor.fetchall()

#print(str(records[0]))

#collect all entries with matching deviceID and timestamp together
result = []
for record in records:
    to_insert = []
    for row in result:
        if row[0] == record[3] and row[1] == record[0]:
            to_insert = row
    if to_insert == []:
        to_insert.append(record[3])
        to_insert.append(record[0])
        to_insert.append([record[1], record[2]])
        result.append(to_insert)
    else:
        to_insert.append([record[1], record[2]])

#add together all entries with matching power types
print(str(result) + "\n\n")

hdf5 = []
for row in result:
    row.remove(row[1])
    temp = [row[0]]
    for i, element in enumerate(row[1:], start=1):
        signal = True
        for to_find in temp[1:]:
            #print(str(to_find) + str(element) + "\n")
            if to_find[0] == element[0]:#fix
                signal = False
                to_find[1] += element[1]
                #print(str(element) + "  " + str(thing) + "\n")
                #row.remove(thing)
        if signal:
            temp.append(element)
    hdf5.append(temp)
for row in hdf5:
    print(str(row) + "\n")

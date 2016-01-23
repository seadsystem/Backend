from pandas.io.pytables import HDFStore
from pandas import DataFrame
import psycopg2

DATABASE = "seads"
USER = "ianlofgren"
TABLE = "data_raw"

store = HDFStore('store.h5')
con = psycopg2.connect(database = DATABASE, user = USER)
cursor = con.cursor()
cursor.execute(" select serial, type, data - lag(data, 14) over \
                 (order by time), time, device from data_raw where \
                 serial = 466419818 and device != 'PowerS' and device \
                 != 'PowerG' limit 56 ;")
records = cursor.fetchall()

for row in records:
    print(str(row) + '\n')


#collect all entries with matching deviceID and timestamp together
results = []
for record in records[14:]:
    to_insert = []
    for row in results:
        if row[0] == record[3] and row[1] == record[0]:
            to_insert = row
    if to_insert == []:
        to_insert.append(record[3])
        to_insert.append(record[0])
        to_insert.append([record[1], record[2]])
        results.append(to_insert)
    else:
        to_insert.append([record[1], record[2]])

#add together all entries with matching types
indexes = []
values = {}
for row in results:
    indexes.append(row[0])
    del row[:2]
    temp = {}
    for data in row:
        if data[0] in temp:
            temp[data[0]] += data[1]
        else:
            temp[data[0]] = data[1]
    for key,value in temp.items():
        if key in values:
            values[key].append(value)
        else:
            values[key] = [value]

dfs = DataFrame(values, index=indexes)
store['dfs'] = dfs
print(str(store['dfs']))

"""
hdf5 = []
for row in result:
    temp = {}
    for i, element in enumerate(row[1:], start=1):
        if element[0] in temp:
            temp[element[0]] += element[1]
        else:
            temp[element[0]] = element[1]
    hdf5.append(temp)

values = []
index = []
columns = []
for row in hdf5:
    values.append([value for key, value in row.items() if key != 'time'])
    index.append([value for key, value in row.items() if key == 'time'])
    columns += [key for key, value in row.items() if key not in columns]
    #print(str(row) + "\n")
columns.remove('time');
#print(str(values))
#print(str(index))
#print(str(columns))
#dfs =
#print(str(dfs))
"""

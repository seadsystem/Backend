from pandas.io.pytables import HDFStore
from pandas import DataFrame

"""
Converts the given records to .hd5 format and outputs the resulting file
"""
def convert_to_hdf5_file(records, file_name="store.h5"):
#collect all entries with matching deviceID and timestamp together
    if file_name[len(file_name)-3:] != ".h5":
        raise ValueError('File name: ' + file_name + ' must end with .h5')
    store = HDFStore('store.h5')
    [values, indexes] = convert_to_hdf5(records)
    dfs = DataFrame(values, index=indexes)
    store['dfs'] = dfs

def convert_to_hdf5(records):
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

    for key,value in values.items():
        if len(value) != len(indexes):
            raise Exception('Malformed record, check your query')

    return [values, indexes]

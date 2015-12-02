# DEPENDS ON:
#   pandas
#   sqlalchemy
#   numpy?
#   pytables
#   conda install -c https://conda.binstar.org/trent psycopg2
#
# What is left to do:
#   - combine tables so that there is one table for each meter
#       * What about current and other ambiguous names?
#   - change tables to ascending order
#       * do this in SQL query or in DataFrame?
#   - make sure units are in SI form not cumulative
#       * !!!! optional field is cumulative energy !!!!
#       * what is energy and what is power??
#   - ensure DF has proper units for columns
#   - input DF tables into HDF5 file with proper hierarchy
#   - input metadata into HDF5
#
#
# https://github.com/nilmtk/nilmtk/blob/master/docs/manual/development_guide/writing_a_dataset_converter.md

import pandas
from sqlalchemy import create_engine, text

DATABASE = "jesse"
USER = "jesse"
TABLE = "data_raw100k"



def make_engine(database, user, host='localhost', port='5432'):
    url = ('postgresql://' + user + '@' + host + ':' + port + '/'
            + database)
    return create_engine(url)

def make_device_list(engine, table):
    deviceQ = "SELECT DISTINCT device FROM {table}"
    result = engine.execute(text(deviceQ.format(table=table)))
    # clean up list on single item lists
    result = [item for dudlist in result for item in dudlist]
    return result

def make_units_dict(engine, table):
    # select every unique device and its type and store in dict
    unitsQ = """
        SELECT device,
            (SELECT type
             FROM {table} b
             WHERE a.device = b.device
             LIMIT 1)
        FROM {table} a
        GROUP BY device
        """
    units_result = engine.execute(text(unitsQ.format(table=table)))
    #fix so propper syntax to create dict from  device and type
    return {row['device']: row['type'] for row in units_result}


def db_to_dataframe(engine, table, time_s, time_f, device, units):
    # makes new df with time and delta (data) columns
    sql_query = """
        SELECT
            time,
            CAST(lag(data) OVER (ORDER BY time DESC) - data
                AS NUMERIC) / 1e3 AS delta
        FROM {table}
        WHERE device = '{device}'
            AND time BETWEEN '{time_s}'
            AND '{time_f}'
            ORDER BY time DESC OFFSET 1
        """
    sql_query =sql_query.format(table=table, device=device, time_s=time_s,
                                time_f = time_f)
    return pandas.read_sql(sql_query, engine)

def dataframe_to_hdf5(dataframe, device):
    # http://glowingpython.blogspot.com/2014/08/quick-hdf5-with-pandas.html
    # http://pandas.pydata.org/pandas-docs/version/0.17.0/api.html#hdfstore-pytables-hdf5
    pass

def export_to_hdf5(db, user, table, time_s, time_f,
                   host='localhost', port='5432'):
    engine = make_engine(db, user)
    device_list = make_device_list(engine, table)
    units = make_units_dict(engine, table)
    print(units)
    hdf = pandas.HDFStore('{table}.h5'.format(table=table))
    for device in device_list:
        df = db_to_dataframe(engine, table, time_s, time_f, device, units)
        dataframe_to_hdf5(df, device)

if __name__ == "__main__":
    df = export_to_hdf5(DATABASE, USER, TABLE, '2015-06-10 15:50:17',
                        '2015-06-10 17:34:14')

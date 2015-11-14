# DEPENDS ON:
#   pandas
#   sqlalchemy
#   numpy?
#   pytables
import sys
import pandas
from pandas.io import sql
from sqlalchemy import create_engine
from contextlib import closing


DATABASE = "jesse"
USER = "jesse"
TABLE = "data_raw100k"

# try connecting to the db
def make_engine(database, user, host='localhost', port='5432'):
        url = ('postgresql://' + user + '@' + host + ':' + port + '/'
            + database)
        return create_engine(url)

if __name__ == '__main__':
    engine = make_engine(DATABASE, USER)
    # generate dataframe from connection
    dataframe = pandas.read_sql_table(TABLE, engine)


import sys
import psycopg2
import psycopg2.extras
import pandas
from pandas.io import sql

DATABASE = "seads"
# use api user or ask ian to make new user for converter?
USER = "jesse"
TABLENAME = "data_raw"

# try connecting to the db
def connect_to_db(database, user):
    try:
        return db_connection = psycopg2.connect("dbname='" + database +
                                                "' user='" + user + "'")
    finally:
        if db_connection:
            db_conenction.close()


connection = connect_to_db(DATABASE, USER)
# generate dataframe from connection
dataframe = pandas.read_sql_table()

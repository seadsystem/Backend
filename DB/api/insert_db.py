import psycopg2
import psycopg2.extras
import json
import datetime

# Database user credentials
DATABASE = "seads"
USER = "seadapi"
TABLE = "data_label"

def insert(parsed_url, data):
    """
    Handle parsed URL data and query the database as appropriate

    :param parsed_url: Array of url parameters
    :param data: json data from post request body
    """
    body = json.loads(data)
    data_dict = dict(body['data'])
    if 'device_id' not in parsed_url.keys():
        raise Exception("Received malformed URL data")
    if 'label' not in data_dict.keys():
        raise Exception("POST body incorrect")
    if 'start_time' not in  data_dict.keys():
        raise  Exception("POST body incorrect")
    if 'end_time' not in  data_dict.keys():
        raise  Exception("POST body incorrect")

    query_dict = dict()
    query_dict['start_time'] = datetime.datetime.fromtimestamp(data_dict['start_time'])
    query_dict['end_time'] = datetime.datetime.fromtimestamp(data_dict['end_time'])
    query_dict['label'] = data_dict['label']
    query_dict['serial'] = parsed_url['device_id']
    query = "INSERT INTO " + TABLE + " (serial, start_time, end_time, label) VALUES (%(serial)s, %(start_time)s, %(end_time)s, %(label)s) RETURNING *;"
    res = perform_insert(query, query_dict)
    result = '{"data":{'
    result += '"device_id":"' + str(res['serial']) + '",'
    result += '"start_time":"' + str(int(res['start_time'].timestamp())) + '",'
    result += '"end_time":"' + str(int(res['end_time'].timestamp())) + '",'
    result += '"label":"' + res['label'] + '"}}'
    return result


def perform_insert(query, params):
    """
    Initiate a connection to the database and return a cursor to return db rows a dictionaries

    :param query: SQL query string
    :param params: List of SQL query parameters
    """
    con = None
    try:
        con = psycopg2.connect(database=DATABASE, user=USER)
        cursor = con.cursor()
        print("Query:", query)
        print("Parameters:", params)
        cursor.execute(query, params)
        return params
    except psycopg2.DatabaseError as e:
        print('Database error: %s' % e)
    finally:
        if con:
            con.close()


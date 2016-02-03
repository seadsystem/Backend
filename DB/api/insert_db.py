import psycopg2
import psycopg2.extras
import Analysis_3 as A
import detect_events as D

# Database user credentials
DATABASE = "seads"
USER = "ianlofgren"
TABLE = "data_labels"

def insert(parsed_url, data):
    """
    Handle parsed URL data and query the database as appropriate

    :param parsed_url: Array of url parameters
    """
    print(parsed_url)
    print(data)
    if 'device_id' not in parsed_url.keys():
        raise Exception("Received malformed URL data")

    device_id = parsed_url["device_id"]
    data["device_id"] = device_id
    query = "INSERT INTO" + TABLE +
    if "label" in parsed_url.keys():

def perform_insert(insert_query, data):
    a = 1

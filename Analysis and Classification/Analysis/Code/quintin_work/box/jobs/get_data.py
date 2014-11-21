'''
Created By: Quintin Leong
Created Date: November 5th, 2014
File Name: get_data.py
File Description: Utility to pull all consolidated content data from database in a clean nested format.
'''

import MySQLdb, sys
import Classes as classes
HOST = "sead.systems"
USER = "dataeng"
PASSWD = "dataeng"
DB = "shempserver"

DEBUG_MODE = False
FREQUENCY = {'AC Voltage':2400, 'AC Current':2400, 'Wattage':1, 'Temperature':0.2}
ENDPOINT = "scratch.data_landing"

def check_debug():
    global DEBUG_MODE
    if((len(sys.argv) == 2)):
        if((sys.argv[1] == "DEBUG")):
            DEBUG_MODE = True
            print "DEBUG mode entered."

def execute_raw_query(cur, query):
    data_raw = []
    response_length = 0
    try:
        response_length = cur.execute(query)
        data_raw = cur.fetchall()
    except MySQLdb.Error, e:
        try:
            print "MySQLdb Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQLdb Error: %s" % str(e)

    if (DEBUG_MODE):
        print "\nQuery executed successfully: "+query
        print "Entries returned: "+str(response_length)

    return list(data_raw)


def get_distinct_sensor_id(cur):
    if(DEBUG_MODE):print "\nGetting distinct sensor_id in data_raw from MySQL..."
    query = "SELECT DISTINCT(sensor_id) FROM shempserver.data_raw;"
    response = []
    response = execute_raw_query(cur, query)
    response = [r[0] for r in response]
    return response

def get_metadata(cur, sensor_id_list):
    if(DEBUG_MODE):print "\nGetting metadata for each sensor_id..."
    metadata = {}

    packet_id = get_next_packet_id(cur)

    for sensor_id in sensor_id_list:
        query = "SELECT s.sensor_id, s.sensor_type_id, st.sensor_type, s.device_id "+\
                "FROM sensors s JOIN sensor_types st "+\
	            "ON s.sensor_type_id = st.sensor_type_id "+\
                "WHERE s.sensor_id = %s;" % (str(sensor_id),)

        if(DEBUG_MODE):print "Executing: "+query

        response_length = cur.execute(query)
        if(response_length != 1): "Error executing query for sensor: "+str(sensor_id)
        response = cur.fetchone()

        if(response[0] not in metadata.keys()):
            metadata[str(sensor_id)] = {"sensor_type_id": response[1], "packet_id":packet_id,
                                        "sensor_type": response[2], "device_id":response[3]}
            packet_id += 1

    if(DEBUG_MODE):
        print "\nMetadata returned: "
        for key in metadata:
            print "Key: "+key
            print "Value: "+str(metadata[key])
    return metadata

def get_next_packet_id(cur):
    query = "SELECT MAX(packet_id) FROM "+ENDPOINT+";"
    packet_id= execute_raw_query(cur, query)

    # If no packet_id, then table must be empty, return 1 in this case
    if(packet_id[0][0] == None):
        if(DEBUG_MODE):
            print "\nEndpoint table is empty, spawning first packet_id."
        return 1


    new_packet_id = int(packet_id[0][0]) + 1
    if(DEBUG_MODE):
        print "\nRetrieved next packet_id"
        print "Old packet_id: "+str(packet_id)
        print "New packet_id: "+str(new_packet_id)
    return new_packet_id


def update_endpoint(cur, data_list):
    query = "INSERT INTO "+ENDPOINT+" (device_id,sensor_id,packet_id,sensor_type_id,sensor_type,"+\
            "`data`,frequency,microstamp) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"
    for item in data_list:
        print item.give_tuple()




def main():
    global PRODUCT

    check_debug()
    data_raw = []
    sensor_id = None
    metadata = None

    # Get references to the database
    db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB)
    cur = db.cursor()

    truncate_query = "TRUNCATE TABLE shempserver.data_raw;"

    # Get a distinct list of sensor_ids from shempserver.data_raw table
    sensor_id = get_distinct_sensor_id(cur)

    # Get the metadata associated with each sensor_id
    metadata = get_metadata(cur, sensor_id)

    # Get raw row data from seads plug data landing table
    select_query = "SELECT * FROM shempserver.data_raw;"
    data_raw = execute_raw_query(cur, select_query)

    # Check that there is work to do
    if(len(data_raw) == 0):
        # No work to do, so exit
        exit()


    # Create DatRaw objects and fill in missing fields. Insert into product after.
    product = []
    while(len(data_raw) > 0):
        data_row = classes.DataRaw(data_raw.pop())
        sensor_id = data_row.get_sensor_id()

        # Get values for fields to be entered in data_row object
        device_id = metadata[sensor_id]['device_id']
        packet_id = metadata[sensor_id]['packet_id']
        sensor_type_id = metadata[sensor_id]['sensor_type_id']
        sensor_type = metadata[sensor_id]['sensor_type']
        frequency = FREQUENCY[sensor_type]

        # Set all of the missing fields
        data_row.set_device_id(device_id)
        data_row.set_packet_id(packet_id)
        data_row.set_sensor_type_id(sensor_type_id)
        data_row.set_sensor_type(sensor_type)
        data_row.set_frequency(frequency)

        product.append(data_row)

    if(DEBUG_MODE): print "[%d] data objects created" % (len(product),)







    cur.close()
    db.close()
    # END MAIN ##############################################################################



if __name__ == "__main__":
    main()
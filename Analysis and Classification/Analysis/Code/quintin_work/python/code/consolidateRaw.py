'''
Created By: Quintin Leong
Create Date: November 4th
File Name: consolidateRaw.py
File Description: Gathers all metadata for raw csv files from MySQL database.
'''

import csv, os, MySQLdb
import Classes as Classes

HOST = "sead.systems"
USER = "root"
PASSWD = "teammantey"
DB = "shempserver"

PRODUCT = {}

def get_csv_files():
    directory = os.getcwd()+'/'
    files = os.listdir(directory)
    return [file for file in files if file.endswith(".csv")]

def process_file(cur, file_name):
    global PRODUCT
    bucket = file_name.split("_")[0].lower()
    data = []
    print bucket


    # Create bucket if it doesn't exist.
    # Bucket is an appliance category such as "microvwaves"
    if(bucket not in PRODUCT.keys()):
        PRODUCT[bucket] = {}

    # Create slot for file name of originating data
    # Assumes file naming convention: bucket_number.csv
    if(file_name not in PRODUCT[bucket].keys()):
        PRODUCT[bucket][file_name] = {}


    with open(file_name, 'r') as csvfile:
        # Get a reader object to the csv file
        reader = csv.reader(csvfile, delimiter=",", )

        # Discard column headers from csv file
        reader.next()
        for row in reader:
            data_entry = Classes.RawDataRow(row)
            data.append(data_entry)
    resolve_data_types(cur, data)

def resolve_data_types(cur, data_list):
    for data_object in data_list:
        query = "SELECT st.sensor_type FROM shempserver.sensors s "+\
                "JOIN shempserver.sensor_types st " + \
                "ON s.sensor_type_id = st.sensor_type_id AND s.sensor_id = %s"
        print query
        #cur.execute(query, (str(data_object.get_sensor_id()),))


def add_data_to_bucket(bucket, file_name, data_list):
    global PRODUCT



def main():
    print "Progarm starting"
    global PRODUCT
    #db = MySQLdb.connect(host=HOST,user=USER, passwd=PASSWD, db=DB)
    #cur = db.cursor()

    #Get all csv file names in current directory
    files = get_csv_files()

    # Process each file
    for file in files:
        data = process_file(cur, file)

    print "Program finished."
    #END MAIN#############################################


if __name__ == "__main__":
    main()
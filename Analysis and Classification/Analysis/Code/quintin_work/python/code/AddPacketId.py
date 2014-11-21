'''
Created By: Quintin Leong
File Name: AddPacketId.py
File Description: This script goes through all csv files in the current directory and appends a packet_id
    to each appliance gathering session. One packet_id represents one appliance reading. The csv files should
    be in the raw SEAD plug format from the data landing table in the original MySQL DB implementation.
    
    The input file should have the following 4 columns:
    |  sensor_id  |  data  |  microstamp  |  device_microstamp  |
    
    The output file will have the following 5 columns:
    |  sensor_id  | packet_id  | data  |  microstamp  | device_microstamp  |
    
    packet_id is of type INT(10)
'''


import csv, os


class Row:

    def __init__(self, row):
        self.sensor_id = row[0]
        self.packet_id = None
        self.data = row[1]
        self.microstamp = row[2]
        self.device_microstamp = row[3]

    def set_packet_id(self, new_packet_id):
        self.packet_id = new_packet_id

    def csv_output(self):
        return [self.sensor_id, self.packet_id, self.data, self.microstamp, self.device_microstamp]

def get_csv_files():
    directory = os.getcwd()+'/'
    files = os.listdir(directory)
    return [file for file in files if file.endswith(".csv")]

def process_file(file_name):
    bucket = file_name.split("_")[0].lower()
    packet_id = file_name.split("_")[1].split(".")[0]
    header = None
    data = []
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        #Save column header
        header = reader.next()
        for row in reader:
            row_object = Row(row)
            row_object.set_packet_id(packet_id)
            data.append(row_object)

    header.insert(1, 'packet_id')

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(header)
        for item in data:
            writer.writerow(item.csv_output())




def main():

    files = get_csv_files()

    for file in files:
        process_file(file)
        print file+" finished processing..."

    print "Job done!"
    #END MAIN

if __name__ == "__main__":
    main()
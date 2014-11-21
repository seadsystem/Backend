'''
Created By: Quintin Leong
File Name: Classes.py
File Description: Class file that acts as a utility file for AddPacketId.py script. 
                  Keep with AddPacketId.py at all times.

'''
import time, datetime, MySQLdb


class RawDataRow:


    def __init__(self, row):
        self.sensor_id = row[0]
        self.sensor_type = None
        self.data = row[1]
        self.microstamp = row[2]
        self.device_microstamp = row[3]


    def __str__(self):
        s = "Sensor id: "+str(self.sensor_id)
        s += "\nData: "+str(self.data)
        s += "\nMicrostamp: "+str(self.microstamp)
        s += "\nDevice microstamp: "+str(self.device_microstamp)
        return s
    def get_sensor_id(self):
        return int(self.sensor_id)

    def get_data(self):
        return float(self.data)

    def set_sensor_type(self, new_sensor_type):
        self.sensor_type = new_sensor_type


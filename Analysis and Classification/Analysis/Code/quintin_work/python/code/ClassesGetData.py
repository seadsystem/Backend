'''
Created By: Quintin Leong
Created Date: November 5th, 2014
File Name: Classes.py
File Description: Class representations to interact with database.
'''


class DataRaw:

    def __init__(self, row):
        self.device_id = None
        self.sensor_id = row[0]
        self.packet_id = None
        self.sensor_type_id = None
        self.sensor_type = None
        self.data = row[1]
        self.frequency = None
        self.microstamp = row[2]

    def __str__(self):
        s = "\n\nDevice id: "+str(self.device_id)
        s += "\nSensor id: "+str(self.sensor_id)
        s += "\nPacket id: "+str(self.packet_id)
        s += "\nSensor Type id: "+str(self.sensor_type_id)
        s += "\nSensor Type: "+str(self.sensor_type)
        s += "\nData: "+str(self.data)
        s += "\nFrequency: "+str(self.frequency)
        s += "\nMicrostamp: "+str(self.microstamp)
        return s

    def give_tuple(self):
        ret = tuple(str(self.device_id),
                    str(self.sensor_id),
                    str(self.packet_id),
                    str(self.sensor_type_id),
                    str(self.sensor_type),
                    str(self.data),
                    str(self.frequency),
                    str(self.microstamp))
        return ret


    def get_sensor_id(self):
        return str(self.sensor_id)

    def get_data(self):
        return str(self.data)

    def get_microstamp(self):
        return str(self.microstamp)

    def get_device_microstamp(self):
        return str(self.device_microstamp)

    def set_device_id(self, new_device_id):
        self.device_id = new_device_id

    def set_packet_id(self, new_packet_id):
        self.packet_id = new_packet_id

    def set_sensor_type_id(self, new_sensor_type_id):
        self.sensor_type_id = new_sensor_type_id

    def set_sensor_type(self, new_sensor_type):
        self.sensor_type = new_sensor_type

    def set_frequency(self, new_frequency):
        self.frequency = new_frequency


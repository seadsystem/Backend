import database
import math

# convert double time to device-compatible format
# Example
# input : 1393540108
# output: "1612822282800000"
def double_to_ascii_time(double_time):
	days = math.floor(double_time / (60*60*24))
	hours = math.floor((double_time % (60*60*24)) / (60*60))
	minutes = math.floor((double_time % (60*60)) / (60))
	seconds = math.floor((double_time % (60)) / (1))
	milliseconds = math.floor(((double_time * 1000) %1000))
	clock_time = math.floor(((double_time * 12000) %12))
	result = "%03d%02d%02d%02d%03d%02d" %(days, hours, minutes, seconds, milliseconds, clock_time)
	return result

# create string to enable/disable sensor on SHEMP
# String decomposition:
# L : location of sensor (internal/external)
# T : type of sensor (check config for types)
# sE/D: sensor enable/disable
# P : sensor period. Refer to function for format
# C: : hard-coded 00001
def sensor_setting_to_string(sensor):
	string = ""
	string += "@S"
	string += "L"+str(sensor['location'])
	string += "T"+str(sensor['type'])
	if(sensor['enabled']):
		string += "sE"
		string += "P"+str(double_to_ascii_time(sensor['period']))
		string += "C"+"%05d" %1
		string += "\n"
	else:
		string += "sD"
		string += "\n"
	return string

# Make a string for outbound communication.
def configure_string(settings):
	conf = ""
	for sensor in range(len(settings)):
		conf += sensor_setting_to_string(settings[sensor])
	return conf

def generate_conf(db, serial):
	# look up settings in database, if device exist in database, return conf, a string of stuff about the device.
	device = database.find_device_by_serial(serial, db)
	if(device == None):
		print "no device found for this serial: "+report['serial']
		return None
	device_id = device['device_id']
	device_name = device['device_name']
	#print "device found: "+self.device_name+"("+str(self.device_id)+")"
	# get/send configuration string to device
	settings = database.get_settings_for_device(device_id, db)
	conf = configure_string(settings)
	return conf

db = database.connect_to_mysql()
print generate_conf(db, "000001")

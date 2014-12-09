# ============================================================
# File: config.py
# Description: Configuration File
# Created by Bryan Smith
# January 27, 2014
#
# Smart Home Energy Monitoring Project (SHEMP)
# supported by CITRIS at UCSC
# http://www.shempserver.com
# ============================================================

# Database Info
# ********** CHANGE ME **************
databaseUserName = "root"
databaseUserPassword = "teammantey"
databaseHostName = "localhost"
databaseName = "shempserver"
base_dir = "/usr"
base_data_dir = base_dir + "data/"

# Socket server information
listen_port = 9000
buff = 1024
socket_timeout = 60 # seconds

# SHEMP Sensor Calibrations
shemp_sensor_calibration = {
   'W': 0.165,
	'V': 0.16,
	'I': 1,
	'T': 0.1,
	'A': 1,
	'L': 1}

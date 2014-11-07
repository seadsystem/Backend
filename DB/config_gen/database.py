# ============================================================
# File: database.py
# Description: Scripts to access the database
# Created by Bryan Smith
# January 27, 2014
#
# Smart Home Energy Monitoring Project (SHEMP)
# supported by CITRIS at UCSC
# http://www.shempserver.com
# ============================================================

import MySQLdb

import config

def store_report(query, db):
   if (db == None): return False
   cur = db.cursor()
   cur.execute(query)
   db.commit()
   cur.close()
   return True
   
def connect_to_mysql():
   db = MySQLdb.connect(host=config.databaseHostName, # your host, usually localhost
                        user=config.databaseUserName, # your username
                        passwd=config.databaseUserPassword, # your password
                        db=config.databaseName) # name of the data base
   return db
   
   
def get_settings_for_device(device_id, db):
	# This returns all sensors and relays associated with the device id
	# if (db == None):
    # db = connect_to_mysql()
	# Sensor
   get_sensors_query = "SELECT   s.sensor_id "\
                             +", s.device_id "\
                             +", sensor_types.sensor_type AS type "\
                             +", s.internal AS location "\
                             +", s.external_port "\
                             +", s.enabled "\
                             +", period "\
                        +"FROM   sensors s "\
                  +"INNER JOIN   sensor_types ON sensor_types.sensor_type_id=s.sensor_type_id "\
                        +"WHERE  device_id= "+str(device_id)+" "\
                         +"AND   sensor_types.sensor_type != 'DC Voltage' "\
                         +"AND   sensor_types.sensor_type != 'DC Current' "
   cur = db.cursor(MySQLdb.cursors.DictCursor)
   cur.execute(get_sensors_query)
   settings = cur.fetchall()
   for sensor in range(len(settings)):
      if (settings[sensor]['location'] == 0): settings[sensor]['location'] = "E";
      else: settings[sensor]['location'] = "I";
      if(settings[sensor]['type'] == "AC Voltage"): settings[sensor]['type'] = "V";
      elif(settings[sensor]['type'] == "DC Voltage"): settings[sensor]['type'] = "V";
      elif(settings[sensor]['type'] == "AC Current"): settings[sensor]['type'] = "I";
      elif(settings[sensor]['type'] == "DC Current"): settings[sensor]['type'] = "I";
      elif(settings[sensor]['type'] == "Wattage"): settings[sensor]['type'] = "W";
      elif(settings[sensor]['type'] == "Temperature"): settings[sensor]['type'] = "T";
      elif(settings[sensor]['type'] == "Light"): settings[sensor]['type'] = "L";
      elif(settings[sensor]['type'] == "Sound"): settings[sensor]['type'] = "S";
   cur.close()
   return settings
   
def find_device_by_serial(serial, db):
   device = None
   deviceQuery = "SELECT * FROM devices WHERE device_serial='"+serial+"' LIMIT 1";
   cur = db.cursor(MySQLdb.cursors.DictCursor)
   cur.execute(deviceQuery)
   device = cur.fetchall()
   cur.close()
   if(len(device)==0): return None
   return device[0]
   

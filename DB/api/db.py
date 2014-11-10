# Python 3
import psycopg2
import psycopg2.extras

# Database user credentials
DATABASE = ""
USER	 = ""

def query(parsed_url):
	'''
		Handle parsed URL data and query the database
		as appropriate
	'''
	if 'type' in parsed_url.keys():
		results = retrieve_by_type(
			parsed_url['device_id'],
			parsed_url['start_time'],
			parsed_url['end_time'],
			parsed_url['type'],
		)
	elif 'start_time' in parsed_url.keys():
		results = retrieve_within_timeframe(
			parsed_url['device_id'],
			parsed_url['start_time'],
			parsed_url['end_time']
		)
	elif 'device_id' in parsed_url.keys():
		results = retrieve_historical(parsed_url['device_id'])
	else:
		raise Exception("Recieved malform URL data")

	return format_data(results, 'array')

def retrieve_by_type(device_id, start_time, end_time, type):
	'''
	   Return sensor data of a specific type for a device
	   within a specified timeframe
	'''
	data = [
		['Time', 'KW/H', 'Temp'],
		['1', 50, 70],
		['2', 60, 77],
		['3', 80, 82],
		['4', 50, 76],
		['5', 50, 70],
		['6', 50, 70],
		['7', 60, 77],
		['8', 80, 82],
		['9', 50, 76],
		['10', 50, 70],
		['11', 50, 70],
		['12', 60, 77],
		['13', 80, 82],
		['14', 50, 76],
		['15', 50, 70],
		['16', 50, 70],
		['17', 60, 77],
		['18', 80, 82],
		['19', 50, 76],
		['20', 50, 70]
	]
	return data

def retrieve_within_timeframe(device_id, start_time, end_time):
	'''
	   Return sensor data for a device within a specified timeframe
	'''
	query = "SELECT * FROM crosstab(" +\
				"'SELECT time, type, data from data_raw " +\
				"WHERE serial = %s AND time BETWEEN %s AND %s'" +\
			") AS ct_result(time TIMESTAMP, I DECIMAL, W DECIMAL, V DECIMAL, T DECIMAL);"
	params = (int(device_id), start_time, end_time)
	rows = perform_query(query, params)
	return rows

def retrieve_historical(device_id):
	'''
	   Return sensor data for a specific device
	   TODO: add a page size limit?
	'''
	query = "SELECT * FROM crosstab(" +\
				"'SELECT time, type, data from data_raw " +\
				"WHERE serial = %s'" +\
			") AS ct_result(time TIMESTAMP, I DECIMAL, W DECIMAL, V DECIMAL, T DECIMAL);"
	params = (int(device_id), )
	rows = perform_query(query, params)
	return rows

def perform_query(query, params):
	'''
		Initiate a connection to the database and return a cursor
		to return db rows a dictionaries
		Returns cursor
	'''
	con = None
	try:
		con = psycopg2.connect("dbname='" + DATABASE +
				"' user='" + USER + "'")
		cursor = con.cursor()
		cursor.execute(query, params)
		return cursor.fetchall()

	except psycopg2.DatabaseError as e:
		print('Database error: %s' % e)

	finally:
		if con:
			con.close()

def format_data(data, format):
	'''
		Process rows of data returned by the db and format
		them appropriately
	'''
	if format == 'array':
		return str(data)

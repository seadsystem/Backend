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
	query = write_crosstab("WHERE serial = %s AND time BETWEEN %s AND %s AND type = %s")
	params = (int(device_id), start_time, end_time, type)
	rows = perform_query(query, params)
	return rows

def retrieve_within_timeframe(device_id, start_time, end_time):
	'''
	   Return sensor data for a device within a specified timeframe
	'''
	query = write_crosstab("WHERE serial = %s AND time BETWEEN %s AND %s")
	params = (int(device_id), start_time, end_time)
	rows = perform_query(query, params)
	return rows

def retrieve_historical(device_id):
	'''
	   Return sensor data for a specific device
	   TODO: add a page size limit?
	'''
	query = write_crosstab("WHERE serial = %s")
	params = (int(device_id), )
	rows = perform_query(query, params)
	return rows

def write_crosstab(where):
	query = "SELECT * FROM crosstab(" +\
				"'SELECT time, type, data from data_raw " + where + "'"\
			") AS ct_result(time TIMESTAMP, I DECIMAL, W DECIMAL, V DECIMAL, T DECIMAL);"
	return query

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

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
		header = ['time', parsed_url['type']]
	elif 'start_time' in parsed_url.keys():
		results = retrieve_within_timeframe(
			parsed_url['device_id'],
			parsed_url['start_time'],
			parsed_url['end_time']
		)
		header = ['time', 'I', 'W', 'V', 'T']
	elif 'device_id' in parsed_url.keys():
		results = retrieve_historical(parsed_url['device_id'])
		header = ['time', 'I', 'W', 'V', 'T']
	else:
		raise Exception("Recieved malform URL data")

	return format_data(header, results)

def retrieve_by_type(device_id, start_time, end_time, data_type):
	'''
	   Return sensor data of a specific type for a device
	   within a specified timeframe
	'''
	query = "SELECT time, data FROM data_raw WHERE serial = %s AND time BETWEEN to_timestamp(%s) AND to_timestamp(%s) AND type = %s;"
	params = (device_id, start_time, end_time, data_type)
	rows = perform_query(query, params)
	return rows

def retrieve_within_timeframe(device_id, start_time, end_time):
	'''
	   Return sensor data for a device within a specified timeframe
	'''
	query = write_crosstab("WHERE serial = %s AND time BETWEEN to_timestamp(%s) AND to_timestamp(%s)")
	params = (device_id, start_time, end_time)
	rows = perform_query(query, params)
	return rows

def retrieve_historical(device_id):
	'''
	   Return sensor data for a specific device
	   TODO: add a page size limit?
	'''
	query = write_crosstab("WHERE serial = %s")
	params = (device_id, )
	rows = perform_query(query, params)
	return rows

def write_crosstab(where):
	'''
	   Write a PostgreSQL crosstab() query to create a pivot table
	   and rearrage the data into a more useful form
	'''
	query = "SELECT * FROM crosstab(" +\
				"'SELECT time, type, data from data_raw " + where + "'," +\
				" 'SELECT unnest(ARRAY[''I'', ''W'', ''V'', ''T''])') " + \
			"AS ct_result(time TIMESTAMP, I SMALLINT, W SMALLINT, V SMALLINT, T SMALLINT);"
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

def format_data(header, data):
	'''
		Process rows of data returned by the db and format
		them appropriately
	'''
	data.insert(0, header)
	return map(lambda x: str(list(map(str, x))) + '\n', data)

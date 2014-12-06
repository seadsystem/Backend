import psycopg2
import psycopg2.extras

# Database user credentials
DATABASE = "seads"
USER     = "seadapi"
TABLE    = "data_raw"


def query(parsed_url):
	"""
	Handle parsed URL data and query the database as appropriate

	:param parsed_url: Array of url parameters
	:return: Generator of result strings
	"""
	if 'device_id' not in parsed_url.keys():
		raise Exception("Relieved malformed URL data")

	header = ['time', 'I', 'W', 'V', 'T']
	start_time = end_time = data_type = subset = limit = None
	if 'type' in parsed_url.keys():
		data_type = parsed_url['type']
		header = ['time', parsed_url['type']]
	if 'start_time' in parsed_url.keys():
		start_time = parsed_url['start_time']
	if 'end_time' in parsed_url.keys():
		end_time = parsed_url['end_time']
	if 'subset' in parsed_url.keys():
		subset = parsed_url['subset']
	if 'limit' in parsed_url.keys():
		limit = parsed_url['limit']

	if start_time or end_time or data_type or subset or limit:
		results = retrieve_within_filters(
			parsed_url['device_id'],
			start_time,
			end_time,
			data_type,
			subset,
			limit,
		)
	else:
		results = retrieve_historical(parsed_url['device_id'])

	return format_data(header, results)


def retrieve_within_filters(device_id, start_time, end_time, data_type, subset, limit):
	"""
	Return sensor data for a device within a specified timeframe

	:param device_id: The serial number of the device in question
	:param start_time: The start of the time range for which to query for data
	:param end_time: The end of the time range for which to query for data
	:param data_type: The type of data to query for
	:param subset: The size of the subset
	:param limit: Truncate result to this many rows
	:return: Generator of database row tuples
	"""

	# Initialize parameter list and WHERE clause
	params = [device_id]
	where = None

	# Add subset size parameter if set
	if subset:
		params.insert(0, float(subset) + 1.0)

	# Generate WHERE clause
	if start_time and end_time:
		where = "WHERE serial = %s AND time BETWEEN to_timestamp(%s) AND to_timestamp(%s)"
		params.append(start_time)
		params.append(end_time)
	elif start_time:
		where = "WHERE serial = %s AND time >= to_timestamp(%s)"
		params.append(start_time)
	elif end_time:
		where = "WHERE serial = %s AND time <= to_timestamp(%s)"
		params.append(end_time)
	if data_type:
		if where:
			where += " AND type = %s"
		else:
			where = "WHERE serial = %s AND type = %s"
		params.append(data_type)
		query = "SELECT time, data FROM " + TABLE + " as raw " + where
		if subset:
			query = write_subsample(query, False)

	else:
		# If no data type is set we return all data types
		query = write_crosstab(where, TABLE)
		if subset:
			query = write_subsample(query, True)

	# Required for LIMIT, analysis code assumes sorted data
	query += " ORDER BY time DESC"

	if limit:
		query += " LIMIT %s"
		params.append(limit)

	query += ";"
	rows = perform_query(query, tuple(params))
	return rows


def retrieve_historical(device_id):
	"""
	Return ALL sensor data for a specific device
	TODO: add a page size limit?

	:param device_id: The serial number of the device in question
	:return: Generator of database row tuples
	"""
	query = write_crosstab("WHERE serial = %s")
	params = (device_id, )
	rows = perform_query(query, params)
	return rows


def write_crosstab(where, data = TABLE):
	"""
	Write a PostgreSQL crosstab() query to create a pivot table and rearrange the data into a more useful form

	:param where: WHERE clause for SQL query
	:param data: Table or subquery from which to get the data
	:return: Complete SQL query
	"""
	query = "SELECT * FROM crosstab(" +\
				"'SELECT time, type, data from " + data + " as raw " + where + "'," +\
				" 'SELECT unnest(ARRAY[''I'', ''W'', ''V'', ''T''])') " + \
			"AS ct_result(time TIMESTAMP, I SMALLINT, W SMALLINT, V SMALLINT, T SMALLINT)"
	return query


def perform_query(query, params):
	"""
	Initiate a connection to the database and return a cursor to return db rows a dictionaries

	:param query: SQL query string
	:param params: List of SQL query parameters
	:return: Result cursor
	"""
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


def format_data(header, data, json=False):
	"""
	Process rows of data returned by the db and format them appropriately

	:param header: The first row of the result
	:param data: Result cursor
	:return: Generator of result strings
	"""
	data.insert(0, header)
	formatted = map(lambda x: str(list(map(str, x))) + ',\n', data)
	formatted.insert(0, "[\n")
	formatted.append("]\n")
	if json:
		formatted.insert(0, "{ data:\n")
		formatted.append("}\n")
	return formatted


def write_subsample(query, crosstab=False):
	"""
	Adds subsampling to a query. This should be the absolute last step in query building. This function call should be immediately proceeded with params.insert(0, subset).

	:param query: The exiting query to subsample
	:param crosstab: Whether or not the query is a crosstab
	:return: Query with subsampling enabled.
	"""
	new_query = "SELECT "
	if crosstab:
		new_query += "time, I, W, V, T"  # SELECT all data type columns
	else:
		new_query += "time, data"  # Single data type query
	new_query += ''' FROM (
	SELECT *, ((row_number() OVER (ORDER BY "time"))
		%% ceil(count(*) OVER () / %s)::int) AS rn
	FROM ('''
	new_query += query
	new_query += ''') AS subquery
	) sub
WHERE sub.rn = 0'''
	return new_query
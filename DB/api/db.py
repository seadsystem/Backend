import psycopg2
import psycopg2.extras
import Analysis_3 as A

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
		raise Exception("Received malformed URL data")

	header = ['time', 'I', 'W', 'V', 'T']
	start_time = end_time = data_type = subset = limit = None
	json = reverse = classify = False
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
	if 'json' in parsed_url.keys():
		json = parsed_url['json']
	if 'reverse' in parsed_url.keys():
		reverse = parsed_url['reverse']
	if 'classify' in parsed_url.keys():
		classify = parsed_url['classify']

	if classify:
		if serial and start_time and end_time:
			classification = classify_data(serial, start_time, end_time)
			return classification
		else:
			raise Exception("Received malformed URL data")

	results = retrieve_within_filters(
		parsed_url['device_id'],
		start_time,
		end_time,
		data_type,
		subset,
		limit,
		reverse,
	)

	return format_data(header, results, json)


def retrieve_within_filters(device_id, start_time, end_time, data_type, subset, limit, reverse):
	"""
	Return sensor data for a device within a specified timeframe

	:param device_id: The serial number of the device in question
	:param start_time: The start of the time range for which to query for data
	:param end_time: The end of the time range for which to query for data
	:param data_type: The type of data to query for
	:param subset: The size of the subset
	:param limit: Truncate result to this many rows
	:param reverse: Return results in reverse order
	:return: Generator of database row tuples
	"""

	# Initialize parameter list and WHERE clause
	params = [device_id]
	where = "WHERE serial = %s"

	# Add subset size parameter if set
	if subset:
		params.insert(0, float(subset) + 1.0)

	# Generate WHERE clause
	if start_time and end_time:
		where += " AND time BETWEEN to_timestamp(%s) AND to_timestamp(%s)"
		params.append(start_time)
		params.append(end_time)
	elif start_time:
		where += " AND time >= to_timestamp(%s)"
		params.append(start_time)
	elif end_time:
		where += " AND time <= to_timestamp(%s)"
		params.append(end_time)
	if data_type:
		if where:
			where += " AND type = %s"
		else:
			where += " AND type = %s"
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
	query += " ORDER BY time"

	if reverse:
		query += " ASC"
	else:
		query += " DESC"

	if limit:
		query += " LIMIT %s"
		params.append(limit)

	query += ";"
	rows = perform_query(query, tuple(params))
	return rows

def classify_data(serial, start_time, end_time):
	"""
	Classify a set of raw data

	:param serial: Integer device serial number
	:param start_time: First occuring timestamp
	:param end_time: First occuring timestamp
	:return: classification type as string
	"""
	query = "SELECT data FROM data_raw WHERE type = 'I' AND serial = %s AND time BETWEEN to_timestamp(%s) AND to_timestamp(%s)"
	current_data = perform_query(query, (serial, start_time, end_time))
	classification = A.run(current_data)
	return classification

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
		print("Query:", query)
		print("Parameters:", params)
		cursor.execute(query, params)
		return cursor.fetchall()

	except psycopg2.DatabaseError as e:
		print('Database error: %s' % e)

	finally:
		if con:
			con.close()


def format_data_row(row):
	"""
	Formats result row into result row string
	:param row: Result row
	:return: Result row string
	"""
	return '[' + ", ".join(map(lambda x: '"' + str(x) + '"', row)) + ']'


def format_data(header, data, json=False):
	"""
	Process rows of data returned by the db and format them appropriately

	:param header: The first row of the result
	:param data: Result cursor
	:param json: Whether or not to use JSON format.
	:return: Generator of result strings
	"""
	if json:
		yield '{\n"data": '
	yield "[\n" + format_data_row(header)  # No comma before header
	for row in data:
		yield ',\n' + format_data_row(row)
	yield "\n]\n"
	if json:
		yield "}\n"


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

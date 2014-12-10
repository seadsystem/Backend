#!/usr/bin/python

import psycopg2

# Database user credentials
DATABASE = "seads"
USER     = "seadapi"
TABLE    = "data_raw"

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

query = "SELECT COUNT(*) FROM classifications WHERE classification = 'microwave'"
params = None

perform_query(query, params)
print type(query)
print query

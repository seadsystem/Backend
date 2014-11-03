# Python 3
import re

def parse(url):
	'''
		Match the URL against a set of routing rules
		TODO update to use GET params
	'''
	if re.match('^/\d+/\d+/\d+/\w+$', url):
		# API request for data within a certain timeframe of a certain type
		# /device_id/start_time/end_time/type
		tokens = url.split('/')
		query_options = {
				'device_id': tokens[1],
				'start_time': tokens[2],
				'end_time': tokens[3],
				'type': tokens[4],
				}
	elif re.match('^/\d+/\d+/\d+$', url):
		# API request for data within a certain timeframe
		# /device_id/start_time/end_time
		tokens = url.split('/')
		query_options = {
				'device_id': tokens[1],
				'start_time': tokens[2],
				'end_time': tokens[3],
				}
	elif re.match('^/\d+$', url):
		# API request for all data for historical data
		# /device_id
		query_options = {
				'device_id': url[1:]
				}
	else:
		raise Exception("Not Found: Did not match")
	
	return query_options

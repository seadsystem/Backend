# Python 3
import re
import urllib.parse

def parse(url):
	'''
		Match the URL against a set of routing rules
	'''
	url_components = urllib.parse.urlparse(url)
	path = url_components.path
	params = urllib.parse.parse_qs(url_components.query)

	''' Extract device_id from URL '''
	if re.match('^/\d+$', path):
		device_id = path[1:]
	else:
		raise Exception("Not Found")

	''' Build query options as per present query parameters '''
	if 'type' in params.keys() and 'start_time' in params.keys() and \
		'end_time' in params.keys():
		query_options = {
				'device_id': device_id,
				'start_time': params['start_time'],
				'end_time': params['end_time'],
				'type': params['type'],
				}
	elif 'start_time' in params.keys() and 'end_time' in params.keys():
		query_options = {
				'device_id': device_id,
				'start_time': params['start_time'],
				'end_time': params['end_time'],
				}
	elif device_id:
		query_options = {
				'device_id': device_id
				}
	else:
		raise Exception("Not Found")

	return query_options

import re
import urllib.parse


def parse(url):
	"""
	Match the URL against a set of routing rules

	:param url: The path from the request
	:return: Array of URL parameters
	"""
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
		start_time = params['start_time'][0]
		end_time = params['end_time'][0]
		query_options = {
				'device_id': int(device_id),
				'start_time': int(start_time),
				'end_time': int(end_time),
				'type': params['type'][0],
				}
	elif 'start_time' in params.keys() and 'end_time' in params.keys():
		start_time = params['start_time'][0]
		end_time = params['end_time'][0]
		query_options = {
				'device_id': int(device_id),
				'start_time': int(start_time),
				'end_time': int(end_time),
				}
	elif device_id:
		query_options = {
				'device_id': int(device_id)
				}
	else:
		raise Exception("Not Found")

	if 'subset' in params.keys():
		query_options['subset'] = int(params['end_time'][0])

	return query_options

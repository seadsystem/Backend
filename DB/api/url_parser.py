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
	query_options = {
		'device_id': None,
		'start_time': None,
		'end_time': None,
		'subset': None,
		"limit": None,
		}

	''' Extract device_id from URL '''
	if re.match('^/\d+$', path):
		query_options['device_id'] = int(path[1:])
	else:
		raise Exception("Serial Not Found")

	''' Iterate over possible parameters and set query options accordingly '''
	for param in ['start_time', 'end_time', 'subset', 'limit']:  # Cast integer parameters
		if param in params.keys():
			query_options[param] = int(params[param][0])
	if 'type' in params.keys():  # Set character parameter
		query_options['type'] = params['type'][0]

	# Serial number required
	if not query_options['device_id']:
		raise Exception("Not Found")

	return query_options

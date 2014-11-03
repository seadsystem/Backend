# Python 3

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
		['10', 50, 70]
	]
	return data

def retrieve_historical(device_id):
	'''
	   Return sensor data for a specific device
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

def format_data(data, format):
    if format == 'array':
        return str(data)

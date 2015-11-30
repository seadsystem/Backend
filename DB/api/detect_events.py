def detect(time_series, threshold):
	"""
	Detects a list of events events in a result set returned from the db. An event is defined
	as a increase or descrease in power that is above some threshold.

	:param time_series: a generator created by the retrieve_within_filters function
						contains dates and power readings
	:param threshold: the threshold value for event detection
	:return eventList: a python matrix containing a list of times for detected events
	"""
	if threshold == 0:
		raise Exception("Threshold cannot be 0, try another value.")

	def convert_to_float(data_point):
		data_point[1] = float(data_point[1])

	response_list = list(map(time_series[1:], convert_to_float))

	event_list = []

	t1 = response_list[1]
	t2 = response_list[2]
	t3 = response_list[3]
	t4 = response_list[4]
	t5 = response_list[5]
	t6 = response_list[6]

	prev_avg = (t1[1] + t2[1] + t3[1] + t4[1] + t5[1]) / 5
	curr_avg = (t2[1] + t3[1] + t4[1] + t5[1] + t6[1]) / 5

	for i, data in enumerate(response_list[7:], start=7):

		if (curr_avg / prev_avg) > threshold:
			event_list.append(tuple([t4[0], "rising"]))
		if (curr_avg / prev_avg) < (1 / threshold):
			event_list.append(tuple([t4[0], "falling"]))

		t1 = t2
		t2 = t3
		t3 = t4
		t4 = t5
		t5 = t6
		t6 = response_list[i]
		prev_avg = (t1[1] + t2[1] + t3[1] + t4[1] + t5[1]) / 5
		curr_avg = (t2[1] + t3[1] + t4[1] + t5[1] + t6[1]) / 5

	return event_list


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

	event_list = []

	t1 = time_series[1]
	t2 = time_series[2]
	t3 = time_series[3]
	t4 = time_series[4]
	t5 = time_series[5]
	t6 = time_series[6]


	prev_avg = (t1[1] + t2[1] + t3[1] + t4[1] + t5[1]) / 5
	curr_avg = (float(t2[1]) + float(t3[1]) + float(t4[1]) + float(t5[1]) + float(t6[1])) / 5

	for i, data in enumerate(time_series[7:], start=7):

		if (curr_avg / prev_avg) > threshold:
			event_list.append(tuple([t4[0], "rising"]))
		if (curr_avg / prev_avg) < (1 / threshold):
			event_list.append(tuple([t4[0], "falling"]))

		t1 = t2
		t2 = t3
		t3 = t4
		t4 = t5
		t5 = t6
		t6 = time_series[i]
		prev_avg = (float(t1[1]) + float(t2[1]) + float(t3[1]) + float(t4[1]) + float(t5[1])) / 5
		curr_avg = (float(t2[1]) + float(t3[1]) + float(t4[1]) + float(t5[1]) + float(t6[1])) / 5

	return event_list
	

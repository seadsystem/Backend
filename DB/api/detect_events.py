from itertools import cycle


def detect(time_series, threshold):
	"""
	take in a series of time and power readings and return a list of events

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

	prev_avg = (float(t1[1]) + float(t2[1]) + float(t3[1]) + float(t4[1]) + float(t5[1])) / 5
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


'''
	#avrgCurrent:  array containing moving avrg values
	#deltaCurrent: array containing delta values (from moving average)
	#eventList:    array to be passed back, list of detected events
	#t1-t5:        hold values for moving avrg and delta calculations
	#tx:           iteration counter
	#center:       contains location of center of scope (relative to head)

	avrgCurrent = []
	deltaCurrent = []
	eventList = []
	times = []
	avrg   = 0
	delta  = 0
	event  = 0
	t1     = 0
	t2     = 0
	t3     = 0
	t4     = 0
	t5     = 0
	center = -2

	#Caluclate moving average first
	for i, value in enumerate(time_series):

		#calculate average once buffer is loaded
		if (i >= 4):
			avrg = (t1+t2+t3+t4+t5)/5
			avrgCurrent.append(avrg)

		#load in the value
		t5 = t4
		t4 = t3
		t3 = t2
		t2 = t1
		t1 = float(value[1])
		center = center + 1
		times.append(value[0])

	#reset itor
	tx = 0
	center = -2

	#calculate delta and use delta to detect event
	for value in avrgCurrent:

		#calculate delta once buffer is loaded
		if tx >= 5:
			delta = value - t3

			if delta > .01:
				event = (times[center], delta)
				eventList.append(event)

			elif delta < -.01:
				event = (times[center], delta)
				eventList.append(event)

		t5 = t4
		t4 = t3
		t3 = t2
		t2 = t1
		t1 = float(value)
		tx = tx + 1
		center = center + 1
'''
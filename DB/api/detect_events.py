def detect(time_series, threshold, windowSize=5):
    """
    Detects a list of events events in a result set returned from the db. An event is defined
    as a increase or descrease in power that is above some threshold.

    :param time_series: a generator created by the retrieve_within_filters function
                        contains dates and power readings
    :param threshold: the threshold value for event detection
    :param windowSize(default=5): window size of sliding window
    :return eventList: a python matrix containing a list of times for detected events
    """
    if threshold == 0:
        raise Exception("Threshold cannot be 0, try another value.")

    if windowSize < 2:
        raise Exception("Window must have a value of at least 2.")

    def convert_to_float(data_point):
        data = list(data_point)
        data[1] = float(data[1])
        return data

    response_list = list(map(convert_to_float, time_series[1:]))

    window_list = response_list[:windowSize]
    prev_avg = sum(item[1] for item in window_list)/windowSize

    window_list = response_list[1:windowSize+1]
    curr_avg = sum(item[1] for item in window_list)/windowSize

    event_list = []

    counter = 2
    center = windowSize/2
    for i, data in enumerate(response_list[7:], start=6):

        if (curr_avg / prev_avg) > threshold:
            event_list.append(tuple([window_list[center][0], "rising"]))
        if (curr_avg / prev_avg) < (1 / threshold):
            event_list.append(tuple([window_list[center][0], "falling"]))

        window_list = response_list[counter:counter+windowSize]
        prev_avg = curr_avg
        curr_avg = sum(item[1] for item in window_list)/windowSize

        counter += 1

    return event_list

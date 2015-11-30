def detect(time_series):

    """
    take in a series of time and power readings and return a list of events

    :param time_series: a generator created by the retrieve_within_filters function
                        contains dates and power readings

    :return eventList: a python matrix containing a list of times for detected events
    """

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
    tx     = 0
    center = -2

    #Caluclate moving average first
    for value in time_series:

        #calculate average once buffer is loaded
        if (tx >= 5):
            avrg = (t1+t2+t3+t4+t5)/5
            avrgCurrent.append(avrg)

        #load in the value
        t5 = t4
        t4 = t3
        t3 = t2
        t2 = t1
        t1 = float(value[1])
        tx = tx + 1
        center = center + 1
        times.append(value[0])

    #reset itor
    tx = 0
    center = -2

    #calculate delta and use delta to detect event
    for value in avrgCurrent:

        #calculate delta once buffer is loaded
        if (tx >= 5):
            delta = value - t3

            if (delta > .001):
                event = [times[center], delta]
                eventList.append(event)

            elif (delta < -.001):
                event = [times[center], delta]
                eventList.append(event)

        t5 = t4
        t4 = t3
        t3 = t2
        t2 = t1
        t1 = float(value)
        tx = tx + 1
        center = center + 1

    return eventList

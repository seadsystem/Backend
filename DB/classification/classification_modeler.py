import math
import datetime
import pickle
from sklearn.ensemble import RandomForestClassifier

hour = 3600
fiveMinutes = 300
fridge = 5
microwave = 11
stove = 14
classifier = RandomForestClassifier(n_estimators=1000, max_depth=None,min_samples_split=1, max_features=3)


def readInput(channel, house):
    input = []
    filepath = "redd/house_%d/channel_%d.dat" %(house, channel)
    for line in open(filepath,'r'):
        item = line.rstrip()
        input.append(item)
    return input


def getDayOfTheWeek(timestamp):
    d = datetime.datetime.fromtimestamp(timestamp)
    return d.weekday()


def getTimeOfTheDay(timestamp):
    d = datetime.datetime.fromtimestamp(timestamp)
    return d.hour


def printFeatureInstance(feature):
    print("Mean power: %d" %(feature[0]))
    print("Standart deviation: %d" %(feature[1]))
    print("Time of the day: %d" %(feature[2]))
    print("Peak: %d" %(feature[3]))
    print("Energy consumed: %d" %(feature[4]))
    print("Day of the week: %d" %(feature[5]))


def getStandartDeviation(points, mean):
    total = 0
    for point in points:
        delta = (point - mean)
        deviation = delta*delta
        total += deviation
    mean = total / fiveMinutes
    return math.sqrt(mean)


def form5MinuteInstance(input, low, high):
    if high >= len(input):
        return
    total = 0
    window = []
    timestamp = int(input[-1].split()[0])
    for index in range(low,high):
        item = input[index]
        split = item.split()
        data = float(split[1])
        window.append(data)
        total += data

    mean = total / fiveMinutes
    standartDeviation = getStandartDeviation(window,mean)
    dayOfTheWeek = getDayOfTheWeek(timestamp)
    timeOfTheDay = getTimeOfTheDay(timestamp)
    peak = max(window)

    featureInstance = [mean,standartDeviation,timeOfTheDay,peak,total,dayOfTheWeek]

    return featureInstance


def getInstances(input,low,high):
    instances = []
    for index in range(low,high,fiveMinutes):
        instance = form5MinuteInstance(input,index,index + fiveMinutes)
        instances.append(instance)
    return instances


def isRunning(input,low,high,deviceId):
    for i in range(low,high):
        value = input[i].split()[1]
        if float(value) > 10:
            return 1
    return 0


def combineInputs(inputs):
    points = []
    for i in range(0,len(inputs[0])):
        total = 0
        timestamp = int(inputs[0][i].split()[0])
        for input in inputs:
            split = input[i].split()
            value = float(split[1])
            total += value

        entry = "%d %f" % (timestamp, total)
        points.append(entry)
    return points


def extractRunningLabels(input, low, high):
    runningLabels = []
    for i in range(low, high, fiveMinutes):
        running = isRunning(input, i, i+fiveMinutes, 5)
        runningLabels.append(running)
    return runningLabels


def combineLabels(labels):
    running = []
    for i in range(0, len(labels[0])):
        total = 0
        for j in range(0, len(labels)):
            label = labels[j]
            total += label[i] << j
        running.append(total)
    return running


def getRunningLabels(inputs, low, high):
    labels = []
    for input in inputs:
        label = extractRunningLabels(input, low, high)
        labels.append(label)
    return combineLabels(labels)


def getInputs(l,h,house):
    inputs = []
    for i in range(l,h):
        inputs.append(readInput(i,house))
    return inputs


def performTests(aggregate, inputs, low, high, clr):
    testCases = getInstances(aggregate, low, high)
    actualResults = getRunningLabels(inputs, low, high)
    numberOfTests = len(testCases)
    successful = float(0)
    for i in range(0, numberOfTests):
        testCase = testCases[i]
        actual = actualResults[i]
        # print("Actual: %s" %(actual))
        # print("Predicted: %s" %(classifier.predict([testCase])))
        if actual == clr.predict([testCase])[0]:
            successful += 1
    print("Score: %f%%" % (successful/numberOfTests))


inputs = getInputs(3,20,1)
aggregate = combineInputs(inputs)

instances = getInstances(aggregate,0,hour*30)
runningLabels = getRunningLabels(inputs,0,hour*30)

classifier.fit(instances, runningLabels)
clr = classifier
performTests(aggregate, inputs, hour*30, hour*60, clr)

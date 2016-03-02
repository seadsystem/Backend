import datetime
import math
import uuid
from sklearn.ensemble import RandomForestClassifier
import DB.classification.models as models
import math
import statistics

USER = "seadapi"
DATABASE = "seads"
testdata = [
        [datetime.datetime(2015, 12, 18, 0, 1, 32), -6375, 'heater'],
        [datetime.datetime(2015, 12, 18, 0, 1, 33), -6375, 'heater'],
        [datetime.datetime(2015, 12, 18, 0, 1, 34), -6377, 'heater'],
        [datetime.datetime(2015, 12, 18, 0, 1, 35), -6381, 'heater'],
        [datetime.datetime(2015, 12, 18, 0, 1, 36), -6376, 'heater'],
        [datetime.datetime(2015, 12, 18, 0, 1, 37), -6373, 'heater'],
        [datetime.datetime(2015, 12, 16, 0, 0, 4), -125, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 5), -126, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 6), -126, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 7), -124, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 8), -126, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 9), -124, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 10), -126, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 11), -125, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 12), -126, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 13), -127, 'fridge']
]


class RandomForestModel(models.BaseClassifier):

    def __init__(self, date_time=datetime.datetime.utcnow(), model_field=None,
                 n_estimators=1000, max_depth=None, _id=str(uuid.uuid4()), min_samples_split=1,
                 max_features=2, window_size=2):
        """

        :param date_time:
        :param model_field:
        :param n_estimators:
        :param max_depth:
        :param _id:
        :param min_samples_split:
        :param max_features:
        :param window_size:
        :return:
        """
        if model_field is None:
            model = RandomForestClassifier(n_estimators=n_estimators,
                                           max_depth=max_depth,
                                           min_samples_split=min_samples_split,
                                           max_features=max_features,)
        else:
            model = model_field
	self.window_size = window_size
        super(RandomForestModel, self).__init__(model_type="RandomForestClassifier",
                                                created_at=date_time, model=model, _id=_id)

    def classify(self, start_time=datetime.datetime.now(), 
		end_time=datetime.datetime.now()-date.timedelta(seconds=self.window), 
		panel=None, serial=None):
        print(end_time)
        data = models.BaseClassifier.classification_data(start_time=start_time, end_time=end_time,
                                                         panel=panel, serial=serial)
        to_fit = RandomForestModel.create_samples(data)
        return self.model.predict(to_fit)

    def train(self, data=testdata):
        samples = RandomForestModel.create_samples(data)
        labels = RandomForestModel.create_labels(data)
	self.model.fit(samples, labels)

    def extract_values(self, data):
        result = []
        for i in data:
            result.append(i[1])
        return result

    def create_samples(self, inputs):
        if(len(inputs) < self.window_size):
            print("Input is smaller than window_size! Unpredictable results!")
        if(len(inputs) % self.window_size != 0):
            print("Input is not an even multiple of window_size!")
        result = []

        variable_increments = self.input_slice(inputs)

        for i in range(len(variable_increments)):
            values = self.extract_values(variable_increments[i])
            stdev = self.get_std_dev(variable_increments[i])
            peak = max(values)
            dayofweek = int(variable_increments[i][0][0].weekday())
            timeofday = int(variable_increments[i][0][0].hour)
            toInsert = [stdev, peak, dayofweek, timeofday]
            toInsert.extend(values)
            result.append(toInsert)
        return result

    def input_slice(self, inputs):
        result = []
        for i in range(int(len(inputs)/self.window_size)):
            result.append(inputs[i*self.window_size:(i+1)*self.window_size])
        return result

    def create_labels(self, inputs):
        result = []
        data = self.input_slice(inputs)
        for datum in data:
            # for elem in datum:
            result.append(ord(datum[0][2][0]))
        return result

    def get_std_dev(self, data):
        """
        Gets standard deviation. Data is assumed to be [[something, datapoint, ...],[something, datapoint]...].
        Extracts just datapoint from each array for stdev purposes.
        :param data:
        :return:
        """
        mean = 0
        data_arr = []
        for i in data:
	    data_arr.append(i[1])
	return statistics.stdev(data_arr)


    @staticmethod
    def get_model(_id):
        model_row = super(RandomForestModel, RandomForestModel).get_model(_id)
        model = RandomForestModel(date_time=model_row['created_at'], _id=model_row['id'],
                                  model_field=model_row['model'])
        return model

model2 = RandomForestModel()
model2.train()
model2.store()
modelDict = RandomForestModel.get_model(model2.id)
print(str(modelDict.model))
print(modelDict.classify(panel="Panel3", serial=466419818))

ourmodel = RandomForestModel()
ourmodel.train()
print(ourmodel.classify())
'''
model = RandomForestModel()
model.store()
modelDict = RandomForestModel.get_model(model.id)
print(str(modelDict))
'''

hour = 3600
fiveMinutes = 300
fridge = 5
microwave = 11
stove = 14



def readInput():
    input = []
    filepath = "testdata.txt" 
    for line in open(filepath,'r'):
        item = line.rstrip()
        input.append(item)
    return input


def getStandardDeviation(points, mean):
    total = 0
    for point in points:
        delta = (point - mean)
        deviation = delta*delta
        total += deviation
    mean = total / fiveMinutes
    return math.sqrt(mean)


def printFeatureInstance(feature):
    print("Mean power: %d" %(feature[0]))
    print("Standart deviation: %d" %(feature[1]))
    print("Time of the day: %d" %(feature[2]))
    print("Peak: %d" %(feature[3]))
    print("Energy consumed: %d" %(feature[4]))
    print("Day of the week: %d" %(feature[5]))




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
    standartDeviation = getStandardDeviation(window,mean)
    # dayOfTheWeek = getDayOfTheWeek(timestamp)
    # timeOfTheDay = getTimeOfTheDay(timestamp)
    # peak = max(window)

    featureInstance = [mean,standartDeviation,timeOfTheDay,peak,total,dayOfTheWeek]

    return featureInstance


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
    for i in range(0,len(labels[0])):
        total = 0
        for j in range(0,len(labels)):
            label = labels[j]
            total += label[i] << j
        running.append(total)
    return running



ourmodel = RandomForestModel()
ourmodel.train()
# print(ourmodel.classify(testdata))
>>>>>>> 3d94029fcacdd0bcdfd7b5badf47b18d7c6c955e

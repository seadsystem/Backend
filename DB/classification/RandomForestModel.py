import datetime
import math
from sklearn.ensemble import RandomForestClassifier
import DB.classification.models as models
import math

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
        [datetime.datetime(2015, 12, 16, 0, 0, 13), -127, 'fridge'],
        [datetime.datetime(2015, 12, 16, 0, 0, 14), -127, 'fridge']
]


class RandomForestModel(models.BaseClassifier):

    def __init__(self, date_time=datetime.datetime.utcnow().timestamp(), model_field=None,
                 n_estimators=1000, max_depth=None, _id=None, min_samples_split=1, max_features=2):
        if model_field is None:
            model = RandomForestClassifier(n_estimators=n_estimators,
                                           max_depth=max_depth,
                                           min_samples_split=min_samples_split,
                                           max_features=max_features)
        else:
            model = model_field
        super(RandomForestModel, self).__init__(model_type="RandomForestClassifier",
                                                created_at=date_time, model=model, _id=_id)
    runlength = 3

    def create_samples(self, inputs):
        result = []
        for i in range(len(inputs)-1):
            result.append([inputs[i][1], inputs[i+1][1]])
        return result

    def create_features(self, inputs):
        result = []
        for i in inputs[:-1]:
            result.append(ord(i[2][0]))
        return result

    def classify(self, data):
        toFit = self.createSamples(data)
        print(self.model.predict(toFit))

    def train(self, data):
        to_fit = self.create_samples(data)
        return self.model.predict(to_fit)

    def train(self):
        inputs = testdata
        samples = self.createSamples(inputs)
        features = self.createFeatures(inputs)
        # boston = load_boston()
        # print(boston.data[20:])

        # aggregate = combineInputs(inputs)
        samples = self.create_samples(inputs)
        features = self.create_features(inputs)
        # for i in samples:
        #     print(i)
        # for i in features:
        #     print(i)
        # instances = getInstances(aggregate,0,hour*30)
        # runningLabels = getRunningLabels(inputs,0,hour*30)

        self.model.fit(samples, features)

    def createSamples(self,inputs):
        result = []
        for i in range(len(inputs)-1):
            result.append([inputs[i][1], inputs[i+1][1]])
        return result

    def createFeatures(self,inputs):
        result = []
        for i in inputs[:-1]:
            result.append(ord(i[2][0]))
        return result
    @staticmethod
    def get_model(_id):
        model_row = super(RandomForestModel, RandomForestModel).get_model(_id)
        model = RandomForestModel(date_time=model_row.created_at, _id=model_row.id,
                                  model_field=model_row.model)
        return model

'''model = RandomForestModel()
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




def printFeatureInstance(feature):
    print("Mean power: %d" %(feature[0]))
    print("Standart deviation: %d" %(feature[1]))
    print("Time of the day: %d" %(feature[2]))
    print("Peak: %d" %(feature[3]))
    print("Energy consumed: %d" %(feature[4]))
    print("Day of the week: %d" %(feature[5]))


def getStandardDeviation(points, mean):
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
    standartDeviation = getStandardDeviation(window,mean)
    dayOfTheWeek = getDayOfTheWeek(timestamp)
    timeOfTheDay = getTimeOfTheDay(timestamp)
    peak = max(window)

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
print(ourmodel.classify(testdata))
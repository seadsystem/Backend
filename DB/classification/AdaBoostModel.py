import datetime
import uuid
from sklearn.ensemble import AdaBoostClassifier
# import DB.classification.models as models
import models
import statistics


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


class AdaBoostModel(models.BaseClassifier):
    window_size = None
    labels = []

    def __init__(self, date_time=datetime.datetime.utcnow(), model_field=None,
                id=str(uuid.uuid4()), window_size=2, labels=[]):
        """
        :param date_time:
        :param n_estimators:
        :param max_depth:
        :param _id:
        :param min_samples_split:
        :param window_size:
        :return:
        """
        if model_field is None:
            model = AdaBoostClassifier()
        else:
            model = model_field
        self.window_size = window_size
        self.labels = labels
        self.trained = False
        super(AdaBoostModel, self).__init__(model_type="AdaBoostClassifier",
                                                created_at=date_time, model=model, _id=_id)

    def classify(self, time=None, serial=None, panel=None):
        start_time = time - self.window_size
        data = models.BaseClassifier.classification_data(start_time=start_time, end_time=time,
                                                         panel=panel, serial=serial)
        return self.classify_data(data)

    def classify_data(self, data):
        if(not self.trained):
            raise ValueError("Classifier not trained!")
        to_fit = self.create_samples(data)
        predicted = self.model.predict(to_fit)
        result = []
        for i in predicted:
            result.append(self.disaggregate_labels(i))
        return result

    def get_index(self, label):
        """
        gets the index of the label. If it's not there, adds the label.
        :param label:
        :return:
        """
        if label in self.labels:
            return self.labels.index(label)
        else:
            self.labels.append(label)
            return self.labels.index(label)

    def add_all_labels(self, data):
        for i in data:
            self.get_index(i[2])

    def aggregate_labels(self, labels):
        """
        aggregates array of labels into a binary bitstring
        binary bitstring gets parsed as int
        :return:
        """
        boolean_arr = []
        for label in labels:
            self.get_index(label)

        for label in self.labels:
            if label in labels:
                boolean_arr.append(True)
            else:
                boolean_arr.append(False)
        bit_string = ''.join(['1' if x else '0' for x in boolean_arr])
        #leading 1 to avoid removal of leading 0's
        bit_string = '1' + bit_string
        result = int(bit_string)
        return result

    def disaggregate_labels(self, labels):
        """

        :param labels: integer value, of the form 010110, etc.
        :return:
        """
        result = []
        bitstring = str(labels)
        #remove leading 1(added to avoid removal of leading 0's
        bitstring = bitstring[1:]
        for i in range(len(bitstring)):
            if(bitstring[i] == '1'):
                result.append(self.labels[i])
        return result

    def train(self, data=testdata):
        self.add_all_labels(data)
        samples = self.create_samples(data)
        labels = self.create_labels(data)
        self.model.fit(samples, labels)
        self.trained = True

    def extract_values(self, data):
        """
        Extracts the values from the data and gives them back as an array
        :param data: In the format [anything, datum, ...], [anything, datum, ...], ...
        :return: [datum, datum, ...]
        """
        result = []
        for i in data:
            if(len(i) < 2):
                raise ValueError("Length of input list is less than 2!")
            result.append(i[1])
        return result

    def create_samples(self, inputs):
        if len(inputs) < self.window_size:
            raise ValueError("Input is smaller than window_size! Unpredictable results!")
        if len(inputs) % self.window_size != 0:
            raise ValueError("Input is not an even multiple of window_size!")
        result = []
        variable_increments = self.input_slice(inputs)

        for i in range(len(variable_increments)):
            values = self.extract_values(variable_increments[i])
            stdev = self.get_std_dev(variable_increments[i])
            peak = max(values)
            dayofweek = int(variable_increments[i][0][0].weekday())
            timeofday = int(variable_increments[i][0][0].hour)
            to_insert = [stdev, peak, dayofweek, timeofday]
            to_insert.extend(values)
            result.append(to_insert)
        return result

    def input_slice(self, inputs):
        """
        Splits inputs into arrays of size self.window_size.
        If window_size = 2, behaves like:
        [a, b, c, d, e, f] -> [[a, b], [c, d], [e, f]]
        :param inputs:
        :return:
        """
        result = []
        for i in range(int(len(inputs) / self.window_size)):
            result.append(inputs[i * self.window_size:(i + 1) * self.window_size])
        return result

    def create_labels(self, inputs):
        result = []
        data = self.input_slice(inputs)
        for datum in data:
            datum_labels = []
            for elem in datum:
                #aggregate all labels present per input slice
                if elem[2] not in datum_labels:
                    datum_labels.append(elem[2])

            result.append(self.aggregate_labels(datum_labels))
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
    def get_model():
        model_row = models.BaseClassifier.get_model()
        return RandomForestModel(date_time=model_row['created_at'],
                                 _id=model_row['id'],
                                 model_field=model_row['model'],
                                 window_size=model_row['window_size'],
                                 labels=model_row['labels'])

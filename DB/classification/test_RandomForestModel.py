import psycopg2
import unittest
#import DB.classification.RandomForestModel as rfm
import DB.classification.RandomForestModel as rfm
import datetime
import random

DATABASE = "seads"
USER = "seadapi"
TABLE = "data_raw"

class TestRandomForestModel(unittest.TestCase):


    def test_model_input_not_multiple_of_window_size(self):
        try:
            model = rfm.RandomForestModel()
            model.train()
            model.classify_data([datetime.datetime(2015, 12, 18, 0, 1, 32), -6375, 'heater'])
        except Exception as e:
            self.assertEqual(str(e), "Input is not an even multiple of window_size!")

    def test_model_training_initial(self):
        try:
            model = rfm.RandomForestModel()
            model.train()
        except Exception as e:
            print(e.str())
            self.fail("Training failed!")

    def test_model_classify(self):
        try:
            model = rfm.RandomForestModel()
            model.train()
            model.classify_data([[datetime.datetime(2015, 12, 18, 0, 1, 32), -6375, 'heater'],
                [datetime.datetime(2015, 12, 18, 0, 1, 33), -6375, 'heater']])
        except Exception as e:
            print(e.str())
            self.fail("Classify failed")

    def test_bad_input_data(self):
        try:
            model = rfm.RandomForestModel()
            model.train()
            model.classify_data(["bad", "input", ["data"], ["bad", "input", "data"]])
        except TypeError as e:
            self.assertEqual(str(e), "can't convert type 'str' to numerator/denominator")

    def test_aggregate_disaggregate_labels(self):
        model = rfm.RandomForestModel()
        labels = ['a', 'b', 'c', 'string', 'more', 'otherdata', 'some stuff']
        for i in range(10):
            teststr = [''.join(random.choice('0123456789ABCDEF') for i in range(3))]
            aggregated = model.aggregate_labels(teststr)
            disaggregated = model.disaggregate_labels(aggregated)
            self.assertEqual(teststr, disaggregated)

    # this functionality is actually in baseclassifier
    # def test_bad_classify_call(self):
    #     try:
    #         model = rfm.RandomForestModel()
    #         model.train()
    #         mode.classify(-1000)
    #     except Exception as e:
    #         self.assertEqual(str(e), "File name: Hello must end with .h5")

    def test_classify_before_train(self):
        try:
            model = rfm.RandomForestModel()
            model.classify_data([[datetime.datetime(2015, 12, 18, 0, 1, 32), -6375, 'heater'],
                [datetime.datetime(2015, 12, 18, 0, 1, 33), -6375, 'heater']])
        except ValueError as e:
            self.assertEqual(str(e), "Classifier not trained!")

if __name__ == '__main__':
    unittest.main()

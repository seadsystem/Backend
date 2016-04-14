import psycopg2
import unittest
import RandomForestModel as rfm
import datetime

DATABASE = "seads"
USER = "nsokolni"
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

    def test_model_classify(self):
        try:
            model = rfm.RandomForestModel()
            model.train()
            model.classify_data([[datetime.datetime(2015, 12, 18, 0, 1, 32), -6375, 'heater'],
                [datetime.datetime(2015, 12, 18, 0, 1, 33), -6375, 'heater']])
        except Exception as e:
            print(e.str())


    # def test_bad_input_data(self):
    #         con = psycopg2.connect(database = DATABASE, user = USER)
    #         cursor = con.cursor()
    #         cursor.execute(" select serial, type, data - lag(data, 14) over \
    #                          (order by time), time, device from data_raw where \
    #                          serial = 466419818 and device != 'PowerS' and device \
    #                          != 'PowerG' limit 140;")
    #         records = cursor.fetchall()

    #         try:
    #             open('store.h5')
    #         except:
    #             self.assertFail()

    # def test_bad_classify_call(self):
    #     try:
    #         con = psycopg2.connect(database = DATABASE, user = USER)
    #         cursor = con.cursor()
    #         cursor.execute(" select serial, type, data - lag(data, 14) over \
    #                          (order by time), time, device from data_raw where \
    #                          serial = 466419818 and device != 'PowerS' and device \
    #                          != 'PowerG' limit 140;")
    #         records = cursor.fetchall()
    #         self.assertFail()
    #     except Exception as e:
    #         self.assertEqual(str(e), "File name: Hello must end with .h5")

if __name__ == '__main__':
    unittest.main()

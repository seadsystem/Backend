import dataset_converter as conv
import psycopg2
import unittest
import RandomForestModel as rfm

DATABASE = "seads"
USER = "nsokolni"
TABLE = "data_raw"

class TestRandomForestModel(unittest.TestCase):

    def test_model_training(self):
        try:
            con = psycopg2.connect(database = DATABASE, user = USER)
            cursor = con.cursor()
            cursor.execute(" select serial, type, data - lag(data, 14) over \
                             (order by time), time, device from data_raw where \
                             serial = 466419818 and device != 'PowerS' and device \
                             != 'PowerG' limit 139;") 
            records = cursor.fetchall()
            file_to_write = open("test_data_incorrect.test", "wb")
            

        except Exception as e:
            self.assertEqual(str(e), 'Malformed record, check your query')

    def test_bad_input_data(self):
            con = psycopg2.connect(database = DATABASE, user = USER)
            cursor = con.cursor()
            cursor.execute(" select serial, type, data - lag(data, 14) over \
                             (order by time), time, device from data_raw where \
                             serial = 466419818 and device != 'PowerS' and device \
                             != 'PowerG' limit 140;")
            records = cursor.fetchall()

            try:
                open('store.h5')
            except:
                self.assertFail()

    def test_bad_classify_call(self):
        try:
            con = psycopg2.connect(database = DATABASE, user = USER)
            cursor = con.cursor()
            cursor.execute(" select serial, type, data - lag(data, 14) over \
                             (order by time), time, device from data_raw where \
                             serial = 466419818 and device != 'PowerS' and device \
                             != 'PowerG' limit 140;")
            records = cursor.fetchall()
            self.assertFail()
        except Exception as e:
            self.assertEqual(str(e), "File name: Hello must end with .h5")

if __name__ == '__main__':
    unittest.main()

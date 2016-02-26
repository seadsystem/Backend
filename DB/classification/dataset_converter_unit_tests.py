iimport dataset_converter as conv
import psycopg2
import unittest
import pickle

DATABASE = "seads"
USER = "nsokolni"
TABLE = "data_raw"

class TestHDF5Conversion(unittest.TestCase):

    def test_malformed_record(self):
        try:
            con = psycopg2.connect(database = DATABASE, user = USER)
            cursor = con.cursor()
            cursor.execute(" select serial, type, data - lag(data, 14) over \
                             (order by time), time, device from data_raw where \
                             serial = 466419818 and device != 'PowerS' and device \
                             != 'PowerG' limit 139;") 
            records = cursor.fetchall()
            file_to_write = open("test_data_incorrect.test", "wb")
            pickle.dump(file_to_write, records)
#            [indexes, values] = conv.convert_to_hdf5(records)
#            self.assertFail()
        except Exception as e:
            self.assertEqual(str(e), 'Malformed record, check your query')

    def test_HDF5_conversion_to_file(self):
            con = psycopg2.connect(database = DATABASE, user = USER)
            cursor = con.cursor()
            cursor.execute(" select serial, type, data - lag(data, 14) over \
                             (order by time), time, device from data_raw where \
                             serial = 466419818 and device != 'PowerS' and device \
                             != 'PowerG' limit 140;")
            records = cursor.fetchall()
            conv.convert_to_hdf5_file(records)
            try:
                open('store.h5')
            except:
                self.assertFail()

    def test_bad_file_name(self):
        try:
            con = psycopg2.connect(database = DATABASE, user = USER)
            cursor = con.cursor()
            cursor.execute(" select serial, type, data - lag(data, 14) over \
                             (order by time), time, device from data_raw where \
                             serial = 466419818 and device != 'PowerS' and device \
                             != 'PowerG' limit 140;")
            records = cursor.fetchall()
            conv.convert_to_hdf5_file(records, "Hello")
            self.assertFail()
        except Exception as e:
            self.assertEqual(str(e), "File name: Hello must end with .h5")

if __name__ == '__main__':
    unittest.main()

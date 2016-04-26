import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import unittest
import DB.classification.models as bc
from DB.classification.RandomForestModel import RandomForestModel
from os import rename, remove

DATABASE = "test_seads"
USER = "test_seadapi"

class TestBaseClassifier(unittest.TestCase):
    """
    :summary: Unit test for BaseClassifier. Tests store and get_model
    """
    @classmethod
    def setUpClass(cls):
        try:
            rename("db_info", "db_info_back")
        except OSError as e:
            pass
        db_info = open("db_info", 'w')
        db_info.write("test_seads\ntest_seadapi\n")
        db_info.close()
        bc.BaseClassifier.reload_db_info()

        cls.root_con = psycopg2.connect(database="postgres", user="postgres", port=5432)
        cls.root_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cls.root_cur = cls.root_con.cursor()

        cls.root_cur.execute("CREATE USER "+USER+";")
        cls.root_cur.execute("CREATE DATABASE "+DATABASE+";")
        
        setup_con = psycopg2.connect(database=DATABASE, user="postgres", port=5432)
        setup_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        setup_cur = setup_con.cursor()
        # Take from the puppet script
        setup_cur.execute("""
CREATE TABLE data_raw (
    serial BIGINT NOT NULL,
    type CHAR(1) NOT NULL,
    data BIGINT NOT NULL,
    time TIMESTAMP NOT NULL,
    device TEXT NULL
);

CREATE INDEX data_raw_serial_time_type_device_idx ON data_raw(serial, time, type, device);
CLUSTER data_raw USING data_raw_serial_time_type_device_idx;

CREATE TABLE data_label (
    serial BIGINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    label TEXT NOT NULL
);

CREATE TABLE classifier_model (
    id UUID NOT NULL,
    window_size INT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    model_type TEXT NOT NULL,
    model bytea NOT NULL,
    labels TEXT[] NULL,
    trained BOOLEAN NULL
);
        """)

        setup_cur.execute("GRANT ALL ON DATABASE "+DATABASE+" TO "+USER+";")
        setup_cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO "+USER+";")
        
        setup_cur.close()
        setup_con.close()
        
    def test_can_connect_DB(self):
        """
        :summary: Sanity check to make sure that we can access the database we just created
        """
        psycopg2.connect(database=DATABASE, user=USER, port=5432)
        
        
    def test_abstract_unimplemented(self):
        """
        :summary: Sanity check to make sure the base class doesnt implement behavior reserved for derived classes
        """
        abstractclassifier = bc.BaseClassifier()
        try:
            abstractclassifier.train()
            self.fail("Train should not be implemented by the abstract base class")
        except NotImplementedError:
            pass
        try:
            abstractclassifier.classify()
            self.fail("Classify should not be implemented by the abstract base class")
        except NotImplementedError:
            pass

    def test_store_get_model(self):
        """
        :summary: Checks that a random forest model can be stored and retrieved
        """
        try:
            bc.BaseClassifier.get_model()
            self.fail("Successfully got a model when no such model existed")
        except:
            pass
            
        randommodel = RandomForestModel()
        randommodel.store()

        bc.BaseClassifier.get_model()
        
    @classmethod
    def tearDownClass(cls):
        cls.root_cur.execute("DROP DATABASE "+DATABASE+";")
        cls.root_cur.execute("DROP USER "+USER+";")
        cls.root_cur.close()
        cls.root_con.close()

        try:
            rename("db_info_back", "db_info")
        except:
            remove("db_info")
            pass

if __name__ == '__main__':
    unittest.main()

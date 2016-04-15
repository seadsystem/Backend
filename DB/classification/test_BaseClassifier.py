import psycopg2
import unittest
import models as bc

import RandomForestModel as rfm

DATABASE = "seads"
USER = "seadapi"

class TestBaseClassifier(unittest.TestCase):
    def setUp(self):
        # fite me irl
        self.abstractclassifier = bc.BaseClassifier()

    def test_can_connect_DB(self):
        psycopg2.connect(database=DATABASE, user=USER, port=5432)
        
    def test_abstract_unimplemented(self):
        try:
            self.abstractclassifier.train()
            self.fail("Train should not be implemented by the abstract base class")
        except NotImplementedError:
            pass
        try:
            self.abstractclassifier.store()
            self.fail("Store should not be implemented by the abstract base class")
        except NotImplementedError:
            pass
            
    def tearDown(self):
        pass
    

if __name__ == '__main__':
    unittest.main()


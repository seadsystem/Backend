import datetime
import pickle
import psycopg2
import uuid


def insert_query_builder(table=None, to_insert=None):
    attrs = list(to_insert.keys())
    result = "INSERT INTO " + table + "("
    for i in range(len(attrs)):
        result += attrs[i]
        if i != len(attrs)-1:
            result += ","
    result += ") VALUES ("
    for i in range(len(attrs)):
        result += "%("+attrs[i]+")s"
        if i != len(attrs)-1:
            result += ","
    result += ") RETURNING *;"
    return result


def post_query_builder():
    raise NotImplementedError


class ClassifierModel(object):
    """
    :summary: Base class that all other classifiers will inherit from
    """
    model_type = None
    created_at = None
    id = None
    model = None

    def __init__(self, model_type="default", created_at=datetime.datetime.utcnow(),
                 model=None):
        """
        :summary: Classirfier Model constructo
        :param date_time (optional): timestamp, defaults to utcnow(), named parameter
        :param model_type (optional): string, defaults to 'default',  named parameter
        """
        self.model_type = model_type
        self.created_at = created_at
        self.model = model
        self.id = uuid.uuid4()

    def store(self):
        """
        :summary: stores *trained* model to db
        """
        try:
            blob = pickle.dumps(self.model)
            self.model = blob
        except pickle.PickleError as e:
            raise ValueError("Model pickling failed", e)

        try:
            con = psycopg2.connect(database="seads", user="ianlofgren")
        except psycopg2.Error() as e:
            raise ConnectionError("Database connection on model insert", e)

        try:
            cursor = con.cursor()
            self.id = str(self.id)
            print(self.__dict__)
            query = insert_query_builder("classifier_model", self.__dict__)
            print(query)
            cursor.execute(query, self.__dict__)
        except psycopg2.Error as e:
            raise IOError("Model insert failed", e)
        finally:
            con.commit()
            con.close()

    def train(self):
        raise NotImplementedError


clr = ClassifierModel()
clr.store()
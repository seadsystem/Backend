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


class BaseClassifier(object):
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
        :summary: Classifier Model constructor
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
            if self.model is None:
                raise AttributeError("Model not instantiated")
            blob = pickle.dumps(self.model)
            self.model = blob
        except pickle.PickleError as e:
            raise ValueError("Model pickling failed", e)
        except AttributeError as e:
            raise AttributeError(e)

        try:
            con = psycopg2.connect(database="seads", user="ianlofgren")
        except psycopg2.Error() as e:
            raise ConnectionError("Database connection on model insert", e)

        try:
            cursor = con.cursor()
            self.id = str(self.id)
            query = insert_query_builder("classifier_model", self.__dict__)
            cursor.execute(query, self.__dict__)
        except psycopg2.Error as e:
            raise IOError("Model insert failed", e)
        finally:
            con.commit()
            con.close()

    def train(self):
        raise NotImplementedError

    def classify(self):
        raise NotImplementedError

    @staticmethod
    def training_data(panel="Panel1"):
        try:
            con = psycopg2.connect(database="seads", user="ianlofgren")
        except psycopg2.Error() as e:
            raise ConnectionError("Database connection on training data fetch failed", e)

        try:
            cursor = con.cursor()
            query = "SELECT data_raw.time, data_raw.data- lag(data_raw.data) OVER " + \
                    "(ORDER BY data_raw.time), data_label.label " + \
                    "FROM data_raw, data_label " + \
                    "WHERE data_raw.serial=data_label.serial " + \
                    "AND data_raw.type='P' " + \
                    "AND data_raw.device='" + panel + "' " + \
                    "AND time BETWEEN data_label.start_time AND data_label.end_time;"
            cursor.execute(query)
            return cursor.fetchall()
        except psycopg2.Error() as e:
            raise IOError("Training data fetch failed", e)
        finally:
            if con:
                con.close()

print(str(BaseClassifier.training_data(panel="Panel3")))

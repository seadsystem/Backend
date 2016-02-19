import datetime
import pickle
import psycopg2
import uuid
from sklearn.ensemble import RandomForestClassifier


classifier = RandomForestClassifier(n_estimators=1000, max_depth=None,min_samples_split=1, max_features=3)
print(str(classifier))
pickle.dumps(classifier)

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
    """
    model_type = None
    date_time = None
    id = None
    model = None

    def __init__(self, model_type="default", date_time=datetime.datetime.utcnow().timestamp(),
                 model=None):
        """
        :summary: Classirfier Model constructo
        :param date_time (optional): timestamp, defaults to utcnow(), named parameter
        :param model_type (optional): string, defaults to 'default',  named parameter
        """
        self.model_type = model_type
        self.date_time = date_time
        self.model = model
        self.id = uuid.uuid4()
        return self

    def store(self):
        """
        :summary: stores *trained* model to db
        """
        try:
            blob = pickle.dumps(classifier)
        except pickle.PickleError as e:
            raise ValueError("Model pickling failed", e)

        try:
            con = psycopg2.connect(database="seads", user="ianlofgren")
        except psycopg2.Error() as e:
            raise ConnectionError("Database connection on model insert", e)

        try:
            cursor = con.cursor()
            query = "INSERT INTO classifier_model (id, date_time, model_type, model) (%(id)s, \
                    %(date_time)s, %(model_type)s, %(model)s) RETURNING *;"
            values = dict()
            values['id'] = self.id
            values['date_time'] = self.date_time
            values['model_type'] = self.model_type
            values['model'] = self.model
            cursor.execute(query, values)
        except psycopg2.Error as e:
            raise IOError("Model insert failed", e)
        finally:
            con.commit()
            con.close()

    def train(self):
        raise NotImplementedError

class RandomForestModel(ClassifierModel):
    def __init__(self, model_type="RandomForest",
                 date_time=datetime.datetime.utcnow().timestamp(),
                 n_estimators=1000,
                 max_depth=None,
                 min_samples_split=1,
                 max_features=3):

        model = RandomForestClassifier(n_estimators=n_estimators,
                                            max_depth=max_depth,
                                            min_samples_split=min_samples_split,
                                            max_features=max_features)
        super(self, model_type=model_type, date_time=date_time, model=model)
        return self









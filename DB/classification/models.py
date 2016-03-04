import datetime
import pickle
import psycopg2
import uuid
import functools

USER = "seadapi"
DATABASE = "seads"


class Memoized(object):
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated). Taken from https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    """

    def __init__(self, func):
         self.func = func
         self.cache = {}

    def __call__(self, *args):
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


class BaseClassifier(object):
    """
    :summary: Base class that all other classifiers will inherit from
    """
    model_type = None
    created_at = None
    model = None
    _id = None

    def __init__(self, model_type="default", created_at=datetime.datetime.utcnow(),
                 model=None, _id=str(uuid.uuid4())):
        """
        :summary: BaseClassifier constructor
        :param date_time (optional): timestamp, defaults to utcnow(), named parameter
        :param model_type (optional): string, defaults to 'default',  named parameter
        """
        self.model_type = model_type
        self.created_at = created_at
        self.model = model
        self.id = _id

    def store(self):
        """
        :summary: stores *trained* model to db
        """
        try:
            if self.model is None:
                raise AttributeError("Model not instantiated")
            blob = pickle.dumps(self.model)
            pickle.loads(blob)
            self.model = psycopg2.Binary(blob)

        except pickle.PickleError as e:
            raise ValueError("Model pickling failed", e)
        except AttributeError as e:
            raise AttributeError(e)

        try:
            con = psycopg2.connect(database=DATABASE, user=USER)
        except Exception as e:
            raise psycopg2.Error("Database connection on model insert", e)

        try:
            cursor = con.cursor()
            query = insert_query_builder("classifier_model", self.__dict__)
            cursor.execute(query, self.__dict__)
        except Exception as e:
            raise psycopg2.Error("Model insert failed", e)
        finally:
            con.commit()
            con.close()

    def train(self, data=None):
        """
        :summary: override this method in your derived classifier class to train your model
        :param data: data to train with
        """
        raise NotImplementedError

    def classify(self, time=None, serial=None, panel=None):
        """
        :summary: override this method in your derived classifier class to return a vector of labels
        :param time: time of data to classify with
        """
        raise NotImplementedError

    @staticmethod
    @Memoized
    def get_model():
        try:
            con = psycopg2.connect(database=DATABASE, user=USER)
        except psycopg2.Error as e:
            raise ConnectionError("Database connection on model insert", e)

        try:
            cursor = con.cursor()
            query = "SELECT * FROM classifier_model ORDER BY created_at DESC LIMIT 1;"
            cursor.execute(query)
            model_row = cursor.fetchall()
        except psycopg2.Error as e:
            raise IOError("Model lookup failed", e)
        finally:
            con.close()
        try:
            classifier_blob = model_row[0][4]
            classifier = pickle.loads(classifier_blob)
            model = {'id': model_row[0][0],
                     'created_at': model_row[0][2],
                     'model_type': model_row[0][3],
                     'model': classifier,
                     'window_size': model_row[0][1]}
        except Exception as e:
            raise ValueError("Model pickling failed", e)
        return model

    @staticmethod
    def classification_data(panel="Panel1", start_time=None, end_time=None, serial=None):
        """
        :summary: gets data to run classifier on
        :param panel: panel to get power data from
        :param serial: serial of device that is requesting classification
        :param start_time: start time of classification data
        :param end_time: end_time of classification data
        :return: last second from serial and panel if start_time and end_time are not provided,
         else all seconds from serial and panel between start_time and end_time
        """

        try:
            con = psycopg2.connect(database=DATABASE, user=USER)
        except Exception as e:
            raise psycopg2.Error("Database connection on classification data fetch failed", e)
        try:
            most_recent = False
            cursor = con.cursor()
            params = {'panel': panel,
                      'id': serial}
            query = "SELECT time, data - lag(data) OVER (ORDER BY time DESC) as data FROM data_raw \
                    WHERE device=%(panel)s and serial=%(id)s and time >= \
                    to_timestamp(%(start_time)s) and time <= to_timestamp(%(end_time)s);"
            params['start_time'] = start_time
            params['end_time'] = end_time

            cursor.execute(query, params)
            results = cursor.fetchall()

            # first result is null data, blows up classifier, so just omit it
            return results[1:]
        except Exception as e:
            raise psycopg2.Error("Classification data fetch failed", e)
        finally:
            if con:
                con.close()

    @staticmethod
    def training_data(panel="Panel1"):
        """
        :summary: grabs power data in data_raw that corresponds to the labels in data_label
        :param panel: which panel to fetch power data from, for all three call three times
        :return: data between all start_time and end_time in data_label with associated label
        """
        try:
            con = psycopg2.connect(database=DATABASE, user=USER)
        except psycopg2.Error as e:
            raise ConnectionError("Database connection on training data fetch failed", e)
        try:
            cursor = con.cursor()
            query = "SELECT data_raw.time, data_raw.data- lag(data_raw.data) OVER  \
                    (ORDER BY data_raw.time) as data, data_label.label  \
                    FROM data_raw, data_label  \
                    WHERE data_raw.serial=data_label.serial  \
                    AND data_raw.type='P'  \
                    AND data_raw.device=%(device)s \
                    AND time BETWEEN data_label.start_time AND data_label.end_time;"
            cursor.execute(query, {'device': panel})
            return cursor.fetchall()
        except psycopg2.Error as e:
            raise IOError("Training data fetch failed", e)
        finally:
            if con:
                con.close()


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

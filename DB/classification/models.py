import datetime
import pickle
import psycopg2
import uuid

USER = "seadapi"
DATABASE = "seads"


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
        :summary: BaseClassifier constructor
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
            con = psycopg2.connect(database=DATABASE, user=USER)
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
        """
        :summary: override this method in your derived classifier class to train your model
        """
        raise NotImplementedError

    def classify(self):
        """
        :summary: override this method in your derived classifier class to return a vector of labels
        """
        raise NotImplementedError

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
        except psycopg2.Error() as e:
            raise ConnectionError("Database connection on classification data fetch failed", e)
        try:
            most_recent = False
            cursor = con.cursor()
            params = {'panel': panel,
                      'id': serial}
            query = "SELECT time, data - lag(data) OVER (ORDER BY time DESC) as data FROM \
                        data_raw WHERE device=%(panel)s and serial=%(id)s"
            if start_time is None and end_time is None:
                query += "LIMIT 2;"
                most_recent = True
            else:
                query += "and time BETWEEN to_timestamp(%(start_time)s) and \
                to_timestamp(%(end_time)s);"
                params['start_time'] = start_time
                params['end_time'] = end_time

            cursor.execute(query, params)
            results = cursor.fetchall()
            if most_recent:
                return results[0]
            else:
                return results
        except psycopg2.Error() as e:
            raise IOError("Training data fetch failed", e)
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
            con = psycopg2.connect(database="seads", user="ianlofgren")
        except psycopg2.Error() as e:
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
        except psycopg2.Error() as e:
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


#print(str(BaseClassifier.training_data(panel="Panel3")))

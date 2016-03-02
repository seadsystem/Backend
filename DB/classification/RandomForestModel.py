import datetime
import math
import uuid
from sklearn.ensemble import RandomForestClassifier
import DB.classification.models as models

USER = "seadapi"
DATABASE = "seads"


class RandomForestModel(models.BaseClassifier):

    def __init__(self, date_time=datetime.datetime.utcnow(), model_field=None,
                 n_estimators=1000, max_depth=None, _id=str(uuid.uuid4()), min_samples_split=1,
                 max_features=2):
        if model_field is None:
            model = RandomForestClassifier(n_estimators=n_estimators,
                                           max_depth=max_depth,
                                           min_samples_split=min_samples_split,
                                           max_features=max_features)
        else:
            model = model_field

        super(RandomForestModel, self).__init__(model_type="RandomForestClassifier",
                                                created_at=date_time, model=model, _id=_id)

    def classify(self, start_time=datetime.datetime.now(),
                 end_time=None, panel=None, serial=None):
        end_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
        print(end_time)
        data = models.BaseClassifier.classification_data(start_time=start_time, end_time=end_time,
                                                         panel=panel, serial=serial)
        to_fit = RandomForestModel.create_samples(data)
        return self.model.predict(to_fit)

    def train(self):
        inputs = models.BaseClassifier.training_data()
        inputs2 = models.BaseClassifier.training_data(panel='Panel2')
        inputs3 = models.BaseClassifier.training_data(panel='Panel3')
        inputs.append(inputs2)
        inputs.append(inputs3)
        samples = RandomForestModel.create_samples(inputs)
        features = RandomForestModel.create_features(inputs)
        self.model.fit(samples, features)

    @staticmethod
    def get_model(_id):
        model_row = super(RandomForestModel, RandomForestModel).get_model(_id)
        model = RandomForestModel(date_time=model_row['created_at'], _id=model_row['id'],
                                  model_field=model_row['model'])
        return model

    @staticmethod
    def create_samples(inputs):
        print(inputs[:3])
        result = []
        for i in range(len(inputs)-1):
            result.append([inputs[i][1], inputs[i+1][1]])
        return result

    @staticmethod
    def create_features(inputs):
        print(inputs[:3])
        result = []
        for i in inputs[:-1]:
            result.append(ord(i[2][0]))
        return result


model2 = RandomForestModel()
model2.train()
model2.store()
modelDict = RandomForestModel.get_model(model2.id)
print(str(modelDict.model))
print(modelDict.classify(panel="Panel3", serial=466419818))

ourmodel = RandomForestModel()
ourmodel.train()
print(ourmodel.classify())

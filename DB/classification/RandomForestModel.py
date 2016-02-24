import datetime
from sklearn.ensemble import RandomForestClassifier
import DB.classification.models as models
import pickle
import psycopg2

USER = "seadapi"
DATABASE = "seads"

class RandomForestModel(models.BaseClassifier):
    def __init__(self, created_at=datetime.datetime.utcnow(), n_estimators=1000, max_depth=None,
                 min_samples_split=1, max_features=3, model_field=None, _id=None):

        if model_field is None:
            model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth,
                                           min_samples_split=min_samples_split,
                                           max_features=max_features)
        else:
            model = model_field
        super(RandomForestModel, self).__init__(model_type="RandomForestClassifier",
                                                created_at=created_at, model=model)

    def train(self):
        hello = "woah"

    def classify(self):
        hello = "woah"

    @staticmethod
    def get_model(_id):
        modelRow = super(RandomForestModel, RandomForestModel).get_model(_id)
        model = RandomForestModel(created_at=modelRow.created_at, _id=modelRow.id, model_field=modelRow)
        return model

model = RandomForestModel()
model.store()
modelDict = RandomForestModel.get_model(model.id)
print(str(modelDict))
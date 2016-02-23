import datetime
from sklearn.ensemble import RandomForestClassifier
import DB.classification.models as models


class RandomForestModel(models.BaseClassifier):
    def __init__(self,
                 date_time=datetime.datetime.utcnow().timestamp(),
                 n_estimators=1000,
                 max_depth=None,

                 min_samples_split=1,
                 max_features=3):
        model = RandomForestClassifier(n_estimators=n_estimators,
                                       max_depth=max_depth,
                                       min_samples_split=min_samples_split,
                                       max_features=max_features)
        super().__init__(model_type="RandomForestClassifier", created_at=date_time, model=model)

    def train(self):

        hello = "woah"

    def classify(self):
        hello = "woah"

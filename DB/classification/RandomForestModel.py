import datetime
from sklearn.ensemble import RandomForestClassifier
from models import ClassifierModel

class RandomForestModel(ClassifierModel):
    def __init__(self,
                 date_time=datetime.datetime.utcnow().timestamp(),
                 n_estimators=1000,
                 max_depth=None,
                 min_samples_split=1,
                 max_features=3):
        super().__init__(model_type="RandomForestClassifier", date_time=date_time)
        model = RandomForestClassifier(n_estimators=n_estimators,
                                            max_depth=max_depth,
                                            min_samples_split=min_samples_split,
                                            max_features=max_features)
        return self

    def train(self):
        hello = "woah"
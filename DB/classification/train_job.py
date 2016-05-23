from models import BaseClassifier
from RandomForestModel import RandomForestModel
from AdaBoostModel import AdaBoostModel

model_list = [RandomForestModel()]#, AdaBoostModel()]

train_data_panel1 = BaseClassifier.training_data("Panel1")
#train_data_panel2 = BaseClassifier.training_data("Panel2")
#train_data_panel3 = BaseClassifier.training_data("Panel3")

for model in model_list:
    model.train(train_data_panel1)
    #model.train(train_data_panel2)
    #model.train(train_data_panel3)
    model.store()

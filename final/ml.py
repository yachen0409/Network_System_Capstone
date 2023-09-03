import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
import warnings
import optuna
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.tree  import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.naive_bayes import BernoulliNB
from lightgbm import LGBMClassifier
from sklearn.feature_selection import RFE
import itertools
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
from tabulate import tabulate
import os
import pickle
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)
p = 0.01
# for dirname, _, filenames in os.walk('./data'):
#     for filename in filenames:
#         print(os.path.join(dirname, filename))
dataset=pd.read_csv('/home/iammrchen/Desktop/nscap/final/data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv').convert_dtypes()
dataset = dataset[~dataset.isin([np.nan, np.inf, -np.inf]).any(1)]
train, test = train_test_split(dataset, test_size=0.3)
# train = train[~train.isin([np.nan, np.inf, -np.inf]).any(1)]
# print(train.describe())
# print(inf.shape())
# test=pd.read_csv('./data/Test_data.csv')
##! 可有可無？
def le(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            label_encoder = LabelEncoder()
            df[col] = label_encoder.fit_transform(df[col])
        elif df[col].dtype == 'float64':
            print(f'hit float64! ({df[col]})')

le(train)
le(test)
##!end
# train.drop(['num_outbound_cmds'], axis=1, inplace=True)
# test.drop(['num_outbound_cmds'], axis=1, inplace=True)
# print(train)
# print(train.head())
# for key, value in train.items():
#      print(key)
X_train = train.drop(labels=["Label"], axis=1)
Y_train = train['Label']
X_test = test.drop(labels=["Label"], axis=1)
Y_test = test['Label']

rfc = RandomForestClassifier(verbose=True)
rfe = RFE(rfc, n_features_to_select=10)
rfe = rfe.fit(X_train, Y_train)

feature_map = [(i, v) for i, v in itertools.zip_longest(rfe.get_support(), X_train.columns)]
selected_features = [v for i, v in feature_map if i==True]
print(selected_features)
X_train = X_train[selected_features]
X_test = X_test[selected_features]
# print('end')

scale = StandardScaler()
X_train = scale.fit_transform(X_train)
X_test = scale.fit_transform(X_test)
# test = scale.fit_transform(test)

# x_train, x_test, y_train, y_test = train_test_split(X_train, Y_train, train_size=0.70, random_state=2)

# def objective(trial):
#     n_neighbors = trial.suggest_int('KNN_n_neighbors', 2, 16, log=False)
#     classifier_obj = KNeighborsClassifier(n_neighbors=n_neighbors)
#     classifier_obj.fit(x_train, y_train)
#     accuracy = classifier_obj.score(x_test, y_test)
#     return accuracy
# study_KNN = optuna.create_study(direction='maximize')
# # study_KNN.optimize(objective, n_trials=1)
# print(study_KNN.best_trial)
# KNN_model = KNeighborsClassifier(n_neighbors=study_KNN.best_trial.params['KNN_n_neighbors'])
KNN_model = KNeighborsClassifier()
KNN_model.fit(X_train, Y_train)

KNN_train, KNN_test = KNN_model.score(X_train, Y_train), KNN_model.score(X_test, Y_test)
prediction = KNN_model.predict(X_test)
# print(prediction)
# print(Y_test)
filename = f'model/KNN_model_{KNN_train}.pkl'
pickle.dump(KNN_model, open(filename, 'wb'))
print(f"Train Score: {KNN_train}")
print(f"Test Score: {KNN_test}")
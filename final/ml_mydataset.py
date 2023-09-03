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
import glob
import pickle
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)
p=0.1
# for dirname, _, filenames in os.walk('./data'):
#     for filename in filenames:
#         print(os.path.join(dirname, filename))
csv_files = glob.glob('mydata/*.{}'.format('csv'))
dataset = pd.concat([pd.read_csv(file) for file in csv_files ], ignore_index=True).convert_dtypes()
dataset = dataset.sample(frac=p)
print(dataset.info())
# dataset=pd.read_csv('/home/iammrchen/Desktop/nscap/final/data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv').convert_dtypes()
dataset = dataset[~dataset.isin([np.nan, np.inf, -np.inf]).any(1)].astype('str')
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
print('label encoding for train data......')
le(train)
print('label encoding for test data......')
le(test)
##!end
# train.drop(['num_outbound_cmds'], axis=1, inplace=True)
# test.drop(['num_outbound_cmds'], axis=1, inplace=True)
# print(train)
# print(train.head())
# for key, value in train.items():
#      print(key)
X_train = train.drop(labels=["label"], axis=1)
Y_train = train['label']
X_test = test.drop(labels=["label"], axis=1)
Y_test = test['label']

rfc = RandomForestClassifier(verbose=True)
rfe = RFE(rfc, n_features_to_select=10)
print('randomForestClassifing......')
rfe = rfe.fit(X_train, Y_train)

filename = f'model/my_RFE_model.pkl'
pickle.dump(rfe, open(filename, 'wb'))
feature_map = [(i, v) for i, v in itertools.zip_longest(rfe.get_support(), X_train.columns)]
selected_features = [v for i, v in feature_map if i==True]
# print(selected_features)
# print('-------------------------------------------')
X_train = X_train[selected_features]
X_test = X_test[selected_features]
# print('end')

scale = StandardScaler()
X_train = scale.fit_transform(X_train)
X_test = scale.fit_transform(X_test)

KNN_model = KNeighborsClassifier()
KNN_model.fit(X_train, Y_train)

KNN_train, KNN_test = KNN_model.score(X_train, Y_train), KNN_model.score(X_test, Y_test)
prediction = KNN_model.predict(X_test)
# print(prediction)
# print(Y_test)
filename = f'model/my_KNN_model_{KNN_train}.pkl'
pickle.dump(KNN_model, open(filename, 'wb'))
print(f"Train Score: {KNN_train}")
print(f"Test Score: {KNN_test}")
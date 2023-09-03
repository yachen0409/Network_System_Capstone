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
def verify(input_filename):
    warnings.filterwarnings('ignore')
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    # csv_files = glob.glob('testdata/*.{}'.format('csv'))
    p = 1
    dataset = pd.read_csv(input_filename).convert_dtypes()
    dataset = dataset.sample(frac=p)
    print(dataset.info())
    test = dataset[~dataset.isin([np.nan, np.inf, -np.inf]).any(1)].astype('str')
    # ##! 可有可無？
    def le(df):
        for col in df.columns:
            if df[col].dtype == 'object':
                label_encoder = LabelEncoder()
                df[col] = label_encoder.fit_transform(df[col])
            elif df[col].dtype == 'float64':
                print(f'hit float64! ({df[col]})')
    print('label encoding for test data......')
    le(test)
    ##!end
    if 'label' in dataset.columns:
        X_test = test.drop(labels=["label"], axis=1)
        # Y_test = test['label']
    else:
        X_test = test

    selected_features = None
    with open('model/my_RFE_model.pkl', 'rb') as file:
        rfe = pickle.load(file)
        feature_map = [(i, v) for i, v in itertools.zip_longest(rfe.get_support(), X_test.columns)]
        selected_features = [v for i, v in feature_map if i==True]
        print(selected_features)
        X_test = X_test[selected_features]
    filename = 'model/my_KNN_model_0.9997728821258233.pkl'
    with open(filename, 'rb') as file:
        KNN_model = pickle.load(file)
        prediction = KNN_model.predict(X_test)
        ddos_num = 0
        for result in prediction:
            if result == 1:
                ddos_num += 1
        print(prediction)
        print(f"DDoS Likelyhood: {ddos_num/len(prediction)}")
            
        

if __name__ == '__main__':
    input_filename = 'testdata/ddos_update_ddos2.csv'
    verify(input_filename)

# Import Modules
import datetime
import itertools
#import graphviz
import keras
import matplotlib.pyplot as plt
#import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn
#import tensorflow as tf


# Keras Imports
from keras import models, layers
from keras import regularizers
from keras.models import Model, load_model, Sequential
from keras.layers import Input, Dense, Dropout, Embedding
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn import preprocessing, model_selection

# Regression Example With Boston Dataset: Standardized and Larger
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
# load dataset


# Preprocesing
from sklearn.decomposition import PCA
from sklearn.externals import joblib
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.preprocessing import StandardScaler

# Sklearn Models
from sklearn.preprocessing import LabelEncoder
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.covariance import EllipticEnvelope
from sklearn.pipeline import make_pipeline
from sklearn.utils.class_weight import compute_sample_weight
from keras.utils import np_utils

# Metrics
from sklearn.metrics import (confusion_matrix, precision_recall_curve, auc,
                             roc_curve, recall_score, classification_report,
                             f1_score, precision_score, recall_score,
                             precision_recall_fscore_support, roc_auc_score)

# Model Selection
from sklearn.model_selection import (cross_val_score, KFold, train_test_split,
                                     GridSearchCV, cross_validate,
                                     StratifiedKFold)

# Set Numpy and Python Random Seed
seed = 7
np.random.seed(seed)



filename = "/home/bjur/PycharmProjects/invter_app/venv/data/BOMB_DB.csv"
df = pd.read_csv(filename, sep = ";", encoding='utf8',decimal=",")
df_melt = pd.melt(df, id_vars =["model","potencia_kW","potencia_cv"])
df = df_melt.dropna(subset=['variable', 'value'])
df['variable'] = df['variable'].replace(regex=',', value=".").astype(float)
df['value'] = df['value'].astype(float)
df['max_curve'] = df.groupby(['model'], group_keys=False).transform('max')['value']
df['min_curve'] = df.groupby(['model'], group_keys=False).transform('min')['value']
df['max_q'] = df.groupby(['model'], group_keys=False).transform('max')['variable']
df['min_q'] = df.groupby(['model'], group_keys=False).transform('min')['variable']
df['gradient'] = (df['max_q']-df['min_q'])/(df['max_curve']-df['min_curve'])

X = df[['gradient','value','potencia_kW']]
Y = df['variable']
# define the model



def larger_model():
	# create model
	model = Sequential()
	model.add(Dense(20, input_dim=3, kernel_initializer='normal', activation='relu'))
	model.add(Dense(20, kernel_initializer='normal', activation='relu'))
	model.add(Dense(20, kernel_initializer='normal', activation='relu'))
	model.add(Dense(1, kernel_initializer='normal'))
	# Compile model
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model


import pickle
# evaluate model with standardized dataset
#estimators = []
#estimators.append(('standardize', StandardScaler()))
#estimators.append(('mlp', KerasRegressor(build_fn=larger_model, epochs=100, batch_size=5, verbose=0)))
pipeline=KerasRegressor(build_fn=larger_model, epochs=100, batch_size=5, verbose=0)
#pipeline = Pipeline(estimators)
#kfold = KFold(n_splits=10)
#results = cross_val_score(pipeline, X, Y, cv=kfold)
pipeline.fit(X, Y)


#print("Larger: %.2f (%.2f) MSE" % (results.mean(), results.std()))

gra= 62.346
gra = 0.021
p_h= 340.000
pot = 4.00
Xnew = np.array([[0.021,300.000,4.00]])

result = pipeline.predict(Xnew)
print(result)

filename = '/home/bjur/PycharmProjects/invter_app/venv/data/finalized_modelB.sav'
#pickle.dump(pipeline, open(filename, 'wb'))
pipeline.model.save('modelBV1.h5')

from keras.models import load_model

# Instantiate the model as you please (we are not going to use this)
model2 = KerasRegressor(build_fn=larger_model, epochs=10, batch_size=10, verbose=1)


model2.model = load_model('modelBV1.h5')

# Now you can use this to predict on new data (without fitting model2, because it uses the older saved model)
print(model2.predict(Xnew))


#import joblib
#joblib.dump(pipeline, 'model_bomb.sav')
#print('Saved %s pipeline to file' % pipe_dict[best_clf])



# Regression Example With Boston Dataset: Standardized and Larger
#from pandas import read_csv
#from keras.models import Sequential
#from keras.layers import Dense
#import keras.backend as K
#from keras.wrappers.scikit_learn import KerasRegressor
#import keras
import tensorflow as tf

#from sklearn.model_selection import cross_val_score
#from sklearn.model_selection import KFold
#from sklearn.preprocessing import StandardScaler
#from sklearn.pipeline import Pipeline
# load dataset
#dataset = dataframe.values
# split into input (X) and output (Y) variables
#X = df[['gradient','value','potencia_kW']]
#Y = df['variable']
# define the model
def larger_model():
	# create model
	model =  tf.keras.Sequential()
	model.add( tf.keras.Dense(20, input_dim=3, kernel_initializer='normal', activation='relu'))
	model.add( tf.keras.Dense(20, kernel_initializer='normal', activation='relu'))
	model.add( tf.keras.Dense(20, kernel_initializer='normal', activation='relu'))
	model.add( tf.keras.Dense(1, kernel_initializer='normal'))
	# Compile model
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model

import pickle
import numpy as np
#gradiente,punto altura, potenciakw
Xnew = np.array([[0.021,300.000,4.00]])
filename ='/home/bjur/PycharmProjects/invter_app/venv/data/finalized_model.sav'
filename = "model_bomb.sav"
loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.predict(Xnew)
result

